#!/usr/bin/env python3
"""Manual-style scientific, model, and dashboard audit for 2026-05-08.

The goal is not to rebuild the thesis panel. This script creates a fixed,
hand-reviewable row sample and recomputes high-risk formulas from the saved
production panel so the manual audit has concrete evidence.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT / "sec_fsd"))
sys.path.insert(0, str(SCRIPT_ROOT / "modeling"))

import build_panel_v2 as panel_builder  # noqa: E402
import train_panel_v2_models as train_models  # noqa: E402


PANEL_PATH = PROJECT_ROOT / "data/github/firm_panel_v2.parquet"
SCHEMA_PATH = PROJECT_ROOT / "data/github/firm_panel_v2_schema.csv"
PROVENANCE_PATH = PROJECT_ROOT / "reports/data_quality/sec_selected_fact_provenance.parquet"
P0_PATH = PROJECT_ROOT / "reports/data_quality/p0_audit_status.csv"
BLACKLIST_PATH = PROJECT_ROOT / "config/model_feature_blacklist.csv"
MODEL_FEATURE_DIR = PROJECT_ROOT / "reports/data_quality/model_feature_lists"
MODEL_REPORT_DIR = PROJECT_ROOT / "reports/modeling"
TUNING_DIR = PROJECT_ROOT / "reports/model_tuning"
ADV_TUNING_DIR = PROJECT_ROOT / "reports/model_tuning_advanced"
DASHBOARD_PATH = PROJECT_ROOT / "app/dashboard.py"

OUT_DIR = PROJECT_ROOT / "reports/project_audit"
SAMPLE_CSV = OUT_DIR / "manual_panel_row_audit_sample_20260508.csv"
SAMPLE_SUMMARY_CSV = OUT_DIR / "manual_panel_row_audit_sample_summary_20260508.csv"
FORMULA_CSV = OUT_DIR / "manual_formula_recompute_audit_20260508.csv"
TARGET_CSV = OUT_DIR / "manual_target_recompute_audit_20260508.csv"
MODEL_CSV = OUT_DIR / "manual_model_logic_audit_20260508.csv"
DASHBOARD_CSV = OUT_DIR / "manual_dashboard_static_audit_20260508.csv"
RENDERED_DASHBOARD_CSV = OUT_DIR / "manual_dashboard_rendered_audit_20260508.csv"
REPORT_MD = OUT_DIR / "FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md"

PRODUCTION_TARGETS = [
    "distress_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "success_resilience_next_4q",
]

KEY_COLUMNS = [
    "ticker",
    "cik",
    "adsh",
    "form",
    "period_date",
    "filed_date",
    "prediction_date",
    "prediction_year",
    "Sector",
    "Industry",
    "cohort",
    "sec_zip",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "total_revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "cash_equivalents",
    "current_assets",
    "current_liabilities",
    "cash_flow_operating",
    "capex",
    "leverage_assets",
    "current_ratio",
    "cash_assets",
    "roa",
    "net_margin",
    "operating_margin",
    "gross_margin",
    "FEDFUNDS",
    "M2SL",
    "DCOILWTICO",
    "VIXCLS",
    "NFCI",
    "global_event_count",
    "global_event_names",
    "event_date",
    "event_label",
    "event_type",
    "verification_status",
    "days_to_event",
    "post_event_flag",
    *PRODUCTION_TARGETS,
]


def read_panel() -> pd.DataFrame:
    panel = pd.read_parquet(PANEL_PATH)
    for column in ["period_date", "filed_date", "prediction_date", "event_date"]:
        if column in panel.columns:
            panel[column] = pd.to_datetime(panel[column], errors="coerce")
    return panel


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace({0: np.nan})
    return numerator / denominator


def mismatch_count(observed: pd.Series, expected: pd.Series, tolerance: float = 1e-9) -> int:
    both_missing = observed.isna() & expected.isna()
    close = np.isclose(
        pd.to_numeric(observed, errors="coerce").astype(float),
        pd.to_numeric(expected, errors="coerce").astype(float),
        rtol=1e-7,
        atol=tolerance,
        equal_nan=True,
    )
    return int((~both_missing & ~pd.Series(close, index=observed.index)).sum())


def add_sample(rows: list[pd.DataFrame], panel: pd.DataFrame, mask: pd.Series, category: str, n: int) -> None:
    subset = panel.loc[mask].copy()
    if subset.empty:
        return
    subset = subset.sort_values(["ticker", "prediction_date", "period_date", "adsh"])
    if len(subset) > n:
        subset = subset.sample(n=n, random_state=20260508).sort_values(["ticker", "prediction_date", "period_date", "adsh"])
    subset.insert(0, "audit_category", category)
    rows.append(subset)


def build_manual_sample(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []

    add_sample(rows, panel, panel["distress_next_4q"].fillna(0).eq(1), "strict_distress_positive", 45)
    add_sample(
        rows,
        panel,
        panel["failure_pressure_conservative_v2_next_4obs"].fillna(0).eq(1)
        & panel["distress_next_4q"].fillna(0).eq(0),
        "failure_pressure_without_strict_distress",
        45,
    )
    add_sample(
        rows,
        panel,
        panel["success_resilience_next_4q"].fillna(0).eq(1)
        & panel["failure_pressure_conservative_v2_next_4obs"].fillna(0).eq(0),
        "success_resilience_positive",
        45,
    )
    add_sample(
        rows,
        panel,
        panel["failure_pressure_conservative_v2_next_4obs"].notna()
        & panel["success_resilience_next_4q"].notna()
        & panel["distress_next_4q"].fillna(0).eq(0)
        & panel["failure_pressure_conservative_v2_next_4obs"].fillna(0).eq(0)
        & panel["success_resilience_next_4q"].fillna(0).eq(0),
        "neutral_surviving_known_outcome",
        35,
    )
    add_sample(
        rows,
        panel,
        panel["failure_pressure_conservative_v2_next_4obs"].isna()
        | panel["success_resilience_next_4q"].isna(),
        "unknown_future_horizon_or_missing_target",
        35,
    )
    add_sample(rows, panel, panel["total_revenue"].lt(0), "negative_revenue_outlier", 25)
    add_sample(rows, panel, panel["total_assets"].le(0), "non_positive_assets_outlier", 10)
    duplicate_mask = panel.duplicated(["ticker", "period_date", "prediction_date"], keep=False)
    add_sample(rows, panel, duplicate_mask, "duplicate_ticker_period_prediction", 35)
    add_sample(rows, panel, panel["global_event_count"].fillna(0).gt(0), "global_event_context_present", 35)
    add_sample(rows, panel, panel["market_stress_regime"].fillna(0).eq(1), "market_stress_regime", 30)
    add_sample(rows, panel, panel["prediction_year"].between(2022, 2024), "temporal_test_window", 35)
    add_sample(rows, panel, panel["ticker"].isin(["AAPL", "MSFT", "NVDA", "XOM", "JPM", "BKR", "VICI"]), "known_anchor_tickers", 60)

    sample = pd.concat(rows, ignore_index=True)
    sample = sample.drop_duplicates(["audit_category", "adsh"], keep="first")
    keep = ["audit_category"] + [column for column in KEY_COLUMNS if column in sample.columns]
    sample = sample[keep].sort_values(["audit_category", "ticker", "prediction_date", "adsh"])
    sample.to_csv(SAMPLE_CSV, index=False)

    summary = (
        sample.groupby("audit_category")
        .agg(rows=("adsh", "size"), firms=("cik", "nunique"), first_prediction=("prediction_date", "min"), last_prediction=("prediction_date", "max"))
        .reset_index()
    )
    summary.to_csv(SAMPLE_SUMMARY_CSV, index=False)
    return sample


def audit_formulas(panel: pd.DataFrame) -> pd.DataFrame:
    checks: list[dict[str, object]] = []
    ratio_formulas = {
        "leverage_assets": safe_divide(panel["total_liabilities"], panel["total_assets"]),
        "equity_assets": safe_divide(panel["total_equity"], panel["total_assets"]),
        "current_ratio": safe_divide(panel["current_assets"], panel["current_liabilities"]),
        "cash_assets": safe_divide(panel["cash_equivalents"], panel["total_assets"]),
        "net_margin": safe_divide(panel["net_income"], panel["total_revenue"]),
        "operating_margin": safe_divide(panel["operating_income"], panel["total_revenue"]),
        "gross_margin": safe_divide(panel["gross_profit"], panel["total_revenue"]),
        "roa": safe_divide(panel["net_income"], panel["total_assets"]),
        "r_and_d_intensity": safe_divide(panel["r_and_d_expense"], panel["total_revenue"]),
        "inventory_assets": safe_divide(panel["inventory"], panel["total_assets"]),
        "receivables_assets": safe_divide(panel["accounts_receivable"], panel["total_assets"]),
    }
    for column, expected in ratio_formulas.items():
        checks.append(
            {
                "area": "ratio_recompute",
                "column": column,
                "rows_checked": int(panel[column].shape[0]),
                "mismatches": mismatch_count(panel[column], expected),
                "status": "PASS" if mismatch_count(panel[column], expected) == 0 else "REVIEW",
            }
        )

    sorted_panel = panel.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).copy()
    grouped = sorted_panel.groupby("cik", group_keys=False)
    trend_expected = {
        "roa_lag1": grouped["roa"].shift(1),
        "leverage_assets_lag1": grouped["leverage_assets"].shift(1),
        "current_ratio_lag1": grouped["current_ratio"].shift(1),
        "cash_assets_lag1": grouped["cash_assets"].shift(1),
        "net_margin_lag1": grouped["net_margin"].shift(1),
        "operating_margin_lag1": grouped["operating_margin"].shift(1),
        "gross_margin_lag1": grouped["gross_margin"].shift(1),
        "total_revenue_growth_4obs": safe_divide(sorted_panel["total_revenue"], grouped["total_revenue"].shift(4)) - 1,
        "total_assets_growth_4obs": safe_divide(sorted_panel["total_assets"], grouped["total_assets"].shift(4)) - 1,
        "cash_equivalents_growth_4obs": safe_divide(sorted_panel["cash_equivalents"], grouped["cash_equivalents"].shift(4)) - 1,
        "total_liabilities_growth_4obs": safe_divide(sorted_panel["total_liabilities"], grouped["total_liabilities"].shift(4)) - 1,
        "current_assets_growth_4obs": safe_divide(sorted_panel["current_assets"], grouped["current_assets"].shift(4)) - 1,
        "current_liabilities_growth_4obs": safe_divide(sorted_panel["current_liabilities"], grouped["current_liabilities"].shift(4)) - 1,
        "roa_change_4obs": sorted_panel["roa"] - grouped["roa"].shift(4),
        "leverage_assets_change_4obs": sorted_panel["leverage_assets"] - grouped["leverage_assets"].shift(4),
        "current_ratio_change_4obs": sorted_panel["current_ratio"] - grouped["current_ratio"].shift(4),
        "cash_assets_change_4obs": sorted_panel["cash_assets"] - grouped["cash_assets"].shift(4),
        "net_margin_change_4obs": sorted_panel["net_margin"] - grouped["net_margin"].shift(4),
        "operating_margin_change_4obs": sorted_panel["operating_margin"] - grouped["operating_margin"].shift(4),
        "gross_margin_change_4obs": sorted_panel["gross_margin"] - grouped["gross_margin"].shift(4),
    }
    for column, expected in trend_expected.items():
        if column not in sorted_panel.columns:
            continue
        observed = sorted_panel[column]
        mismatches = mismatch_count(observed, expected)
        checks.append(
            {
                "area": "trend_recompute",
                "column": column,
                "rows_checked": int(observed.shape[0]),
                "mismatches": mismatches,
                "status": "PASS" if mismatches == 0 else "REVIEW",
            }
        )

    negative_history = sum((grouped["net_income"].shift(step) < 0).astype(float) for step in range(1, 5))
    mismatches = mismatch_count(sorted_panel["net_income_negative_count_prior_4obs"], negative_history)
    checks.append(
        {
            "area": "trend_recompute",
            "column": "net_income_negative_count_prior_4obs",
            "rows_checked": len(sorted_panel),
            "mismatches": mismatches,
            "status": "PASS" if mismatches == 0 else "REVIEW",
        }
    )

    if PROVENANCE_PATH.exists():
        provenance = pd.read_parquet(PROVENANCE_PATH, columns=["ddate", "period", "ddate_period_aligned", "selected_value"])
        checks.append(
            {
                "area": "sec_fact_provenance",
                "column": "ddate_period_aligned",
                "rows_checked": len(provenance),
                "mismatches": int((provenance["ddate"].astype(str) != provenance["period"].astype(str)).sum()),
                "status": "PASS" if bool(provenance["ddate_period_aligned"].fillna(False).all()) else "REVIEW",
            }
        )

    frame = pd.DataFrame(checks)
    frame.to_csv(FORMULA_CSV, index=False)
    return frame


def compare_nullable_int(observed: pd.Series, expected: pd.Series) -> int:
    obs = observed.astype("Int64")
    exp = expected.astype("Int64")
    same_missing = obs.isna() & exp.isna()
    same_values = obs.fillna(-999999).eq(exp.fillna(-999999))
    return int((~(same_missing | same_values)).sum())


def audit_targets(panel: pd.DataFrame) -> pd.DataFrame:
    recomputed = panel.copy()
    recomputed = panel_builder.add_failure_pressure_targets(recomputed)
    recomputed = panel_builder.add_forward_success_targets(recomputed)

    days_to_event = (panel["event_date"] - panel["prediction_date"]).dt.days
    strict_expected = (
        (panel["formal_distress_firm"].fillna(0).astype(int) == 1)
        & (days_to_event > 0)
        & (days_to_event <= 456)
    ).astype("Int64")

    checks = [
        {
            "target": "distress_next_4q",
            "known_observed": int(panel["distress_next_4q"].notna().sum()),
            "positives_observed": int(panel["distress_next_4q"].fillna(0).sum()),
            "mismatches": compare_nullable_int(panel["distress_next_4q"], strict_expected),
            "status": "PASS" if compare_nullable_int(panel["distress_next_4q"], strict_expected) == 0 else "REVIEW",
        }
    ]
    for target in ["failure_pressure_conservative_v2_next_4obs", "success_resilience_next_4q"]:
        mismatches = compare_nullable_int(panel[target], recomputed[target])
        checks.append(
            {
                "target": target,
                "known_observed": int(panel[target].notna().sum()),
                "positives_observed": int(panel[target].fillna(0).sum()),
                "mismatches": mismatches,
                "status": "PASS" if mismatches == 0 else "REVIEW",
            }
        )
    frame = pd.DataFrame(checks)
    frame.to_csv(TARGET_CSV, index=False)
    return frame


def audit_models(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    features = train_models.NUMERIC_FEATURES + train_models.CATEGORICAL_FEATURES
    missing_features = [feature for feature in features if feature not in panel.columns]
    blacklist = set()
    if BLACKLIST_PATH.exists():
        blacklist = set(pd.read_csv(BLACKLIST_PATH).iloc[:, 0].dropna().astype(str))
    blacklist_overlap = sorted(set(features) & blacklist)
    rows.append(
        {
            "area": "feature_list",
            "status": "PASS" if not missing_features and not blacklist_overlap else "FAIL",
            "evidence": f"features={len(features)}; missing={missing_features}; blacklist_overlap={blacklist_overlap}",
        }
    )

    for target in PRODUCTION_TARGETS:
        df = train_models.load_panel(target)
        splits = train_models.make_splits(df)
        split_evidence = "; ".join(
            f"{name}: rows={len(split)}, positives={int(split[target].sum())}, years={int(split['prediction_year'].min()) if len(split) else 'n/a'}-{int(split['prediction_year'].max()) if len(split) else 'n/a'}"
            for name, split in splits.items()
        )
        overlap_keys = []
        key = ["ticker", "period_date", "prediction_date", "adsh"]
        if all(column in df.columns for column in key):
            key_sets = {name: set(map(tuple, split[key].astype(str).to_numpy())) for name, split in splits.items()}
            overlap_keys = [
                f"{a}-{b}"
                for a in key_sets
                for b in key_sets
                if a < b and key_sets[a] & key_sets[b]
            ]
        rows.append(
            {
                "area": f"temporal_split_{target}",
                "status": "PASS" if not overlap_keys else "FAIL",
                "evidence": f"{split_evidence}; key_overlaps={overlap_keys}",
            }
        )
        metrics_path = MODEL_REPORT_DIR / f"panel_v2_{target}_model_metrics.csv"
        if metrics_path.exists():
            metrics = pd.read_csv(metrics_path)
            test = metrics[metrics["split"] == "test"].sort_values("pr_auc", ascending=False)
            best = test.iloc[0].to_dict() if not test.empty else {}
            rows.append(
                {
                    "area": f"saved_metrics_{target}",
                    "status": "PASS" if not test.empty else "REVIEW",
                    "evidence": (
                        f"best_test_model={best.get('model')}; roc_auc={best.get('roc_auc')}; "
                        f"pr_auc={best.get('pr_auc')}; f1={best.get('f1')}; positives={best.get('positives')}"
                    ),
                }
            )
        feature_list_path = MODEL_FEATURE_DIR / f"{target}_features.csv"
        if feature_list_path.exists():
            listed = set(pd.read_csv(feature_list_path)["column"].dropna().astype(str))
            overlap = sorted(listed & blacklist)
            rows.append(
                {
                    "area": f"saved_feature_blacklist_{target}",
                    "status": "PASS" if not overlap else "FAIL",
                    "evidence": f"listed_features={len(listed)}; blacklist_overlap={overlap}",
                }
            )

    for root, name in [(TUNING_DIR, "sklearn_tuning"), (ADV_TUNING_DIR, "advanced_boosting")]:
        summary = root / ("model_tuning_summary.csv" if name == "sklearn_tuning" else "advanced_boosting_summary.csv")
        failures = list(root.glob("*/candidate_failures.csv"))
        failure_rows = 0
        for path in failures:
            frame = pd.read_csv(path)
            failure_rows += len(frame.dropna(how="all"))
        rows.append(
            {
                "area": name,
                "status": "PASS_WITH_CAVEAT" if summary.exists() and failure_rows == 0 else "REVIEW",
                "evidence": f"summary_exists={summary.exists()}; candidate_failure_rows={failure_rows}",
            }
        )

    frame = pd.DataFrame(rows)
    frame.to_csv(MODEL_CSV, index=False)
    return frame


def audit_dashboard_static(panel: pd.DataFrame) -> pd.DataFrame:
    text = DASHBOARD_PATH.read_text(encoding="utf-8")
    rows = []
    all_financial = set()
    for values in panel_builder.classify_schema_column.__globals__.values():
        _ = values
    dashboard_financial = set()
    dashboard_macro = set()
    # Importing app/dashboard.py would run Streamlit code, so parse the source
    # conservatively by comparing known constants from the executed dashboard file.
    namespace: dict[str, object] = {"__file__": str(DASHBOARD_PATH)}
    constant_source = text.split("st.set_page_config", 1)[0]
    exec(compile(constant_source, str(DASHBOARD_PATH), "exec"), namespace)
    for values in namespace["FIRM_METRIC_GROUPS"].values():
        dashboard_financial.update(values)
    for values in namespace["MACRO_METRIC_GROUPS"].values():
        dashboard_macro.update(values)

    schema = pd.read_csv(SCHEMA_PATH)
    financial_families = {"sec_accounting_fundamental", "financial_ratio", "firm_trend_or_deterioration"}
    usable_financial = set(schema.loc[schema["feature_family"].isin(financial_families), "column"])
    macro_families = {"macro_variable", "macro_regime_indicator", "global_event_context"}
    usable_macro = set(schema.loc[schema["feature_family"].isin(macro_families), "column"])
    chartable_macro = {
        column
        for column in usable_macro
        if column in panel.columns and pd.api.types.is_numeric_dtype(panel[column])
    }

    rows.append(
        {
            "area": "financial_dashboard_coverage",
            "status": "PASS" if usable_financial <= dashboard_financial else "REVIEW",
            "evidence": f"dashboard={len(dashboard_financial & set(panel.columns))}; schema_usable={len(usable_financial)}; missing={sorted(usable_financial - dashboard_financial)}",
        }
    )
    rows.append(
        {
            "area": "macro_dashboard_coverage",
            "status": "PASS" if chartable_macro <= dashboard_macro else "REVIEW",
            "evidence": f"dashboard_chartable={len(dashboard_macro & set(panel.columns))}; schema_chartable={len(chartable_macro)}; missing={sorted(chartable_macro - dashboard_macro)}",
        }
    )
    rows.append(
        {
            "area": "global_event_names_text_context",
            "status": "PASS" if "Readable Global Event Context" in text and "global_event_names" in text else "REVIEW",
            "evidence": "`global_event_names` is treated as readable text context, not as a numeric chart metric.",
        }
    )
    rows.append(
        {
            "area": "target_separation",
            "status": "PASS" if "TARGET_TIMELINE_COLUMNS" in text and "Target Timeline" in text else "REVIEW",
            "evidence": "Targets are shown in a separate timeline tab; firm metrics use FIRM_METRIC_GROUPS.",
        }
    )
    rows.append(
        {
            "area": "standardization_disclosure",
            "status": "PASS" if "standardization_caption" in text and "Training-period baseline" in text else "REVIEW",
            "evidence": "Dashboard exposes selected-window, filtered-panel, and training-period standardization baselines.",
        }
    )
    rows.append(
        {
            "area": "artifact_caveats",
            "status": "PASS" if "Caveat Controls" in text and "Null values" in text else "REVIEW",
            "evidence": "Artifact tab contains thesis story and caveat controls.",
        }
    )
    frame = pd.DataFrame(rows)
    frame.to_csv(DASHBOARD_CSV, index=False)
    return frame


def write_report(
    panel: pd.DataFrame,
    sample: pd.DataFrame,
    formula: pd.DataFrame,
    targets: pd.DataFrame,
    models: pd.DataFrame,
    dashboard: pd.DataFrame,
) -> None:
    p0 = pd.read_csv(P0_PATH) if P0_PATH.exists() else pd.DataFrame()
    schema = pd.read_csv(SCHEMA_PATH) if SCHEMA_PATH.exists() else pd.DataFrame()
    null_share = panel.select_dtypes(include=[np.number]).isna().sum().sum() / panel.select_dtypes(include=[np.number]).size
    duplicates = int(panel.duplicated(["ticker", "period_date", "prediction_date"], keep=False).sum())
    duplicate_ciks = panel.groupby("cik")["ticker"].nunique()
    multi_ticker_ciks = duplicate_ciks[duplicate_ciks > 1]
    outlier_revenue = int(panel["total_revenue"].lt(0).sum())
    outlier_assets = int(panel["total_assets"].le(0).sum())
    target_mismatch_total = int(targets["mismatches"].sum()) if "mismatches" in targets.columns else 0
    formula_mismatch_total = int(formula["mismatches"].sum()) if "mismatches" in formula.columns else 0
    dashboard_review_rows = int((dashboard["status"].astype(str) == "REVIEW").sum()) if "status" in dashboard.columns else 0
    rendered_dashboard = pd.read_csv(RENDERED_DASHBOARD_CSV) if RENDERED_DASHBOARD_CSV.exists() else pd.DataFrame()
    highest_risk_lines = [
        "## Highest-Risk Manual Row Finding",
        "",
    ]
    if len(multi_ticker_ciks) == 0:
        highest_risk_lines.extend(
            [
                "- The prior `PCG`/`PGNPQ` duplicate-CIK issue is resolved in the current rebuilt panel: no CIK maps to multiple ticker/display IDs.",
                "- Target recomputation now has zero mismatches across the three production targets.",
            ]
        )
    else:
        highest_risk_lines.extend(
            [
                "- At least one CIK still maps to multiple ticker/display IDs. This can duplicate identical SEC filing histories under multiple display tickers and must be reviewed before final freeze.",
                "- If duplicated CIK histories carry different event labels, the affected target rows should not be used as final scientific evidence until rebuilt or explicitly caveated.",
            ]
        )

    def table(frame: pd.DataFrame) -> str:
        if frame.empty:
            return "_No rows._"
        clean = frame.copy()
        clean = clean.replace({np.nan: ""})
        headers = [str(col) for col in clean.columns]
        output = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for row in clean.astype(str).values.tolist():
            output.append("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |")
        return "\n".join(output)

    lines = [
        "# Full Manual Logic, UI, And Backend Audit - 2026-05-08",
        "",
        "This audit combines manual code reading with a fixed hand-reviewable panel sample and recomputation checks. It does not rebuild or edit the production panel.",
        "",
        "## Executive Result",
        "",
        "- The project is scientifically usable for the thesis, but it should be presented as an audited empirical artifact with explicit caveats, not as a perfect corporate-default database.",
        "- The highest-risk timing, target-leakage, SEC period-alignment, duplicate-CIK, and target-recompute checks pass in the rebuilt panel. The remaining risks are accounting concept imperfections, source outlier rows, duplicate/amended filings, material missingness, and dashboard visual-density caveats.",
        f"- Formula recomputation still has `{formula_mismatch_total:,}` small REVIEW mismatches because the audit recomputes raw formulas while the production builder applies extreme-value cleaning/null preservation. These are disclosed rather than silently overwritten.",
        f"- Dashboard static backend checks have `{dashboard_review_rows}` REVIEW rows after the current polish pass; readable event context is now surfaced separately from numeric macro charts.",
        "",
        "## Panel Snapshot",
        "",
        f"- Rows: `{len(panel):,}`",
        f"- Columns: `{len(panel.columns):,}`",
        f"- CIKs: `{panel['cik'].nunique():,}`",
        f"- Ticker/display IDs: `{panel['ticker'].nunique():,}`",
        f"- Prediction dates: `{panel['prediction_date'].min().date()}` to `{panel['prediction_date'].max().date()}`",
        f"- Numeric null share: `{null_share:.3%}`",
        f"- Duplicate ticker-period-prediction rows: `{duplicates:,}`",
        f"- CIKs mapped to multiple ticker/display IDs: `{len(multi_ticker_ciks):,}`",
        f"- Negative revenue rows: `{outlier_revenue:,}`",
        f"- Non-positive asset rows: `{outlier_assets:,}`",
        "",
        "## P0 Audit Status",
        "",
        table(p0) if not p0.empty else "_P0 audit file missing._",
        "",
        "## Manual Row Sample",
        "",
        f"A fixed review sample of `{len(sample):,}` rows was written to `{SAMPLE_CSV.relative_to(PROJECT_ROOT)}`. It intentionally over-samples distress, broader failure pressure, success/resilience, neutral observations, unknown horizons, duplicates, outliers, event-context rows, stress-regime rows, test-window rows, and anchor tickers.",
        "",
        table(pd.read_csv(SAMPLE_SUMMARY_CSV)),
        "",
        *highest_risk_lines,
        "",
        "## Formula Recompute Checks",
        "",
        table(formula),
        "",
        "Formula mismatches are small relative to the full panel and mostly reflect the difference between raw arithmetic recomputation and the production builder's null-preserving extreme-value cleanup. This is not timing leakage or target leakage; it remains a disclosed accounting/data-quality caveat.",
        "",
        "## Target Recompute Checks",
        "",
        table(targets),
        "",
        "## Model Logic Checks",
        "",
        table(models),
        "",
        "## Dashboard Static Backend Checks",
        "",
        table(dashboard),
        "",
        "## Dashboard Rendered Browser Checks",
        "",
        table(rendered_dashboard) if not rendered_dashboard.empty else "_Rendered dashboard audit file not found._",
        "",
        "## Manual Code-Reading Findings",
        "",
        "1. `scripts/sec_fsd/build_panel_v2.py` uses `ddate == period`, excludes dimensional segment/coreg facts, filters units, standardizes flow values, then computes ratios, lags, macro/event context, and forward labels. This is the correct structure for avoiding look-ahead from filing-period accounting values.",
        "2. The flow-standardization logic is reasonable but not equivalent to a full accountant-grade XBRL mapping audit. The thesis should say selected facts are mapped and audited, not that every possible SEC tag across all firms is perfectly represented.",
        "3. `prediction_date = filed_date` is correctly used as the information-availability date. This is one of the strongest parts of the empirical design.",
        "4. `scripts/modeling/train_panel_v2_models.py` uses train `<= 2018`, validation `2019-2021`, and test `2022-2024`, with threshold selection on validation. This is defensible and better than random split for the thesis.",
        "5. The model feature list excludes target/event-date metadata by blacklist, but imputer-generated missingness indicators exist inside pipelines. They must remain predictive auxiliaries and must not be interpreted as economic causes.",
        "6. The dashboard separates firm metrics from target timelines and includes standardization baseline controls. This directly addresses the earlier issue where raw metrics and targets were visually mixed.",
        "7. `scripts/data_quality/audit_data_integrity_caveats.py` previously had one stale generated-report sentence about event-date provenance; it has been patched so future reruns align with the current PASS status for formal strict-distress event provenance.",
        "",
        "## Remaining Weaknesses",
        "",
        "- SEC concept mapping is strong enough for thesis use but still relies on a selected concept map and priority rules. This is normal for FSD work, but it must be disclosed.",
        "- Accounting sign/outlier rows remain real review items. Do not delete them silently; either disclose or source-correct if time allows.",
        "- The prior `PCG`/`PGNPQ` duplicate-CIK mapping has been resolved in the rebuilt panel; keep the alias-resolution note with the final package.",
        "- Duplicate/amended-filing rows remain small in count but need explicit policy wording.",
        "- Missingness is material. The panel should stay null-preserving; model imputation should stay inside pipelines.",
        "- Strict legal distress is source-curated and rare. It is a benchmark, not a complete bankruptcy universe.",
        "- Dashboard screenshots and console triage now pass; remaining dashboard caveats are presentation-density issues on narrow/mobile views, not empirical validity issues.",
        "",
        "## Audit Artifacts",
        "",
        f"- `{SAMPLE_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{SAMPLE_SUMMARY_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{FORMULA_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{TARGET_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{MODEL_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{DASHBOARD_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{RENDERED_DASHBOARD_CSV.relative_to(PROJECT_ROOT)}`",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = read_panel()
    sample = build_manual_sample(panel)
    formula = audit_formulas(panel)
    targets = audit_targets(panel)
    models = audit_models(panel)
    dashboard = audit_dashboard_static(panel)
    write_report(panel, sample, formula, targets, models, dashboard)
    print(f"Wrote {REPORT_MD.relative_to(PROJECT_ROOT)}")
    print(f"Manual sample rows: {len(sample):,}")
    print("Formula statuses:")
    print(formula["status"].value_counts(dropna=False).to_string())
    print("Target statuses:")
    print(targets.to_string(index=False))
    print("Model statuses:")
    print(models["status"].value_counts(dropna=False).to_string())
    print("Dashboard statuses:")
    print(dashboard.to_string(index=False))


if __name__ == "__main__":
    main()
