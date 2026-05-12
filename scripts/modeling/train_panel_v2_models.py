#!/usr/bin/env python3
"""Train baseline models for the rebuilt panel with temporal validation."""

from __future__ import annotations

import json
import argparse
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
PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
MODEL_DIR = PROJECT_ROOT / "models/panel_v2"
REPORT_DIR = PROJECT_ROOT / "reports/modeling"
FIG_DIR = PROJECT_ROOT / "reports/figures/modeling"
DATA_QUALITY_DIR = PROJECT_ROOT / "reports/data_quality"
FEATURE_LIST_DIR = DATA_QUALITY_DIR / "model_feature_lists"
BLACKLIST_PATH = PROJECT_ROOT / "config/model_feature_blacklist.csv"

DEFAULT_TARGET = "distress_next_4q"


NUMERIC_FEATURES = [
    "total_assets",
    "total_liabilities",
    "long_term_debt",
    "short_term_debt",
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
    "roa_lag1",
    "leverage_assets_lag1",
    "current_ratio_lag1",
    "cash_assets_lag1",
    "net_margin_lag1",
    "operating_margin_lag1",
    "gross_margin_lag1",
    "total_revenue_growth_4obs",
    "total_assets_growth_4obs",
    "cash_equivalents_growth_4obs",
    "total_liabilities_growth_4obs",
    "current_assets_growth_4obs",
    "current_liabilities_growth_4obs",
    "roa_change_4obs",
    "leverage_assets_change_4obs",
    "current_ratio_change_4obs",
    "cash_assets_change_4obs",
    "net_margin_change_4obs",
    "operating_margin_change_4obs",
    "gross_margin_change_4obs",
    "net_income_negative_count_prior_4obs",
    "BAMLH0A0HYM2",
    "FEDFUNDS",
    "GDPC1",
    "GS10",
    "INDPRO",
    "INDPRO_yoy_pct",
    "M2SL",
    "M2SL_yoy_pct",
    "NFCI",
    "UNRATE",
    "USEPUINDXD",
    "VIXCLS",
    "T10Y2Y",
    "T10Y3M",
    "DCOILWTICO",
    "DCOILWTICO_yoy_pct",
    "DTWEXBGS",
    "DTWEXBGS_yoy_pct",
    "CPIAUCSL",
    "CPIAUCSL_yoy_pct",
    "PPIACO",
    "PPIACO_yoy_pct",
    "PAYEMS",
    "PAYEMS_yoy_pct",
    "RSAFS",
    "RSAFS_yoy_pct",
    "HOUST",
    "HOUST_yoy_pct",
    "BUSLOANS",
    "BUSLOANS_yoy_pct",
    "DRTSCILM",
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
    "global_event_count",
    "global_event_severity_sum",
    "global_event_banking_stress_count",
    "global_event_banking_stress_severity",
    "global_event_commodity_oil_count",
    "global_event_commodity_oil_severity",
    "global_event_financial_crisis_count",
    "global_event_financial_crisis_severity",
    "global_event_financial_market_count",
    "global_event_financial_market_severity",
    "global_event_geopolitical_war_count",
    "global_event_geopolitical_war_severity",
    "global_event_monetary_inflation_count",
    "global_event_monetary_inflation_severity",
    "global_event_natural_disaster_count",
    "global_event_natural_disaster_severity",
    "global_event_pandemic_count",
    "global_event_pandemic_severity",
    "global_event_political_policy_count",
    "global_event_political_policy_severity",
    "global_event_sovereign_debt_count",
    "global_event_sovereign_debt_severity",
    "global_event_supply_chain_count",
    "global_event_supply_chain_severity",
    "global_event_trade_policy_count",
    "global_event_trade_policy_severity",
    "prediction_quarter",
]

CATEGORICAL_FEATURES = ["Sector"]


def load_panel(target: str) -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in ["period_date", "filed_date", "prediction_date", "event_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "prediction_date" not in df.columns:
        raise ValueError("Panel is missing prediction_date. Rebuild it with scripts/sec_fsd/build_panel_v2.py.")

    df = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    if "post_event_flag" in df.columns:
        df = df[df["post_event_flag"].fillna(0).astype(int) == 0].copy()
    df = df[df[target].notna()].copy()
    df[target] = df[target].astype(int)
    return df


def make_splits(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    year = df["prediction_date"].dt.year
    return {
        "train": df[year <= 2018].copy(),
        "validation": df[(year >= 2019) & (year <= 2021)].copy(),
        "test": df[(year >= 2022) & (year <= 2024)].copy(),
    }


def load_feature_blacklist() -> set[str]:
    if not BLACKLIST_PATH.exists():
        return set()
    blacklist = pd.read_csv(BLACKLIST_PATH)
    first_col = blacklist.columns[0]
    return set(blacklist[first_col].dropna().astype(str))


def validate_features(df: pd.DataFrame, features: list[str]) -> list[str]:
    missing = [feature for feature in features if feature not in df.columns]
    if missing:
        raise ValueError(f"Configured model features are missing from the panel: {missing}")

    blacklisted = sorted(set(features) & load_feature_blacklist())
    if blacklisted:
        raise ValueError(f"Configured model features include leakage/audit-only columns: {blacklisted}")
    return features


def save_feature_list(target: str, features: list[str]) -> None:
    FEATURE_LIST_DIR.mkdir(parents=True, exist_ok=True)
    roles = {
        feature: "numeric" if feature in NUMERIC_FEATURES else "categorical"
        for feature in features
    }
    pd.DataFrame(
        {
            "target": target,
            "column": features,
            "role": [roles[feature] for feature in features],
            "source": "scripts/modeling/train_panel_v2_models.py",
        }
    ).to_csv(FEATURE_LIST_DIR / f"{target}_features.csv", index=False)


def build_preprocessor() -> ColumnTransformer:
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
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def build_models() -> dict[str, Pipeline]:
    return {
        "logistic_l2": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        solver="liblinear",
                        random_state=42,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=400,
                        min_samples_leaf=5,
                        class_weight="balanced_subsample",
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "gradient_boosting": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    GradientBoostingClassifier(
                        n_estimators=250,
                        learning_rate=0.04,
                        max_depth=3,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }


def predict_proba(model: Pipeline, x: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(x)[:, 1]


def choose_threshold(y_true: np.ndarray, proba: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    if len(thresholds) == 0:
        return 0.5
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(f1))])


def evaluate(model_name: str, split_name: str, y_true: np.ndarray, proba: np.ndarray, threshold: float) -> dict:
    y_pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "model": model_name,
        "split": split_name,
        "rows": int(len(y_true)),
        "positives": int(y_true.sum()),
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


def class_weight_sample(y: pd.Series) -> np.ndarray:
    counts = y.value_counts().to_dict()
    n = len(y)
    return y.map({klass: n / (2 * count) for klass, count in counts.items()}).to_numpy()


def get_feature_names(model: Pipeline) -> list[str]:
    preprocessor = model.named_steps["preprocess"]
    return list(preprocessor.get_feature_names_out())


def feature_importance(model_name: str, model: Pipeline) -> pd.DataFrame:
    names = get_feature_names(model)
    estimator = model.named_steps["model"]
    if hasattr(estimator, "coef_"):
        values = np.abs(estimator.coef_[0])
    elif hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    else:
        return pd.DataFrame()

    return (
        pd.DataFrame({"model": model_name, "feature": names, "importance": values})
        .sort_values("importance", ascending=False)
        .head(30)
    )


def plot_curves(metrics_frame: pd.DataFrame, predictions: dict[str, dict[str, np.ndarray]], target: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    for model_name, payload in predictions.items():
        y_true = payload["test_y"]
        proba = payload["test_proba"]
        if len(np.unique(y_true)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y_true, proba)
        auc = roc_auc_score(y_true, proba)
        plt.plot(fpr, tpr, label=f"{model_name} AUC={auc:.3f}")
    plt.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title(f"{target} ROC curve, test period 2022-2024")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"panel_v2_{target}_test_roc.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 6))
    for model_name, payload in predictions.items():
        y_true = payload["test_y"]
        proba = payload["test_proba"]
        if len(np.unique(y_true)) < 2:
            continue
        precision, recall, _ = precision_recall_curve(y_true, proba)
        ap = average_precision_score(y_true, proba)
        plt.plot(recall, precision, label=f"{model_name} AP={ap:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"{target} precision-recall curve, test period 2022-2024")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"panel_v2_{target}_test_precision_recall.png", dpi=200)
    plt.close()

    test_metrics = metrics_frame[metrics_frame["split"] == "test"].sort_values("pr_auc", ascending=False)
    plt.figure(figsize=(8, 5))
    plt.bar(test_metrics["model"], test_metrics["pr_auc"])
    plt.ylabel("Average precision")
    plt.title(f"{target} model comparison on temporal test period")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"panel_v2_{target}_model_comparison_pr_auc.png", dpi=200)
    plt.close()

    if target == DEFAULT_TARGET:
        for source, dest in [
            (FIG_DIR / f"panel_v2_{target}_test_roc.png", FIG_DIR / "panel_v2_test_roc.png"),
            (
                FIG_DIR / f"panel_v2_{target}_test_precision_recall.png",
                FIG_DIR / "panel_v2_test_precision_recall.png",
            ),
            (
                FIG_DIR / f"panel_v2_{target}_model_comparison_pr_auc.png",
                FIG_DIR / "panel_v2_model_comparison_pr_auc.png",
            ),
        ]:
            dest.write_bytes(source.read_bytes())


def plot_feature_importance(importances: pd.DataFrame, target: str) -> None:
    if importances.empty:
        return
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for model_name, group in importances.groupby("model"):
        top = group.sort_values("importance", ascending=True).tail(15)
        plt.figure(figsize=(8, 6))
        labels = top["feature"].str.replace("num__", "", regex=False).str.replace("cat__", "", regex=False)
        plt.barh(labels, top["importance"])
        plt.title(f"Top feature importance: {model_name} / {target}")
        plt.tight_layout()
        target_path = FIG_DIR / f"panel_v2_{target}_feature_importance_{model_name}.png"
        plt.savefig(target_path, dpi=200)
        plt.close()
        if target == DEFAULT_TARGET:
            (FIG_DIR / f"panel_v2_feature_importance_{model_name}.png").write_bytes(target_path.read_bytes())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train temporal-validation panel models.")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Binary target column to model.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target = args.target
    output_prefix = f"panel_v2_{target}"

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_panel(target)
    splits = make_splits(df)
    split_summary = []
    for name, split in splits.items():
        split_summary.append({"split": name, "rows": len(split), "positives": int(split[target].sum())})
    split_summary_frame = pd.DataFrame(split_summary)
    split_summary_frame.to_csv(REPORT_DIR / f"{output_prefix}_temporal_split_summary.csv", index=False)

    features = validate_features(df, NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    save_feature_list(target, features)
    models = build_models()
    metrics = []
    importances = []
    predictions = {}

    x_train = splits["train"][features]
    y_train = splits["train"][target].astype(int)
    x_val = splits["validation"][features]
    y_val = splits["validation"][target].astype(int)
    x_test = splits["test"][features]
    y_test = splits["test"][target].astype(int)

    for model_name, model in models.items():
        print(f"Training {model_name}")
        if model_name == "gradient_boosting":
            model.fit(x_train, y_train, model__sample_weight=class_weight_sample(y_train))
        else:
            model.fit(x_train, y_train)

        val_proba = predict_proba(model, x_val)
        threshold = choose_threshold(y_val.to_numpy(), val_proba)

        for split_name, x_split, y_split in [
            ("train", x_train, y_train),
            ("validation", x_val, y_val),
            ("test", x_test, y_test),
        ]:
            proba = predict_proba(model, x_split)
            metrics.append(evaluate(model_name, split_name, y_split.to_numpy(), proba, threshold))

        predictions[model_name] = {
            "test_y": y_test.to_numpy(),
            "test_proba": predict_proba(model, x_test),
        }
        importances.append(feature_importance(model_name, model))
        joblib.dump(model, MODEL_DIR / f"{target}_{model_name}.joblib")

    metrics_frame = pd.DataFrame(metrics)
    metrics_frame.to_csv(REPORT_DIR / f"{output_prefix}_model_metrics.csv", index=False)

    importances_frame = pd.concat([df for df in importances if not df.empty], ignore_index=True)
    importances_frame.to_csv(REPORT_DIR / f"{output_prefix}_feature_importance.csv", index=False)

    plot_curves(metrics_frame, predictions, target)
    plot_feature_importance(importances_frame, target)

    best = metrics_frame[metrics_frame["split"] == "test"].sort_values("pr_auc", ascending=False).head(1)
    (REPORT_DIR / f"{output_prefix}_best_model.json").write_text(
        json.dumps(best.to_dict(orient="records")[0], indent=2),
        encoding="utf-8",
    )

    if target == DEFAULT_TARGET:
        split_summary_frame.to_csv(REPORT_DIR / "panel_v2_temporal_split_summary.csv", index=False)
        metrics_frame.to_csv(REPORT_DIR / "panel_v2_model_metrics.csv", index=False)
        importances_frame.to_csv(REPORT_DIR / "panel_v2_feature_importance.csv", index=False)
        (REPORT_DIR / "panel_v2_best_model.json").write_text(
            json.dumps(best.to_dict(orient="records")[0], indent=2),
            encoding="utf-8",
        )
    print(metrics_frame[metrics_frame["split"] == "test"].to_string(index=False))


if __name__ == "__main__":
    main()
