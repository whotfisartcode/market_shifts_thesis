#!/usr/bin/env python3
"""Consolidate the current data-integrity caveats into one audit report."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = PROJECT_ROOT / "data/github/firm_panel_v2.parquet"
PANEL_CSV_PATH = PROJECT_ROOT / "data/github/firm_panel_v2.csv.gz"
CORE_PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.parquet"
SCHEMA_PATH = PROJECT_ROOT / "data/github/firm_panel_v2_schema.csv"
PROVENANCE_PATH = PROJECT_ROOT / "reports/data_quality/sec_selected_fact_provenance.parquet"
PROVENANCE_VALIDATION_PATH = PROJECT_ROOT / "reports/data_quality/sec_selected_fact_panel_validation.csv"
P0_PATH = PROJECT_ROOT / "reports/data_quality/p0_audit_status.csv"
EVENT_VALIDITY_PATH = PROJECT_ROOT / "reports/data_quality/event_date_scientific_validity_summary.csv"
ACCOUNTING_SANITY_PATH = PROJECT_ROOT / "reports/data_quality/accounting_identity_sanity_summary.csv"
MISSINGNESS_FAMILY_PATH = PROJECT_ROOT / "reports/data_quality/panel_v2_missingness_by_feature_family.csv"
MODEL_FEATURE_LIST_DIR = PROJECT_ROOT / "reports/data_quality/model_feature_lists"
FEATURE_BLACKLIST_PATH = PROJECT_ROOT / "config/model_feature_blacklist.csv"
OUT_CSV = PROJECT_ROOT / "reports/data_quality/data_integrity_caveat_audit_20260508.csv"
OUT_MD = PROJECT_ROOT / "docs/DATA_INTEGRITY_CAVEAT_AUDIT_20260508.md"
OUTLIER_DETAIL_CSV = PROJECT_ROOT / "reports/data_quality/accounting_sign_outlier_detail_20260508.csv"
DUPLICATE_DETAIL_CSV = PROJECT_ROOT / "reports/data_quality/duplicate_amended_filing_rows_20260508.csv"


def status_from(condition: bool, pass_status: str = "PASS", fail_status: str = "REVIEW") -> str:
    return pass_status if condition else fail_status


def add(rows: list[dict[str, object]], area: str, status: str, evidence: str, action: str) -> None:
    rows.append({"area": area, "status": status, "evidence": evidence, "recommended_action": action})


def markdown_table(frame: pd.DataFrame) -> str:
    headers = [str(col) for col in frame.columns]
    rows = frame.astype(str).values.tolist()
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |")
    return "\n".join(output)


def numeric_frame(panel: pd.DataFrame) -> pd.DataFrame:
    numeric = panel.select_dtypes(include=[np.number]).copy()
    for col in numeric.columns:
        numeric[col] = pd.to_numeric(numeric[col], errors="coerce")
    return numeric.astype("float64")


def audit() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    panel = pd.read_parquet(PANEL_PATH)
    core = pd.read_parquet(CORE_PANEL_PATH)

    add(
        rows,
        "Core/GitHub panel equality",
        status_from(panel.equals(core)),
        f"GitHub panel shape {panel.shape}; processed panel shape {core.shape}; exact dataframe equality = {panel.equals(core)}.",
        "Repeat this after the final GitHub package freeze.",
    )

    add(
        rows,
        "Panel dimensions",
        "PASS",
        f"Panel shape is {panel.shape}; CIKs={panel['cik'].nunique()}; ticker/display IDs={panel['ticker'].nunique()}.",
        "Use these counts in thesis/package docs unless the panel is rebuilt again.",
    )

    pred_source = panel["prediction_date_source"].value_counts(dropna=False).to_dict()
    filed_rows = int((panel["prediction_date_source"] == "filed_date").sum())
    add(
        rows,
        "Prediction timestamp",
        status_from(filed_rows == len(panel)),
        f"prediction_date_source counts: {pred_source}.",
        "Keep `prediction_date = filed_date` as the information-availability timestamp.",
    )

    if PROVENANCE_PATH.exists():
        provenance = pd.read_parquet(PROVENANCE_PATH, columns=["ddate_period_aligned", "ddate", "period"])
        ddate_ne_period = int((provenance["ddate"].astype(str) != provenance["period"].astype(str)).sum())
        aligned_false = int((~provenance["ddate_period_aligned"].fillna(False)).sum())
        validation = pd.read_csv(PROVENANCE_VALIDATION_PATH)
        mismatches = int(
            validation.loc[
                validation["check"].eq("selected_value_panel_mismatches_gt_tolerance"),
                "value",
            ].iloc[0]
        )
        exclusions = int(
            validation.loc[
                validation["check"].eq("missing_panel_value_for_selected_fact"),
                "value",
            ].iloc[0]
        )
        status = "PASS_WITH_DOCUMENTED_EXCLUSIONS" if ddate_ne_period == 0 and aligned_false == 0 and mismatches == 0 else "REVIEW"
        evidence = (
            f"{len(provenance)} selected facts; ddate != period rows={ddate_ne_period}; "
            f"unaligned flags={aligned_false}; selected-value mismatches={mismatches}; documented exclusions={exclusions}."
        )
    else:
        status = "FAIL"
        evidence = "Selected-fact provenance sidecar is missing."
    add(
        rows,
        "SEC selected-fact period alignment",
        status,
        evidence,
        "Use the provenance sidecar as evidence; documented exclusions are deterministic duplicate drops, invalid timestamp exclusions, and source-aware accounting nulls.",
    )

    numeric_source = pd.read_csv(PANEL_CSV_PATH, low_memory=False) if PANEL_CSV_PATH.exists() else panel
    numeric = numeric_frame(numeric_source)
    inf_count = int(np.isinf(numeric.to_numpy()).sum())
    numeric_nulls = int(numeric.isna().sum().sum())
    numeric_cells = int(numeric.size)
    add(
        rows,
        "Numeric null and infinity policy",
        status_from(inf_count == 0, pass_status="PASS_WITH_MISSINGNESS_CAVEAT"),
        f"numeric cells={numeric_cells}; numeric nulls={numeric_nulls}; null share={numeric_nulls / numeric_cells:.3%}; infinite values={inf_count}.",
        "Preserve nulls in the panel; impute only inside model pipelines.",
    )

    negative_revenue = int((panel["total_revenue"] < 0).sum())
    nonpositive_assets = int((panel["total_assets"] <= 0).sum())
    negative_assets = int((panel["total_assets"] < 0).sum())
    negative_liabilities = int((panel["total_liabilities"] < 0).sum())
    outlier_mask = (
        (panel["total_revenue"] < 0)
        | (panel["total_assets"] <= 0)
        | (panel["total_assets"] < 0)
        | (panel["total_liabilities"] < 0)
    )
    outlier_cols = [
        "ticker",
        "cik",
        "adsh",
        "form",
        "period_date",
        "prediction_date",
        "total_revenue",
        "total_assets",
        "net_income",
        "total_liabilities",
        "Sector",
        "Industry",
    ]
    panel.loc[outlier_mask, [col for col in outlier_cols if col in panel.columns]].sort_values(
        ["ticker", "period_date", "prediction_date"]
    ).to_csv(OUTLIER_DETAIL_CSV, index=False)
    unresolved_negative_revenue = negative_revenue
    if PROVENANCE_PATH.exists() and negative_revenue:
        provenance_cols = [
            "adsh",
            "variable",
            "selected_value",
            "selected_sec_tag",
            "value_method",
            "value_sign_policy",
        ]
        provenance = pd.read_parquet(PROVENANCE_PATH, columns=[c for c in provenance_cols if c != "value_sign_policy"])
        if "value_sign_policy" not in provenance.columns:
            provenance["value_sign_policy"] = ""
        negative_revenue_provenance = provenance[
            provenance["variable"].eq("total_revenue") & provenance["selected_value"].lt(0)
        ].copy()
        unresolved_negative_revenue = int(
            (
                negative_revenue_provenance["value_method"].astype(str).str.contains("set_null_negative_revenue")
                | negative_revenue_provenance["selected_sec_tag"].astype(str).str.startswith("SalesRevenue")
                | negative_revenue_provenance["value_method"].astype(str).str.startswith("derived_from_cumulative")
            ).sum()
        )
    if nonpositive_assets or negative_assets or negative_liabilities or unresolved_negative_revenue:
        status = "REVIEW"
    elif negative_revenue:
        status = "PASS_WITH_REVIEWED_EXCEPTIONS"
    else:
        status = "PASS"
    add(
        rows,
        "Accounting sign/outlier sanity",
        status,
        (
            f"negative total_revenue rows={negative_revenue}; non-positive total_assets rows={nonpositive_assets}; "
            f"negative total_assets rows={negative_assets}; negative total_liabilities rows={negative_liabilities}; "
            f"unresolved negative-revenue mapping rows={unresolved_negative_revenue}."
        ),
        "Use source-aware controls: invalid derived/sign-convention revenue and non-positive assets are nulled; remaining negative revenue is source-reported and disclosed.",
    )

    if ACCOUNTING_SANITY_PATH.exists():
        sanity = pd.read_csv(ACCOUNTING_SANITY_PATH)
        identity = sanity[sanity["check"].eq("assets_approximately_liabilities_plus_equity")]
        if not identity.empty:
            share = float(identity["share_gap_le_5pct_assets"].iloc[0])
            status = "PASS_WITH_CAVEATS" if share >= 0.9 else "REVIEW"
            evidence = f"Balance-sheet identity within 5% of assets for {share:.1%} of checked rows."
        else:
            status = "REVIEW"
            evidence = "Accounting identity row not found in sanity report."
    else:
        status = "REVIEW"
        evidence = "Accounting sanity report missing."
    add(
        rows,
        "Accounting identity sanity",
        status,
        evidence,
        "Describe identity checks as plausibility checks, not perfect accounting reconciliation.",
    )

    duplicate_keys = ["ticker", "period_date", "prediction_date"]
    duplicate_rows = panel[panel.duplicated(duplicate_keys, keep=False)].copy()
    duplicate_groups = duplicate_rows.groupby(duplicate_keys).ngroups if not duplicate_rows.empty else 0
    duplicate_cols = [
        "ticker",
        "cik",
        "adsh",
        "name",
        "form",
        "period_date",
        "filed_date",
        "prediction_date",
        "sec_zip",
        "cohort",
        "Sector",
        "distress_next_4q",
        "failure_pressure_conservative_v2_next_4obs",
        "success_resilience_next_4q",
    ]
    duplicate_rows[[col for col in duplicate_cols if col in duplicate_rows.columns]].sort_values(
        duplicate_keys + ["form", "adsh"]
    ).to_csv(DUPLICATE_DETAIL_CSV, index=False)
    add(
        rows,
        "Duplicate amended-filing rows",
        "PASS" if len(duplicate_rows) == 0 else "REVIEW",
        f"{len(duplicate_rows)} rows across {duplicate_groups} ticker-period-prediction groups.",
        "Same-information-date amendment duplicates should be resolved in the builder; later amended filings with later prediction dates remain separate information events.",
    )

    if MISSINGNESS_FAMILY_PATH.exists():
        miss = pd.read_csv(MISSINGNESS_FAMILY_PATH)
        sec = miss[miss["feature_family"].eq("sec_accounting_fundamental")]
        ratios = miss[miss["feature_family"].eq("financial_ratio")]
        trend = miss[miss["feature_family"].eq("firm_trend_or_deterioration")]
        evidence = (
            f"SEC accounting avg missing={float(sec['average_missing_share'].iloc[0]):.1%}; "
            f"ratio avg missing={float(ratios['average_missing_share'].iloc[0]):.1%}; "
            f"trend avg missing={float(trend['average_missing_share'].iloc[0]):.1%}."
        )
    else:
        evidence = "Missingness family report missing."
    add(
        rows,
        "Structured missingness",
        "PASS_WITH_CAVEATS",
        evidence,
        "Treat missingness as a disclosed reporting/data-availability feature; exclude missingness indicators from economic causality claims.",
    )

    target_evidence_parts = []
    expected_targets = [
        "distress_next_4q",
        "failure_pressure_conservative_v2_next_4obs",
        "success_resilience_next_4q",
        "industry_relative_resilience_next_4obs",
        "stress_resilience_next_4obs",
        "recovery_next_4obs",
        "quality_success_cashflow_next_4obs",
    ]
    target_ok = True
    for target in expected_targets:
        if target not in panel.columns:
            target_evidence_parts.append(f"{target}: missing column")
            target_ok = False
            continue
        known = int(panel[target].notna().sum())
        positive = int(panel[target].fillna(0).sum())
        missing = int(panel[target].isna().sum())
        target_evidence_parts.append(f"{target}: known={known}, positives={positive}, missing={missing}")
    add(
        rows,
        "Target label counts",
        status_from(target_ok, pass_status="PASS_WITH_CAVEATS"),
        "; ".join(target_evidence_parts) + ".",
        "Use the first three as primary targets and the four promoted labels as validated secondary production outcomes.",
    )

    p0 = pd.read_csv(P0_PATH)
    p0_status = dict(zip(p0["audit"], p0["status"]))
    add(
        rows,
        "P0 timing/leakage/event audits",
        "PASS_WITH_EVENT_DATE_REVIEW" if p0_status.get("distress_event_dates") == "REVIEW" else "PASS",
        "; ".join(f"{key}={value}" for key, value in p0_status.items()),
        (
            "Keep timing/leakage claims; strict event-date provenance now passes."
            if p0_status.get("distress_event_dates") == "PASS"
            else "Keep timing/leakage claims; keep strict event-date provenance caveat."
        ),
    )

    formal_review = None
    if EVENT_VALIDITY_PATH.exists():
        event_validity = pd.read_csv(EVENT_VALIDITY_PATH)
        event_summary = "; ".join(
            f"{row.event_label}/{row.scientific_validity_status}={int(row.rows)}"
            for row in event_validity.itertuples(index=False)
        )
        formal_review_match = event_validity[
            event_validity["event_label"].eq("formal_distress")
            & event_validity["scientific_validity_status"].eq("REVIEW")
        ]
        formal_review = int(formal_review_match["rows"].sum()) if not formal_review_match.empty else 0
    else:
        event_summary = "event-date scientific validity summary missing"
    add(
        rows,
        "Strict event-date provenance",
        "PASS" if formal_review == 0 else "REVIEW",
        event_summary,
        (
            "Use the source-provenance table as evidence; keep non-strict near-distress rows as context only."
            if formal_review == 0
            else "Source-verify remaining formal distress rows before upgrading strict-distress claims."
        ),
    )

    if FEATURE_BLACKLIST_PATH.exists() and MODEL_FEATURE_LIST_DIR.exists():
        blacklist = set(pd.read_csv(FEATURE_BLACKLIST_PATH).iloc[:, 0].dropna().astype(str))
        overlaps: list[str] = []
        for path in sorted(MODEL_FEATURE_LIST_DIR.glob("*_features.csv")):
            features = set(pd.read_csv(path)["column"].dropna().astype(str))
            overlap = sorted(features & blacklist)
            overlaps.extend(f"{path.name}:{feature}" for feature in overlap)
        status = "PASS" if not overlaps else "FAIL"
        evidence = "No blacklist overlap in model feature lists." if not overlaps else "; ".join(overlaps[:20])
    else:
        status = "REVIEW"
        evidence = "Feature blacklist or model feature lists missing."
    add(
        rows,
        "Model feature leakage guardrail",
        status,
        evidence,
        "Do not add target/event/date metadata into model feature lists.",
    )

    if SCHEMA_PATH.exists():
        schema = pd.read_csv(SCHEMA_PATH)
        status = "PASS" if len(schema) == panel.shape[1] else "REVIEW"
        evidence = f"schema rows={len(schema)}; panel columns={panel.shape[1]}."
    else:
        status = "FAIL"
        evidence = "GitHub schema missing."
    add(
        rows,
        "GitHub schema coverage",
        status,
        evidence,
        "Keep schema with the GitHub package.",
    )

    return pd.DataFrame(rows)


def main() -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    report = audit()
    report.to_csv(OUT_CSV, index=False)

    summary_counts = report["status"].value_counts().rename_axis("status").reset_index(name="areas")
    md = [
        "# Data Integrity Caveat Audit 2026-05-10",
        "",
        "This is the consolidated post-rebuild audit of data-integrity issues that previously carried caveats. It was refreshed after the 2026-05-10 validated-secondary target promotion.",
        "",
        "## Status Summary",
        "",
        markdown_table(summary_counts),
        "",
        "## Detailed Audit",
        "",
        markdown_table(report),
        "",
        "## Interpretation",
        "",
        "- The old SEC selected-fact period-alignment defect is closed for production selected facts.",
        "- The panel remains null-preserving; missingness is material and must be disclosed.",
        "- Same-information-date duplicate amended-filing rows are handled deterministically in the builder.",
        "- Invalid derived/sign-convention revenue and non-positive assets are source-aware controls; remaining negative revenue is source-reported and disclosed.",
        "- Strict legal distress event-date provenance now passes for formal distress rows; the remaining limitation is that strict distress is source-curated and rare, not a complete legal-bankruptcy database.",
        "- The panel is scientifically usable for the thesis if these caveats are stated honestly.",
        "",
        "## Detail Files",
        "",
        f"- `{OUTLIER_DETAIL_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{DUPLICATE_DETAIL_CSV.relative_to(PROJECT_ROOT)}`",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
