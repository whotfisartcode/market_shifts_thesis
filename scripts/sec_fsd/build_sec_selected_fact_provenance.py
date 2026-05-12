#!/usr/bin/env python3
"""Build row-level provenance for selected SEC FSD accounting facts.

This script does not change the production panel. It reconstructs the selected
SEC facts using the same concept map and qtrs policy as the panel builder, then
writes a sidecar audit table showing which raw SEC tag/value became each panel
accounting variable.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import build_panel_v2 as panel_builder  # noqa: E402


OUT_DIR = PROJECT_ROOT / "reports/data_quality"
PROVENANCE_PARQUET = OUT_DIR / "sec_selected_fact_provenance.parquet"
PROVENANCE_CSV_GZ = OUT_DIR / "sec_selected_fact_provenance.csv.gz"
SUMMARY_CSV = OUT_DIR / "sec_selected_fact_provenance_summary.csv"
METHOD_CSV = OUT_DIR / "sec_selected_fact_method_summary.csv"
VALIDATION_CSV = OUT_DIR / "sec_selected_fact_panel_validation.csv"
VALIDATION_REVIEW_ROWS_CSV = OUT_DIR / "sec_selected_fact_panel_validation_review_rows.csv"


def collect_long_raw(universe: pd.DataFrame, concept_map: pd.DataFrame) -> pd.DataFrame:
    selected_ciks = set(universe["cik"].dropna().astype(int))
    zip_paths = sorted(path for path in panel_builder.ZIP_DIR.glob("*.zip") if path.name[:4].isdigit())
    rows = []

    for index, path in enumerate(zip_paths, start=1):
        sub = panel_builder.read_sub(path, selected_ciks)
        if sub.empty:
            continue

        num = panel_builder.read_num(path, set(sub["adsh"].astype(str)), concept_map)
        if num.empty:
            continue

        num = num.merge(concept_map, on="tag", how="inner")
        num = num.merge(sub, on="adsh", how="inner")
        statement_conditions = [
            ((num["statement"] == "balance") & (num["qtrs"] == 0)).fillna(False).to_numpy(dtype=bool),
            ((num["statement"] == "flow") & (num["qtrs"].isin([1, 2, 3, 4]))).fillna(False).to_numpy(dtype=bool),
            ((num["statement"] == "shares") & (num["qtrs"].isin([0, 1, 4]))).fillna(False).to_numpy(dtype=bool),
            ((num["statement"] == "eps") & (num["qtrs"].isin([1, 4]))).fillna(False).to_numpy(dtype=bool),
        ]
        num["statement_rank"] = np.select(statement_conditions, [0, 0, 0, 0], default=9)
        num = num[num["statement_rank"] == 0]
        if not num.empty:
            rows.append(num)

        if index % 10 == 0:
            print(f"Scanned {index}/{len(zip_paths)} SEC ZIPs")

    if not rows:
        raise RuntimeError("No SEC numeric rows matched selected universe/concept map")

    long_raw = pd.concat(rows, ignore_index=True)
    long_raw["reported_value"] = long_raw["value"]
    long_raw = panel_builder.normalize_sec_sign_conventions(long_raw)
    long_raw["normalized_reported_value"] = long_raw["value"]
    long_raw["period_date"] = pd.to_datetime(
        long_raw["period"].astype("Int64").astype(str),
        format="%Y%m%d",
        errors="coerce",
    )
    long_raw["filed_date"] = pd.to_datetime(
        long_raw["filed"].astype("Int64").astype(str),
        format="%Y%m%d",
        errors="coerce",
    )
    return long_raw


def standardize_with_provenance(long_raw: pd.DataFrame) -> pd.DataFrame:
    long_raw = long_raw.copy()
    long_raw["segments"] = long_raw["segments"].fillna("")
    long_raw["coreg"] = long_raw["coreg"].fillna("")
    long_raw = panel_builder.filter_current_period_facts(long_raw)
    if long_raw.empty:
        return long_raw.assign(
            selected_value=pd.Series(dtype="float64"),
            value_method=pd.Series(dtype="object"),
            prior_cumulative_qtrs=pd.Series(dtype="object"),
            prior_cumulative_value=pd.Series(dtype="float64"),
            prior_cumulative_adsh=pd.Series(dtype="object"),
        )

    long_raw = long_raw.sort_values(["adsh", "variable", "qtrs", "priority", "tag"])
    long_raw = long_raw.drop_duplicates(["adsh", "variable", "qtrs"], keep="first")

    non_flow = long_raw[long_raw["statement"] != "flow"].copy()
    qtrs_preference = {
        "balance": {0: 0},
        "shares": {0: 0, 1: 1, 4: 2},
        "eps": {1: 0, 4: 1},
    }
    if not non_flow.empty:
        non_flow["qtrs_rank"] = non_flow.apply(
            lambda row: qtrs_preference.get(str(row["statement"]), {}).get(int(row["qtrs"]), 9),
            axis=1,
        )
        non_flow = non_flow.sort_values(["adsh", "variable", "qtrs_rank", "priority", "tag"])
        non_flow = non_flow.drop_duplicates(["adsh", "variable"], keep="first")
        non_flow["selected_value"] = non_flow["value"]
        non_flow["value_method"] = "reported"
        non_flow["prior_cumulative_qtrs"] = pd.NA
        non_flow["prior_cumulative_value"] = np.nan
        non_flow["prior_cumulative_adsh"] = pd.NA

    flow = long_raw[long_raw["statement"] == "flow"].copy()
    standardized_flow = pd.DataFrame()
    if not flow.empty:
        groups = []
        for _, group in flow.groupby(["cik", "variable", "fy"], dropna=False):
            selected = standardize_flow_group_with_provenance(group)
            if not selected.empty:
                groups.append(selected)
        if groups:
            standardized_flow = pd.concat(groups, ignore_index=True)

    out = pd.concat([non_flow, standardized_flow], ignore_index=True)
    out = out.sort_values(["adsh", "variable", "priority", "tag"])
    out = out.drop_duplicates(["adsh", "variable"], keep="first")
    return out


def standardize_flow_group_with_provenance(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values(["period_date", "filed_date", "qtrs", "priority", "tag"])
    selected: dict[str, pd.Series] = {}
    latest_cumulative: dict[int, tuple[float, str]] = {}

    for _, row in group.iterrows():
        adsh = str(row["adsh"])
        qtrs = int(row["qtrs"])
        fp = str(row["fp"]) if pd.notna(row["fp"]) else ""
        normalized_value = float(row["value"])

        candidate = None
        if qtrs == 1:
            candidate = row.copy()
            candidate["selected_value"] = normalized_value
            candidate["value_method"] = "reported_single_period"
            candidate["prior_cumulative_qtrs"] = pd.NA
            candidate["prior_cumulative_value"] = np.nan
            candidate["prior_cumulative_adsh"] = pd.NA
        elif qtrs in {2, 3, 4} and (qtrs - 1) in latest_cumulative:
            prior_value, prior_adsh = latest_cumulative[qtrs - 1]
            candidate = row.copy()
            candidate["selected_value"] = normalized_value - prior_value
            candidate["value_method"] = f"derived_from_cumulative_qtrs_{qtrs}_minus_{qtrs - 1}"
            if str(row.get("variable")) == "total_revenue" and candidate["selected_value"] < 0:
                candidate["selected_value"] = np.nan
                candidate["value_method"] = f"{candidate['value_method']}_set_null_negative_revenue"
            candidate["prior_cumulative_qtrs"] = qtrs - 1
            candidate["prior_cumulative_value"] = prior_value
            candidate["prior_cumulative_adsh"] = prior_adsh

        if candidate is not None and (adsh not in selected or qtrs == 1):
            selected[adsh] = candidate

        if qtrs > 1 or (qtrs == 1 and fp == "Q1"):
            latest_cumulative[qtrs] = (normalized_value, adsh)

    if not selected:
        return pd.DataFrame(columns=group.columns.tolist())

    return pd.DataFrame(selected.values())


def enrich_and_order(selected: pd.DataFrame, universe: pd.DataFrame) -> pd.DataFrame:
    selected = selected.copy()
    universe_cols = [c for c in ["cik", "ticker", "firm_id", "shortname", "Sector", "Industry", "cohort"] if c in universe.columns]
    selected = selected.merge(universe[universe_cols].drop_duplicates("cik"), on="cik", how="left")
    selected["is_derived_flow"] = selected["value_method"].astype(str).str.startswith("derived_from_cumulative")
    selected["source_zip"] = selected["sec_zip"]
    selected["selected_sec_tag"] = selected["tag"]
    selected["selected_value"] = selected["selected_value"].astype(float)

    ordered_cols = [
        "adsh",
        "cik",
        "ticker",
        "firm_id",
        "shortname",
        "Sector",
        "Industry",
        "cohort",
        "variable",
        "selected_sec_tag",
        "selected_value",
        "reported_value",
        "normalized_reported_value",
        "value_sign_policy",
        "value_method",
        "is_derived_flow",
        "qtrs",
        "uom",
        "segments",
        "coreg",
        "statement",
        "priority",
        "form",
        "period",
        "period_date",
        "filed",
        "filed_date",
        "fy",
        "fp",
        "ddate",
        "ddate_period_aligned",
        "source_zip",
        "prior_cumulative_qtrs",
        "prior_cumulative_value",
        "prior_cumulative_adsh",
    ]
    ordered_cols = [col for col in ordered_cols if col in selected.columns]
    return selected[ordered_cols].sort_values(["cik", "period_date", "filed_date", "adsh", "variable"])


def validate_against_panel(provenance: pd.DataFrame) -> pd.DataFrame:
    panel_path = panel_builder.FULL_PANEL_PARQUET
    panel = pd.read_parquet(panel_path)
    variables = sorted(set(provenance["variable"]) & set(panel.columns))
    panel_unique = panel[["adsh", *variables]].drop_duplicates()
    long_panel = panel_unique.melt(id_vars=["adsh"], value_vars=variables, var_name="variable", value_name="panel_value")
    merged = provenance[["adsh", "variable", "selected_value"]].merge(long_panel, on=["adsh", "variable"], how="left")
    merged["abs_diff"] = (merged["selected_value"] - merged["panel_value"]).abs()
    review_rows = provenance[
        [
            "adsh",
            "cik",
            "ticker",
            "variable",
            "selected_sec_tag",
            "selected_value",
            "value_method",
            "form",
            "period_date",
            "filed_date",
            "source_zip",
        ]
    ].merge(long_panel, on=["adsh", "variable"], how="left")
    review_rows = review_rows[review_rows["panel_value"].isna()].copy()
    invalid_path = OUT_DIR / "invalid_prediction_timestamp_rows.csv"
    dropped_path = OUT_DIR / "dropped_duplicate_filing_rows.csv"
    accounting_controls_path = OUT_DIR / "accounting_quality_controls_applied.csv"
    invalid_adsh = set()
    if invalid_path.exists():
        invalid_adsh = set(pd.read_csv(invalid_path)["adsh"].dropna().astype(str))
    dropped_adsh = set()
    if dropped_path.exists():
        dropped_adsh = set(pd.read_csv(dropped_path)["adsh"].dropna().astype(str))
    accounting_null_pairs: set[tuple[str, str]] = set()
    if accounting_controls_path.exists():
        accounting_controls = pd.read_csv(accounting_controls_path)
        for _, row in accounting_controls.iterrows():
            adsh = str(row.get("adsh", ""))
            for variable in str(row.get("columns_set_null", "")).split(";"):
                variable = variable.strip()
                if adsh and variable:
                    accounting_null_pairs.add((adsh, variable))

    def explain_missing(row: pd.Series) -> str:
        adsh = str(row["adsh"])
        variable = str(row["variable"])
        method = str(row.get("value_method", ""))
        if adsh in invalid_adsh:
            return "selected fact belongs to an invalid timestamp row excluded from production panel"
        if adsh in dropped_adsh:
            return "selected fact belongs to a same-information-date duplicate row dropped by deterministic amendment policy"
        if (adsh, variable) in accounting_null_pairs:
            return "selected fact was intentionally nulled by source-aware accounting quality controls"
        if pd.isna(row.get("selected_value")) and "set_null_negative_revenue" in method:
            return "selected negative derived revenue was intentionally left null"
        return "not documented / requires review"

    if not review_rows.empty:
        review_rows["review_explanation"] = review_rows.apply(explain_missing, axis=1)
    else:
        review_rows["review_explanation"] = pd.Series(dtype="object")
    review_rows.to_csv(VALIDATION_REVIEW_ROWS_CSV, index=False)

    tol = 1e-9
    missing_count = int(merged["panel_value"].isna().sum())
    missing_explained = missing_count == 0 or (
        not review_rows.empty and review_rows["review_explanation"].ne("not documented / requires review").all()
    )
    missing_status = "PASS_WITH_DOCUMENTED_EXCLUSIONS" if missing_count and missing_explained else "REVIEW"
    if missing_count == 0:
        missing_status = "PASS"
    return pd.DataFrame(
        [
            {
                "check": "selected_fact_rows",
                "value": len(provenance),
                "status": "INFO",
            },
            {
                "check": "matched_panel_values",
                "value": int(merged["panel_value"].notna().sum()),
                "status": "INFO",
            },
            {
                "check": "missing_panel_value_for_selected_fact",
                "value": missing_count,
                "status": missing_status,
            },
            {
                "check": "selected_value_panel_mismatches_gt_tolerance",
                "value": int((merged["abs_diff"].fillna(0) > tol).sum()),
                "status": "REVIEW" if (merged["abs_diff"].fillna(0) > tol).any() else "PASS",
            },
        ]
    )


def write_summaries(provenance: pd.DataFrame) -> None:
    summary = (
        provenance.groupby(["variable", "statement"], dropna=False)
        .agg(
            selected_fact_rows=("adsh", "size"),
            firms=("cik", "nunique"),
            selected_tags=("selected_sec_tag", lambda s: "; ".join(sorted(set(s.dropna().astype(str))))),
            methods=("value_method", lambda s: "; ".join(sorted(set(s.dropna().astype(str))))),
            derived_flow_rows=("is_derived_flow", "sum"),
            first_period=("period_date", "min"),
            last_period=("period_date", "max"),
        )
        .reset_index()
    )
    summary.to_csv(SUMMARY_CSV, index=False)

    method_summary = (
        provenance.groupby(["variable", "selected_sec_tag", "value_method"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["variable", "rows"], ascending=[True, False])
    )
    method_summary.to_csv(METHOD_CSV, index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    universe = panel_builder.read_universe()
    concept_map = panel_builder.read_concept_map()
    long_raw = collect_long_raw(universe, concept_map)
    selected = standardize_with_provenance(long_raw)
    provenance = enrich_and_order(selected, universe)

    provenance.to_parquet(PROVENANCE_PARQUET, index=False)
    provenance.to_csv(PROVENANCE_CSV_GZ, index=False)
    write_summaries(provenance)
    validation = validate_against_panel(provenance)
    validation.to_csv(VALIDATION_CSV, index=False)

    print(f"Wrote {PROVENANCE_PARQUET.relative_to(PROJECT_ROOT)} rows={len(provenance):,}")
    print(f"Wrote {PROVENANCE_CSV_GZ.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {SUMMARY_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {METHOD_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {VALIDATION_CSV.relative_to(PROJECT_ROOT)}")
    print(validation.to_string(index=False))


if __name__ == "__main__":
    main()
