#!/usr/bin/env python3
"""Calibration, ranking, and interpretation gate for production target families.

This script is deliberately report-only. Model and calibrator choices are made
on the validation period only; test-period results are final holdout diagnostics.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modeling.train_panel_v2_models import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_models as build_production_models,
    class_weight_sample,
    validate_features,
)
from scripts.modeling.run_exploratory_target_lab import (  # noqa: E402
    FINANCIAL_QUALITY_FEATURES,
    MARKET_HEALTH_FEATURES,
    add_exploratory_targets,
    add_financial_quality_features,
    add_market_health_v2_features,
    build_features as build_exploratory_features,
    build_model as build_exploratory_model,
    clean_financial_quality_extremes,
    feature_group,
    make_splits,
)


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
MODELING_DIR = PROJECT_ROOT / "reports/modeling"
TARGET_LAB_DIR = PROJECT_ROOT / "reports/target_lab"
FIG_MODELING_DIR = PROJECT_ROOT / "reports/figures/modeling"
FIG_CALIBRATION_DIR = FIG_MODELING_DIR / "calibration_curves"
FIG_TARGET_LAB_DIR = PROJECT_ROOT / "reports/figures/target_lab"

DATE_COLS = ["period_date", "filed_date", "prediction_date", "event_date"]

PRODUCTION_TARGETS = [
    "distress_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "success_resilience_next_4q",
]

VALIDATED_SECONDARY_TARGETS = [
    "industry_relative_resilience_next_4obs",
    "stress_resilience_next_4obs",
    "recovery_next_4obs",
    "quality_success_cashflow_next_4obs",
]

ROBUSTNESS_EXTENSION_TARGETS = [
    "sector_relative_improvement_next_4obs",
    "persistent_resilience_next_6obs",
]

RANKING_TOP_PCTS = [0.01, 0.05, 0.10]
PROBABILITY_THRESHOLDS = [0.10, 0.25, 0.50, 0.75, 0.90]
MIN_KNOWN_ROWS = 1_000
MIN_POSITIVES = 50
MIN_TEST_POSITIVES = 10


@dataclass
class TargetRun:
    target: str
    target_family: str
    selected_model_name: str
    selected_model: object
    features: list[str]
    splits: dict[str, pd.DataFrame]
    raw_probabilities: dict[str, np.ndarray]
    calibrated_probabilities: dict[str, dict[str, np.ndarray]]
    selected_calibrator: str
    validation_pr_auc: float
    validation_brier: float


class IdentityCalibrator:
    def fit(self, scores: np.ndarray, y: np.ndarray) -> "IdentityCalibrator":
        return self

    def predict(self, scores: np.ndarray) -> np.ndarray:
        return np.clip(scores, 0.0, 1.0)


class SigmoidCalibrator:
    def __init__(self) -> None:
        self.model = LogisticRegression(solver="lbfgs", max_iter=1000)

    def fit(self, scores: np.ndarray, y: np.ndarray) -> "SigmoidCalibrator":
        self.model.fit(scores.reshape(-1, 1), y)
        return self

    def predict(self, scores: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(scores.reshape(-1, 1))[:, 1]


class IsotonicCalibrator:
    def __init__(self) -> None:
        self.model = IsotonicRegression(out_of_bounds="clip")

    def fit(self, scores: np.ndarray, y: np.ndarray) -> "IsotonicCalibrator":
        self.model.fit(scores, y)
        return self

    def predict(self, scores: np.ndarray) -> np.ndarray:
        return np.asarray(self.model.predict(scores), dtype=float)


def load_base_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_candidates = set(NUMERIC_FEATURES) | {
        *PRODUCTION_TARGETS,
        "post_event_flag",
        "formal_distress_firm",
    }
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).reset_index(drop=True)


def load_exploratory_frame(base: pd.DataFrame) -> pd.DataFrame:
    df = add_financial_quality_features(base)
    df = clean_financial_quality_extremes(df)
    df, _coverage = add_market_health_v2_features(df)
    return add_exploratory_targets(df)


def prepare_target_frame(df: pd.DataFrame, target: str) -> pd.DataFrame:
    frame = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    if "post_event_flag" in frame.columns:
        frame = frame[frame["post_event_flag"].fillna(0).astype(int) == 0].copy()
    frame = frame[frame[target].notna()].copy()
    frame[target] = frame[target].astype(int)
    return frame


def candidate_models(target_family: str, features: list[str]) -> dict[str, object]:
    if target_family == "production":
        return build_production_models()
    return {
        name: build_exploratory_model(name, features)
        for name in ["logistic_l2", "random_forest", "gradient_boosting"]
    }


def fit_model(model: object, model_name: str, x_train: pd.DataFrame, y_train: pd.Series) -> None:
    if model_name == "gradient_boosting":
        model.fit(x_train, y_train, model__sample_weight=class_weight_sample(y_train))
    else:
        model.fit(x_train, y_train)


def binary_auc(y_true: np.ndarray, proba: np.ndarray, metric: str) -> float:
    if len(np.unique(y_true)) < 2:
        return np.nan
    if metric == "roc_auc":
        return float(roc_auc_score(y_true, proba))
    if metric == "pr_auc":
        return float(average_precision_score(y_true, proba))
    raise ValueError(metric)


def choose_threshold(y_true: np.ndarray, proba: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return 0.5
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    if len(thresholds) == 0:
        return 0.5
    f1_values = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(f1_values))])


def expected_calibration_error(y_true: np.ndarray, proba: np.ndarray, bins: int = 10) -> float:
    frame = pd.DataFrame({"y": y_true, "p": np.clip(proba, 0.0, 1.0)})
    frame["bin"] = pd.qcut(frame["p"].rank(method="first"), q=min(bins, len(frame)), duplicates="drop")
    ece = 0.0
    for _bin, group in frame.groupby("bin", observed=True):
        weight = len(group) / len(frame)
        ece += weight * abs(group["y"].mean() - group["p"].mean())
    return float(ece)


def fit_calibrators(y_val: np.ndarray, val_scores: np.ndarray) -> dict[str, object]:
    calibrators = {
        "uncalibrated": IdentityCalibrator(),
        "sigmoid_validation": SigmoidCalibrator(),
        "isotonic_validation": IsotonicCalibrator(),
    }
    fitted = {}
    for name, calibrator in calibrators.items():
        try:
            fitted[name] = calibrator.fit(np.asarray(val_scores, dtype=float), y_val)
        except Exception as exc:  # pragma: no cover - defensive report path
            print(f"Skipping calibrator {name}: {exc}")
    return fitted


def calibration_metric_row(
    target: str,
    target_family: str,
    model_name: str,
    calibrator_name: str,
    split_name: str,
    y_true: np.ndarray,
    proba: np.ndarray,
    selected_model: bool,
    selected_calibrator: bool,
) -> dict[str, object]:
    proba = np.clip(proba, 0.0, 1.0)
    return {
        "target": target,
        "target_family": target_family,
        "model": model_name,
        "calibrator": calibrator_name,
        "split": split_name,
        "rows": int(len(y_true)),
        "positives": int(y_true.sum()),
        "positive_share": float(y_true.mean()) if len(y_true) else np.nan,
        "brier_score": float(brier_score_loss(y_true, proba)) if len(y_true) else np.nan,
        "log_loss": float(log_loss(y_true, proba, labels=[0, 1])) if len(np.unique(y_true)) > 1 else np.nan,
        "expected_calibration_error_10bin": expected_calibration_error(y_true, proba) if len(y_true) else np.nan,
        "roc_auc": binary_auc(y_true, proba, "roc_auc"),
        "pr_auc": binary_auc(y_true, proba, "pr_auc"),
        "mean_predicted_probability": float(np.mean(proba)) if len(proba) else np.nan,
        "observed_positive_rate": float(y_true.mean()) if len(y_true) else np.nan,
        "selected_model_by_validation_pr_auc": selected_model,
        "selected_calibrator_by_validation_brier": selected_calibrator,
        "selection_note": "model selected by validation PR-AUC; calibrator selected by validation Brier score",
    }


def threshold_row(
    target: str,
    target_family: str,
    model_name: str,
    calibrator_name: str,
    split_name: str,
    y_true: np.ndarray,
    proba: np.ndarray,
    threshold: float,
    threshold_type: str,
    threshold_label: str,
) -> dict[str, object]:
    y_pred = (proba >= threshold).astype(int)
    predicted = int(y_pred.sum())
    return {
        "target": target,
        "target_family": target_family,
        "model": model_name,
        "calibrator": calibrator_name,
        "split": split_name,
        "threshold_type": threshold_type,
        "threshold_label": threshold_label,
        "threshold": float(threshold),
        "rows": int(len(y_true)),
        "positives": int(y_true.sum()),
        "selected_rows": predicted,
        "selected_share": predicted / len(y_true) if len(y_true) else np.nan,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "base_rate": float(y_true.mean()) if len(y_true) else np.nan,
        "lift_vs_base_rate": (
            precision_score(y_true, y_pred, zero_division=0) / float(y_true.mean())
            if len(y_true) and float(y_true.mean()) > 0
            else np.nan
        ),
    }


def ranking_rows(
    target: str,
    target_family: str,
    model_name: str,
    calibrator_name: str,
    split_name: str,
    y_true: np.ndarray,
    proba: np.ndarray,
) -> list[dict[str, object]]:
    rows = []
    for pct in RANKING_TOP_PCTS:
        n = max(1, int(math.ceil(len(proba) * pct)))
        order = np.argsort(-proba)
        selected = order[:n]
        cutoff = float(np.min(proba[selected])) if len(selected) else 1.0
        y_pred = np.zeros_like(y_true, dtype=int)
        y_pred[selected] = 1
        rows.append(
            {
                "target": target,
                "target_family": target_family,
                "model": model_name,
                "calibrator": calibrator_name,
                "split": split_name,
                "threshold_type": "top_rank_share",
                "threshold_label": f"top_{int(pct * 100)}pct",
                "threshold": cutoff,
                "rows": int(len(y_true)),
                "positives": int(y_true.sum()),
                "selected_rows": int(n),
                "selected_share": float(pct),
                "precision": precision_score(y_true, y_pred, zero_division=0),
                "recall": recall_score(y_true, y_pred, zero_division=0),
                "f1": f1_score(y_true, y_pred, zero_division=0),
                "base_rate": float(y_true.mean()) if len(y_true) else np.nan,
                "lift_vs_base_rate": (
                    precision_score(y_true, y_pred, zero_division=0) / float(y_true.mean())
                    if len(y_true) and float(y_true.mean()) > 0
                    else np.nan
                ),
            }
        )
    for threshold in PROBABILITY_THRESHOLDS:
        rows.append(
            threshold_row(
                target,
                target_family,
                model_name,
                calibrator_name,
                split_name,
                y_true,
                proba,
                threshold,
                "probability_threshold",
                f"p_ge_{threshold:.2f}",
            )
        )
    f1_threshold = choose_threshold(y_true, proba)
    rows.append(
        threshold_row(
            target,
            target_family,
            model_name,
            calibrator_name,
            split_name,
            y_true,
            proba,
            f1_threshold,
            "split_f1_optimal_diagnostic",
            "diagnostic_split_f1_optimal",
        )
    )
    return rows


def run_target_models(
    df: pd.DataFrame,
    target: str,
    target_family: str,
    features: list[str],
) -> tuple[TargetRun | None, list[dict[str, object]]]:
    target_frame = prepare_target_frame(df, target)
    known_rows = len(target_frame)
    positives = int(target_frame[target].sum()) if known_rows else 0
    if known_rows < MIN_KNOWN_ROWS or positives < MIN_POSITIVES:
        return None, [
            {
                "target": target,
                "target_family": target_family,
                "status": "SKIPPED",
                "known_rows": known_rows,
                "positives": positives,
                "reason": f"below minimum known rows ({MIN_KNOWN_ROWS}) or positives ({MIN_POSITIVES})",
            }
        ]

    splits = make_splits(target_frame)
    if any(split.empty or split[target].nunique() < 2 for split in splits.values()):
        return None, [
            {
                "target": target,
                "target_family": target_family,
                "status": "SKIPPED",
                "known_rows": known_rows,
                "positives": positives,
                "reason": "one or more temporal splits has fewer than two classes",
            }
        ]
    if int(splits["test"][target].sum()) < MIN_TEST_POSITIVES:
        return None, [
            {
                "target": target,
                "target_family": target_family,
                "status": "SKIPPED",
                "known_rows": known_rows,
                "positives": positives,
                "reason": f"test positives below {MIN_TEST_POSITIVES}",
            }
        ]

    x_train = splits["train"][features]
    y_train = splits["train"][target].astype(int)
    x_val = splits["validation"][features]
    y_val = splits["validation"][target].astype(int)
    x_test = splits["test"][features]
    y_test = splits["test"][target].astype(int)

    model_selection_rows = []
    fitted_models: dict[str, object] = {}
    raw_probability_by_model: dict[str, dict[str, np.ndarray]] = {}

    for model_name, model in candidate_models(target_family, features).items():
        print(f"Training {target} / {model_name}")
        fit_model(model, model_name, x_train, y_train)
        fitted_models[model_name] = model

        split_scores = {
            "train": model.predict_proba(x_train)[:, 1],
            "validation": model.predict_proba(x_val)[:, 1],
            "test": model.predict_proba(x_test)[:, 1],
        }
        raw_probability_by_model[model_name] = split_scores
        for split_name, split_df in splits.items():
            y_split = split_df[target].astype(int).to_numpy()
            proba = split_scores[split_name]
            model_selection_rows.append(
                {
                    "target": target,
                    "target_family": target_family,
                    "model": model_name,
                    "split": split_name,
                    "rows": int(len(y_split)),
                    "positives": int(y_split.sum()),
                    "roc_auc": binary_auc(y_split, proba, "roc_auc"),
                    "pr_auc": binary_auc(y_split, proba, "pr_auc"),
                    "brier_score_uncalibrated": float(brier_score_loss(y_split, np.clip(proba, 0.0, 1.0))),
                    "selection_metric": "validation_pr_auc",
                }
            )

    selection_frame = pd.DataFrame(model_selection_rows)
    validation_rows = selection_frame[selection_frame["split"] == "validation"].copy()
    selected_model_name = (
        validation_rows.sort_values(["pr_auc", "roc_auc"], ascending=False)
        .iloc[0]["model"]
    )
    selected_model = fitted_models[str(selected_model_name)]
    raw_probabilities = raw_probability_by_model[str(selected_model_name)]

    y_val_np = y_val.to_numpy()
    calibrators = fit_calibrators(y_val_np, raw_probabilities["validation"])
    calibrated_probabilities = {
        calibrator_name: {
            split_name: calibrator.predict(scores)
            for split_name, scores in raw_probabilities.items()
        }
        for calibrator_name, calibrator in calibrators.items()
    }

    validation_briers = {
        name: brier_score_loss(y_val_np, np.clip(scores_by_split["validation"], 0.0, 1.0))
        for name, scores_by_split in calibrated_probabilities.items()
    }
    selected_calibrator = min(validation_briers, key=validation_briers.get)

    validation_pr_auc = float(
        validation_rows[validation_rows["model"] == selected_model_name]["pr_auc"].iloc[0]
    )
    return (
        TargetRun(
            target=target,
            target_family=target_family,
            selected_model_name=str(selected_model_name),
            selected_model=selected_model,
            features=features,
            splits=splits,
            raw_probabilities=raw_probabilities,
            calibrated_probabilities=calibrated_probabilities,
            selected_calibrator=selected_calibrator,
            validation_pr_auc=validation_pr_auc,
            validation_brier=float(validation_briers[selected_calibrator]),
        ),
        model_selection_rows,
    )


def write_calibration_plot(run: TargetRun) -> None:
    FIG_CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    selected = run.selected_calibrator
    plt.figure(figsize=(7, 6))
    for split_name in ["validation", "test"]:
        y_true = run.splits[split_name][run.target].astype(int).to_numpy()
        proba = np.clip(run.calibrated_probabilities[selected][split_name], 0.0, 1.0)
        frame = pd.DataFrame({"y": y_true, "p": proba})
        frame["bin"] = pd.qcut(frame["p"].rank(method="first"), q=min(10, len(frame)), duplicates="drop")
        curve = frame.groupby("bin", observed=True).agg(mean_pred=("p", "mean"), observed=("y", "mean"))
        plt.plot(curve["mean_pred"], curve["observed"], marker="o", label=split_name)
    plt.plot([0, 1], [0, 1], color="black", linewidth=1, linestyle="--")
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Observed positive rate")
    plt.title(f"Calibration curve: {run.target}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_CALIBRATION_DIR / f"{run.target}_calibration_curve.png", dpi=180)
    plt.close()


def transformed_feature_frame(run: TargetRun, split_name: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    x_split = run.splits[split_name][run.features]
    y_true = run.splits[split_name][run.target].astype(int).to_numpy()
    preprocessor = run.selected_model.named_steps["preprocess"]
    transformed = preprocessor.transform(x_split)
    names = preprocessor.get_feature_names_out()
    if not isinstance(transformed, np.ndarray):
        transformed = transformed.toarray()
    frame = pd.DataFrame(transformed, columns=names, index=x_split.index)
    return frame, y_true, run.calibrated_probabilities[run.selected_calibrator][split_name]


def clean_feature_name(name: str) -> str:
    raw = name.replace("num__", "").replace("cat__", "")
    if raw.startswith("missingindicator_"):
        return "Missing value: " + raw.replace("missingindicator_", "")
    if raw.startswith("Sector_"):
        return "Sector: " + raw.replace("Sector_", "")
    return raw


def base_feature_name(name: str) -> str:
    raw = name.replace("num__", "").replace("cat__", "")
    if raw.startswith("missingindicator_"):
        return raw.replace("missingindicator_", "")
    if raw.startswith("Sector_"):
        return "Sector"
    return raw


def reason_code(name: str) -> str:
    group = feature_group(name)
    raw = base_feature_name(name)
    if "missingindicator_" in name:
        return "data_availability_signal"
    if raw in FINANCIAL_QUALITY_FEATURES:
        return "cash_flow_quality"
    if raw in MARKET_HEALTH_FEATURES:
        return "market_stress_regime"
    if group == "macro_conditions":
        if raw in {"BAMLH0A0HYM2", "NFCI", "DRTSCILM", "T10Y2Y", "T10Y3M", "BUSLOANS", "BUSLOANS_yoy_pct"}:
            return "credit_and_financial_conditions"
        if raw in {"INDPRO", "INDPRO_yoy_pct", "PAYEMS", "PAYEMS_yoy_pct", "RSAFS", "RSAFS_yoy_pct", "HOUST", "HOUST_yoy_pct", "UNRATE", "GDPC1"}:
            return "real_activity_conditions"
        return "macro_price_policy_conditions"
    if group == "global_event_context":
        return "global_event_exposure"
    if group == "industry_sector":
        return "sector_positioning"
    if group == "firm_trend":
        return "firm_momentum_or_deterioration"
    if raw in {"leverage_assets", "equity_assets", "current_ratio", "cash_assets"}:
        return "balance_sheet_leverage_liquidity"
    if raw in {"net_margin", "operating_margin", "gross_margin", "roa", "r_and_d_intensity", "inventory_assets", "receivables_assets"}:
        return "profitability_and_efficiency"
    if raw in {"total_liabilities", "long_term_debt", "short_term_debt", "current_liabilities"}:
        return "balance_sheet_obligations"
    if raw in {"net_income", "gross_profit", "operating_income", "total_revenue"}:
        return "earnings_and_scale"
    if raw in {"total_assets", "current_assets", "cash_equivalents", "total_equity", "capex", "cash_flow_operating"}:
        return "asset_base_liquidity_and_investment"
    return "accounting_fundamentals"


def native_importance(run: TargetRun) -> pd.DataFrame:
    estimator = run.selected_model.named_steps["model"]
    names = run.selected_model.named_steps["preprocess"].get_feature_names_out()
    if hasattr(estimator, "coef_"):
        signed_values = estimator.coef_[0]
        values = np.abs(signed_values)
        coefficient_sign = np.sign(signed_values)
    elif hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
        coefficient_sign = np.full(len(values), np.nan)
    else:
        return pd.DataFrame()

    frame = pd.DataFrame(
        {
            "target": run.target,
            "target_family": run.target_family,
            "model": run.selected_model_name,
            "selected_calibrator": run.selected_calibrator,
            "feature": names,
            "feature_clean": [clean_feature_name(name) for name in names],
            "base_feature": [base_feature_name(name) for name in names],
            "feature_group": [feature_group(name) for name in names],
            "reason_code": [reason_code(name) for name in names],
            "native_importance": values,
            "coefficient_sign_if_linear": coefficient_sign,
        }
    )
    total = frame["native_importance"].sum()
    frame["native_importance_share"] = frame["native_importance"] / total if total else np.nan
    return frame.sort_values("native_importance", ascending=False)


def direction_effects(run: TargetRun, importance: pd.DataFrame) -> pd.DataFrame:
    transformed, y_true, proba = transformed_feature_frame(run, "test")
    rows = []
    top_features = importance.head(60)["feature"].tolist()
    top_cutoff = np.quantile(proba, 0.90) if len(proba) else np.nan
    top_score_mask = proba >= top_cutoff

    for feature in top_features:
        if feature not in transformed.columns:
            continue
        values = transformed[feature].astype(float)
        valid = values.notna() & pd.Series(proba, index=values.index).notna()
        if valid.sum() < 20 or values.loc[valid].nunique(dropna=True) < 2:
            spearman = np.nan
        else:
            spearman = float(values.loc[valid].corr(pd.Series(proba, index=values.index).loc[valid], method="spearman"))
        top_mean = float(values.loc[top_score_mask].mean()) if top_score_mask.any() else np.nan
        rest_mean = float(values.loc[~top_score_mask].mean()) if (~top_score_mask).any() else np.nan
        mean_positive = float(values.loc[y_true == 1].mean()) if (y_true == 1).any() else np.nan
        mean_negative = float(values.loc[y_true == 0].mean()) if (y_true == 0).any() else np.nan
        diff_top_rest = top_mean - rest_mean if pd.notna(top_mean) and pd.notna(rest_mean) else np.nan
        if pd.notna(diff_top_rest) and abs(diff_top_rest) > 1e-9:
            direction = "higher_values_associated_with_higher_model_score" if diff_top_rest > 0 else "lower_values_associated_with_higher_model_score"
        elif pd.notna(spearman) and abs(spearman) > 1e-9:
            direction = "higher_values_associated_with_higher_model_score" if spearman > 0 else "lower_values_associated_with_higher_model_score"
        else:
            direction = "direction_unclear_or_flat"
        rows.append(
            {
                "target": run.target,
                "target_family": run.target_family,
                "model": run.selected_model_name,
                "calibrator": run.selected_calibrator,
                "feature": feature,
                "feature_clean": clean_feature_name(feature),
                "base_feature": base_feature_name(feature),
                "feature_group": feature_group(feature),
                "reason_code": reason_code(feature),
                "test_spearman_feature_vs_score": spearman,
                "test_top_decile_mean": top_mean,
                "test_rest_mean": rest_mean,
                "test_top_decile_minus_rest": diff_top_rest,
                "test_positive_class_mean": mean_positive,
                "test_negative_class_mean": mean_negative,
                "test_positive_minus_negative": mean_positive - mean_negative if pd.notna(mean_positive) and pd.notna(mean_negative) else np.nan,
                "direction_label": direction,
                "direction_interpretation": "Association with model score on the temporal test split; not a causal effect.",
            }
        )
    return pd.DataFrame(rows)


def permutation_feature_importance(run: TargetRun) -> pd.DataFrame:
    x_test = run.splits["test"][run.features]
    y_test = run.splits["test"][run.target].astype(int)
    if y_test.nunique() < 2:
        return pd.DataFrame()
    n_rows = min(len(x_test), 4_000)
    sample = x_test.sample(n=n_rows, random_state=42) if len(x_test) > n_rows else x_test
    y_sample = y_test.loc[sample.index]
    result = permutation_importance(
        run.selected_model,
        sample,
        y_sample,
        scoring="average_precision",
        n_repeats=5,
        random_state=42,
        # Serial execution avoids sandbox semaphore failures from joblib's
        # process backend and keeps this report reproducible on restricted runs.
        n_jobs=1,
    )
    out = pd.DataFrame(
        {
            "target": run.target,
            "target_family": run.target_family,
            "model": run.selected_model_name,
            "feature": run.features,
            "feature_clean": [clean_feature_name(feature) for feature in run.features],
            "base_feature": run.features,
            "feature_group": [feature_group(feature) for feature in run.features],
            "reason_code": [reason_code(feature) for feature in run.features],
            "permutation_importance_mean_pr_auc_drop": result.importances_mean,
            "permutation_importance_std": result.importances_std,
            "scoring": "average_precision",
            "split": "test",
            "sample_rows": len(sample),
            "interpretation_note": "Drop in PR-AUC after permuting one raw input column on the temporal test split; not causal.",
        }
    )
    return out.sort_values("permutation_importance_mean_pr_auc_drop", ascending=False)


def reason_summary(importance: pd.DataFrame, direction: pd.DataFrame, permutation: pd.DataFrame) -> pd.DataFrame:
    if importance.empty:
        return pd.DataFrame()
    merged = importance.merge(
        direction[["target", "feature", "direction_label", "test_top_decile_minus_rest"]],
        on=["target", "feature"],
        how="left",
    )
    rows = []
    for (target, model, reason), group in merged.groupby(["target", "model", "reason_code"], observed=True):
        perm_group = permutation[(permutation["target"] == target) & (permutation["reason_code"] == reason)]
        positive_direction = int((group["direction_label"] == "higher_values_associated_with_higher_model_score").sum())
        negative_direction = int((group["direction_label"] == "lower_values_associated_with_higher_model_score").sum())
        if positive_direction > negative_direction:
            dominant_direction = "mostly_higher_values_raise_model_score"
        elif negative_direction > positive_direction:
            dominant_direction = "mostly_lower_values_raise_model_score"
        else:
            dominant_direction = "mixed_or_unclear"
        top_features = (
            group.sort_values("native_importance", ascending=False)["feature_clean"]
            .head(5)
            .tolist()
        )
        rows.append(
            {
                "target": target,
                "model": model,
                "reason_code": reason,
                "native_importance_share": float(group["native_importance_share"].sum()),
                "top_native_features": "; ".join(top_features),
                "dominant_direction_label": dominant_direction,
                "positive_direction_feature_count": positive_direction,
                "negative_direction_feature_count": negative_direction,
                "permutation_importance_mean_pr_auc_drop": (
                    float(perm_group["permutation_importance_mean_pr_auc_drop"].sum())
                    if not perm_group.empty
                    else np.nan
                ),
                "interpretation_note": "Reason codes summarize model associations; they are not causal mechanisms.",
            }
        )
    return pd.DataFrame(rows).sort_values(["target", "native_importance_share"], ascending=[True, False])


def plot_top_interpretation(importance: pd.DataFrame) -> None:
    if importance.empty:
        return
    FIG_TARGET_LAB_DIR.mkdir(parents=True, exist_ok=True)
    for target, group in importance.groupby("target"):
        top = group.sort_values("native_importance", ascending=True).tail(15)
        plt.figure(figsize=(9, 6))
        plt.barh(top["feature_clean"], top["native_importance"])
        plt.xlabel("Native model importance")
        plt.title(f"Exploratory feature importance: {target}")
        plt.tight_layout()
        plt.savefig(FIG_TARGET_LAB_DIR / f"{target}_feature_level_importance.png", dpi=180)
        plt.close()


def markdown_table(df: pd.DataFrame) -> str:
    """Render a compact GitHub-style markdown table without optional deps."""
    if df.empty:
        return ""
    text = df.fillna("").astype(str)
    columns = list(text.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in text.itertuples(index=False):
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def write_summary(
    runs: list[TargetRun],
    calibration_metrics: pd.DataFrame,
    ranking_metrics: pd.DataFrame,
    reason_codes: pd.DataFrame,
    model_selection: pd.DataFrame,
    skipped: list[dict[str, object]],
) -> None:
    TARGET_LAB_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Validation Extension Gate Summary",
        "",
        "Generated by `scripts/modeling/run_validation_extension_gate.py`.",
        "",
        "This gate adds calibration, ranking, and feature-level interpretation diagnostics across primary production, validated secondary production, and robustness-extension targets.",
        "",
        "## Selection Policy",
        "",
        "- Candidate base models are selected by validation-period PR-AUC.",
        "- Probability calibrators are fitted on the validation period and selected by validation Brier score.",
        "- Test-period metrics are final holdout diagnostics and are not used for model or calibrator selection.",
        "",
        "## Selected Models and Calibrators",
        "",
    ]
    if runs:
        selected = pd.DataFrame(
            [
                {
                    "target": run.target,
                    "family": run.target_family,
                    "model": run.selected_model_name,
                    "calibrator": run.selected_calibrator,
                    "validation_pr_auc": round(run.validation_pr_auc, 4),
                    "validation_brier": round(run.validation_brier, 4),
                }
                for run in runs
            ]
        )
        lines.append(markdown_table(selected))
    else:
        lines.append("_No target passed the gate._")
    lines.extend(["", "## Test Calibration Metrics", ""])
    if not calibration_metrics.empty:
        selected_test = calibration_metrics[
            (calibration_metrics["split"] == "test")
            & (calibration_metrics["selected_model_by_validation_pr_auc"])
            & (calibration_metrics["selected_calibrator_by_validation_brier"])
        ].copy()
        lines.append(
            selected_test[
                [
                    "target",
                    "target_family",
                    "model",
                    "calibrator",
                    "rows",
                    "positives",
                    "brier_score",
                    "expected_calibration_error_10bin",
                    "roc_auc",
                    "pr_auc",
                    "mean_predicted_probability",
                    "observed_positive_rate",
                ]
            ]
            .round(4)
            .pipe(markdown_table)
        )
    else:
        lines.append("_No calibration metrics were generated._")
    lines.extend(["", "## Test Ranking Snapshot", ""])
    ranking_snapshot = ranking_metrics[
        (ranking_metrics["split"] == "test")
        & (ranking_metrics["threshold_type"] == "top_rank_share")
        & (ranking_metrics["threshold_label"].isin(["top_1pct", "top_5pct", "top_10pct"]))
    ].copy()
    if not ranking_snapshot.empty:
        lines.append(
            ranking_snapshot[
                [
                    "target",
                    "threshold_label",
                    "selected_rows",
                    "precision",
                    "recall",
                    "lift_vs_base_rate",
                ]
            ]
            .round(4)
            .pipe(markdown_table)
        )
    else:
        lines.append("_No ranking metrics were generated._")
    lines.extend(["", "## Extension Reason-Code Snapshot", ""])
    if not reason_codes.empty:
        top_reasons = reason_codes.groupby("target", as_index=False, group_keys=False).head(5)
        lines.append(
            top_reasons[
                [
                    "target",
                    "reason_code",
                    "native_importance_share",
                    "dominant_direction_label",
                    "top_native_features",
                ]
            ]
            .round(4)
            .pipe(markdown_table)
        )
    else:
        lines.append("_No secondary/extension reason-code output was generated._")
    if skipped:
        lines.extend(["", "## Skipped Targets", "", markdown_table(pd.DataFrame(skipped))])
    lines.extend(
        [
            "",
            "## Files Written",
            "",
            "- `reports/modeling/calibration_metrics.csv`",
            "- `reports/modeling/threshold_ranking_metrics.csv`",
            "- `reports/modeling/calibration_model_selection.csv`",
            "- `reports/target_lab/exploratory_feature_level_importance.csv`",
            "- `reports/target_lab/exploratory_feature_direction_effects.csv`",
            "- `reports/target_lab/exploratory_permutation_importance.csv`",
            "- `reports/target_lab/exploratory_reason_code_summary.csv`",
            "- `reports/figures/modeling/calibration_curves/`",
            "- `reports/figures/target_lab/*_feature_level_importance.png`",
        ]
    )
    (TARGET_LAB_DIR / "validation_extension_gate_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    MODELING_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_LAB_DIR.mkdir(parents=True, exist_ok=True)
    FIG_CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    FIG_TARGET_LAB_DIR.mkdir(parents=True, exist_ok=True)

    base = load_base_panel()
    exploratory = load_exploratory_frame(base)

    production_features = validate_features(base, NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    exploratory_features = build_exploratory_features(exploratory)

    target_specs = [
        *[(target, "production", base, production_features) for target in PRODUCTION_TARGETS],
        *[
            (target, "validated_secondary_production", exploratory, exploratory_features)
            for target in VALIDATED_SECONDARY_TARGETS
        ],
        *[(target, "robustness_extension", exploratory, exploratory_features) for target in ROBUSTNESS_EXTENSION_TARGETS],
    ]

    runs: list[TargetRun] = []
    skipped: list[dict[str, object]] = []
    model_selection_rows: list[dict[str, object]] = []
    calibration_rows: list[dict[str, object]] = []
    ranking_metric_rows: list[dict[str, object]] = []
    feature_importance_frames: list[pd.DataFrame] = []
    direction_frames: list[pd.DataFrame] = []
    permutation_frames: list[pd.DataFrame] = []

    for target, target_family, df, features in target_specs:
        run, selection_or_skip = run_target_models(df, target, target_family, features)
        if run is None:
            skipped.extend(selection_or_skip)
            continue
        runs.append(run)
        model_selection_rows.extend(selection_or_skip)

        for calibrator_name, split_scores in run.calibrated_probabilities.items():
            for split_name in ["validation", "test"]:
                y_true = run.splits[split_name][run.target].astype(int).to_numpy()
                proba = np.clip(split_scores[split_name], 0.0, 1.0)
                calibration_rows.append(
                    calibration_metric_row(
                        run.target,
                        run.target_family,
                        run.selected_model_name,
                        calibrator_name,
                        split_name,
                        y_true,
                        proba,
                        True,
                        calibrator_name == run.selected_calibrator,
                    )
                )
                if calibrator_name == run.selected_calibrator:
                    ranking_metric_rows.extend(
                        ranking_rows(
                            run.target,
                            run.target_family,
                            run.selected_model_name,
                            calibrator_name,
                            split_name,
                            y_true,
                            proba,
                        )
                    )
        write_calibration_plot(run)

        if run.target_family in {"validated_secondary_production", "robustness_extension"}:
            importance = native_importance(run)
            direction = direction_effects(run, importance)
            permutation = permutation_feature_importance(run)
            if not importance.empty:
                feature_importance_frames.append(importance)
            if not direction.empty:
                direction_frames.append(direction)
            if not permutation.empty:
                permutation_frames.append(permutation)

    model_selection = pd.DataFrame(model_selection_rows)
    calibration_metrics = pd.DataFrame(calibration_rows)
    ranking_metrics = pd.DataFrame(ranking_metric_rows)
    feature_importance = (
        pd.concat(feature_importance_frames, ignore_index=True) if feature_importance_frames else pd.DataFrame()
    )
    direction_effect = pd.concat(direction_frames, ignore_index=True) if direction_frames else pd.DataFrame()
    permutation = pd.concat(permutation_frames, ignore_index=True) if permutation_frames else pd.DataFrame()
    reason_codes = reason_summary(feature_importance, direction_effect, permutation)

    model_selection.to_csv(MODELING_DIR / "calibration_model_selection.csv", index=False)
    calibration_metrics.to_csv(MODELING_DIR / "calibration_metrics.csv", index=False)
    ranking_metrics.to_csv(MODELING_DIR / "threshold_ranking_metrics.csv", index=False)
    feature_importance.to_csv(TARGET_LAB_DIR / "exploratory_feature_level_importance.csv", index=False)
    direction_effect.to_csv(TARGET_LAB_DIR / "exploratory_feature_direction_effects.csv", index=False)
    permutation.to_csv(TARGET_LAB_DIR / "exploratory_permutation_importance.csv", index=False)
    reason_codes.to_csv(TARGET_LAB_DIR / "exploratory_reason_code_summary.csv", index=False)

    plot_top_interpretation(feature_importance)
    write_summary(runs, calibration_metrics, ranking_metrics, reason_codes, model_selection, skipped)

    selected_manifest = [
        {
            "target": run.target,
            "target_family": run.target_family,
            "selected_model": run.selected_model_name,
            "selected_calibrator": run.selected_calibrator,
            "validation_pr_auc": run.validation_pr_auc,
            "validation_brier": run.validation_brier,
        }
        for run in runs
    ]
    (MODELING_DIR / "calibration_selected_models.json").write_text(
        json.dumps(selected_manifest, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote validation extension gate outputs for {len(runs)} targets")


if __name__ == "__main__":
    main()
