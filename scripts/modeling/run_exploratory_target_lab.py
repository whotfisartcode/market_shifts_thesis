#!/usr/bin/env python3
"""Run the controlled target lab without changing the production panel.

The production panel is the 31,702 x 190 source artifact after validated
secondary target promotion. This script builds an in-memory extension frame with
financial-quality features, market-health v2 scores, promoted secondary labels,
diagnostic labels, and robustness-extension labels, then writes profiles and
baseline temporal-model diagnostics under reports/target_lab.
"""

from __future__ import annotations

import sys
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

from scripts.modeling.train_panel_v2_models import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    validate_features,
)


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
FRED_DIR = PROJECT_ROOT / "data/raw/fred"
FRED_CATALOG_PATH = PROJECT_ROOT / "config/fred_series_catalog.csv"
OUT_DIR = PROJECT_ROOT / "reports/target_lab"
FIG_DIR = PROJECT_ROOT / "reports/figures/target_lab"
DATA_QUALITY_DIR = PROJECT_ROOT / "reports/data_quality"

DATE_COLS = ["period_date", "filed_date", "prediction_date", "event_date"]

EXPLORATORY_TARGETS = [
    "industry_relative_resilience_next_4obs",
    "stress_resilience_next_4obs",
    "recovery_next_4obs",
    "deterioration_next_4obs",
    "quality_success_cashflow_next_4obs",
    "sector_relative_improvement_next_4obs",
    "persistent_resilience_next_6obs",
]

FINANCIAL_QUALITY_FEATURES = [
    "cfo_assets",
    "cfo_margin",
    "accruals_assets",
    "working_capital_assets",
    "cash_to_current_liabilities",
    "capex_intensity_assets",
    "capex_intensity_revenue",
    "debt_to_cfo",
]

MARKET_HEALTH_FEATURES = [
    "market_stress_score_v2",
    "market_health_score_v2",
    "credit_stress_score",
    "real_activity_pressure_score",
    "policy_uncertainty_score",
    "stress_elevated_v2",
]

MIN_KNOWN_ROWS = 1_000
MIN_POSITIVES = 50
MIN_TEST_POSITIVES = 10


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace({0: np.nan})
    return numerator / denominator


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_candidates = set(NUMERIC_FEATURES) | {
        "distress_next_4q",
        "failure_pressure_conservative_v2_next_4obs",
        "success_resilience_next_4q",
        "post_event_flag",
        "formal_distress_firm",
        "days_to_event",
        "healthy_current",
        "total_debt",
        *FINANCIAL_QUALITY_FEATURES,
        *MARKET_HEALTH_FEATURES,
    }
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).reset_index(drop=True)
    return df


def add_financial_quality_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in [
        "cash_flow_operating",
        "total_assets",
        "total_revenue",
        "net_income",
        "current_assets",
        "current_liabilities",
        "cash_equivalents",
        "capex",
        "long_term_debt",
        "short_term_debt",
    ]:
        if col not in df.columns:
            df[col] = np.nan

    total_debt = df["long_term_debt"].fillna(0) + df["short_term_debt"].fillna(0)
    total_debt = total_debt.where(df[["long_term_debt", "short_term_debt"]].notna().any(axis=1))
    df["total_debt_for_quality"] = total_debt

    df["cfo_assets"] = safe_divide(df["cash_flow_operating"], df["total_assets"])
    df["cfo_margin"] = safe_divide(df["cash_flow_operating"], df["total_revenue"])
    df["accruals_assets"] = safe_divide(df["net_income"] - df["cash_flow_operating"], df["total_assets"])
    df["working_capital_assets"] = safe_divide(df["current_assets"] - df["current_liabilities"], df["total_assets"])
    df["cash_to_current_liabilities"] = safe_divide(df["cash_equivalents"], df["current_liabilities"])
    df["capex_intensity_assets"] = safe_divide(df["capex"], df["total_assets"])
    df["capex_intensity_revenue"] = safe_divide(df["capex"], df["total_revenue"])

    usable_cfo = df["cash_flow_operating"].where(df["cash_flow_operating"] > 0)
    df["debt_to_cfo"] = safe_divide(df["total_debt_for_quality"], usable_cfo)
    return df


def clean_financial_quality_extremes(df: pd.DataFrame, threshold: float = 100.0) -> pd.DataFrame:
    df = df.copy()
    rows = []
    for feature in FINANCIAL_QUALITY_FEATURES:
        if feature not in df.columns:
            continue
        values = pd.to_numeric(df[feature], errors="coerce")
        extreme = values.abs() > threshold
        rows.append(
            {
                "feature": feature,
                "threshold_abs_gt": threshold,
                "values_set_null": int(extreme.fillna(False).sum()),
                "missing_share_after": float(values.mask(extreme).isna().mean()),
            }
        )
        if extreme.any():
            df.loc[extreme, feature] = np.nan
    DATA_QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(DATA_QUALITY_DIR / "financial_quality_feature_extreme_cleanup.csv", index=False)
    return df


def component_indicator(df: pd.DataFrame, column: str, condition) -> pd.Series:
    if column not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype="float64")
    values = pd.to_numeric(df[column], errors="coerce")
    out = pd.Series(np.nan, index=df.index, dtype="float64")
    valid = values.notna()
    out.loc[valid] = condition(values.loc[valid]).astype(float)
    return out


def add_market_health_v2_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    components = {
        "vix_ge_25": ("VIXCLS", component_indicator(df, "VIXCLS", lambda s: s >= 25.0), "market_stress_score_v2"),
        "hy_oas_ge_5": (
            "BAMLH0A0HYM2",
            component_indicator(df, "BAMLH0A0HYM2", lambda s: s >= 5.0),
            "market_stress_score_v2;credit_stress_score",
        ),
        "nfci_positive": (
            "NFCI",
            component_indicator(df, "NFCI", lambda s: s > 0.0),
            "market_stress_score_v2;credit_stress_score",
        ),
        "loan_standards_tightening": (
            "DRTSCILM",
            component_indicator(df, "DRTSCILM", lambda s: s > 0.0),
            "market_stress_score_v2;credit_stress_score",
        ),
        "yield_curve_inverted": (
            "T10Y2Y/T10Y3M",
            pd.concat(
                [
                    component_indicator(df, "T10Y2Y", lambda s: s < 0.0),
                    component_indicator(df, "T10Y3M", lambda s: s < 0.0),
                ],
                axis=1,
            ).max(axis=1, skipna=True),
            "market_stress_score_v2;credit_stress_score",
        ),
        "inflation_yoy_ge_4": (
            "CPIAUCSL_yoy_pct",
            component_indicator(df, "CPIAUCSL_yoy_pct", lambda s: s >= 4.0),
            "market_stress_score_v2",
        ),
        "oil_yoy_ge_30": (
            "DCOILWTICO_yoy_pct",
            component_indicator(df, "DCOILWTICO_yoy_pct", lambda s: s >= 30.0),
            "market_stress_score_v2",
        ),
        "dollar_yoy_ge_5": (
            "DTWEXBGS_yoy_pct",
            component_indicator(df, "DTWEXBGS_yoy_pct", lambda s: s >= 5.0),
            "market_stress_score_v2",
        ),
        "retail_sales_yoy_negative": (
            "RSAFS_yoy_pct",
            component_indicator(df, "RSAFS_yoy_pct", lambda s: s < 0.0),
            "market_stress_score_v2;real_activity_pressure_score",
        ),
        "busloans_yoy_negative": (
            "BUSLOANS_yoy_pct",
            component_indicator(df, "BUSLOANS_yoy_pct", lambda s: s < 0.0),
            "credit_stress_score",
        ),
        "unrate_ge_6": (
            "UNRATE",
            component_indicator(df, "UNRATE", lambda s: s >= 6.0),
            "real_activity_pressure_score",
        ),
        "industrial_production_yoy_negative": (
            "INDPRO_yoy_pct",
            component_indicator(df, "INDPRO_yoy_pct", lambda s: s < 0.0),
            "real_activity_pressure_score",
        ),
        "payrolls_yoy_negative": (
            "PAYEMS_yoy_pct",
            component_indicator(df, "PAYEMS_yoy_pct", lambda s: s < 0.0),
            "real_activity_pressure_score",
        ),
        "housing_yoy_negative": (
            "HOUST_yoy_pct",
            component_indicator(df, "HOUST_yoy_pct", lambda s: s < 0.0),
            "real_activity_pressure_score",
        ),
    }

    component_frame = pd.DataFrame({name: payload[1] for name, payload in components.items()}, index=df.index)
    stress_cols = [name for name, payload in components.items() if "market_stress_score_v2" in payload[2]]
    credit_cols = [name for name, payload in components.items() if "credit_stress_score" in payload[2]]
    activity_cols = [name for name, payload in components.items() if "real_activity_pressure_score" in payload[2]]

    df["market_stress_score_v2"] = component_frame[stress_cols].mean(axis=1, skipna=True)
    df["market_health_score_v2"] = 1.0 - df["market_stress_score_v2"]
    df["credit_stress_score"] = component_frame[credit_cols].mean(axis=1, skipna=True)
    df["real_activity_pressure_score"] = component_frame[activity_cols].mean(axis=1, skipna=True)

    if "USEPUINDXD" in df.columns:
        epu = pd.to_numeric(df["USEPUINDXD"], errors="coerce")
        df["policy_uncertainty_score"] = ((epu - 100.0) / 200.0).clip(lower=0.0, upper=1.0)
    else:
        df["policy_uncertainty_score"] = np.nan

    df["stress_elevated_v2"] = (
        (df["market_stress_score_v2"] >= 0.30)
        | (df["credit_stress_score"] >= 0.50)
        | (df.get("market_stress_regime", pd.Series(0, index=df.index)).fillna(0).astype(float) == 1)
    ).astype("Int64")

    coverage_rows = []
    for name, (source, values, score_group) in components.items():
        coverage_rows.append(
            {
                "component": name,
                "source_column": source,
                "score_group": score_group,
                "available_rows": int(values.notna().sum()),
                "coverage_share": float(values.notna().mean()),
                "positive_rows": int(values.fillna(0).sum()),
            }
        )
    coverage_rows.append(
        {
            "component": "policy_uncertainty_scaled",
            "source_column": "USEPUINDXD",
            "score_group": "policy_uncertainty_score",
            "available_rows": int(df["policy_uncertainty_score"].notna().sum()),
            "coverage_share": float(df["policy_uncertainty_score"].notna().mean()),
            "positive_rows": int((df["policy_uncertainty_score"].fillna(0) > 0).sum()),
        }
    )
    return df, pd.DataFrame(coverage_rows)


def future_shifts(df: pd.DataFrame, column: str, horizon: int = 4) -> list[pd.Series]:
    grouped = df.groupby("cik", group_keys=False)[column]
    return [grouped.shift(-step) for step in range(1, horizon + 1)]


def valid_count(series_list: list[pd.Series]) -> pd.Series:
    return pd.concat([series.notna().astype(int) for series in series_list], axis=1).sum(axis=1)


def condition_count(series_list: list[pd.Series], condition) -> pd.Series:
    return pd.concat([condition(series).fillna(False).astype(int) for series in series_list], axis=1).sum(axis=1)


def nullable_label(positive: pd.Series, known: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=positive.index, dtype="Int64")
    known = known.fillna(False)
    out.loc[known] = positive.loc[known].fillna(False).astype(int).astype("Int64")
    return out


def add_sector_year_thresholds(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    group_cols = ["Sector", "prediction_year"]
    for col, suffix, func in [
        ("roa", "median", "median"),
        ("net_margin", "median", "median"),
        ("leverage_assets", "q75", lambda s: s.quantile(0.75)),
    ]:
        out_col = f"sector_year_{col}_{suffix}"
        if col in df.columns:
            df[out_col] = df.groupby(group_cols, dropna=False)[col].transform(func)
            fallback = df.groupby("prediction_year", dropna=False)[col].transform(func)
            df[out_col] = df[out_col].fillna(fallback)
        else:
            df[out_col] = np.nan
    return df


def add_exploratory_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = add_sector_year_thresholds(df.copy())

    adsh_future = future_shifts(df, "adsh")
    adsh_future_6 = future_shifts(df, "adsh", horizon=6)
    df["future_observation_count_4obs_lab"] = valid_count(adsh_future)
    df["future_observation_count_6obs_lab"] = valid_count(adsh_future_6)

    net_income = future_shifts(df, "net_income")
    roa = future_shifts(df, "roa")
    net_margin = future_shifts(df, "net_margin")
    leverage = future_shifts(df, "leverage_assets")
    equity_assets = future_shifts(df, "equity_assets")
    cfo = future_shifts(df, "cash_flow_operating")

    roa_median = future_shifts(df, "sector_year_roa_median")
    margin_median = future_shifts(df, "sector_year_net_margin_median")
    leverage_q75 = future_shifts(df, "sector_year_leverage_assets_q75")

    net_income_6 = future_shifts(df, "net_income", horizon=6)
    roa_6 = future_shifts(df, "roa", horizon=6)
    leverage_6 = future_shifts(df, "leverage_assets", horizon=6)

    future_net_income_valid = valid_count(net_income)
    future_roa_valid = valid_count(roa)
    future_margin_valid = valid_count(net_margin)
    future_leverage_valid = valid_count(leverage)
    future_equity_valid = valid_count(equity_assets)
    future_cfo_valid = valid_count(cfo)
    future_health_valid = valid_count(
        [
            pd.concat([net_income[i], roa[i], leverage[i]], axis=1).dropna(how="any").iloc[:, 0]
            .reindex(df.index)
            for i in range(4)
        ]
    )
    future_health_valid_6 = valid_count(
        [
            pd.concat([net_income_6[i], roa_6[i], leverage_6[i]], axis=1).dropna(how="any").iloc[:, 0]
            .reindex(df.index)
            for i in range(6)
        ]
    )

    future_income_positive = condition_count(net_income, lambda s: s > 0)
    future_income_nonpositive = condition_count(net_income, lambda s: s <= 0)
    future_roa_positive = condition_count(roa, lambda s: s > 0)
    future_roa_nonpositive = condition_count(roa, lambda s: s <= 0)
    future_leverage_ok = condition_count(leverage, lambda s: s.between(0, 0.85, inclusive="both"))
    future_cfo_positive = condition_count(cfo, lambda s: s > 0)

    healthy_parts = []
    healthy_parts_6 = []
    quality_cashflow_parts = []
    relative_valid_parts = []
    relative_good_parts = []
    relative_profit_valid_parts = []
    relative_profit_above_parts = []
    for i in range(4):
        healthy = (
            (net_income[i] > 0)
            & (roa[i] > 0)
            & leverage[i].between(0, 0.85, inclusive="both")
        )
        healthy_valid = net_income[i].notna() & roa[i].notna() & leverage[i].notna()
        healthy_parts.append((healthy & healthy_valid).astype(int))

        quality = healthy & (cfo[i] > 0)
        quality_valid = healthy_valid & cfo[i].notna()
        quality_cashflow_parts.append((quality & quality_valid).astype(int))

        relative_profit_valid = (
            (roa[i].notna() & roa_median[i].notna())
            | (net_margin[i].notna() & margin_median[i].notna())
        )
        above_sector = (
            (roa[i].notna() & roa_median[i].notna() & (roa[i] > roa_median[i]))
            | (net_margin[i].notna() & margin_median[i].notna() & (net_margin[i] > margin_median[i]))
        )
        leverage_relative_valid = leverage[i].notna() & leverage_q75[i].notna()
        leverage_not_worst_quartile = leverage[i] <= leverage_q75[i]
        relative_valid_parts.append((relative_profit_valid & leverage_relative_valid).astype(int))
        relative_good_parts.append((above_sector & leverage_not_worst_quartile & leverage_relative_valid).astype(int))
        relative_profit_valid_parts.append(relative_profit_valid.astype(int))
        relative_profit_above_parts.append((above_sector & relative_profit_valid).astype(int))

    for i in range(6):
        healthy_6 = (
            (net_income_6[i] > 0)
            & (roa_6[i] > 0)
            & leverage_6[i].between(0, 0.85, inclusive="both")
        )
        healthy_valid_6 = net_income_6[i].notna() & roa_6[i].notna() & leverage_6[i].notna()
        healthy_parts_6.append((healthy_6 & healthy_valid_6).astype(int))

    future_healthy_count = pd.concat(healthy_parts, axis=1).sum(axis=1)
    future_healthy_count_6 = pd.concat(healthy_parts_6, axis=1).sum(axis=1)
    future_quality_cashflow_count = pd.concat(quality_cashflow_parts, axis=1).sum(axis=1)
    relative_valid_count = pd.concat(relative_valid_parts, axis=1).sum(axis=1)
    relative_good_count = pd.concat(relative_good_parts, axis=1).sum(axis=1)
    relative_profit_valid_count = pd.concat(relative_profit_valid_parts, axis=1).sum(axis=1)
    relative_profit_above_count = pd.concat(relative_profit_above_parts, axis=1).sum(axis=1)

    leverage_last = leverage[-1]
    equity_last = equity_assets[-1]
    leverage_increase = leverage_last - df["leverage_assets"]
    equity_decline = equity_last - df["equity_assets"]

    formal = df["distress_next_4q"].fillna(0).astype(int) == 1
    formal_next_6q = (
        (df["formal_distress_firm"].fillna(0).astype(int) == 1)
        & (pd.to_numeric(df["days_to_event"], errors="coerce") > 0)
        & (pd.to_numeric(df["days_to_event"], errors="coerce") <= 684)
    )
    post_event = df["post_event_flag"].fillna(0).astype(int) == 1
    enough_future_obs = df["future_observation_count_4obs_lab"] >= 3
    enough_future_obs_6 = df["future_observation_count_6obs_lab"] >= 5

    relative_known = ((enough_future_obs & (relative_valid_count >= 3)) | formal) & ~post_event
    df["industry_relative_resilience_next_4obs"] = nullable_label(
        (relative_good_count >= 3) & ~formal,
        relative_known,
    )

    stress_current = df["stress_elevated_v2"].fillna(0).astype(int) == 1
    stress_known = stress_current & (((future_health_valid >= 3) & enough_future_obs) | formal) & ~post_event
    df["stress_resilience_next_4obs"] = nullable_label(
        (future_healthy_count >= 3) & ~formal,
        stress_known,
    )

    current_weak_components = pd.concat(
        [
            (df["net_income"].notna() & (df["net_income"] <= 0)).astype(int),
            (df["roa"].notna() & (df["roa"] <= 0)).astype(int),
            (df["leverage_assets"].notna() & (df["leverage_assets"] > 0.85)).astype(int),
            (df["current_ratio"].notna() & (df["current_ratio"] < 1.0)).astype(int),
            (df["cash_assets"].notna() & (df["cash_assets"] < 0.03)).astype(int),
        ],
        axis=1,
    ).sum(axis=1)
    current_weak = current_weak_components >= 1
    recovery_known = current_weak & (((future_health_valid >= 3) & enough_future_obs) | formal) & ~post_event
    recovery_positive = (
        (future_healthy_count >= 2)
        & (future_income_positive >= 2)
        & (future_roa_positive >= 2)
        & (future_leverage_ok >= 2)
        & ~formal
    )
    df["recovery_next_4obs"] = nullable_label(recovery_positive, recovery_known)

    current_serious_pressure = (
        ((df["net_income"].notna()) & (df["net_income"] <= 0))
        | ((df["roa"].notna()) & (df["roa"] <= 0))
        | ((df["leverage_assets"].notna()) & (df["leverage_assets"] > 0.85))
    )
    current_pressure_known = df[["net_income", "roa", "leverage_assets"]].notna().any(axis=1)
    currently_not_serious = current_pressure_known & ~current_serious_pressure
    deterioration_known = currently_not_serious & enough_future_obs & ~post_event
    production_failure = df["failure_pressure_conservative_v2_next_4obs"].fillna(0).astype(int) == 1
    repeated_negative_profitability = (
        ((future_income_nonpositive >= 2) & (future_net_income_valid >= 3))
        | ((future_roa_nonpositive >= 2) & (future_roa_valid >= 3))
    )
    balance_deterioration = (
        ((future_leverage_valid >= 3) & (leverage_increase >= 0.15))
        | ((future_equity_valid >= 3) & (equity_decline <= -0.15))
    )
    df["deterioration_next_4obs"] = nullable_label(
        formal | production_failure | repeated_negative_profitability | balance_deterioration,
        deterioration_known | (currently_not_serious & formal & ~post_event),
    )

    quality_known = (
        ((future_net_income_valid >= 3) & (future_roa_valid >= 3) & (future_leverage_valid >= 3) & (future_cfo_valid >= 3))
        | formal
    ) & ~post_event
    df["quality_success_cashflow_next_4obs"] = nullable_label(
        (future_quality_cashflow_count >= 3) & ~formal,
        quality_known,
    )

    current_roa_valid = df["roa"].notna() & df["sector_year_roa_median"].notna()
    current_margin_valid = df["net_margin"].notna() & df["sector_year_net_margin_median"].notna()
    current_relative_valid = current_roa_valid | current_margin_valid
    current_above_any_peer_median = (
        (current_roa_valid & (df["roa"] > df["sector_year_roa_median"]))
        | (current_margin_valid & (df["net_margin"] > df["sector_year_net_margin_median"]))
    )
    currently_below_peer_median = current_relative_valid & ~current_above_any_peer_median
    improvement_known = (
        currently_below_peer_median
        & (((relative_profit_valid_count >= 3) & enough_future_obs) | formal)
        & ~post_event
    )
    df["sector_relative_improvement_next_4obs"] = nullable_label(
        currently_below_peer_median & (relative_profit_above_count >= 2) & ~formal,
        improvement_known,
    )

    persistent_known = (((future_health_valid_6 >= 5) & enough_future_obs_6) | formal_next_6q) & ~post_event
    df["persistent_resilience_next_6obs"] = nullable_label(
        (future_healthy_count_6 >= 5) & ~formal_next_6q,
        persistent_known,
    )

    return df


def make_splits(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    year = df["prediction_date"].dt.year
    return {
        "train": df[year <= 2018].copy(),
        "validation": df[(year >= 2019) & (year <= 2021)].copy(),
        "test": df[(year >= 2022) & (year <= 2024)].copy(),
    }


def target_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    model_frame = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    for target in EXPLORATORY_TARGETS:
        for split_name, split_df in {"all_model_years": model_frame, **make_splits(model_frame)}.items():
            values = split_df[target]
            known = values.notna()
            positives = int(values.fillna(0).astype(int).sum())
            rows.append(
                {
                    "target": target,
                    "split": split_name,
                    "rows": int(len(split_df)),
                    "known_rows": int(known.sum()),
                    "unknown_rows": int((~known).sum()),
                    "positives": positives,
                    "positive_share_known": positives / known.sum() if known.sum() else np.nan,
                    "firms_with_positive": int(split_df.loc[values.fillna(0).astype(int) == 1, "cik"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def target_by_year_sector(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    model_frame = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    for target in EXPLORATORY_TARGETS:
        grouped = model_frame.groupby(["prediction_year", "Sector"], dropna=False)
        for (year, sector), group in grouped:
            values = group[target]
            known = values.notna()
            positives = int(values.fillna(0).astype(int).sum())
            rows.append(
                {
                    "target": target,
                    "prediction_year": year,
                    "Sector": sector,
                    "rows": int(len(group)),
                    "known_rows": int(known.sum()),
                    "positives": positives,
                    "positive_share_known": positives / known.sum() if known.sum() else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_features(df: pd.DataFrame) -> list[str]:
    numeric = [
        feature
        for feature in [*NUMERIC_FEATURES, *FINANCIAL_QUALITY_FEATURES, *MARKET_HEALTH_FEATURES]
        if feature in df.columns and df[feature].notna().any()
    ]
    categorical = [feature for feature in CATEGORICAL_FEATURES if feature in df.columns]
    return validate_features(df, numeric + categorical)


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    numeric_features = [feature for feature in features if feature not in CATEGORICAL_FEATURES]
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


def build_model(model_name: str, features: list[str]) -> Pipeline:
    if model_name == "logistic_l2":
        estimator = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear", random_state=42)
    elif model_name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=220,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        )
    elif model_name == "gradient_boosting":
        estimator = GradientBoostingClassifier(n_estimators=160, learning_rate=0.045, max_depth=3, random_state=42)
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
    f1_values = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(f1_values))])


def evaluate(
    target: str,
    model_name: str,
    split_name: str,
    y_true: np.ndarray,
    proba: np.ndarray,
    threshold: float,
) -> dict:
    y_pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "target": target,
        "model": model_name,
        "split": split_name,
        "rows": int(len(y_true)),
        "positives": int(y_true.sum()),
        "positive_share": float(y_true.mean()) if len(y_true) else np.nan,
        "threshold_from_validation": threshold,
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
    if "missingindicator_" in feature:
        return "missingness_indicator"
    raw = clean_feature_name(feature)
    if raw in FINANCIAL_QUALITY_FEATURES:
        return "financial_quality_cashflow"
    if raw in MARKET_HEALTH_FEATURES:
        return "market_health_v2"
    if raw.startswith("global_event_"):
        return "global_event_context"
    if raw.startswith("Sector_") or raw == "Sector":
        return "industry_sector"
    if raw.endswith("_lag1") or raw.endswith("_growth_4obs") or raw.endswith("_change_4obs"):
        return "firm_trend"
    if raw in {
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
    }:
        return "financial_ratio"
    if raw in {
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
    }:
        return "macro_conditions"
    if raw.startswith("Missing:") or "missingindicator_" in feature:
        return "missingness_indicator"
    return "accounting_fundamental"


def extract_group_importance(model: Pipeline, target: str, model_name: str) -> pd.DataFrame:
    estimator = model.named_steps["model"]
    if not (hasattr(estimator, "coef_") or hasattr(estimator, "feature_importances_")):
        return pd.DataFrame()
    names = model.named_steps["preprocess"].get_feature_names_out()
    values = np.abs(estimator.coef_[0]) if hasattr(estimator, "coef_") else estimator.feature_importances_
    frame = pd.DataFrame(
        {
            "target": target,
            "model": model_name,
            "feature": names,
            "feature_clean": [clean_feature_name(name) for name in names],
            "feature_group": [feature_group(name) for name in names],
            "importance": values,
        }
    )
    grouped = frame.groupby(["target", "model", "feature_group"], as_index=False)["importance"].sum()
    grouped["importance_share"] = grouped["importance"] / grouped.groupby(["target", "model"])["importance"].transform("sum")
    return grouped


def plot_curves(target: str, model_name: str, y_true: np.ndarray, proba: np.ndarray) -> None:
    if len(np.unique(y_true)) < 2:
        return
    target_slug = target.replace("/", "_")
    precision, recall, _ = precision_recall_curve(y_true, proba)
    fpr, tpr, _ = roc_curve(y_true, proba)

    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, label=f"{model_name} AP={average_precision_score(y_true, proba):.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(target)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{target_slug}_best_precision_recall.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"{model_name} AUC={roc_auc_score(y_true, proba):.3f}")
    plt.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title(target)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{target_slug}_best_roc.png", dpi=180)
    plt.close()


def train_exploratory_models(df: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_frame = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    model_frame = model_frame[model_frame["post_event_flag"].fillna(0).astype(int) == 0].copy()
    model_names = ["logistic_l2", "random_forest", "gradient_boosting"]
    metric_rows = []
    importance_frames = []

    for target in EXPLORATORY_TARGETS:
        target_df = model_frame[model_frame[target].notna()].copy()
        known_rows = len(target_df)
        positives = int(target_df[target].fillna(0).astype(int).sum())
        if known_rows < MIN_KNOWN_ROWS or positives < MIN_POSITIVES:
            metric_rows.append(
                {
                    "target": target,
                    "model": "SKIPPED",
                    "split": "all",
                    "rows": known_rows,
                    "positives": positives,
                    "skip_reason": f"below minimum known rows ({MIN_KNOWN_ROWS}) or positives ({MIN_POSITIVES})",
                }
            )
            continue

        target_df[target] = target_df[target].astype(int)
        splits = make_splits(target_df)
        if any(split.empty or split[target].nunique() < 2 for split in splits.values()):
            metric_rows.append(
                {
                    "target": target,
                    "model": "SKIPPED",
                    "split": "all",
                    "rows": known_rows,
                    "positives": positives,
                    "skip_reason": "one or more temporal splits has fewer than two classes",
                }
            )
            continue
        if int(splits["test"][target].sum()) < MIN_TEST_POSITIVES:
            metric_rows.append(
                {
                    "target": target,
                    "model": "SKIPPED",
                    "split": "all",
                    "rows": known_rows,
                    "positives": positives,
                    "skip_reason": f"test positives below {MIN_TEST_POSITIVES}",
                }
            )
            continue

        x_train = splits["train"][features]
        y_train = splits["train"][target].astype(int)
        x_val = splits["validation"][features]
        y_val = splits["validation"][target].astype(int)
        x_test = splits["test"][features]
        y_test = splits["test"][target].astype(int)

        best_test = {"pr_auc": -np.inf}
        for model_name in model_names:
            model = build_model(model_name, features)
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
                row = evaluate(target, model_name, split_name, y_split.to_numpy(), proba, threshold)
                row["skip_reason"] = ""
                metric_rows.append(row)
                if split_name == "test" and pd.notna(row["pr_auc"]) and row["pr_auc"] > best_test["pr_auc"]:
                    best_test = {
                        "pr_auc": row["pr_auc"],
                        "model": model_name,
                        "y_true": y_split.to_numpy(),
                        "proba": proba,
                    }
            importance_frames.append(extract_group_importance(model, target, model_name))

        if "y_true" in best_test:
            plot_curves(target, best_test["model"], best_test["y_true"], best_test["proba"])

    metrics = pd.DataFrame(metric_rows)
    importance = pd.concat([frame for frame in importance_frames if not frame.empty], ignore_index=True)
    return metrics, importance


def write_feature_audit(df: pd.DataFrame) -> None:
    rows = []
    source_map = {
        "cfo_assets": "cash_flow_operating / total_assets",
        "cfo_margin": "cash_flow_operating / total_revenue",
        "accruals_assets": "(net_income - cash_flow_operating) / total_assets",
        "working_capital_assets": "(current_assets - current_liabilities) / total_assets",
        "cash_to_current_liabilities": "cash_equivalents / current_liabilities",
        "capex_intensity_assets": "capex / total_assets",
        "capex_intensity_revenue": "capex / total_revenue",
        "debt_to_cfo": "(long_term_debt + short_term_debt) / positive cash_flow_operating",
    }
    for feature in FINANCIAL_QUALITY_FEATURES:
        values = pd.to_numeric(df[feature], errors="coerce")
        finite = values.replace([np.inf, -np.inf], np.nan)
        rows.append(
            {
                "feature": feature,
                "definition": source_map[feature],
                "feature_family": "financial_quality_cashflow",
                "known_rows": int(finite.notna().sum()),
                "missing_rows": int(finite.isna().sum()),
                "missing_share": float(finite.isna().mean()),
                "infinite_rows": int(np.isinf(values).sum()),
                "min": finite.min(),
                "p01": finite.quantile(0.01),
                "p99": finite.quantile(0.99),
                "max": finite.max(),
                "abs_gt_100_rows": int((finite.abs() > 100).fillna(False).sum()),
            }
        )
    DATA_QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(DATA_QUALITY_DIR / "financial_quality_feature_audit.csv", index=False)


def write_market_timing_audit(df: pd.DataFrame) -> None:
    prediction_dates = (
        df[["prediction_date"]]
        .dropna()
        .drop_duplicates()
        .sort_values("prediction_date")
        .reset_index(drop=True)
    )
    rows = []
    source_columns = sorted(
        {
            "VIXCLS",
            "BAMLH0A0HYM2",
            "NFCI",
            "DRTSCILM",
            "T10Y2Y",
            "T10Y3M",
            "CPIAUCSL",
            "DCOILWTICO",
            "DTWEXBGS",
            "RSAFS",
            "BUSLOANS",
            "UNRATE",
            "INDPRO",
            "PAYEMS",
            "HOUST",
            "USEPUINDXD",
        }
    )
    for series_id in source_columns:
        path = FRED_DIR / f"{series_id}.csv"
        if not path.exists():
            rows.append(
                {
                    "series_id": series_id,
                    "status": "MISSING_RAW_SERIES",
                    "matched_prediction_dates": 0,
                    "future_date_violations": np.nan,
                    "max_lag_days": np.nan,
                    "alignment_policy": "last known FRED value at or before prediction_date",
                }
            )
            continue
        fred = pd.read_csv(path)
        date_col = next((col for col in fred.columns if col.lower() in {"date", "observation_date"}), fred.columns[0])
        fred_dates = (
            fred[[date_col]]
            .rename(columns={date_col: "fred_date"})
            .assign(fred_date=lambda x: pd.to_datetime(x["fred_date"], errors="coerce"))
            .dropna()
            .sort_values("fred_date")
        )
        merged = pd.merge_asof(prediction_dates, fred_dates, left_on="prediction_date", right_on="fred_date", direction="backward")
        lag_days = (merged["prediction_date"] - merged["fred_date"]).dt.days
        future_violations = int((merged["fred_date"] > merged["prediction_date"]).fillna(False).sum())
        rows.append(
            {
                "series_id": series_id,
                "status": "PASS" if future_violations == 0 else "FAIL",
                "matched_prediction_dates": int(merged["fred_date"].notna().sum()),
                "future_date_violations": future_violations,
                "max_lag_days": float(lag_days.max()) if lag_days.notna().any() else np.nan,
                "alignment_policy": "last known FRED value at or before prediction_date",
            }
        )
    DATA_QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(DATA_QUALITY_DIR / "market_health_v2_timing_audit.csv", index=False)


def plot_market_health(df: pd.DataFrame) -> None:
    yearly = (
        df[df["prediction_date"].dt.year.between(2009, 2024)]
        .groupby("prediction_year", as_index=False)
        .agg(
            market_stress_score_v2=("market_stress_score_v2", "mean"),
            market_health_score_v2=("market_health_score_v2", "mean"),
            credit_stress_score=("credit_stress_score", "mean"),
            real_activity_pressure_score=("real_activity_pressure_score", "mean"),
            policy_uncertainty_score=("policy_uncertainty_score", "mean"),
        )
    )
    plt.figure(figsize=(10, 6))
    for col in [
        "market_stress_score_v2",
        "credit_stress_score",
        "real_activity_pressure_score",
        "policy_uncertainty_score",
    ]:
        plt.plot(yearly["prediction_year"], yearly[col], marker="o", label=col)
    plt.xlabel("Prediction year")
    plt.ylabel("Average score")
    plt.ylim(0, 1)
    plt.title("Market health v2 component scores by year")
    plt.legend()
    plt.tight_layout()
    modeling_fig_dir = PROJECT_ROOT / "reports/figures/modeling"
    modeling_fig_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(modeling_fig_dir / "market_health_v2_by_year.png", dpi=180)
    plt.close()


def plot_target_balance(profile: pd.DataFrame) -> None:
    data = profile[profile["split"] == "all_model_years"].copy()
    data = data.sort_values("positive_share_known")
    plt.figure(figsize=(10, 5))
    plt.barh(data["target"], data["positive_share_known"])
    plt.xlabel("Positive share among known labels")
    plt.title("Exploratory target balance")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "exploratory_target_balance.png", dpi=180)
    plt.close()


def plot_metric_summary(metrics: pd.DataFrame) -> None:
    test = metrics[(metrics["split"] == "test") & (metrics["model"] != "SKIPPED")].copy()
    if test.empty:
        return
    summary = test.sort_values("pr_auc", ascending=True)
    summary["label"] = summary["target"] + " / " + summary["model"]
    plt.figure(figsize=(11, 7))
    plt.barh(summary["label"], summary["pr_auc"])
    plt.xlabel("Test PR-AUC")
    plt.title("Exploratory target lab test PR-AUC")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "exploratory_model_pr_auc.png", dpi=180)
    plt.close()


def frame_as_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    table = frame.copy()
    for col in table.columns:
        if pd.api.types.is_float_dtype(table[col]):
            table[col] = table[col].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
        else:
            table[col] = table[col].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(table.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in table.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)


def write_summary(profile: pd.DataFrame, metrics: pd.DataFrame, feature_groups: pd.DataFrame) -> None:
    best = pd.DataFrame()
    if not metrics.empty and "pr_auc" in metrics.columns:
        test = metrics[(metrics["split"] == "test") & (metrics["model"] != "SKIPPED")].copy()
        if not test.empty:
            best = test.sort_values("pr_auc", ascending=False).groupby("target", as_index=False).head(1)

    lines = [
        "# Exploratory Target Lab Summary",
        "",
        "Generated by `scripts/modeling/run_exploratory_target_lab.py`.",
        "",
        "The lab is intentionally report-oriented. It uses the 31,702 x 190 production panel as input and adds or recomputes target-lab labels/features in memory for target profiling and temporal model diagnostics. Four validated secondary labels are production target columns; diagnostic and robustness-extension labels remain in-memory/report-only.",
        "",
        "## Target Profiles",
        "",
        frame_as_markdown(profile[profile["split"] == "all_model_years"]),
        "",
        "## Best Test Runs",
        "",
        frame_as_markdown(
            best[
                [
                    "target",
                    "model",
                    "rows",
                    "positives",
                    "roc_auc",
                    "pr_auc",
                    "precision",
                    "recall",
                    "f1",
                ]
            ]
        )
        if not best.empty
        else "_No exploratory target met the modeling gates._",
        "",
        "## Feature-Group Notes",
        "",
    ]
    if not feature_groups.empty:
        top_groups = (
            feature_groups.sort_values("importance_share", ascending=False)
            .groupby(["target", "model"], as_index=False)
            .head(3)
        )
        lines.append(frame_as_markdown(top_groups))
    else:
        lines.append("_No feature-importance output was generated._")
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Existing production targets remain unchanged.",
            "- Exploratory targets are not headline thesis outcomes unless they pass profile, leakage, model sanity, and interpretation checks.",
            "- Forward-looking target components are label-construction variables only and are not included in model features.",
            "- Post-event rows are excluded from model fitting.",
            "- Strict formal distress blocks success/resilience/recovery labels in the target window.",
        ]
    )
    (OUT_DIR / "exploratory_target_lab_summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_missing_fred_inventory() -> None:
    proposed = ["STLFSI4", "ANFCI", "CFNAI", "BAMLC0A4CBBB", "BAMLC0A0CM", "USEPUINDXD"]
    if FRED_CATALOG_PATH.exists():
        catalog = pd.read_csv(FRED_CATALOG_PATH)
        catalog_ids = set(catalog["series_id"].astype(str))
    else:
        catalog_ids = set()
    rows = []
    for series_id in proposed:
        rows.append(
            {
                "series_id": series_id,
                "in_catalog": series_id in catalog_ids,
                "raw_file_exists": (FRED_DIR / f"{series_id}.csv").exists(),
                "extension_action": "already_available" if series_id in catalog_ids and (FRED_DIR / f"{series_id}.csv").exists() else "candidate_for_optional_download_gate",
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "proposed_fred_extension_inventory.csv", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_panel()
    df = add_financial_quality_features(df)
    df = clean_financial_quality_extremes(df)
    df, market_coverage = add_market_health_v2_features(df)
    df = add_exploratory_targets(df)

    profile = target_profile(df)
    by_year_sector = target_by_year_sector(df)
    features = build_features(df)
    metrics, feature_groups = train_exploratory_models(df, features)

    profile.to_csv(OUT_DIR / "exploratory_target_profiles.csv", index=False)
    by_year_sector.to_csv(OUT_DIR / "exploratory_target_by_year_sector.csv", index=False)
    metrics.to_csv(OUT_DIR / "exploratory_model_metrics.csv", index=False)
    feature_groups.to_csv(OUT_DIR / "exploratory_feature_group_importance.csv", index=False)
    market_coverage.to_csv(DATA_QUALITY_DIR / "market_health_v2_component_coverage.csv", index=False)

    write_feature_audit(df)
    write_market_timing_audit(df)
    write_missing_fred_inventory()
    plot_market_health(df)
    plot_target_balance(profile)
    plot_metric_summary(metrics)
    write_summary(profile, metrics, feature_groups)

    print(f"Wrote exploratory target lab outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
