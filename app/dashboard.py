"""Interactive dashboard for the market-shifts thesis artifact."""

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data/github/firm_panel_v2.csv.gz"
METRICS_PATH = ROOT / "reports/modeling/panel_v2_model_metrics.csv"
IMPORTANCE_PATH = ROOT / "reports/modeling/panel_v2_feature_importance.csv"
SPLIT_PATH = ROOT / "reports/modeling/panel_v2_temporal_split_summary.csv"
TARGET_TWEAK_PATH = ROOT / "reports/target_tweak_experiments/dashboard_best_target_rows.csv"
FEATURE_ABLATION_PATH = ROOT / "reports/target_tweak_experiments/dashboard_feature_set_performance.csv"
FACTOR_GROUP_PATH = ROOT / "reports/target_tweak_experiments/dashboard_factor_group_best_models.csv"
CALIBRATION_PATH = ROOT / "reports/modeling/calibration_metrics.csv"
THRESHOLD_RANKING_PATH = ROOT / "reports/modeling/threshold_ranking_metrics.csv"
VALIDATED_SECONDARY_PROFILE_PATH = ROOT / "reports/target_lab/validated_secondary_target_profiles.csv"
REASON_CODE_PATH = ROOT / "reports/target_lab/exploratory_reason_code_summary.csv"
FEATURE_LEVEL_PATH = ROOT / "reports/target_lab/exploratory_feature_level_importance.csv"
FEATURE_DIRECTION_PATH = ROOT / "reports/target_lab/exploratory_feature_direction_effects.csv"
TARGET_LAB_GROUP_PATH = ROOT / "reports/target_lab/exploratory_feature_group_importance.csv"

TARGET_INFO = [
    {
        "label": "Strict legal distress",
        "column": "distress_next_4q",
        "tier": "Primary",
        "role": "Rare-event legal distress benchmark",
    },
    {
        "label": "Broader failure pressure",
        "column": "failure_pressure_conservative_v2_next_4obs",
        "tier": "Primary",
        "role": "Main downside factor-analysis outcome",
    },
    {
        "label": "Success / resilience",
        "column": "success_resilience_next_4q",
        "tier": "Primary",
        "role": "Main upside factor-analysis outcome",
    },
    {
        "label": "Industry-relative resilience",
        "column": "industry_relative_resilience_next_4obs",
        "tier": "Validated secondary",
        "role": "Peer-relative future resilience outcome",
    },
    {
        "label": "Stress resilience",
        "column": "stress_resilience_next_4obs",
        "tier": "Validated secondary",
        "role": "Resilience conditional on elevated market stress",
    },
    {
        "label": "Recovery",
        "column": "recovery_next_4obs",
        "tier": "Validated secondary",
        "role": "Turnaround from weak current condition",
    },
    {
        "label": "Cash-flow quality success",
        "column": "quality_success_cashflow_next_4obs",
        "tier": "Validated secondary",
        "role": "Profitability supported by operating cash flow",
    },
]

TARGETS = {item["label"]: item["column"] for item in TARGET_INFO}
TARGET_LABEL_BY_COLUMN = {item["column"]: item["label"] for item in TARGET_INFO}
TARGET_TIER_BY_COLUMN = {item["column"]: item["tier"] for item in TARGET_INFO}
PRIMARY_TARGETS = [item["column"] for item in TARGET_INFO if item["tier"] == "Primary"]
VALIDATED_SECONDARY_TARGETS = [item["column"] for item in TARGET_INFO if item["tier"] == "Validated secondary"]

FIRM_METRIC_GROUPS = {
    "Profit & Margins": [
        "roa",
        "net_margin",
        "operating_margin",
        "gross_margin",
        "net_income",
        "operating_income",
        "gross_profit",
        "pretax_income",
        "retained_earnings",
    ],
    "Revenue, Costs & Expenses": [
        "total_revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "r_and_d_expense",
        "r_and_d_intensity",
        "sg_and_a",
        "depreciation_amortization",
    ],
    "Cash Flow & Investment": [
        "cash_flow_operating",
        "cash_flow_investing",
        "cash_flow_financing",
        "capex",
        "ppe_net",
    ],
    "Assets, Liabilities & Equity": [
        "total_assets",
        "total_liabilities",
        "noncurrent_liabilities",
        "total_equity",
        "long_term_debt",
        "short_term_debt",
        "leverage_assets",
        "equity_assets",
    ],
    "Working Capital & Liquidity": [
        "current_assets",
        "current_liabilities",
        "cash_equivalents",
        "accounts_receivable",
        "inventory",
        "current_ratio",
        "cash_assets",
        "inventory_assets",
        "receivables_assets",
    ],
    "Shares & Per-Share": [
        "eps_basic",
        "eps_diluted",
        "shares_outstanding",
        "wavg_shares_basic",
        "wavg_shares_diluted",
    ],
    "Ratios": [
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
    ],
    "Trend & Deterioration": [
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
    ],
}

ALL_FINANCIAL_METRICS = sorted(set().union(*FIRM_METRIC_GROUPS.values()))

TARGET_TIMELINE_COLUMNS = [
    "distress_next_2q",
    "distress_next_4q",
    "distress_next_8q",
    "broad_distress_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "healthy_current",
    "success_profitability_next_4q",
    "success_resilience_next_4q",
    "success_quality_next_4q",
    "industry_relative_resilience_next_4obs",
    "stress_resilience_next_4obs",
    "recovery_next_4obs",
    "quality_success_cashflow_next_4obs",
    "post_event_flag",
]

OUTCOME_CATEGORY_ORDER = [
    "Strict legal distress",
    "Broader pressure, no legal distress",
    "Success / resilience",
    "Neutral / surviving",
    "Unknown future horizon",
]

MACRO_METRIC_GROUPS = {
    "Rates & Credit": [
        "FEDFUNDS",
        "GS10",
        "T10Y2Y",
        "T10Y3M",
        "BAMLH0A0HYM2",
        "NFCI",
        "DRTSCILM",
        "BUSLOANS",
        "BUSLOANS_yoy_pct",
    ],
    "Money & Inflation": [
        "M2SL",
        "M2SL_yoy_pct",
        "CPIAUCSL",
        "CPIAUCSL_yoy_pct",
        "PPIACO",
        "PPIACO_yoy_pct",
    ],
    "Labor & Demand": [
        "UNRATE",
        "PAYEMS",
        "PAYEMS_yoy_pct",
        "RSAFS",
        "RSAFS_yoy_pct",
        "HOUST",
        "HOUST_yoy_pct",
        "INDPRO",
        "INDPRO_yoy_pct",
        "GDPC1",
    ],
    "Markets & Commodities": [
        "VIXCLS",
        "DCOILWTICO",
        "DCOILWTICO_yoy_pct",
        "DTWEXBGS",
        "DTWEXBGS_yoy_pct",
        "USEPUINDXD",
    ],
    "Regime Flags": [
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
    ],
    "Global Events": [
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
    ],
}

METADATA_COLUMNS = {
    "adsh",
    "cik",
    "ticker",
    "name",
    "cohort",
    "Sector",
    "Industry",
    "period_date",
    "filed_date",
    "prediction_date",
    "event_date",
    "event_label",
    "event_type",
    "event_year",
    "verification_status",
    "shortname",
}


st.set_page_config(
    page_title="Market Shifts Distress Dashboard",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, parse_dates=["period_date", "filed_date", "prediction_date", "event_date"])
    return df


@st.cache_data(show_spinner=False)
def load_optional_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_target_outputs(kind: str) -> pd.DataFrame:
    frames = []
    suffix = {
        "metrics": "model_metrics",
        "importance": "feature_importance",
        "splits": "temporal_split_summary",
    }[kind]
    for label, target in TARGETS.items():
        path = ROOT / f"reports/modeling/panel_v2_{target}_{suffix}.csv"
        if path.exists():
            frame = pd.read_csv(path)
            frame.insert(0, "target_label", label)
            frame.insert(1, "target", target)
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def ordered_target_labels(labels: list[str] | pd.Series) -> list[str]:
    available = set(pd.Series(labels).dropna().astype(str))
    ordered = [label for label in TARGETS if label in available]
    return ordered + sorted(available - set(ordered))


def target_display_name(target: str) -> str:
    return TARGET_LABEL_BY_COLUMN.get(str(target), metric_label(str(target)))


def target_summary(frame: pd.DataFrame, target_columns: list[str]) -> pd.DataFrame:
    rows = []
    for item in TARGET_INFO:
        target = item["column"]
        if target not in target_columns or target not in frame.columns:
            continue
        values = pd.to_numeric(frame[target], errors="coerce")
        known = int(values.notna().sum())
        positives = int(values.fillna(0).sum())
        rows.append(
            {
                "tier": item["tier"],
                "target_label": item["label"],
                "target": target,
                "role": item["role"],
                "rows": len(frame),
                "known_rows": known,
                "missing_rows": int(values.isna().sum()),
                "coverage": known / len(frame) if len(frame) else np.nan,
                "positives": positives,
                "positive_share_known": positives / known if known else np.nan,
            }
        )
    return pd.DataFrame(rows)


def format_number(value: object, digits: int = 3) -> str:
    if pd.isna(value):
        return "n/a"
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    if isinstance(value, (float, np.floating)):
        return f"{value:.{digits}f}"
    return str(value)


def display_target_table(frame: pd.DataFrame, height: int = 300) -> None:
    if frame.empty:
        st.info("No target rows available for the current selection.")
        return
    display = frame.copy()
    for col in ["coverage", "positive_share_known"]:
        if col in display.columns:
            display[col] = display[col].map(lambda value: "n/a" if pd.isna(value) else f"{value:.1%}")
    st.dataframe(display, width="stretch", height=height, hide_index=True)


def metric_card(label: str, value: str) -> None:
    st.metric(label, value)


def text_value(label: str, value: str) -> None:
    st.caption(label)
    st.write(value)


def zscore(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = frame.apply(pd.to_numeric, errors="coerce")
    spread = numeric.std(skipna=True).replace(0, pd.NA)
    return (numeric - numeric.mean(skipna=True)) / spread


def available_columns(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in frame.columns]


def numeric_columns(frame: pd.DataFrame, *, exclude: set[str] | None = None) -> list[str]:
    exclude = exclude or set()
    numeric = []
    for column in frame.columns:
        if column in METADATA_COLUMNS or column in exclude:
            continue
        if pd.api.types.is_numeric_dtype(frame[column]) or pd.to_numeric(frame[column], errors="coerce").notna().any():
            numeric.append(column)
    return sorted(numeric)


def metric_label(column: str) -> str:
    return column.replace("_", " ").replace("yoy pct", "YoY %").title()


def default_metrics(frame: pd.DataFrame, candidates: list[str], fallback_count: int = 3) -> list[str]:
    available = available_columns(frame, candidates)
    if available:
        return available[:fallback_count]
    return numeric_columns(frame)[:fallback_count]


def metric_summary(frame: pd.DataFrame, metric: str) -> dict[str, str]:
    series = pd.to_numeric(frame[metric], errors="coerce").dropna()
    if series.empty:
        return {"latest": "n/a", "min": "n/a", "max": "n/a", "observed": "0"}
    return {
        "latest": f"{series.iloc[-1]:,.4g}",
        "min": f"{series.min():,.4g}",
        "max": f"{series.max():,.4g}",
        "observed": f"{len(series):,}",
    }


def chart_frame(frame: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    numeric = frame[metrics].apply(pd.to_numeric, errors="coerce")
    return numeric.mask(~np.isfinite(numeric))


def clean_chart_data(
    data: pd.DataFrame,
    y: str | list[str] | None = None,
    x: str | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    frame = data.copy()
    if y is None:
        y_columns = [column for column in frame.columns if column != x]
    elif isinstance(y, str):
        y_columns = [y]
    else:
        y_columns = list(y)
    y_columns = [column for column in y_columns if column in frame.columns]
    if not y_columns:
        return frame.iloc[0:0], []
    numeric = frame[y_columns].apply(pd.to_numeric, errors="coerce")
    frame[y_columns] = numeric.mask(~np.isfinite(numeric))
    frame = frame.dropna(subset=y_columns, how="all")
    return frame, y_columns


def chart_x_type(series: pd.Series, *, bar: bool = False) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "T"
    if pd.api.types.is_numeric_dtype(series):
        return "O" if bar else "Q"
    return "N"


def chart_with_index(data: pd.DataFrame, x: str | None) -> tuple[pd.DataFrame, str]:
    frame = data.copy()
    if x is not None:
        return frame.dropna(subset=[x]) if x in frame.columns else frame.iloc[0:0], x
    index_name = frame.index.name or "index"
    frame = frame.reset_index()
    if index_name not in frame.columns:
        index_name = frame.columns[0]
    return frame.dropna(subset=[index_name]), index_name


def long_chart_data(data: pd.DataFrame, x: str | None, y_columns: list[str]) -> tuple[pd.DataFrame, str]:
    frame, x_column = chart_with_index(data, x)
    if frame.empty or x_column not in frame.columns:
        return frame.iloc[0:0], x_column
    long = frame[[x_column] + y_columns].melt(
        id_vars=x_column,
        value_vars=y_columns,
        var_name="metric",
        value_name="value",
    )
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    long = long[np.isfinite(long["value"])]
    long["metric_label"] = long["metric"].map(metric_label)
    return long, x_column


def line_chart_safe(data: pd.DataFrame, *, x: str | None = None, y: str | list[str] | None = None, height: int | None = None) -> None:
    chart_data, y_columns = clean_chart_data(data, y=y, x=x)
    if chart_data.empty or not y_columns:
        st.info("No chartable numeric observations for the current selection.")
        return
    long, x_column = long_chart_data(chart_data, x, y_columns)
    if long.empty:
        st.info("No chartable numeric observations for the current selection.")
        return
    x_type = chart_x_type(long[x_column], bar=False)
    chart = (
        alt.Chart(long)
        .mark_line()
        .encode(
            x=alt.X(f"{x_column}:{x_type}", title=metric_label(x_column)),
            y=alt.Y("value:Q", title="Value"),
            color=alt.Color("metric_label:N", title="Metric"),
            tooltip=[
                alt.Tooltip(f"{x_column}:{x_type}", title=metric_label(x_column)),
                alt.Tooltip("metric_label:N", title="Metric"),
                alt.Tooltip("value:Q", title="Value", format=",.4g"),
            ],
        )
        .properties(width=900, height=height or 300)
    )
    st.altair_chart(chart, width="stretch")


def bar_chart_safe(
    data: pd.DataFrame,
    *,
    x: str | None = None,
    y: str | list[str] | None = None,
    color: str | None = None,
    height: int | None = None,
) -> None:
    chart_data, y_columns = clean_chart_data(data, y=y, x=x)
    if chart_data.empty or not y_columns:
        st.info("No chartable numeric observations for the current selection.")
        return
    if len(y_columns) > 1:
        chart_data, x_column = long_chart_data(chart_data, x, y_columns)
        y_column = "value"
        color_column = "metric_label"
    else:
        chart_data, x_column = chart_with_index(chart_data, x)
        y_column = y_columns[0]
        color_column = color
        chart_data[y_column] = pd.to_numeric(chart_data[y_column], errors="coerce")
        chart_data = chart_data[np.isfinite(chart_data[y_column])]
    if chart_data.empty or x_column not in chart_data.columns:
        st.info("No chartable numeric observations for the current selection.")
        return
    x_type = chart_x_type(chart_data[x_column], bar=True)
    encodings = {
        "x": alt.X(f"{x_column}:{x_type}", title=metric_label(x_column)),
        "y": alt.Y(f"{y_column}:Q", title=metric_label(y_column)),
        "tooltip": [
            alt.Tooltip(f"{x_column}:{x_type}", title=metric_label(x_column)),
            alt.Tooltip(f"{y_column}:Q", title=metric_label(y_column), format=",.4g"),
        ],
    }
    if color_column is not None and color_column in chart_data.columns:
        encodings["color"] = alt.Color(f"{color_column}:N", title=metric_label(color_column))
        encodings["tooltip"].append(alt.Tooltip(f"{color_column}:N", title=metric_label(color_column)))
    chart = alt.Chart(chart_data).mark_bar().encode(**encodings).properties(width=900, height=height or 300)
    st.altair_chart(chart, width="stretch")


def context_metric_columns() -> set[str]:
    return set().union(*MACRO_METRIC_GROUPS.values())


def baseline_series(frame: pd.DataFrame, metric: str, context_columns: set[str]) -> pd.Series:
    if metric not in frame.columns:
        return pd.Series(dtype="float64")
    baseline = frame
    if metric in context_columns and "prediction_date" in baseline.columns:
        baseline = baseline.drop_duplicates(subset=["prediction_date"]).sort_values("prediction_date")
    return pd.to_numeric(baseline[metric], errors="coerce").dropna()


def baseline_frame(scope: str, filtered_frame: pd.DataFrame, full_panel: pd.DataFrame) -> pd.DataFrame | None:
    if scope == "Selected firm window":
        return None
    if scope == "Filtered panel/date baseline":
        return filtered_frame
    training = full_panel[full_panel["prediction_year"].between(2009, 2018)].copy()
    return training


def standardized_chart_frame(
    selected_frame: pd.DataFrame,
    metrics: list[str],
    *,
    baseline: pd.DataFrame | None,
    context_columns: set[str],
) -> pd.DataFrame:
    values = chart_frame(selected_frame, metrics)
    standardized = pd.DataFrame(index=values.index)
    for metric in metrics:
        series = values[metric]
        if baseline is None:
            base = series.dropna()
        else:
            base = baseline_series(baseline, metric, context_columns)
        spread = base.std(skipna=True)
        if pd.isna(spread) or spread == 0:
            spread = series.std(skipna=True)
        center = base.mean(skipna=True) if not base.empty else series.mean(skipna=True)
        standardized[metric] = (series - center) / spread if spread and not pd.isna(spread) else pd.NA
    return standardized


def standardization_caption(scope: str) -> str:
    if scope == "Selected firm window":
        return "Z-score uses the selected ticker/date window: (value - selected-window mean) / selected-window standard deviation."
    if scope == "Filtered panel/date baseline":
        return "Z-score uses the current sidebar-filtered panel; macro, regime, and event fields are de-duplicated to one value per prediction date."
    return "Z-score uses the 2009-2018 training-period baseline; macro, regime, and event fields are de-duplicated to one value per prediction date."


def render_metric_charts(
    frame: pd.DataFrame,
    metrics: list[str],
    mode: str,
    key_prefix: str,
    *,
    standardization_scope: str = "Selected firm window",
    standardization_baseline: pd.DataFrame | None = None,
) -> None:
    metrics = [metric for metric in metrics if metric in frame.columns]
    if not metrics:
        st.info("No available metrics for the current selection.")
        return

    if mode == "One raw metric":
        selected = st.selectbox(
            "Metric",
            metrics,
            format_func=metric_label,
            key=f"{key_prefix}_single_metric",
        )
        summary = metric_summary(frame, selected)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest", summary["latest"])
        c2.metric("Minimum", summary["min"])
        c3.metric("Maximum", summary["max"])
        c4.metric("Observed points", summary["observed"])
        line_chart_safe(chart_frame(frame, [selected]), height=320)
        return

    if mode == "Separate raw scales":
        for index, metric in enumerate(metrics):
            summary = metric_summary(frame, metric)
            st.caption(
                f"{metric_label(metric)} | latest {summary['latest']} | min {summary['min']} | max {summary['max']} | observed {summary['observed']}"
            )
            line_chart_safe(chart_frame(frame, [metric]), height=180)
            if index < len(metrics) - 1:
                st.divider()
        return

    standardized = standardized_chart_frame(
        frame,
        metrics,
        baseline=standardization_baseline,
        context_columns=context_metric_columns(),
    )
    line_chart_safe(standardized, height=340)
    st.caption(standardization_caption(standardization_scope))


def add_outcome_category(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    strict = out["distress_next_4q"].fillna(0).eq(1)
    failure = out["failure_pressure_conservative_v2_next_4obs"].fillna(0).eq(1)
    success = out["success_resilience_next_4q"].fillna(0).eq(1)
    known_failure = out["failure_pressure_conservative_v2_next_4obs"].notna()
    known_success = out["success_resilience_next_4q"].notna()

    category = pd.Series("Unknown future horizon", index=out.index, dtype="object")
    category[known_failure & known_success & ~strict & ~failure & ~success] = "Neutral / surviving"
    category[success & ~strict & ~failure] = "Success / resilience"
    category[failure & ~strict] = "Broader pressure, no legal distress"
    category[strict] = "Strict legal distress"
    out["outcome_category"] = pd.Categorical(category, categories=OUTCOME_CATEGORY_ORDER, ordered=True)
    return out


panel = load_panel()
metrics = load_target_outputs("metrics")
importance = load_target_outputs("importance")
splits = load_target_outputs("splits")
target_tweaks = load_optional_csv(TARGET_TWEAK_PATH)
feature_ablation = load_optional_csv(FEATURE_ABLATION_PATH)
factor_groups = load_optional_csv(FACTOR_GROUP_PATH)
calibration_metrics = load_optional_csv(CALIBRATION_PATH)
threshold_metrics = load_optional_csv(THRESHOLD_RANKING_PATH)
validated_secondary_profiles = load_optional_csv(VALIDATED_SECONDARY_PROFILE_PATH)
reason_codes = load_optional_csv(REASON_CODE_PATH)
feature_level = load_optional_csv(FEATURE_LEVEL_PATH)
feature_directions = load_optional_csv(FEATURE_DIRECTION_PATH)
target_lab_groups = load_optional_csv(TARGET_LAB_GROUP_PATH)

st.title("Market Shifts: Firm Distress and Resilience")

with st.sidebar:
    st.header("Filters")
    sectors = sorted(x for x in panel["Sector"].dropna().unique())
    cohorts = sorted(x for x in panel["cohort"].dropna().unique())
    selected_sectors = st.multiselect("Sector", sectors, default=sectors)
    selected_cohorts = st.multiselect("Cohort", cohorts, default=cohorts)
    min_year = int(panel["prediction_year"].min())
    max_year = int(panel["prediction_year"].max())
    year_range = st.slider("Prediction year", min_year, max_year, (max(min_year, 2009), min(max_year, 2024)))

filtered = panel[
    panel["Sector"].isin(selected_sectors)
    & panel["cohort"].isin(selected_cohorts)
    & panel["prediction_year"].between(year_range[0], year_range[1])
].copy()
filtered = add_outcome_category(filtered)

if filtered.empty:
    st.warning("No rows match the current sidebar filters. Adjust sectors, cohorts, or prediction years to restore the dashboard views.")
    st.stop()

overview, data_tab, models_tab, target_lab_tab, firms_tab, artifact_tab = st.tabs(
    ["Overview", "Data Coverage", "Models", "Target Lab", "Firm Explorer", "Artifact Notes"]
)

with overview:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Rows", f"{len(filtered):,}")
    with c2:
        metric_card("Firms", f"{filtered['cik'].nunique():,}")
    with c3:
        metric_card("Strict distress positives", f"{int(filtered['distress_next_4q'].sum()):,}")
    with c4:
        metric_card("Failure-pressure positives", f"{int(filtered['failure_pressure_conservative_v2_next_4obs'].fillna(0).sum()):,}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Success positives", f"{int(filtered['success_resilience_next_4q'].fillna(0).sum()):,}")
    with c2:
        known_failure = int(filtered["failure_pressure_conservative_v2_next_4obs"].notna().sum())
        metric_card("Failure target observed", f"{known_failure:,}")
    with c3:
        known_success = int(filtered["success_resilience_next_4q"].notna().sum())
        metric_card("Success target observed", f"{known_success:,}")
    with c4:
        unknown_outcome = int((filtered["outcome_category"] == "Unknown future horizon").sum())
        metric_card("Unknown outcome horizon", f"{unknown_outcome:,}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        neutral_rows = int((filtered["outcome_category"] == "Neutral / surviving").sum())
        metric_card("Neutral / surviving", f"{neutral_rows:,}")
    with c2:
        text_value(
            "Prediction window",
            f"{filtered['prediction_date'].min().date()} to {filtered['prediction_date'].max().date()}",
        )
    with c3:
        failure_coverage = filtered["failure_pressure_conservative_v2_next_4obs"].notna().mean()
        metric_card("Failure target coverage", f"{failure_coverage:.1%}")
    with c4:
        success_coverage = filtered["success_resilience_next_4q"].notna().mean()
        metric_card("Success target coverage", f"{success_coverage:.1%}")

    secondary_summary = target_summary(filtered, VALIDATED_SECONDARY_TARGETS)
    st.subheader("Validated Secondary Outcomes")
    display_target_table(
        secondary_summary[
            [
                "target_label",
                "role",
                "known_rows",
                "missing_rows",
                "coverage",
                "positives",
                "positive_share_known",
            ]
        ],
        height=190,
    )

    st.subheader("Outcome Composition by Year")
    outcome_yearly = (
        filtered.groupby(["prediction_year", "outcome_category"], observed=False)
        .size()
        .rename("rows")
        .reset_index()
    )
    outcome_totals = outcome_yearly.groupby("prediction_year")["rows"].transform("sum")
    outcome_yearly["share"] = outcome_yearly["rows"] / outcome_totals
    bar_chart_safe(outcome_yearly, x="prediction_year", y="share", color="outcome_category")

    st.subheader("Target Coverage by Year")
    coverage_yearly = (
        filtered.groupby("prediction_year")
        .agg(
            rows=("adsh", "count"),
            failure_target_observed=("failure_pressure_conservative_v2_next_4obs", "count"),
            success_target_observed=("success_resilience_next_4q", "count"),
            unknown_outcome=("outcome_category", lambda s: int((s == "Unknown future horizon").sum())),
        )
        .reset_index()
    )
    coverage_yearly["failure_target_coverage"] = coverage_yearly["failure_target_observed"] / coverage_yearly["rows"]
    coverage_yearly["success_target_coverage"] = coverage_yearly["success_target_observed"] / coverage_yearly["rows"]
    coverage_yearly["unknown_outcome_share"] = coverage_yearly["unknown_outcome"] / coverage_yearly["rows"]
    line_chart_safe(
        coverage_yearly,
        x="prediction_year",
        y=["failure_target_coverage", "success_target_coverage", "unknown_outcome_share"],
    )

    with st.expander("Independent target positive rates"):
        st.caption("These rates are not mutually exclusive categories and do not use the same denominator.")
        independent_yearly = (
            filtered.groupby("prediction_year")
            .agg(
                rows=("adsh", "count"),
                distress=("distress_next_4q", "sum"),
                failure_pressure=("failure_pressure_conservative_v2_next_4obs", "sum"),
                known_failure_pressure=("failure_pressure_conservative_v2_next_4obs", "count"),
                success=("success_resilience_next_4q", "sum"),
                known_success=("success_resilience_next_4q", "count"),
            )
            .reset_index()
        )
        independent_yearly["distress_share_all_rows"] = independent_yearly["distress"] / independent_yearly["rows"]
        independent_yearly["failure_pressure_share_known"] = independent_yearly["failure_pressure"] / independent_yearly[
            "known_failure_pressure"
        ].replace(0, pd.NA)
        independent_yearly["success_share_known"] = independent_yearly["success"] / independent_yearly[
            "known_success"
        ].replace(0, pd.NA)
        line_chart_safe(
            independent_yearly,
            x="prediction_year",
            y=["distress_share_all_rows", "failure_pressure_share_known", "success_share_known"],
        )

    with st.expander("Validated secondary target rates"):
        secondary_rows = []
        for year, group in filtered.groupby("prediction_year"):
            row = {"prediction_year": year}
            for target in VALIDATED_SECONDARY_TARGETS:
                if target not in group:
                    continue
                values = pd.to_numeric(group[target], errors="coerce")
                known = values.notna().sum()
                row[f"{target}_share_known"] = values.fillna(0).sum() / known if known else pd.NA
            secondary_rows.append(row)
        secondary_yearly = pd.DataFrame(secondary_rows)
        y_columns = [column for column in secondary_yearly.columns if column.endswith("_share_known")]
        line_chart_safe(secondary_yearly, x="prediction_year", y=y_columns)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cohort Composition")
        cohort_counts = filtered.groupby("cohort").size().rename("rows").reset_index()
        bar_chart_safe(cohort_counts, x="cohort", y="rows")
    with c2:
        st.subheader("Current Outcome Mix")
        outcome_mix = (
            filtered["outcome_category"]
            .value_counts(sort=False)
            .rename_axis("outcome_category")
            .rename("rows")
            .reset_index()
        )
        outcome_mix["share"] = outcome_mix["rows"] / outcome_mix["rows"].sum()
        st.dataframe(outcome_mix, width="stretch", height=250)

with data_tab:
    st.subheader("Dataset Snapshot")
    st.dataframe(
        filtered[
            [
                "ticker",
                "name",
                "cohort",
                "Sector",
                "period_date",
                "filed_date",
                "prediction_date",
                "form",
                "total_assets",
                "total_revenue",
                "net_income",
                "leverage_assets",
                "roa",
                "FEDFUNDS",
                "VIXCLS",
                "distress_next_4q",
                "failure_pressure_conservative_v2_next_4obs",
                "success_resilience_next_4q",
                "industry_relative_resilience_next_4obs",
                "stress_resilience_next_4obs",
                "recovery_next_4obs",
                "quality_success_cashflow_next_4obs",
                "post_event_flag",
            ]
        ].sort_values(["prediction_date", "ticker"], ascending=[False, True]),
        width="stretch",
        height=420,
    )

    st.subheader("Missingness in Filtered Data")
    missing = (
        filtered.isna()
        .mean()
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index": "column"})
        .sort_values("missing_share", ascending=False)
        .head(25)
    )
    st.dataframe(missing, width="stretch", height=360)

with models_tab:
    st.subheader("Production Target Hierarchy")
    hierarchy = pd.DataFrame(TARGET_INFO)
    st.dataframe(hierarchy[["tier", "label", "column", "role"]], width="stretch", hide_index=True, height=285)

    st.subheader("Temporal Split")
    if not splits.empty:
        selected_split_target = st.selectbox("Target", ordered_target_labels(splits["target_label"].unique()))
        st.dataframe(splits[splits["target_label"] == selected_split_target], width="stretch")
    else:
        st.info("Run scripts/modeling/train_panel_v2_models.py to generate split outputs.")

    st.subheader("Model Metrics")
    if not metrics.empty:
        metric_target = st.selectbox("Metric target", ordered_target_labels(metrics["target_label"].unique()))
        metric_view = metrics[metrics["target_label"] == metric_target]
        st.dataframe(metric_view.sort_values(["split", "pr_auc"], ascending=[True, False]), width="stretch")
        test_metrics = metric_view[metric_view["split"] == "test"].sort_values("pr_auc", ascending=False)
        bar_chart_safe(test_metrics, x="model", y="pr_auc")
    else:
        st.info("Model metrics are not available yet.")

    st.subheader("Top Features")
    if not importance.empty:
        importance_target = st.selectbox("Feature target", ordered_target_labels(importance["target_label"].unique()))
        importance_view = importance[importance["target_label"] == importance_target]
        selected_model = st.selectbox("Model", sorted(importance_view["model"].unique()))
        top = importance_view[importance_view["model"] == selected_model].sort_values("importance", ascending=False).head(20)
        bar_chart_safe(top, x="feature", y="importance")
        st.dataframe(top, width="stretch")
    else:
        st.info("Feature importance outputs are not available yet.")

with target_lab_tab:
    st.subheader("Production Target Coverage")
    production_summary = target_summary(filtered, list(TARGETS.values()))
    display_target_table(
        production_summary[
            [
                "tier",
                "target_label",
                "role",
                "known_rows",
                "missing_rows",
                "coverage",
                "positives",
                "positive_share_known",
            ]
        ],
        height=320,
    )
    if not production_summary.empty:
        chart_data = production_summary[["target_label", "coverage", "positive_share_known", "tier"]].copy()
        bar_chart_safe(chart_data, x="target_label", y=["coverage", "positive_share_known"], color="tier")

    st.subheader("Calibration And Ranking")
    production_targets = set(TARGETS.values())
    calibration_view = calibration_metrics[calibration_metrics["target"].isin(production_targets)].copy()
    if not calibration_view.empty:
        calibration_labels = [
            item["label"] for item in TARGET_INFO if item["column"] in set(calibration_view["target"].astype(str))
        ]
        selected_calibration_label = st.selectbox("Calibration target", calibration_labels, key="calibration_target")
        selected_calibration_target = TARGETS[selected_calibration_label]
        selected_rows = calibration_view[
            calibration_view["target"].eq(selected_calibration_target)
            & calibration_view["split"].eq("test")
            & calibration_view["selected_model_by_validation_pr_auc"].astype(bool)
            & calibration_view["selected_calibrator_by_validation_brier"].astype(bool)
        ].copy()
        if selected_rows.empty:
            selected_rows = (
                calibration_view[
                    calibration_view["target"].eq(selected_calibration_target)
                    & calibration_view["split"].eq("test")
                ]
                .sort_values("brier_score")
                .head(1)
            )
        if not selected_rows.empty:
            selected = selected_rows.iloc[0]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Test PR-AUC", format_number(selected.get("pr_auc")))
            c2.metric("Test ROC-AUC", format_number(selected.get("roc_auc")))
            c3.metric("Brier score", format_number(selected.get("brier_score")))
            c4.metric("ECE 10-bin", format_number(selected.get("expected_calibration_error_10bin")))
            c5.metric("Test positives", f"{int(selected.get('positives', 0)):,}")
            st.caption(
                f"Selected model: {selected.get('model')} with {selected.get('calibrator')}; selection uses validation period only."
            )
        calibration_table = calibration_view[
            calibration_view["target"].eq(selected_calibration_target)
            & calibration_view["split"].isin(["validation", "test"])
        ].sort_values(["split", "brier_score"])
        st.dataframe(calibration_table, width="stretch", height=260)

        ranking_view = threshold_metrics[
            threshold_metrics["target"].eq(selected_calibration_target)
            & threshold_metrics["split"].eq("test")
            & threshold_metrics["threshold_type"].eq("top_rank_share")
        ].copy()
        if not selected_rows.empty and not ranking_view.empty:
            selected_model = selected_rows.iloc[0].get("model")
            selected_calibrator = selected_rows.iloc[0].get("calibrator")
            ranking_view = ranking_view[
                ranking_view["model"].eq(selected_model) & ranking_view["calibrator"].eq(selected_calibrator)
            ]
        if not ranking_view.empty:
            st.subheader("Top-Ranked Review Thresholds")
            st.dataframe(
                ranking_view[
                    [
                        "threshold_label",
                        "selected_rows",
                        "selected_share",
                        "precision",
                        "recall",
                        "base_rate",
                        "lift_vs_base_rate",
                    ]
                ],
                width="stretch",
                height=180,
                hide_index=True,
            )
            bar_chart_safe(ranking_view, x="threshold_label", y=["precision", "recall", "base_rate"])
    else:
        st.info("Calibration and ranking outputs are not available yet.")

    st.subheader("Validated Secondary Reasons And Feature Evidence")
    available_reason_targets = set(reason_codes["target"].astype(str)) if not reason_codes.empty else set()
    secondary_labels = [item["label"] for item in TARGET_INFO if item["column"] in available_reason_targets]
    if secondary_labels:
        default_index = secondary_labels.index("Recovery") if "Recovery" in secondary_labels else 0
        selected_reason_label = st.selectbox("Secondary target", secondary_labels, index=default_index)
        selected_reason_target = TARGETS[selected_reason_label]
        reason_target = reason_codes[reason_codes["target"].eq(selected_reason_target)].copy()
        reason_models = sorted(reason_target["model"].dropna().astype(str).unique())
        default_model_index = reason_models.index("random_forest") if "random_forest" in reason_models else 0
        selected_reason_model = st.selectbox("Reason model", reason_models, index=default_model_index)

        reason_view = reason_target[reason_target["model"].eq(selected_reason_model)].sort_values(
            "native_importance_share",
            ascending=False,
        )
        st.dataframe(
            reason_view[
                [
                    "reason_code",
                    "native_importance_share",
                    "top_native_features",
                    "dominant_direction_label",
                    "permutation_importance_mean_pr_auc_drop",
                    "interpretation_note",
                ]
            ],
            width="stretch",
            height=280,
            hide_index=True,
        )
        bar_chart_safe(reason_view, x="reason_code", y="native_importance_share")

        group_view = pd.DataFrame()
        if not target_lab_groups.empty and {"target", "model"}.issubset(target_lab_groups.columns):
            group_view = target_lab_groups[
                target_lab_groups["target"].eq(selected_reason_target)
                & target_lab_groups["model"].eq(selected_reason_model)
            ].sort_values("importance_share", ascending=False)
        if not group_view.empty:
            st.subheader("Feature Group Shares")
            st.dataframe(group_view, width="stretch", height=220, hide_index=True)
            bar_chart_safe(group_view, x="feature_group", y="importance_share")

        level_view = pd.DataFrame()
        if not feature_level.empty and {"target", "model"}.issubset(feature_level.columns):
            level_view = feature_level[
                feature_level["target"].eq(selected_reason_target)
                & feature_level["model"].eq(selected_reason_model)
            ].sort_values("native_importance_share", ascending=False)
        if not level_view.empty:
            st.subheader("Feature-Level Drivers")
            st.dataframe(
                level_view[
                    [
                        "feature_clean",
                        "feature_group",
                        "reason_code",
                        "native_importance_share",
                        "selected_calibrator",
                    ]
                ].head(25),
                width="stretch",
                height=340,
                hide_index=True,
            )
            bar_chart_safe(level_view.head(20), x="feature_clean", y="native_importance_share", color="reason_code")

        direction_view = pd.DataFrame()
        if not feature_directions.empty and {"target", "model"}.issubset(feature_directions.columns):
            direction_view = feature_directions[
                feature_directions["target"].eq(selected_reason_target)
                & feature_directions["model"].eq(selected_reason_model)
            ].sort_values("test_spearman_feature_vs_score", key=lambda s: s.abs(), ascending=False)
        if not direction_view.empty:
            st.subheader("Direction Of Association")
            st.dataframe(
                direction_view[
                    [
                        "feature_clean",
                        "reason_code",
                        "direction_label",
                        "test_spearman_feature_vs_score",
                        "test_top_decile_minus_rest",
                        "test_positive_minus_negative",
                        "direction_interpretation",
                    ]
                ].head(25),
                width="stretch",
                height=340,
                hide_index=True,
            )
    else:
        st.info("Reason-code and feature-level target-lab outputs are not available yet.")

    with st.expander("Target and feature-set experiment summaries"):
        if not target_tweaks.empty:
            display_cols = [
                "target",
                "model",
                "positives",
                "positive_share",
                "roc_auc_mean",
                "pr_auc_mean",
                "precision_mean",
                "recall_mean",
                "f1_mean",
            ]
            available = [col for col in display_cols if col in target_tweaks.columns]
            st.dataframe(target_tweaks[available].sort_values("pr_auc_mean", ascending=False), width="stretch")
        if not feature_ablation.empty:
            targets = sorted(feature_ablation["target"].dropna().unique())
            selected_target = st.selectbox("Ablation target", targets)
            ablation_view = feature_ablation[feature_ablation["target"] == selected_target].sort_values(
                "pr_auc_mean",
                ascending=False,
            )
            st.dataframe(ablation_view, width="stretch", height=280)
        if not factor_groups.empty:
            factor_targets = sorted(factor_groups["target"].dropna().unique())
            selected_factor_target = st.selectbox("Legacy factor target", factor_targets)
            factor_view = factor_groups[factor_groups["target"] == selected_factor_target].sort_values(
                "importance_share",
                ascending=False,
            )
            st.dataframe(factor_view, width="stretch", height=260)

with firms_tab:
    st.subheader("Firm Explorer")
    tickers = sorted(x for x in filtered["ticker"].dropna().unique())
    default_ticker_index = tickers.index("AAPL") if "AAPL" in tickers else 0
    selected_ticker = st.selectbox("Ticker", tickers, index=default_ticker_index)
    firm = filtered[filtered["ticker"] == selected_ticker].sort_values("prediction_date")
    latest = firm.dropna(subset=["prediction_date"]).iloc[-1] if not firm.empty else pd.Series(dtype="object")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Firm rows", f"{len(firm):,}")
    with c2:
        text_value("Sector", str(firm["Sector"].dropna().iloc[-1]) if firm["Sector"].notna().any() else "n/a")
    with c3:
        text_value("Cohort", str(firm["cohort"].dropna().iloc[-1]) if firm["cohort"].notna().any() else "n/a")
    with c4:
        metric_card("Latest ROA", f"{latest.get('roa', float('nan')):.2%}" if pd.notna(latest.get("roa")) else "n/a")
    with c5:
        metric_card(
            "Latest leverage",
            f"{latest.get('leverage_assets', float('nan')):.2%}" if pd.notna(latest.get("leverage_assets")) else "n/a",
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Strict distress observations", f"{int(firm['distress_next_4q'].fillna(0).sum()):,}")
    with c2:
        metric_card(
            "Failure-pressure observations",
            f"{int(firm['failure_pressure_conservative_v2_next_4obs'].fillna(0).sum()):,}",
        )
    with c3:
        metric_card("Success observations", f"{int(firm['success_resilience_next_4q'].fillna(0).sum()):,}")

    firm_secondary_summary = target_summary(firm, VALIDATED_SECONDARY_TARGETS)
    if not firm_secondary_summary.empty:
        display_target_table(
            firm_secondary_summary[
                ["target_label", "known_rows", "missing_rows", "positives", "positive_share_known"]
            ],
            height=180,
        )

    firm_indexed = firm.set_index("prediction_date")

    firm_metrics_tab, macro_compare_tab, target_timeline_tab, recent_rows_tab = st.tabs(
        ["Firm Metrics", "Macro Compare", "Target Timeline", "Recent Rows"]
    )

    with firm_metrics_tab:
        st.subheader("Firm Metrics")
        firm_group_labels = list(FIRM_METRIC_GROUPS) + ["All Financial Metrics"]
        firm_group = st.selectbox("Metric group", firm_group_labels, key="firm_metric_group")
        if firm_group == "All Financial Metrics":
            firm_options = available_columns(firm_indexed, ALL_FINANCIAL_METRICS)
        else:
            firm_options = available_columns(firm_indexed, FIRM_METRIC_GROUPS[firm_group])

        firm_defaults = default_metrics(firm_indexed, firm_options, fallback_count=3)
        selected_firm_metrics = st.multiselect(
            "Data points",
            firm_options,
            default=firm_defaults,
            format_func=metric_label,
            key=f"firm_metrics_{firm_group}",
        )
        firm_chart_mode = st.radio(
            "Scale mode",
            ["Separate raw scales", "One raw metric", "Standardized comparison"],
            horizontal=True,
            key="firm_chart_mode",
        )
        firm_standardization_scope = "Selected firm window"
        if firm_chart_mode == "Standardized comparison":
            firm_standardization_scope = st.selectbox(
                "Standardization baseline",
                ["Selected firm window", "Filtered panel/date baseline", "Training-period baseline"],
                index=0,
                key="firm_standardization_scope",
            )
        render_metric_charts(
            firm_indexed,
            selected_firm_metrics,
            firm_chart_mode,
            "firm",
            standardization_scope=firm_standardization_scope,
            standardization_baseline=baseline_frame(firm_standardization_scope, filtered, panel),
        )

    with macro_compare_tab:
        st.subheader("Macro Comparison")
        macro_group_labels = list(MACRO_METRIC_GROUPS) + ["All Macro / Regime / Event"]
        macro_group = st.selectbox("Macro group", macro_group_labels, key="macro_metric_group")
        if macro_group == "All Macro / Regime / Event":
            macro_options = available_columns(
                firm_indexed,
                sorted(set().union(*MACRO_METRIC_GROUPS.values())),
            )
        else:
            macro_options = available_columns(firm_indexed, MACRO_METRIC_GROUPS[macro_group])

        macro_defaults = default_metrics(
            firm_indexed,
            ["VIXCLS", "M2SL", "DCOILWTICO", "FEDFUNDS", "NFCI"],
            fallback_count=4,
        )
        macro_defaults = [metric for metric in macro_defaults if metric in macro_options] or macro_options[:4]
        selected_macro_metrics = st.multiselect(
            "Macro, regime, or event data points",
            macro_options,
            default=macro_defaults,
            format_func=metric_label,
            key=f"macro_metrics_{macro_group}",
        )

        firm_compare_options = available_columns(
            firm_indexed,
            FIRM_METRIC_GROUPS["Profit & Margins"]
            + FIRM_METRIC_GROUPS["Assets, Liabilities & Equity"]
            + FIRM_METRIC_GROUPS["Working Capital & Liquidity"]
            + FIRM_METRIC_GROUPS["Trend & Deterioration"],
        )
        firm_compare_metric = st.selectbox(
            "Firm data point to compare against macro context",
            firm_compare_options,
            index=firm_compare_options.index("roa") if "roa" in firm_compare_options else 0,
            format_func=metric_label,
        )
        macro_chart_mode = st.radio(
            "Comparison scale mode",
            ["Standardized comparison", "Separate raw scales", "One raw metric"],
            horizontal=True,
            key="macro_chart_mode",
        )
        macro_standardization_scope = "Training-period baseline"
        if macro_chart_mode == "Standardized comparison":
            macro_standardization_scope = st.selectbox(
                "Standardization baseline",
                ["Training-period baseline", "Filtered panel/date baseline", "Selected firm window"],
                index=0,
                key="macro_standardization_scope",
            )

        combined_metrics = [firm_compare_metric] + selected_macro_metrics
        render_metric_charts(
            firm_indexed,
            combined_metrics,
            macro_chart_mode,
            "macro",
            standardization_scope=macro_standardization_scope,
            standardization_baseline=baseline_frame(macro_standardization_scope, filtered, panel),
        )

        if selected_macro_metrics:
            st.subheader("Macro Values Only")
            macro_only_mode = st.radio(
                "Macro-only scale mode",
                ["Standardized comparison", "Separate raw scales"],
                horizontal=True,
                key="macro_only_chart_mode",
            )
            macro_only_standardization_scope = macro_standardization_scope
            if macro_only_mode == "Standardized comparison" and macro_chart_mode != "Standardized comparison":
                macro_only_standardization_scope = st.selectbox(
                    "Macro-only standardization baseline",
                    ["Training-period baseline", "Filtered panel/date baseline", "Selected firm window"],
                    index=0,
                    key="macro_only_standardization_scope",
                )
            render_metric_charts(
                firm_indexed,
                selected_macro_metrics,
                macro_only_mode,
                "macro_only",
                standardization_scope=macro_only_standardization_scope,
                standardization_baseline=baseline_frame(macro_only_standardization_scope, filtered, panel),
            )

        if "global_event_names" in firm.columns:
            event_columns = available_columns(
                firm,
                [
                    "prediction_date",
                    "global_event_names",
                    "global_event_count",
                    "global_event_severity_sum",
                    "crisis_regime",
                    "market_stress_regime",
                ],
            )
            event_context = firm[event_columns].copy()
            event_context = event_context[
                event_context["global_event_names"].fillna("").astype(str).str.len().gt(0)
                | event_context["global_event_count"].fillna(0).gt(0)
            ]
            if not event_context.empty:
                st.subheader("Readable Global Event Context")
                st.dataframe(event_context.tail(20), width="stretch", height=260)

    with target_timeline_tab:
        st.subheader("Target Timeline")
        target_options = available_columns(firm_indexed, TARGET_TIMELINE_COLUMNS)
        selected_targets = st.multiselect(
            "Target or event labels",
            target_options,
            default=available_columns(
                firm_indexed,
                [
                    "distress_next_4q",
                    "failure_pressure_conservative_v2_next_4obs",
                    "success_resilience_next_4q",
                    "industry_relative_resilience_next_4obs",
                    "stress_resilience_next_4obs",
                    "recovery_next_4obs",
                    "quality_success_cashflow_next_4obs",
                    "post_event_flag",
                ],
            ),
            format_func=metric_label,
        )
        render_metric_charts(firm_indexed, selected_targets, "Separate raw scales", "targets")

    with recent_rows_tab:
        st.subheader("Recent Firm Observations")
        visible_columns = [
            "ticker",
            "name",
            "cohort",
            "Sector",
            "period_date",
            "filed_date",
            "prediction_date",
            "form",
            "total_assets",
            "total_revenue",
            "net_income",
            "roa",
            "leverage_assets",
            "current_ratio",
            "cash_assets",
            "FEDFUNDS",
            "M2SL",
            "DCOILWTICO",
            "VIXCLS",
            "global_event_names",
            "global_event_count",
            "global_event_severity_sum",
            "distress_next_4q",
            "failure_pressure_conservative_v2_next_4obs",
            "success_resilience_next_4q",
            "industry_relative_resilience_next_4obs",
            "stress_resilience_next_4obs",
            "recovery_next_4obs",
            "quality_success_cashflow_next_4obs",
        ]
        visible_columns = available_columns(firm, visible_columns)
        st.dataframe(firm[visible_columns].tail(20), width="stretch", height=420)

with artifact_tab:
    st.subheader("Artifact Description")
    st.write(
        "This dashboard is the practical artifact of the thesis: an interactive analytical tool "
        "for exploring strict legal distress, broader financial pressure, firm-level resilience, "
        "and validated secondary outcomes across industries and macro-market regimes."
    )
    st.subheader("Thesis Story")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "step": "1. Panel",
                    "meaning": "One firm-period observation is analyzed from the SEC filing date, not from the accounting period end date.",
                },
                {
                    "step": "2. Targets",
                    "meaning": "Strict distress, broader pressure, and success/resilience remain primary; four validated secondary outcomes add relative resilience, stress resilience, recovery, and cash-flow-supported success dimensions.",
                },
                {
                    "step": "3. Factors",
                    "meaning": "Firm fundamentals, ratios, and deterioration are interpreted first; macro regimes and events provide market-shift context.",
                },
                {
                    "step": "4. Artifact",
                    "meaning": "The dashboard is a historical decision-support artifact, not a live trading or bankruptcy oracle.",
                },
            ]
        ),
        width="stretch",
        hide_index=True,
    )
    st.subheader("Caveat Controls")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "caveat": "Strict distress event dates",
                    "control": "Source-verified events are separated from REVIEW rows; strict distress is treated as a benchmark.",
                },
                {
                    "caveat": "SEC accounting concepts",
                    "control": "Concept mapping, qtrs handling, missingness, and selected-fact provenance are handled by the panel rebuild scripts and generated local audit outputs.",
                },
                {
                    "caveat": "Null values",
                    "control": "Raw panel nulls are preserved; imputation happens only inside modeling pipelines.",
                },
                {
                    "caveat": "Duplicates/amendments",
                    "control": "Duplicate/amendment cases are audited separately; the production panel is not manually edited.",
                },
                {
                    "caveat": "Interpretation",
                    "control": "Reason codes, feature groups, and direction summaries describe associations on temporal test data, not causal mechanisms.",
                },
            ]
        ),
        width="stretch",
        hide_index=True,
    )
    st.write("Core dataset:", str(PANEL_PATH.relative_to(ROOT)))
    st.write("Model outputs:", str(METRICS_PATH.relative_to(ROOT)))
    st.write("Master explainer:", "docs/MASTER_DATA_MODEL_TARGET_EXPLAINER.md")
    st.write("Caveat register:", "docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md")
    st.write("The dashboard is designed to be reproducible from SEC Financial Statement Data Sets and FRED macro data.")
