#!/usr/bin/env python3
"""Ablation tests for firm-only vs macro/regime feature sets."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
REPORT_DIR = PROJECT_ROOT / "reports/modeling"
FIG_DIR = PROJECT_ROOT / "reports/figures/modeling"
DATA_QUALITY_DIR = PROJECT_ROOT / "reports/data_quality"
FEATURE_LIST_DIR = DATA_QUALITY_DIR / "model_feature_lists"
BLACKLIST_PATH = PROJECT_ROOT / "config/model_feature_blacklist.csv"
TARGET = "distress_next_4q"

FIRM_NUMERIC = [
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
    "prediction_quarter",
]

MACRO_NUMERIC = [
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
]

REGIME_NUMERIC = [
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
]

EVENT_NUMERIC = [
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
]

CATEGORICAL = ["Sector"]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in ["period_date", "filed_date", "prediction_date", "event_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "prediction_date" not in df.columns:
        raise ValueError("Panel is missing prediction_date. Rebuild it with scripts/sec_fsd/build_panel_v2.py.")

    df = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    if "post_event_flag" in df.columns:
        df = df[df["post_event_flag"].fillna(0).astype(int) == 0].copy()
    df[TARGET] = df[TARGET].astype(int)
    return df


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    year = df["prediction_date"].dt.year
    return df[year <= 2018], df[(year >= 2019) & (year <= 2021)], df[(year >= 2022) & (year <= 2024)]


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


def save_ablation_feature_list(feature_sets: dict[str, list[str]]) -> None:
    FEATURE_LIST_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for feature_set, numeric_features in feature_sets.items():
        for feature in numeric_features + CATEGORICAL:
            rows.append(
                {
                    "target": TARGET,
                    "feature_set": feature_set,
                    "column": feature,
                    "role": "numeric" if feature in numeric_features else "categorical",
                    "source": "scripts/modeling/run_panel_v2_ablation.py",
                }
            )
    pd.DataFrame(rows).to_csv(FEATURE_LIST_DIR / f"{TARGET}_ablation_features.csv", index=False)


def preprocessor(numeric_features: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median", add_indicator=True)), ("scaler", StandardScaler())]),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL,
            ),
        ]
    )


def model_specs(numeric_features: list[str]) -> dict[str, Pipeline]:
    return {
        "logistic_l2": Pipeline(
            [
                ("preprocess", preprocessor(numeric_features)),
                ("model", LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("preprocess", preprocessor(numeric_features)),
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
    }


def best_threshold(y_true: pd.Series, proba: np.ndarray) -> float:
    thresholds = np.unique(np.quantile(proba, np.linspace(0.01, 0.99, 99)))
    best = 0.5
    best_f1 = -1.0
    for threshold in thresholds:
        pred = (proba >= threshold).astype(int)
        score = f1_score(y_true, pred, zero_division=0)
        if score > best_f1:
            best_f1 = score
            best = float(threshold)
    return best


def evaluate(y_true: pd.Series, proba: np.ndarray, threshold: float) -> dict:
    pred = (proba >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, proba),
        "pr_auc": average_precision_score(y_true, proba),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    train, validation, test = split(df)

    feature_sets = {
        "firm_only": FIRM_NUMERIC,
        "firm_plus_macro": FIRM_NUMERIC + MACRO_NUMERIC,
        "firm_plus_macro_regime": FIRM_NUMERIC + MACRO_NUMERIC + REGIME_NUMERIC,
        "firm_plus_macro_regime_event": FIRM_NUMERIC + MACRO_NUMERIC + REGIME_NUMERIC + EVENT_NUMERIC,
    }
    for feature_set, numeric_features in feature_sets.items():
        feature_sets[feature_set] = validate_features(df, numeric_features + CATEGORICAL)[: len(numeric_features)]
    save_ablation_feature_list(feature_sets)

    rows = []
    for feature_set, numeric_features in feature_sets.items():
        features = numeric_features + CATEGORICAL
        for model_name, model in model_specs(numeric_features).items():
            model.fit(train[features], train[TARGET])
            val_proba = model.predict_proba(validation[features])[:, 1]
            threshold = best_threshold(validation[TARGET], val_proba)
            test_proba = model.predict_proba(test[features])[:, 1]
            row = {
                "feature_set": feature_set,
                "model": model_name,
                "threshold": threshold,
                "test_rows": len(test),
                "test_positives": int(test[TARGET].sum()),
            }
            row.update(evaluate(test[TARGET], test_proba, threshold))
            rows.append(row)

    out = pd.DataFrame(rows).sort_values(["model", "pr_auc"], ascending=[True, False])
    out.to_csv(REPORT_DIR / "panel_v2_ablation_metrics.csv", index=False)

    plot_data = out.sort_values("pr_auc", ascending=False)
    plt.figure(figsize=(9, 5))
    labels = plot_data["model"] + " / " + plot_data["feature_set"]
    plt.barh(labels, plot_data["pr_auc"])
    plt.xlabel("Test average precision")
    plt.title("Feature-set ablation on temporal test period")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "panel_v2_ablation_pr_auc.png", dpi=200)
    plt.close()
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
