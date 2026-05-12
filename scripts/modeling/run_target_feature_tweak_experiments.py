#!/usr/bin/env python3
"""Second-pass target and feature-set experiments for thesis target design."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modeling.run_broader_target_experiments import (  # noqa: E402
    add_experiment_targets,
    frame_as_markdown,
    load_panel,
    make_splits,
    nullable_label,
)
from scripts.modeling.train_panel_v2_models import CATEGORICAL_FEATURES, NUMERIC_FEATURES, validate_features  # noqa: E402


OUT_ROOT = PROJECT_ROOT / "reports/target_tweak_experiments"


@dataclass(frozen=True)
class TweakSpec:
    folder: str
    title: str
    failure_target: str
    success_target: str
    tweak_summary: str
    failure_definition: str
    success_definition: str


TWEAKS = [
    TweakSpec(
        folder="test_target_tweaks1",
        title="Conservative v2 with stronger deterioration threshold",
        failure_target="failure_pressure_conservative_v2_next_4obs",
        success_target="success_resilience_quality_v2_next_4obs",
        tweak_summary="Tightens deterioration threshold but allows one balance-stress signal with repeated losses.",
        failure_definition="formal distress OR at least 3 future loss observations plus at least one serious stress/deterioration signal",
        success_definition="profitability and resilience, plus either ROA/operating quality or low-stress balance sheet",
    ),
    TweakSpec(
        folder="test_target_tweaks2",
        title="Profitability and ROA decline pressure",
        failure_target="failure_pressure_profit_roa_next_4obs",
        success_target="success_quality_growth_next_4obs",
        tweak_summary="Focuses on profitability failure plus average future ROA or operating-margin weakness.",
        failure_definition="formal distress OR repeated future losses with weak future ROA/operating margin and at least one pressure signal",
        success_definition="positive profitability, quality ROA/operating margin, acceptable leverage, and non-negative revenue or asset growth",
    ),
    TweakSpec(
        folder="test_target_tweaks3",
        title="Balance and liquidity stress pressure",
        failure_target="failure_pressure_balance_liquidity_next_4obs",
        success_target="success_stable_balance_next_4obs",
        tweak_summary="Tests whether balance-sheet/liquidity stress is learnable separately from profitability failure.",
        failure_definition="formal distress OR repeated future loss/unhealthy observations with repeated leverage, current-ratio, or cash stress",
        success_definition="repeated leverage/liquidity health plus positive profitability and non-negative future ROA",
    ),
    TweakSpec(
        folder="test_target_tweaks4",
        title="Sector-adjusted strict pressure",
        failure_target="failure_pressure_sector_strict_next_4obs",
        success_target="success_sector_quality_next_4obs",
        tweak_summary="Uses sector-relative future ROA thresholds to reduce bias against low-margin industries.",
        failure_definition="formal distress OR bottom-quartile future ROA within sector plus repeated losses or deterioration",
        success_definition="sector-above-median future ROA plus profitability and balance health",
    ),
    TweakSpec(
        folder="test_target_tweaks5",
        title="Component-score targets",
        failure_target="failure_pressure_score3_next_4obs",
        success_target="success_score3_next_4obs",
        tweak_summary="Uses explicit component scores for dashboard-friendly success/failure drivers.",
        failure_definition="formal distress OR at least 3 of 5 failure-pressure components",
        success_definition="at least 3 of 5 success-quality components and no score-based failure",
    ),
]


ACCOUNTING_FEATURES = [
    "total_assets",
    "total_liabilities",
    "current_assets",
    "current_liabilities",
    "cash_equivalents",
    "total_equity",
    "total_revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "cash_flow_operating",
    "capex",
]
RATIO_FEATURES = [
    "leverage_assets",
    "equity_assets",
    "current_ratio",
    "cash_assets",
    "net_margin",
    "operating_margin",
    "gross_margin",
    "roa",
    "r_and_d_intensity",
    "inventory_assets",
    "receivables_assets",
]
TREND_FEATURES = [
    feature
    for feature in NUMERIC_FEATURES
    if feature.endswith("_lag1")
    or feature.endswith("_growth_4obs")
    or feature.endswith("_change_4obs")
    or feature == "net_income_negative_count_prior_4obs"
]
REGIME_FEATURES = [
    "high_rate_regime",
    "market_stress_regime",
    "tight_financial_conditions",
    "credit_spread_stress_regime",
    "yield_curve_inversion_regime",
    "inflation_pressure_regime",
    "oil_shock_regime",
    "strong_dollar_regime",
    "demand_slowdown_regime",
    "credit_tightening_regime",
    "crisis_regime",
    "prediction_quarter",
]
EVENT_FEATURES = [feature for feature in NUMERIC_FEATURES if feature.startswith("global_event_")]
MACRO_FEATURES = [
    feature
    for feature in NUMERIC_FEATURES
    if feature not in ACCOUNTING_FEATURES + RATIO_FEATURES + TREND_FEATURES + REGIME_FEATURES + EVENT_FEATURES
]


FEATURE_SETS = {
    "firm_core": ACCOUNTING_FEATURES + RATIO_FEATURES + TREND_FEATURES + CATEGORICAL_FEATURES,
    "ratios_trends_only": RATIO_FEATURES + TREND_FEATURES + CATEGORICAL_FEATURES,
    "raw_accounting_only": ACCOUNTING_FEATURES + CATEGORICAL_FEATURES,
    "macro_event_only": MACRO_FEATURES + REGIME_FEATURES + EVENT_FEATURES + CATEGORICAL_FEATURES,
    "all_features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
}

TARGET_SCAN_MODEL_RUNS = [
    ("logistic_l2", 42),
    ("random_forest", 42),
    ("random_forest", 202),
    ("gradient_boosting", 42),
    ("gradient_boosting", 202),
]
FEATURE_SET_MODEL_RUNS = [
    ("logistic_l2", 42),
    ("random_forest", 42),
    ("gradient_boosting", 42),
]


def add_second_pass_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = add_experiment_targets(df).copy()

    formal = df["distress_next_4q"].fillna(0).astype(int) == 1
    valid_horizon = df["future_observation_count_4obs"] >= 3
    valid_or_formal = valid_horizon | formal

    profit_failure = (df["future_income_nonpositive_count_4obs"] >= 2) & (df["future_net_income_valid_count_4obs"] >= 3)
    severe_profit_failure = (df["future_income_nonpositive_count_4obs"] >= 3) & (
        df["future_net_income_valid_count_4obs"] >= 3
    )
    weak_roa = (df["future_roa_mean_4obs"] <= 0) & (df["future_roa_valid_count_4obs"] >= 3)
    weak_operating = (df["future_operating_margin_mean_4obs"] <= 0) & (
        df["future_operating_margin_valid_count_4obs"] >= 3
    )
    unhealthy_future = (df["future_unhealthy_count_4obs"] >= 3) & valid_horizon
    balance_stress_any = (
        (df["future_leverage_stress_count_4obs"] >= 1)
        | (df["future_liquidity_stress_count_4obs"] >= 1)
        | (df["future_cash_stress_count_4obs"] >= 1)
    ) & valid_horizon
    balance_stress_repeated = (
        (df["future_leverage_stress_count_4obs"] >= 2)
        | (df["future_liquidity_stress_count_4obs"] >= 2)
        | (df["future_cash_stress_count_4obs"] >= 2)
    ) & valid_horizon
    strong_deterioration = (
        (df["future_roa_change_4obs"] <= -0.04)
        | (df["future_revenue_growth_4obs"] <= -0.15)
        | (df["future_assets_growth_4obs"] <= -0.15)
    ) & valid_horizon
    moderate_deterioration = (
        (df["future_roa_change_4obs"] <= -0.025)
        | (df["future_revenue_growth_4obs"] <= -0.10)
        | (df["future_assets_growth_4obs"] <= -0.10)
    ) & valid_horizon
    sector_weak_roa = (
        (df["future_roa_valid_count_4obs"] >= 3)
        & (df["future_roa_mean_4obs"] <= df["sector_future_roa_q25"])
    )

    profit_success = (df["future_income_positive_count_4obs"] >= 3) & (df["future_net_income_valid_count_4obs"] >= 3)
    resilience_success = (df["future_healthy_count_4obs"] >= 3) & valid_horizon
    balance_success = (df["future_leverage_ok_count_4obs"] >= 3) & (df["future_cash_stress_count_4obs"] <= 1) & valid_horizon
    quality_success = (
        (df["future_roa_mean_4obs"] > 0.01)
        & (df["future_operating_margin_mean_4obs"] > 0)
        & (df["future_roa_valid_count_4obs"] >= 3)
    )
    strong_quality_success = (
        (df["future_roa_mean_4obs"] > 0.02)
        & (df["future_operating_margin_mean_4obs"] > 0)
        & (df["future_leverage_quality_count_4obs"] >= 3)
        & (df["future_roa_valid_count_4obs"] >= 3)
    )
    growth_success = (
        (df["future_revenue_growth_4obs"] >= 0)
        | (df["future_assets_growth_4obs"] >= 0)
    ) & (df["future_revenue_valid_count_4obs"] >= 3)
    sector_quality_success = (
        (df["future_roa_valid_count_4obs"] >= 3)
        & (df["future_roa_mean_4obs"] >= df["sector_future_roa_q60"])
    )

    failure_v2 = formal | (severe_profit_failure & (balance_stress_any | strong_deterioration | unhealthy_future))
    failure_profit_roa = formal | (profit_failure & (weak_roa | weak_operating) & (balance_stress_any | moderate_deterioration))
    failure_balance_liquidity = formal | ((profit_failure | unhealthy_future) & balance_stress_repeated)
    failure_sector_strict = formal | (sector_weak_roa & (profit_failure | moderate_deterioration))

    failure_components = pd.concat(
        [
            profit_failure.astype(int),
            weak_roa.astype(int),
            weak_operating.astype(int),
            balance_stress_repeated.astype(int),
            moderate_deterioration.astype(int),
        ],
        axis=1,
    ).sum(axis=1)
    failure_score3 = formal | ((failure_components >= 3) & valid_horizon)

    df["failure_component_score_5"] = failure_components
    df["failure_pressure_conservative_v2_next_4obs"] = nullable_label(failure_v2, valid_or_formal)
    df["failure_pressure_profit_roa_next_4obs"] = nullable_label(failure_profit_roa, valid_or_formal)
    df["failure_pressure_balance_liquidity_next_4obs"] = nullable_label(failure_balance_liquidity, valid_or_formal)
    df["failure_pressure_sector_strict_next_4obs"] = nullable_label(failure_sector_strict, valid_or_formal)
    df["failure_pressure_score3_next_4obs"] = nullable_label(failure_score3, valid_or_formal)

    success_v2 = profit_success & resilience_success & (quality_success | balance_success) & ~failure_v2
    success_growth = profit_success & strong_quality_success & balance_success & growth_success & ~failure_profit_roa
    success_balance = profit_success & balance_success & (df["future_roa_mean_4obs"] >= 0) & ~failure_balance_liquidity
    success_sector = sector_quality_success & profit_success & balance_success & ~failure_sector_strict

    success_components = pd.concat(
        [
            profit_success.astype(int),
            resilience_success.astype(int),
            balance_success.astype(int),
            quality_success.astype(int),
            growth_success.astype(int),
        ],
        axis=1,
    ).sum(axis=1)
    success_score3 = (success_components >= 3) & ~failure_score3

    df["success_component_score_5"] = success_components
    df["success_resilience_quality_v2_next_4obs"] = nullable_label(success_v2, valid_horizon)
    df["success_quality_growth_next_4obs"] = nullable_label(success_growth, valid_horizon)
    df["success_stable_balance_next_4obs"] = nullable_label(success_balance, valid_horizon)
    df["success_sector_quality_next_4obs"] = nullable_label(success_sector, valid_horizon)
    df["success_score3_next_4obs"] = nullable_label(success_score3, valid_horizon)

    return df


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    numeric_features = [feature for feature in features if feature in NUMERIC_FEATURES]
    categorical_features = [feature for feature in features if feature in CATEGORICAL_FEATURES]
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_features,
            ),
        ],
        remainder="drop",
    )


def build_model(model_name: str, seed: int, features: list[str]) -> Pipeline:
    if model_name == "logistic_l2":
        estimator = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear", random_state=seed)
    elif model_name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=220,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=seed,
            n_jobs=-1,
        )
    elif model_name == "gradient_boosting":
        estimator = GradientBoostingClassifier(n_estimators=160, learning_rate=0.045, max_depth=3, random_state=seed)
    else:
        raise ValueError(model_name)
    return Pipeline([("preprocess", build_preprocessor(features)), ("model", estimator)])


def class_weight_sample(y: pd.Series) -> np.ndarray:
    counts = y.value_counts().to_dict()
    n = len(y)
    return y.map({klass: n / (2 * count) for klass, count in counts.items()}).to_numpy()


def choose_threshold(y_true: np.ndarray, proba: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return 0.5
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    if len(thresholds) == 0:
        return 0.5
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(f1))])


def evaluate(model_name: str, feature_set: str, split_name: str, seed: int, y_true: np.ndarray, proba: np.ndarray, threshold: float) -> dict:
    y_pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "model": model_name,
        "feature_set": feature_set,
        "seed": seed,
        "split": split_name,
        "rows": int(len(y_true)),
        "positives": int(y_true.sum()),
        "positive_share": float(y_true.mean()) if len(y_true) else np.nan,
        "threshold": threshold,
        "roc_auc": roc_auc_score(y_true, proba) if len(np.unique(y_true)) > 1 else np.nan,
        "pr_auc": average_precision_score(y_true, proba) if len(np.unique(y_true)) > 1 else np.nan,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def clean_feature_name(feature: str) -> str:
    return feature.replace("num__", "").replace("cat__", "").replace("missingindicator_", "")


def feature_group(feature: str) -> str:
    raw = clean_feature_name(feature)
    if raw.startswith("Sector_") or raw == "Sector":
        return "sector"
    if raw.startswith("global_event_"):
        return "global_event_context"
    if raw in EVENT_FEATURES:
        return "global_event_context"
    if raw in REGIME_FEATURES:
        return "regime_time"
    if raw in MACRO_FEATURES:
        return "macro"
    if raw in TREND_FEATURES:
        return "firm_trend"
    if raw in RATIO_FEATURES:
        return "financial_ratio"
    if raw in ACCOUNTING_FEATURES:
        return "accounting_fundamental"
    if raw.startswith("Missing:") or "missingindicator_" in feature:
        return "missingness_indicator"
    return "other"


def extract_importance(model: Pipeline, target: str, model_name: str, feature_set: str, seed: int) -> pd.DataFrame:
    estimator = model.named_steps["model"]
    if not (hasattr(estimator, "coef_") or hasattr(estimator, "feature_importances_")):
        return pd.DataFrame()
    names = model.named_steps["preprocess"].get_feature_names_out()
    if hasattr(estimator, "coef_"):
        raw_values = estimator.coef_[0]
        values = np.abs(raw_values)
    else:
        raw_values = estimator.feature_importances_
        values = estimator.feature_importances_
    frame = pd.DataFrame(
        {
            "target": target,
            "model": model_name,
            "feature_set": feature_set,
            "seed": seed,
            "feature": names,
            "feature_clean": [clean_feature_name(name) for name in names],
            "feature_group": [feature_group(name) for name in names],
            "importance": values,
            "signed_value": raw_values,
        }
    )
    return frame.sort_values("importance", ascending=False).head(40)


def train_one(df: pd.DataFrame, target: str, features: list[str], feature_set: str, model_runs: list[tuple[str, int]]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    data = df[df[target].notna()].copy()
    data[target] = data[target].astype(int)
    splits = make_splits(data)
    x_train = splits["train"][features]
    y_train = splits["train"][target].astype(int)
    x_val = splits["validation"][features]
    y_val = splits["validation"][target].astype(int)
    x_test = splits["test"][features]
    y_test = splits["test"][target].astype(int)

    metrics = []
    importances = []
    best = {"pr_auc": -np.inf}
    for model_name, seed in model_runs:
        model = build_model(model_name, seed, features)
        if model_name == "gradient_boosting":
            model.fit(x_train, y_train, model__sample_weight=class_weight_sample(y_train))
        else:
            model.fit(x_train, y_train)

        val_proba = model.predict_proba(x_val)[:, 1]
        threshold = choose_threshold(y_val.to_numpy(), val_proba)
        for split_name, x_split, y_split in [
            ("train", x_train, y_train),
            ("validation", x_val, y_val),
            ("test", x_test, y_test),
        ]:
            proba = model.predict_proba(x_split)[:, 1]
            row = evaluate(model_name, feature_set, split_name, seed, y_split.to_numpy(), proba, threshold)
            row["target"] = target
            metrics.append(row)
            if split_name == "test" and pd.notna(row["pr_auc"]) and row["pr_auc"] > best["pr_auc"]:
                best = {
                    **row,
                    "model_object": model,
                    "test_y": y_split.to_numpy(),
                    "test_proba": proba,
                }
        importances.append(extract_importance(model, target, model_name, feature_set, seed))
    importance = pd.concat([frame for frame in importances if not frame.empty], ignore_index=True)
    return pd.DataFrame(metrics), importance, best


def plot_best_curves(best: dict, target: str, out_dir: Path, prefix: str) -> None:
    if not best or "test_y" not in best or len(np.unique(best["test_y"])) < 2:
        return
    y_true = best["test_y"]
    proba = best["test_proba"]
    precision, recall, _ = precision_recall_curve(y_true, proba)
    fpr, tpr, _ = roc_curve(y_true, proba)
    pr_auc = average_precision_score(y_true, proba)
    roc_auc = roc_auc_score(y_true, proba)

    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, label=f"{best['model']} / {best['feature_set']} AP={pr_auc:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(target)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{prefix}_{target}_best_pr_curve.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"{best['model']} / {best['feature_set']} AUC={roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title(target)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{prefix}_{target}_best_roc_curve.png", dpi=180)
    plt.close()


def target_profile(df: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    rows = []
    splits = make_splits(df)
    for target in targets:
        for split_name, split_df in {"all": df, **splits}.items():
            values = split_df[target]
            known = values.notna()
            positives = int(values.fillna(0).astype(int).sum())
            rows.append(
                {
                    "target": target,
                    "split": split_name,
                    "rows": len(split_df),
                    "known_rows": int(known.sum()),
                    "unknown_rows": int((~known).sum()),
                    "positives": positives,
                    "positive_share_known": positives / known.sum() if known.sum() else np.nan,
                    "firms_with_positive": split_df.loc[values.fillna(0).astype(int) == 1, "cik"].nunique(),
                }
            )
    return pd.DataFrame(rows)


def logic_audit(df: pd.DataFrame, failure_target: str, success_target: str) -> pd.DataFrame:
    failure = df[failure_target].fillna(0).astype(int) == 1
    success = df[success_target].fillna(0).astype(int) == 1
    strict = df["distress_next_4q"].fillna(0).astype(int) == 1
    return pd.DataFrame(
        [
            {"check": "post_event_rows", "value": int(df["post_event_flag"].fillna(0).astype(int).sum())},
            {"check": "failure_success_overlap_rows", "value": int((failure & success).sum())},
            {"check": "strict_distress_missed_by_failure_rows", "value": int((strict & ~failure).sum())},
            {"check": "future_observation_count_lt3_rows", "value": int((df["future_observation_count_4obs"] < 3).sum())},
            {"check": "unknown_failure_rows", "value": int(df[failure_target].isna().sum())},
            {"check": "unknown_success_rows", "value": int(df[success_target].isna().sum())},
        ]
    )


def summarize_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    test = metrics[metrics["split"] == "test"].copy()
    return (
        test.groupby(["target", "feature_set", "model"], as_index=False)
        .agg(
            runs=("seed", "count"),
            positives=("positives", "mean"),
            positive_share=("positive_share", "mean"),
            roc_auc_mean=("roc_auc", "mean"),
            pr_auc_mean=("pr_auc", "mean"),
            precision_mean=("precision", "mean"),
            recall_mean=("recall", "mean"),
            f1_mean=("f1", "mean"),
        )
        .sort_values(["target", "pr_auc_mean"], ascending=[True, False])
    )


def summarize_factor_groups(importances: pd.DataFrame) -> pd.DataFrame:
    if importances.empty:
        return pd.DataFrame()
    grouped = (
        importances.groupby(["target", "feature_set", "model", "feature_group"], as_index=False)["importance"]
        .sum()
        .sort_values(["target", "feature_set", "model", "importance"], ascending=[True, True, True, False])
    )
    totals = grouped.groupby(["target", "feature_set", "model"])["importance"].transform("sum")
    grouped["importance_share"] = grouped["importance"] / totals.replace(0, np.nan)
    return grouped


def plot_metric_summary(summary: pd.DataFrame, out_dir: Path, prefix: str) -> None:
    for metric in ["pr_auc_mean", "f1_mean"]:
        plot_data = summary.copy()
        plot_data["label"] = plot_data["target"] + " / " + plot_data["feature_set"] + " / " + plot_data["model"]
        plot_data = plot_data.sort_values(metric, ascending=True).tail(18)
        plt.figure(figsize=(11, 7))
        plt.barh(plot_data["label"], plot_data[metric])
        plt.xlabel(metric)
        plt.title(f"{prefix} top {metric}")
        plt.tight_layout()
        plt.savefig(out_dir / f"{prefix}_{metric}_top.png", dpi=180)
        plt.close()


def run_target_tweak(df: pd.DataFrame, spec: TweakSpec, all_features: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    out_dir = OUT_ROOT / spec.folder
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tweak_config.json").write_text(json.dumps(spec.__dict__, indent=2), encoding="utf-8")
    targets = [spec.failure_target, spec.success_target]

    profile = target_profile(df, targets)
    audit = logic_audit(df, spec.failure_target, spec.success_target)
    profile.to_csv(out_dir / "target_profile.csv", index=False)
    audit.to_csv(out_dir / "logic_audit.csv", index=False)

    metrics_frames = []
    importance_frames = []
    for target in targets:
        metrics, importance, best = train_one(df, target, all_features, "all_features", TARGET_SCAN_MODEL_RUNS)
        metrics_frames.append(metrics)
        importance_frames.append(importance)
        plot_best_curves(best, target, out_dir, "target_scan")

    metrics = pd.concat(metrics_frames, ignore_index=True)
    importance = pd.concat([frame for frame in importance_frames if not frame.empty], ignore_index=True)
    metrics.insert(0, "experiment", spec.folder)
    importance.insert(0, "experiment", spec.folder)
    metrics.to_csv(out_dir / "target_scan_model_metrics.csv", index=False)
    importance.to_csv(out_dir / "target_scan_feature_importance.csv", index=False)
    summary = summarize_metrics(metrics)
    summary.to_csv(out_dir / "target_scan_metric_summary.csv", index=False)
    factors = summarize_factor_groups(importance)
    factors.to_csv(out_dir / "target_scan_factor_group_summary.csv", index=False)
    plot_metric_summary(summary, out_dir, "target_scan")

    best = summary.sort_values("pr_auc_mean", ascending=False).groupby("target", as_index=False).head(1)
    lines = [
        f"# {spec.folder}: {spec.title}",
        "",
        f"Summary: {spec.tweak_summary}",
        "",
        "## Failure Definition",
        "",
        f"`{spec.failure_target}`: {spec.failure_definition}.",
        "",
        "## Success Definition",
        "",
        f"`{spec.success_target}`: {spec.success_definition}.",
        "",
        "## Target Profile",
        "",
        frame_as_markdown(profile),
        "",
        "## Logic Audit",
        "",
        frame_as_markdown(audit),
        "",
        "## Best Target-Scan Rows",
        "",
        frame_as_markdown(best[["target", "feature_set", "model", "runs", "positives", "positive_share", "roc_auc_mean", "pr_auc_mean", "precision_mean", "recall_mean", "f1_mean"]]),
        "",
    ]
    (out_dir / "run_log.md").write_text("\n".join(lines), encoding="utf-8")
    return metrics, importance


def run_feature_ablation(df: pd.DataFrame, targets: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    out_dir = OUT_ROOT / "feature_set_ablation"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    importance_rows = []
    for target in targets:
        for feature_set, features in FEATURE_SETS.items():
            valid_features = validate_features(df, [feature for feature in features if feature in df.columns])
            print(f"Feature ablation: {target} / {feature_set}")
            metrics, importance, best = train_one(df, target, valid_features, feature_set, FEATURE_SET_MODEL_RUNS)
            rows.append(metrics)
            importance_rows.append(importance)
            plot_best_curves(best, target, out_dir, f"{feature_set}")
    metrics = pd.concat(rows, ignore_index=True)
    importances = pd.concat([frame for frame in importance_rows if not frame.empty], ignore_index=True)
    metrics.to_csv(out_dir / "feature_set_model_metrics.csv", index=False)
    importances.to_csv(out_dir / "feature_set_feature_importance.csv", index=False)
    summary = summarize_metrics(metrics)
    factors = summarize_factor_groups(importances)
    summary.to_csv(out_dir / "feature_set_metric_summary.csv", index=False)
    factors.to_csv(out_dir / "feature_set_factor_group_summary.csv", index=False)
    plot_metric_summary(summary, out_dir, "feature_set_ablation")
    return metrics, importances


def write_root_outputs(target_metrics: pd.DataFrame, target_importance: pd.DataFrame, ablation_metrics: pd.DataFrame, ablation_importance: pd.DataFrame) -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    target_metrics.to_csv(OUT_ROOT / "all_target_tweak_metrics.csv", index=False)
    target_importance.to_csv(OUT_ROOT / "all_target_tweak_feature_importance.csv", index=False)
    target_summary = summarize_metrics(target_metrics)
    target_factors = summarize_factor_groups(target_importance)
    ablation_summary = summarize_metrics(ablation_metrics)
    ablation_factors = summarize_factor_groups(ablation_importance)
    target_summary.to_csv(OUT_ROOT / "target_tweak_comparison.csv", index=False)
    target_factors.to_csv(OUT_ROOT / "target_tweak_factor_group_summary.csv", index=False)
    ablation_summary.to_csv(OUT_ROOT / "feature_ablation_comparison.csv", index=False)
    ablation_factors.to_csv(OUT_ROOT / "feature_ablation_factor_group_summary.csv", index=False)

    best_targets = target_summary.sort_values("pr_auc_mean", ascending=False).groupby("target", as_index=False).head(1)
    best_ablation = ablation_summary.sort_values("pr_auc_mean", ascending=False).groupby("target", as_index=False).head(1)
    best_targets.to_csv(OUT_ROOT / "dashboard_best_target_rows.csv", index=False)
    ablation_summary.to_csv(OUT_ROOT / "dashboard_feature_set_performance.csv", index=False)
    target_factors.to_csv(OUT_ROOT / "dashboard_factor_group_best_models.csv", index=False)
    lines = [
        "# Target And Feature Tweak Experiments",
        "",
        "This second pass tests small target-definition tweaks and feature-set sensitivity.",
        "",
        "## Best Target-Definition Rows",
        "",
        frame_as_markdown(best_targets[["target", "feature_set", "model", "runs", "positives", "positive_share", "roc_auc_mean", "pr_auc_mean", "precision_mean", "recall_mean", "f1_mean"]]),
        "",
        "## Best Feature-Set Rows",
        "",
        frame_as_markdown(best_ablation[["target", "feature_set", "model", "runs", "positives", "positive_share", "roc_auc_mean", "pr_auc_mean", "precision_mean", "recall_mean", "f1_mean"]]),
        "",
        "## Interpretation Prompt",
        "",
        "A target is more thesis-ready when it is predictive, has a defensible economic interpretation, has enough positives in the temporal test split, and does not rely on filling unknown future labels.",
        "",
    ]
    (OUT_ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    df = add_second_pass_targets(load_panel())
    all_features = validate_features(df, NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    pd.DataFrame(
        [
            {"feature_set": name, "feature_count": len([feature for feature in features if feature in df.columns])}
            for name, features in FEATURE_SETS.items()
        ]
    ).to_csv(OUT_ROOT / "feature_set_inventory.csv", index=False)

    target_metrics_frames = []
    target_importance_frames = []
    for spec in TWEAKS:
        print(f"Target tweak: {spec.folder} / {spec.title}")
        metrics, importance = run_target_tweak(df, spec, all_features)
        target_metrics_frames.append(metrics)
        target_importance_frames.append(importance)

    target_metrics = pd.concat(target_metrics_frames, ignore_index=True)
    target_importance = pd.concat([frame for frame in target_importance_frames if not frame.empty], ignore_index=True)

    ablation_targets = [
        "failure_pressure_conservative_next_4obs",
        "failure_pressure_conservative_v2_next_4obs",
        "failure_pressure_profit_roa_next_4obs",
        "success_composite_strict_next_4obs",
        "success_resilience_quality_v2_next_4obs",
        "success_quality_growth_next_4obs",
    ]
    ablation_metrics, ablation_importance = run_feature_ablation(df, ablation_targets)
    write_root_outputs(target_metrics, target_importance, ablation_metrics, ablation_importance)
    print((OUT_ROOT / "README.md").resolve())


if __name__ == "__main__":
    main()
