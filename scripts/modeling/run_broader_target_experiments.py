#!/usr/bin/env python3
"""Run isolated broader success/failure target experiments.

Each experiment writes a self-contained folder under
reports/target_experiments/test_broader_targetsN.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import joblib
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

from scripts.modeling.train_panel_v2_models import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    validate_features,
)


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
OUT_ROOT = PROJECT_ROOT / "reports/target_experiments"
MODEL_ROOT = PROJECT_ROOT / "models/target_experiments"

DATE_COLS = ["period_date", "filed_date", "prediction_date", "event_date"]
SEEDS = [42, 202, 777]


@dataclass(frozen=True)
class ExperimentSpec:
    folder: str
    title: str
    failure_target: str
    success_target: str
    failure_definition: str
    success_definition: str


EXPERIMENTS = [
    ExperimentSpec(
        folder="test_broader_targets1",
        title="Loose broad economic pressure",
        failure_target="failure_pressure_loose_next_4obs",
        success_target="success_composite_loose_next_4obs",
        failure_definition="formal distress OR repeated future losses OR repeated future unhealthy state",
        success_definition="at least two of profitability, resilience, and quality components; blocked by failure pressure",
    ),
    ExperimentSpec(
        folder="test_broader_targets2",
        title="Balanced two-of-three pressure",
        failure_target="failure_pressure_balanced_next_4obs",
        success_target="success_composite_balanced_next_4obs",
        failure_definition="formal distress OR at least two of profitability failure, balance/liquidity stress, and deterioration",
        success_definition="at least two of profitability, balance resilience, and operating/ROA quality; blocked by failure pressure",
    ),
    ExperimentSpec(
        folder="test_broader_targets3",
        title="Sector-relative underperformance",
        failure_target="failure_pressure_sector_relative_next_4obs",
        success_target="success_composite_sector_relative_next_4obs",
        failure_definition="formal distress OR bottom-quartile future ROA within sector-year plus pressure evidence",
        success_definition="sector-year above-median future ROA plus profitability and balance resilience; blocked by failure pressure",
    ),
    ExperimentSpec(
        folder="test_broader_targets4",
        title="Conservative quality gate",
        failure_target="failure_pressure_conservative_next_4obs",
        success_target="success_composite_strict_next_4obs",
        failure_definition="formal distress OR repeated losses plus either balance stress, deterioration, or unhealthy future state",
        success_definition="all three success components: profitability, resilience, and quality; blocked by failure pressure",
    ),
]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in NUMERIC_FEATURES + [
        "distress_next_4q",
        "broad_distress_next_4q",
        "post_event_flag",
        "net_income",
        "roa",
        "leverage_assets",
        "current_ratio",
        "cash_assets",
        "operating_margin",
        "total_revenue",
        "total_assets",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    df = df[df["post_event_flag"].fillna(0).astype(int) == 0].copy()
    df = df.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).reset_index(drop=True)
    return df


def shifted(grouped: pd.core.groupby.SeriesGroupBy, step: int) -> pd.Series:
    return grouped.shift(-step)


def future_shifts(df: pd.DataFrame, col: str) -> list[pd.Series]:
    grouped = df.groupby("cik", group_keys=False)[col]
    return [shifted(grouped, step) for step in range(1, 5)]


def condition_count(shifts: list[pd.Series], condition) -> pd.Series:
    parts = [condition(series).fillna(False).astype(int) for series in shifts]
    return pd.concat(parts, axis=1).sum(axis=1)


def valid_count(shifts: list[pd.Series]) -> pd.Series:
    return pd.concat([series.notna().astype(int) for series in shifts], axis=1).sum(axis=1)


def future_mean(shifts: list[pd.Series]) -> pd.Series:
    return pd.concat(shifts, axis=1).mean(axis=1, skipna=True)


def add_future_components(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    grouped_adsh = df.groupby("cik", group_keys=False)["adsh"]
    df["future_observation_count_4obs"] = sum(
        shifted(grouped_adsh, step).notna().astype(int) for step in range(1, 5)
    )

    net_income = future_shifts(df, "net_income")
    roa = future_shifts(df, "roa")
    leverage = future_shifts(df, "leverage_assets")
    current_ratio = future_shifts(df, "current_ratio")
    cash_assets = future_shifts(df, "cash_assets")
    operating_margin = future_shifts(df, "operating_margin")
    revenue = future_shifts(df, "total_revenue")
    assets = future_shifts(df, "total_assets")

    df["future_net_income_valid_count_4obs"] = valid_count(net_income)
    df["future_roa_valid_count_4obs"] = valid_count(roa)
    df["future_operating_margin_valid_count_4obs"] = valid_count(operating_margin)
    df["future_leverage_valid_count_4obs"] = valid_count(leverage)
    df["future_revenue_valid_count_4obs"] = valid_count(revenue)
    df["future_assets_valid_count_4obs"] = valid_count(assets)

    df["future_income_positive_count_4obs"] = condition_count(net_income, lambda s: s > 0)
    df["future_income_nonpositive_count_4obs"] = condition_count(net_income, lambda s: s <= 0)
    df["future_roa_positive_count_4obs"] = condition_count(roa, lambda s: s > 0)
    df["future_roa_mean_4obs"] = future_mean(roa)
    df["future_operating_margin_mean_4obs"] = future_mean(operating_margin)
    df["future_leverage_ok_count_4obs"] = condition_count(leverage, lambda s: s.between(0, 0.85, inclusive="both"))
    df["future_leverage_quality_count_4obs"] = condition_count(leverage, lambda s: s.between(0, 0.75, inclusive="both"))
    df["future_leverage_stress_count_4obs"] = condition_count(leverage, lambda s: s > 0.85)
    df["future_liquidity_stress_count_4obs"] = condition_count(current_ratio, lambda s: s < 1.0)
    df["future_cash_stress_count_4obs"] = condition_count(cash_assets, lambda s: s < 0.03)
    df["future_operating_margin_positive_count_4obs"] = condition_count(operating_margin, lambda s: s > 0)
    df["future_quality_count_4obs"] = condition_count(
        [pd.concat([roa[i], operating_margin[i], leverage[i]], axis=1) for i in range(4)],
        lambda frame: (frame.iloc[:, 0] > 0.01) & (frame.iloc[:, 1] > 0) & frame.iloc[:, 2].between(0, 0.80),
    )

    unhealthy_parts = []
    healthy_parts = []
    for index in range(4):
        unhealthy_parts.append(
            (
                (net_income[index].notna() & (net_income[index] <= 0))
                | (roa[index].notna() & (roa[index] <= 0))
                | (leverage[index].notna() & (leverage[index] > 0.85))
            ).astype(int)
        )
        healthy_parts.append(
            (
                (net_income[index] > 0)
                & (roa[index] > 0)
                & leverage[index].between(0, 0.85, inclusive="both")
            ).fillna(False).astype(int)
        )
    df["future_unhealthy_count_4obs"] = pd.concat(unhealthy_parts, axis=1).sum(axis=1)
    df["future_healthy_count_4obs"] = pd.concat(healthy_parts, axis=1).sum(axis=1)

    df["future_revenue_last_4obs"] = revenue[-1]
    df["future_assets_last_4obs"] = assets[-1]
    df["future_revenue_growth_4obs"] = df["future_revenue_last_4obs"] / df["total_revenue"].replace(0, np.nan) - 1
    df["future_assets_growth_4obs"] = df["future_assets_last_4obs"] / df["total_assets"].replace(0, np.nan) - 1
    df["future_roa_change_4obs"] = df["future_roa_mean_4obs"] - df["roa"]

    return df


def nullable_label(positive: pd.Series, valid: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=positive.index, dtype="Int64")
    out.loc[valid.fillna(False)] = positive.loc[valid.fillna(False)].fillna(False).astype(int).astype("Int64")
    return out


def add_sector_relative_thresholds(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["future_roa_valid_count_4obs"] >= 3
    global_q25 = df.loc[valid, "future_roa_mean_4obs"].quantile(0.25)
    global_q60 = df.loc[valid, "future_roa_mean_4obs"].quantile(0.60)
    sector_q25 = df.loc[valid].groupby("Sector")["future_roa_mean_4obs"].transform(lambda s: s.quantile(0.25))
    sector_q60 = df.loc[valid].groupby("Sector")["future_roa_mean_4obs"].transform(lambda s: s.quantile(0.60))
    df["sector_future_roa_q25"] = global_q25
    df["sector_future_roa_q60"] = global_q60
    df.loc[valid, "sector_future_roa_q25"] = sector_q25.fillna(global_q25).to_numpy()
    df.loc[valid, "sector_future_roa_q60"] = sector_q60.fillna(global_q60).to_numpy()
    return df


def add_experiment_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = add_future_components(df)
    df = add_sector_relative_thresholds(df)

    formal = df["distress_next_4q"].fillna(0).astype(int) == 1
    valid_horizon = df["future_observation_count_4obs"] >= 3
    valid_or_formal = valid_horizon | formal

    profit_failure = (df["future_income_nonpositive_count_4obs"] >= 2) & (df["future_net_income_valid_count_4obs"] >= 3)
    severe_profit_failure = (df["future_income_nonpositive_count_4obs"] >= 3) & (
        df["future_net_income_valid_count_4obs"] >= 3
    )
    unhealthy_failure = (df["future_unhealthy_count_4obs"] >= 3) & valid_horizon
    balance_stress = (
        (df["future_leverage_stress_count_4obs"] >= 2)
        | (df["future_liquidity_stress_count_4obs"] >= 2)
        | (df["future_cash_stress_count_4obs"] >= 2)
    ) & valid_horizon
    deterioration = (
        (df["future_roa_change_4obs"] <= -0.03)
        | (df["future_revenue_growth_4obs"] <= -0.10)
        | (df["future_assets_growth_4obs"] <= -0.10)
    ) & valid_horizon

    profit_success = (df["future_income_positive_count_4obs"] >= 3) & (df["future_net_income_valid_count_4obs"] >= 3)
    resilience_success = (df["future_healthy_count_4obs"] >= 3) & valid_horizon
    balance_success = (df["future_leverage_ok_count_4obs"] >= 3) & (df["future_cash_stress_count_4obs"] <= 1) & valid_horizon
    quality_success = (
        (df["future_roa_mean_4obs"] > 0.01)
        & (df["future_operating_margin_mean_4obs"] > 0)
        & (df["future_leverage_quality_count_4obs"] >= 3)
        & (df["future_roa_valid_count_4obs"] >= 3)
    )

    failure1_positive = formal | profit_failure | unhealthy_failure
    failure2_components = profit_failure.astype(int) + balance_stress.astype(int) + deterioration.astype(int)
    failure2_positive = formal | (failure2_components >= 2)
    sector_relative_pressure = (
        (df["future_roa_valid_count_4obs"] >= 3)
        & (df["future_roa_mean_4obs"] <= df["sector_future_roa_q25"])
        & (profit_failure | balance_stress | deterioration)
    )
    failure3_positive = formal | sector_relative_pressure
    failure4_positive = formal | (severe_profit_failure & (balance_stress | deterioration | unhealthy_failure))

    df["failure_pressure_loose_next_4obs"] = nullable_label(failure1_positive, valid_or_formal)
    df["failure_pressure_balanced_next_4obs"] = nullable_label(failure2_positive, valid_or_formal)
    df["failure_pressure_sector_relative_next_4obs"] = nullable_label(failure3_positive, valid_or_formal)
    df["failure_pressure_conservative_next_4obs"] = nullable_label(failure4_positive, valid_or_formal)

    success1_score = profit_success.astype(int) + resilience_success.astype(int) + quality_success.astype(int)
    success2_score = profit_success.astype(int) + balance_success.astype(int) + quality_success.astype(int)
    sector_relative_success = (
        (df["future_roa_valid_count_4obs"] >= 3)
        & (df["future_roa_mean_4obs"] >= df["sector_future_roa_q60"])
        & profit_success
        & balance_success
    )
    success4_positive = profit_success & resilience_success & quality_success

    df["success_composite_loose_next_4obs"] = nullable_label((success1_score >= 2) & ~failure1_positive, valid_horizon)
    df["success_composite_balanced_next_4obs"] = nullable_label((success2_score >= 2) & ~failure2_positive, valid_horizon)
    df["success_composite_sector_relative_next_4obs"] = nullable_label(
        sector_relative_success & ~failure3_positive,
        valid_horizon,
    )
    df["success_composite_strict_next_4obs"] = nullable_label(success4_positive & ~failure4_positive, valid_horizon)

    component_cols = [
        "future_observation_count_4obs",
        "future_income_positive_count_4obs",
        "future_income_nonpositive_count_4obs",
        "future_healthy_count_4obs",
        "future_unhealthy_count_4obs",
        "future_roa_mean_4obs",
        "future_roa_change_4obs",
        "future_revenue_growth_4obs",
        "future_assets_growth_4obs",
    ]
    df.attrs["component_cols"] = component_cols
    return df


def make_splits(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    year = df["prediction_date"].dt.year
    return {
        "train": df[year <= 2018].copy(),
        "validation": df[(year >= 2019) & (year <= 2021)].copy(),
        "test": df[(year >= 2022) & (year <= 2024)].copy(),
    }


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    numeric_features = [feature for feature in NUMERIC_FEATURES if feature in features]
    categorical_features = [feature for feature in CATEGORICAL_FEATURES if feature in features]
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric, numeric_features),
            ("cat", categorical, categorical_features),
        ],
        remainder="drop",
    )


def build_model(model_name: str, seed: int, features: list[str]) -> Pipeline:
    if model_name == "logistic_l2":
        estimator = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="liblinear",
            random_state=seed,
        )
    elif model_name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=seed,
            n_jobs=-1,
        )
    elif model_name == "gradient_boosting":
        estimator = GradientBoostingClassifier(
            n_estimators=220,
            learning_rate=0.04,
            max_depth=3,
            random_state=seed,
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")
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


def evaluate(model_name: str, split_name: str, seed: int, y_true: np.ndarray, proba: np.ndarray, threshold: float) -> dict:
    y_pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "model": model_name,
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


def feature_importance(model: Pipeline, model_name: str, target: str, seed: int) -> pd.DataFrame:
    estimator = model.named_steps["model"]
    if not (hasattr(estimator, "coef_") or hasattr(estimator, "feature_importances_")):
        return pd.DataFrame()
    names = model.named_steps["preprocess"].get_feature_names_out()
    values = np.abs(estimator.coef_[0]) if hasattr(estimator, "coef_") else estimator.feature_importances_
    return (
        pd.DataFrame({"target": target, "model": model_name, "seed": seed, "feature": names, "importance": values})
        .sort_values("importance", ascending=False)
        .head(30)
    )


def train_target(df: pd.DataFrame, target: str, out_dir: Path, features: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_df = df[df[target].notna()].copy()
    target_df[target] = target_df[target].astype(int)
    splits = make_splits(target_df)

    metrics = []
    importances = []
    best_payload = None
    best_pr_auc = -np.inf

    x_train = splits["train"][features]
    y_train = splits["train"][target].astype(int)
    x_val = splits["validation"][features]
    y_val = splits["validation"][target].astype(int)
    x_test = splits["test"][features]
    y_test = splits["test"][target].astype(int)

    model_runs = [("logistic_l2", 42)] + [(name, seed) for name in ["random_forest", "gradient_boosting"] for seed in SEEDS]
    for model_name, seed in model_runs:
        model = build_model(model_name, seed, features)
        if model_name == "gradient_boosting":
            model.fit(x_train, y_train, model__sample_weight=class_weight_sample(y_train))
        else:
            model.fit(x_train, y_train)

        val_proba = model.predict_proba(x_val)[:, 1]
        threshold = choose_threshold(y_val.to_numpy(), val_proba)
        test_proba = model.predict_proba(x_test)[:, 1]

        for split_name, x_split, y_split in [
            ("train", x_train, y_train),
            ("validation", x_val, y_val),
            ("test", x_test, y_test),
        ]:
            proba = model.predict_proba(x_split)[:, 1]
            row = evaluate(model_name, split_name, seed, y_split.to_numpy(), proba, threshold)
            row["target"] = target
            metrics.append(row)

        current_pr_auc = average_precision_score(y_test, test_proba) if len(np.unique(y_test)) > 1 else np.nan
        if pd.notna(current_pr_auc) and current_pr_auc > best_pr_auc:
            best_pr_auc = float(current_pr_auc)
            best_payload = {
                "target": target,
                "model": model_name,
                "seed": seed,
                "model_object": model,
                "test_y": y_test.to_numpy(),
                "test_proba": test_proba,
                "test_frame": splits["test"][["ticker", "cik", "prediction_date", "Sector", target]].copy(),
            }
        importances.append(feature_importance(model, model_name, target, seed))

    metrics_frame = pd.DataFrame(metrics)
    importance_frame = pd.concat([frame for frame in importances if not frame.empty], ignore_index=True)

    if best_payload is not None:
        model_dir = MODEL_ROOT / out_dir.name
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_payload["model_object"], model_dir / f"{target}_best_{best_payload['model']}_{best_payload['seed']}.joblib")
        prediction_frame = best_payload["test_frame"].copy()
        prediction_frame["predicted_probability"] = best_payload["test_proba"]
        prediction_frame = prediction_frame.sort_values("predicted_probability", ascending=False)
        prediction_frame.to_csv(out_dir / f"{target}_best_test_predictions.csv", index=False)
        plot_curves(
            best_payload["test_y"],
            best_payload["test_proba"],
            best_payload["target"],
            best_payload["model"],
            best_payload["seed"],
            out_dir,
        )

    return metrics_frame, importance_frame


def plot_curves(y_true: np.ndarray, proba: np.ndarray, target: str, model_name: str, seed: int, out_dir: Path) -> None:
    if len(np.unique(y_true)) < 2:
        return
    precision, recall, _ = precision_recall_curve(y_true, proba)
    fpr, tpr, _ = roc_curve(y_true, proba)
    pr_auc = average_precision_score(y_true, proba)
    roc_auc = roc_auc_score(y_true, proba)

    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, label=f"{model_name} seed={seed}, AP={pr_auc:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Best PR curve: {target}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{target}_best_precision_recall.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"{model_name} seed={seed}, AUC={roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title(f"Best ROC curve: {target}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{target}_best_roc.png", dpi=180)
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


def target_overlap(df: pd.DataFrame, failure_target: str, success_target: str) -> pd.DataFrame:
    known = df[failure_target].notna() & df[success_target].notna()
    failure = df[failure_target].fillna(0).astype(int) == 1
    success = df[success_target].fillna(0).astype(int) == 1
    rows = [
        {"check": "known_both_rows", "value": int(known.sum())},
        {"check": "failure_positive_rows", "value": int((failure & known).sum())},
        {"check": "success_positive_rows", "value": int((success & known).sum())},
        {"check": "failure_success_overlap_rows", "value": int((failure & success & known).sum())},
        {"check": "strict_distress_next_4q_inside_failure", "value": int(((df["distress_next_4q"].fillna(0).astype(int) == 1) & ~failure).sum())},
    ]
    return pd.DataFrame(rows)


def inconsistency_audit(df: pd.DataFrame, failure_target: str, success_target: str) -> pd.DataFrame:
    failure = df[failure_target].fillna(0).astype(int) == 1
    success = df[success_target].fillna(0).astype(int) == 1
    rows = [
        {
            "check": "rows_with_less_than_3_future_observations",
            "value": int((df["future_observation_count_4obs"] < 3).sum()),
            "integrity_action": "future-financial target rows set to unknown unless strict formal distress is known",
        },
        {
            "check": "post_event_rows_in_experiment_frame",
            "value": int(df["post_event_flag"].fillna(0).astype(int).sum()),
            "integrity_action": "post-event rows excluded before target construction",
        },
        {
            "check": "failure_success_overlap_rows",
            "value": int((failure & success).sum()),
            "integrity_action": "success target is explicitly blocked by same-experiment failure target",
        },
        {
            "check": "strict_distress_not_captured_by_failure_rows",
            "value": int(((df["distress_next_4q"].fillna(0).astype(int) == 1) & ~failure).sum()),
            "integrity_action": "formal distress is forced into every experimental failure target",
        },
        {
            "check": "rows_with_unknown_failure_target",
            "value": int(df[failure_target].isna().sum()),
            "integrity_action": "unknown kept as null and removed from model fitting for that target",
        },
        {
            "check": "rows_with_unknown_success_target",
            "value": int(df[success_target].isna().sum()),
            "integrity_action": "unknown kept as null and removed from model fitting for that target",
        },
    ]
    return pd.DataFrame(rows)


def write_experiment_plots(metrics: pd.DataFrame, profile: pd.DataFrame, out_dir: Path) -> None:
    test = metrics[metrics["split"] == "test"].copy()
    summary = (
        test.groupby(["target", "model"], as_index=False)
        .agg(
            pr_auc_mean=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
            roc_auc_mean=("roc_auc", "mean"),
            f1_mean=("f1", "mean"),
            precision_mean=("precision", "mean"),
            recall_mean=("recall", "mean"),
        )
        .sort_values(["target", "pr_auc_mean"], ascending=[True, False])
    )
    summary.to_csv(out_dir / "test_metric_summary.csv", index=False)

    for metric in ["pr_auc_mean", "f1_mean", "recall_mean"]:
        plot_data = summary.copy()
        plot_data["label"] = plot_data["target"] + " / " + plot_data["model"]
        plot_data = plot_data.sort_values(metric, ascending=True)
        plt.figure(figsize=(10, 6))
        plt.barh(plot_data["label"], plot_data[metric])
        plt.xlabel(metric)
        plt.title(f"Test {metric} by target/model")
        plt.tight_layout()
        plt.savefig(out_dir / f"test_{metric}_comparison.png", dpi=180)
        plt.close()

    balance = profile[profile["split"].isin(["train", "validation", "test"])].copy()
    balance["label"] = balance["target"] + " / " + balance["split"]
    plt.figure(figsize=(10, 6))
    plt.barh(balance["label"], balance["positive_share_known"])
    plt.xlabel("Positive share among known labels")
    plt.title("Target class balance by temporal split")
    plt.tight_layout()
    plt.savefig(out_dir / "target_balance_by_split.png", dpi=180)
    plt.close()


def write_run_log(spec: ExperimentSpec, profile: pd.DataFrame, metrics: pd.DataFrame, audit: pd.DataFrame, out_dir: Path) -> None:
    test = metrics[metrics["split"] == "test"].copy()
    best = test.sort_values("pr_auc", ascending=False).groupby("target", as_index=False).head(1)
    lines = [
        f"# {spec.folder}: {spec.title}",
        "",
        "## Definitions",
        "",
        f"- Failure target: `{spec.failure_target}`.",
        f"- Failure definition: {spec.failure_definition}.",
        f"- Success target: `{spec.success_target}`.",
        f"- Success definition: {spec.success_definition}.",
        "",
        "## Integrity Actions",
        "",
        "- Post-event rows are excluded before target construction.",
        "- Rows with fewer than 3 future observations are kept as unknown for future-financial labels unless formal distress is known.",
        "- Success labels are blocked when the same row qualifies as the same-experiment failure-pressure label.",
        "- Unknown labels are not filled; they are removed only from the model fit for that target.",
        "",
        "## Target Profile",
        "",
        frame_as_markdown(profile),
        "",
        "## Best Test Runs By PR-AUC",
        "",
        frame_as_markdown(best[["target", "model", "seed", "rows", "positives", "roc_auc", "pr_auc", "precision", "recall", "f1"]]),
        "",
        "## Inconsistency Audit",
        "",
        frame_as_markdown(audit),
        "",
    ]
    (out_dir / "run_log.md").write_text("\n".join(lines), encoding="utf-8")


def frame_as_markdown(frame: pd.DataFrame) -> str:
    """Small dependency-free Markdown table formatter."""
    if frame.empty:
        return "_No rows._"
    table = frame.copy()
    for col in table.columns:
        if pd.api.types.is_float_dtype(table[col]):
            table[col] = table[col].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
        else:
            table[col] = table[col].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(table.columns)
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in table.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(rows)


def run_experiment(df: pd.DataFrame, spec: ExperimentSpec, features: list[str]) -> pd.DataFrame:
    out_dir = OUT_ROOT / spec.folder
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "experiment_config.json").write_text(json.dumps(spec.__dict__, indent=2), encoding="utf-8")

    targets = [spec.failure_target, spec.success_target]
    profile = target_profile(df, targets)
    overlap = target_overlap(df, spec.failure_target, spec.success_target)
    audit = inconsistency_audit(df, spec.failure_target, spec.success_target)

    profile.to_csv(out_dir / "target_profile.csv", index=False)
    overlap.to_csv(out_dir / "target_overlap.csv", index=False)
    audit.to_csv(out_dir / "inconsistency_audit.csv", index=False)

    metrics_frames = []
    importance_frames = []
    for target in targets:
        metrics, importance = train_target(df, target, out_dir, features)
        metrics_frames.append(metrics)
        importance_frames.append(importance)

    metrics = pd.concat(metrics_frames, ignore_index=True)
    importance = pd.concat([frame for frame in importance_frames if not frame.empty], ignore_index=True)
    metrics.insert(0, "experiment", spec.folder)
    importance.insert(0, "experiment", spec.folder)
    metrics.to_csv(out_dir / "model_metrics.csv", index=False)
    importance.to_csv(out_dir / "feature_importance.csv", index=False)
    write_experiment_plots(metrics, profile, out_dir)
    write_run_log(spec, profile, metrics, audit, out_dir)
    return metrics


def write_cross_experiment_outputs(all_metrics: pd.DataFrame) -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    all_metrics.to_csv(OUT_ROOT / "all_broader_target_model_metrics.csv", index=False)
    test = all_metrics[all_metrics["split"] == "test"].copy()
    summary = (
        test.groupby(["experiment", "target", "model"], as_index=False)
        .agg(
            runs=("seed", "count"),
            positives=("positives", "mean"),
            positive_share=("positive_share", "mean"),
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            pr_auc_mean=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
            precision_mean=("precision", "mean"),
            recall_mean=("recall", "mean"),
            f1_mean=("f1", "mean"),
        )
        .sort_values("pr_auc_mean", ascending=False)
    )
    summary.to_csv(OUT_ROOT / "experiment_comparison.csv", index=False)

    top = summary.sort_values("pr_auc_mean", ascending=False).groupby("target", as_index=False).head(1)
    lines = [
        "# Broader Target Experiment Comparison",
        "",
        "Each `test_broader_targetsN` folder contains its own target profile, model metrics, plots, predictions, and run log.",
        "",
        "## Best Rows By Target",
        "",
        frame_as_markdown(top),
        "",
        "## Integrity Note",
        "",
        "The experiments preserve null/unknown target states for rows without enough future observations. They do not forward-fill missing fundamentals or add invented data.",
        "",
    ]
    (OUT_ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    df = add_experiment_targets(df)
    features = validate_features(df, NUMERIC_FEATURES + CATEGORICAL_FEATURES)

    feature_list = pd.DataFrame({"column": features, "role": ["numeric" if col in NUMERIC_FEATURES else "categorical" for col in features]})
    feature_list.to_csv(OUT_ROOT / "experiment_feature_list.csv", index=False)

    all_metrics = []
    for spec in EXPERIMENTS:
        print(f"Running {spec.folder}: {spec.title}")
        metrics = run_experiment(df, spec, features)
        all_metrics.append(metrics)
    combined = pd.concat(all_metrics, ignore_index=True)
    write_cross_experiment_outputs(combined)
    print((OUT_ROOT / "experiment_comparison.csv").resolve())


if __name__ == "__main__":
    main()
