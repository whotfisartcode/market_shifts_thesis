#!/usr/bin/env python3
"""Audit data lineage, missingness, and SEC flow-period choices for panel_v2."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.sec_fsd.build_panel_v2 import (  # noqa: E402
    ZIP_DIR,
    filter_current_period_facts,
    read_concept_map,
    read_num,
    read_sub,
    read_universe,
)


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
SCHEMA_PATH = PROJECT_ROOT / "data/github/firm_panel_v2_schema.csv"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"

KEY_ACCOUNTING_COLS = [
    "total_assets",
    "total_liabilities",
    "noncurrent_liabilities",
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
    "r_and_d_expense",
]


def collect_selected_sec_rows() -> pd.DataFrame:
    universe = read_universe()
    concept_map = read_concept_map()
    selected_ciks = set(universe["cik"].dropna().astype(int))
    rows = []

    for path in sorted(ZIP_DIR.glob("*.zip")):
        if not path.name[:4].isdigit():
            continue
        sub = read_sub(path, selected_ciks)
        if sub.empty:
            continue
        num = read_num(path, set(sub["adsh"].astype(str)), concept_map)
        if num.empty:
            continue
        num = num.merge(concept_map, on="tag", how="inner")
        num = num.merge(sub, on="adsh", how="inner")

        statement_mask = (
            ((num["statement"] == "balance") & (num["qtrs"] == 0))
            | ((num["statement"] == "flow") & (num["qtrs"].isin([1, 2, 3, 4])))
            | ((num["statement"] == "shares") & (num["qtrs"].isin([0, 1, 4])))
            | ((num["statement"] == "eps") & (num["qtrs"].isin([1, 4])))
        )
        num = num[statement_mask].copy()
        num = filter_current_period_facts(num)
        if num.empty:
            continue
        rows.append(num)

    if not rows:
        return pd.DataFrame()

    long = pd.concat(rows, ignore_index=True)
    long = long.sort_values(["adsh", "variable", "priority", "tag"])
    return long.drop_duplicates(["adsh", "variable"], keep="first")


def summarize_sec_sources(long: pd.DataFrame) -> None:
    if long.empty:
        return

    base = (
        long.groupby(["variable", "statement"], dropna=False)
        .agg(
            selected_values=("value", "count"),
            submissions=("adsh", "nunique"),
            firms=("cik", "nunique"),
            first_period=("period", "min"),
            last_period=("period", "max"),
            tags=("tag", lambda values: "; ".join(sorted(set(values.astype(str)))[:12])),
            uoms=("uom", lambda values: "; ".join(sorted(set(values.astype(str)))[:8])),
            forms=("form", lambda values: "; ".join(sorted(set(values.astype(str)))[:8])),
        )
        .reset_index()
    )

    qtrs = (
        long.assign(qtrs_label=lambda df: "qtrs_" + df["qtrs"].astype("Int64").astype(str))
        .pivot_table(
            index="variable",
            columns="qtrs_label",
            values="value",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )
    out = base.merge(qtrs, on="variable", how="left").sort_values(["statement", "variable"])
    out.to_csv(REPORT_DIR / "sec_fsd_variable_source_audit.csv", index=False)


def summarize_schema_missingness() -> None:
    if not SCHEMA_PATH.exists():
        return
    schema = pd.read_csv(SCHEMA_PATH)
    summary = (
        schema.groupby("feature_family", dropna=False)
        .agg(
            columns=("column", "count"),
            average_missing_share=("missing_share", "mean"),
            max_missing_share=("missing_share", "max"),
            columns_over_50pct_missing=("missing_share", lambda values: int((values > 0.5).sum())),
        )
        .reset_index()
        .sort_values("average_missing_share", ascending=False)
    )
    summary.to_csv(REPORT_DIR / "panel_v2_missingness_by_feature_family.csv", index=False)


def summarize_key_missingness_by_form(panel: pd.DataFrame) -> None:
    rows = []
    group_cols = ["form", "fp"]
    grouped = panel.groupby(group_cols, dropna=False)
    for (form, fp), group in grouped:
        for col in KEY_ACCOUNTING_COLS:
            if col not in group.columns:
                continue
            rows.append(
                {
                    "form": form,
                    "fp": fp,
                    "variable": col,
                    "rows": len(group),
                    "non_missing": int(group[col].notna().sum()),
                    "missing_share": float(group[col].isna().mean()),
                }
            )
    out = pd.DataFrame(rows).sort_values(["variable", "form", "fp"])
    out.to_csv(REPORT_DIR / "panel_v2_key_missingness_by_form_fp.csv", index=False)


def summarize_longitudinal_missingness(panel: pd.DataFrame) -> None:
    rows = []
    sort_cols = [col for col in ["cik", "prediction_date", "period_date", "filed_date"] if col in panel.columns]
    panel = panel.sort_values(sort_cols).copy()

    for col in KEY_ACCOUNTING_COLS:
        if col not in panel.columns:
            continue

        for cik, group in panel.groupby("cik", dropna=False):
            values = group[col]
            missing = values.isna()
            non_missing = values.notna()
            prior_available = values.ffill().notna()
            future_available = values.bfill().notna()

            if non_missing.any():
                first_valid_position = non_missing.to_numpy().argmax()
                last_valid_position = len(non_missing) - non_missing.iloc[::-1].to_numpy().argmax() - 1
                positions = pd.Series(range(len(group)), index=group.index)
                before_first = positions < first_valid_position
                after_last = positions > last_valid_position
            else:
                before_first = pd.Series(True, index=group.index)
                after_last = pd.Series(True, index=group.index)

            rows.append(
                {
                    "cik": cik,
                    "ticker": group["ticker"].iloc[0] if "ticker" in group else pd.NA,
                    "variable": col,
                    "rows": len(group),
                    "non_missing": int(non_missing.sum()),
                    "missing": int(missing.sum()),
                    "missing_share": float(missing.mean()),
                    "firm_ever_reports_variable": bool(non_missing.any()),
                    "missing_with_prior_value_available": int((missing & prior_available).sum()),
                    "missing_with_future_value_available": int((missing & future_available).sum()),
                    "missing_internal_gap_prior_and_future": int((missing & prior_available & future_available).sum()),
                    "missing_before_first_observed_value": int((missing & before_first).sum()),
                    "missing_after_last_observed_value": int((missing & after_last).sum()),
                }
            )

    firm_level = pd.DataFrame(rows)
    firm_level.to_csv(REPORT_DIR / "panel_v2_longitudinal_missingness_by_firm.csv", index=False)

    summary = (
        firm_level.groupby("variable", dropna=False)
        .agg(
            firms=("cik", "nunique"),
            firms_ever_reporting=("firm_ever_reports_variable", "sum"),
            rows=("rows", "sum"),
            non_missing=("non_missing", "sum"),
            missing=("missing", "sum"),
            missing_with_prior_value_available=("missing_with_prior_value_available", "sum"),
            missing_with_future_value_available=("missing_with_future_value_available", "sum"),
            missing_internal_gap_prior_and_future=("missing_internal_gap_prior_and_future", "sum"),
            missing_before_first_observed_value=("missing_before_first_observed_value", "sum"),
            missing_after_last_observed_value=("missing_after_last_observed_value", "sum"),
        )
        .reset_index()
    )
    summary["missing_share"] = summary["missing"] / summary["rows"]
    summary["firm_never_reported_share"] = 1 - (summary["firms_ever_reporting"] / summary["firms"])
    summary["missing_share_with_prior_value_available"] = (
        summary["missing_with_prior_value_available"] / summary["missing"].replace({0: pd.NA})
    )
    summary["missing_internal_gap_share"] = (
        summary["missing_internal_gap_prior_and_future"] / summary["missing"].replace({0: pd.NA})
    )
    summary.to_csv(REPORT_DIR / "panel_v2_longitudinal_missingness_summary.csv", index=False)


def summarize_panel_null_policy(panel: pd.DataFrame) -> None:
    numeric_cols = panel.select_dtypes(include="number").columns
    rows = [
        {
            "check": "panel_numeric_cells",
            "value": int(panel[numeric_cols].size),
            "interpretation": "Total numeric cells in the exported panel.",
        },
        {
            "check": "panel_numeric_null_cells",
            "value": int(panel[numeric_cols].isna().sum().sum()),
            "interpretation": "Null numeric cells preserved in the exported panel; these are not filled in the dataset.",
        },
        {
            "check": "panel_numeric_null_share",
            "value": float(panel[numeric_cols].isna().sum().sum() / panel[numeric_cols].size),
            "interpretation": "Overall numeric null share in the exported panel.",
        },
        {
            "check": "model_numeric_null_treatment",
            "value": "median imputation inside sklearn Pipeline",
            "interpretation": "Modeling can impute during training/scoring, but the persisted dataset remains null-preserving.",
        },
    ]
    pd.DataFrame(rows).to_csv(REPORT_DIR / "panel_v2_null_treatment_audit.csv", index=False)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(PANEL_PATH, low_memory=False)
    long = collect_selected_sec_rows()
    summarize_sec_sources(long)
    summarize_schema_missingness()
    summarize_key_missingness_by_form(panel)
    summarize_longitudinal_missingness(panel)
    summarize_panel_null_policy(panel)
    print("Wrote panel integrity audit reports")


if __name__ == "__main__":
    main()
