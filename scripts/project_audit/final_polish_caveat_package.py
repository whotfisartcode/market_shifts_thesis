#!/usr/bin/env python3
"""Generate final thesis-polish caveat, reproducibility, and interpretation artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"
DATA_QUALITY = REPORTS / "data_quality"
MODELING = REPORTS / "modeling"
REPRO = REPORTS / "reproducibility"
DASHBOARD_REPORTS = REPORTS / "dashboard"
PROJECT_AUDIT = REPORTS / "project_audit"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def markdown_table(df: pd.DataFrame, columns: list[str] | None = None) -> str:
    if columns is None:
        columns = list(df.columns)

    def esc(v: object) -> str:
        if pd.isna(v):
            return ""
        return str(v).replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(esc(row[c]) for c in columns) + " |")
    return "\n".join(lines)


def event_verification_policy() -> pd.DataFrame:
    audit = pd.read_csv(DATA_QUALITY / "final_distress_event_date_audit.csv")

    def final_policy(row: pd.Series) -> str:
        status = str(row.get("scientific_validity_status", ""))
        action = str(row.get("strict_distress_label_action", ""))
        if status == "VERIFIED":
            return "include_as_source_verified_strict_distress"
        if status == "REVIEW_NON_STRICT" or action == "not_strict_formal_distress":
            return "exclude_from_strict_distress_keep_context_only"
        if status == "REVIEW":
            return "retain_only_with_explicit_review_caveat"
        return "not documented / requires review"

    out = audit.copy()
    out["final_policy"] = out.apply(final_policy, axis=1)
    out["thesis_wording"] = out["final_policy"].map(
        {
            "include_as_source_verified_strict_distress": "May be described as source-verified formal distress.",
            "exclude_from_strict_distress_keep_context_only": "Do not count as strict legal distress; context only.",
            "retain_only_with_explicit_review_caveat": "Retained in strict benchmark only with provenance-review caveat.",
            "not documented / requires review": "not documented / requires review",
        }
    )
    keep_cols = [
        "ticker",
        "event_date",
        "event_type",
        "event_label",
        "verification_status",
        "manual_review_status",
        "strict_distress_label_action",
        "panel_rows",
        "distress_next_4q_rows",
        "post_event_rows",
        "scientific_validity_status",
        "final_policy",
        "thesis_wording",
    ]
    return out[[c for c in keep_cols if c in out.columns]]


def duplicate_policy(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    audit = pd.read_csv(DATA_QUALITY / "amendment_duplicate_audit.csv")

    def policy(row: pd.Series) -> str:
        key_type = str(row["key_type"])
        recommendation = str(row["recommendation"])
        if key_type == "cik_period" and "legitimate_multiple_information_dates" in recommendation:
            return "keep_distinct_prediction_dates"
        if key_type == "cik_period" and recommendation == "review_no_automatic_drop":
            return "future_rebuild_resolve_same_cik_period_review_group"
        if key_type == "ticker_period_prediction":
            return "review_ticker_alias_or_same_date_amendment_do_not_drop_manually"
        if key_type == "cik_period_prediction":
            return "future_rebuild_choose_deterministic_single_row_within_same_cik_period_prediction"
        if key_type == "adsh":
            return "review_universe_or_metadata_duplication_no_financial_manual_drop"
        return "not documented / requires review"

    out = audit.copy()
    out["deterministic_policy"] = out.apply(policy, axis=1)
    out["production_panel_action"] = out["deterministic_policy"].map(
        {
            "keep_distinct_prediction_dates": "kept_as_distinct_information_dates",
            "review_ticker_alias_or_same_date_amendment_do_not_drop_manually": "resolved_in_builder_when_same_cik_period_prediction",
            "future_rebuild_choose_deterministic_single_row_within_same_cik_period_prediction": "resolved_in_builder_prefer_non_amended_same_information_date",
            "future_rebuild_resolve_same_cik_period_review_group": "resolved_in_builder_if_same_prediction_date_else_kept",
            "review_universe_or_metadata_duplication_no_financial_manual_drop": "review_metadata_only",
            "not documented / requires review": "not documented / requires review",
        }
    )
    out["future_rebuild_rule"] = out["deterministic_policy"].map(
        {
            "keep_distinct_prediction_dates": "Keep each filing/amendment if prediction_date differs; each is a different information date.",
            "review_ticker_alias_or_same_date_amendment_do_not_drop_manually": "Inspect by CIK/adsh; if same CIK+period+prediction, prefer non-amended form then earliest adsh; if different CIKs, keep as separate firms and fix ticker metadata if needed.",
            "future_rebuild_choose_deterministic_single_row_within_same_cik_period_prediction": "Within same CIK, period_date, and prediction_date, prefer non-amended form, then 10-K/10-Q over amended form, then stable lexicographic adsh.",
            "future_rebuild_resolve_same_cik_period_review_group": "If prediction_date is the same, choose one row through the same non-amended-form and accession-number rule; if prediction_date differs, keep both information dates.",
            "review_universe_or_metadata_duplication_no_financial_manual_drop": "Deduplicate universe metadata by CIK/adsh in a rebuild if rows are exact financial repeats; do not manually delete current rows.",
            "not documented / requires review": "not documented / requires review",
        }
    )

    duplicate_keys = (
        panel.groupby(["ticker", "period_date", "prediction_date"], dropna=False)
        .filter(lambda x: len(x) > 1)
        .sort_values(["ticker", "period_date", "prediction_date", "cik", "adsh"])
    )
    detail_cols = [
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
    detail_cols = [c for c in detail_cols if c in duplicate_keys.columns]
    detail = duplicate_keys[detail_cols].copy()
    return out, detail


def freeze_manifest() -> pd.DataFrame:
    path_patterns = [
        "README.md",
        "requirements.txt",
        "app/dashboard.py",
        "data/github/README.md",
        "data/github/firm_panel_v2.parquet",
        "data/github/firm_panel_v2.csv.gz",
        "data/github/firm_panel_v2_schema.csv",
        "config/sec_fsd_concept_map.csv",
        "config/fred_series_catalog.csv",
        "config/global_event_calendar_seed.csv",
        "config/distress_event_dates.csv",
        "config/model_feature_blacklist.csv",
        "config/universe_v2_draft.csv",
        "docs/CURRENT_STATUS.md",
        "docs/PROJECT_CHRONICLE.md",
        "docs/FINAL_SOURCE_OF_TRUTH_INDEX.md",
        "docs/MASTER_DATA_MODEL_TARGET_EXPLAINER.md",
        "docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md",
        "docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md",
        "docs/SEC_CONCEPT_MAPPING_AUDIT.md",
        "docs/SEC_MAPPING_POLISH_20260509.md",
        "docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md",
        "docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md",
        "docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md",
        "docs/REPRODUCIBILITY_FREEZE_20260507.md",
        "docs/DASHBOARD_THESIS_STORYBOARD.md",
        "docs/MODEL_INTERPRETATION_STABILITY_NOTE.md",
        "reports/modeling/panel_v2_distress_next_4q_model_metrics.csv",
        "reports/modeling/panel_v2_failure_pressure_conservative_v2_next_4obs_model_metrics.csv",
        "reports/modeling/panel_v2_success_resilience_next_4q_model_metrics.csv",
        "reports/modeling/final_feature_group_contribution_table.csv",
        "reports/modeling/final_model_feature_interpretation_table.csv",
        "reports/modeling/model_interpretation_stability_summary.csv",
        "reports/RUN_STATUS_FINAL.md",
        "reports/model_tuning/baseline_vs_tuned_comparison.csv",
        "reports/model_tuning_advanced/advanced_vs_existing_comparison.csv",
        "reports/data_quality/p0_audit_status.csv",
        "reports/data_quality/sec_concept_mapping_summary.csv",
        "reports/data_quality/sec_selected_fact_provenance.parquet",
        "reports/data_quality/sec_selected_fact_provenance_summary.csv",
        "reports/data_quality/sec_selected_fact_panel_validation.csv",
        "reports/data_quality/final_distress_event_date_audit.csv",
        "reports/data_quality/distress_event_final_policy.csv",
        "reports/data_quality/amendment_duplicate_summary.csv",
        "reports/data_quality/duplicate_amendment_deterministic_policy.csv",
        "reports/dashboard/dashboard_polish_checklist.csv",
        "reports/project_audit/dashboard_screenshot_capture.csv",
        "reports/figures/dashboard/overview.png",
        "reports/figures/dashboard/data_coverage.png",
        "reports/figures/dashboard/models_distress.png",
        "reports/figures/dashboard/models_failure_pressure.png",
        "reports/figures/dashboard/models_success_resilience.png",
        "reports/figures/dashboard/target_lab_factor_groups.png",
        "reports/figures/dashboard/firm_explorer.png",
        "reports/figures/dashboard/macro_compare_training_baseline.png",
        "reports/figures/dashboard/artifact_notes.png",
        "reports/documentation/master_column_dictionary.csv",
    ]
    rows = []
    for rel in path_patterns:
        path = ROOT / rel
        if not path.exists():
            rows.append({"path": rel, "exists": False, "size_bytes": None, "sha256": None, "modified_utc": None})
            continue
        stat = path.stat()
        rows.append(
            {
                "path": rel,
                "exists": True,
                "size_bytes": stat.st_size,
                "sha256": sha256_file(path),
                "modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def github_release_file_list(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in manifest.iterrows():
        path = str(row["path"])
        if path.startswith("data/github/"):
            destination = path
            include = True
            reason = "GitHub-ready panel/schema package."
        elif path.startswith("app/") or path in {"README.md", "requirements.txt"}:
            destination = path
            include = True
            reason = "Required to run dashboard/reproduce artifact."
        elif path.startswith("docs/") or path.startswith("reports/"):
            destination = path
            include = True
            reason = "Thesis evidence/documentation artifact."
        elif path.startswith("config/"):
            destination = path
            include = True
            reason = "Rebuild configuration and source-of-truth input definitions."
        else:
            destination = path
            include = False
            reason = "Not part of current release package."
        rows.append({"path": path, "include_in_github_release": include, "destination": destination, "reason": reason})
    rows.append(
        {
            "path": "data/raw/sec_fsd_zips/",
            "include_in_github_release": False,
            "destination": "external SEC download; not committed",
            "reason": "Large raw SEC archives; keep out of GitHub and document download/rebuild instructions.",
        }
    )
    return pd.DataFrame(rows)


def interpretation_stability() -> tuple[pd.DataFrame, pd.DataFrame]:
    groups = pd.read_csv(MODELING / "panel_v2_feature_contribution_economic_groups.csv")
    top_groups = (
        groups.sort_values(["target", "model", "importance_share_ex_missingness"], ascending=[True, True, False])
        .groupby(["target", "model"], as_index=False)
        .head(5)
        .copy()
    )
    pivot = (
        groups.pivot_table(
            index=["target", "feature_group"],
            columns="model",
            values="importance_share_ex_missingness",
            aggfunc="sum",
        )
        .reset_index()
    )
    model_cols = [c for c in pivot.columns if c not in {"target", "feature_group"}]
    pivot["mean_share_across_models"] = pivot[model_cols].mean(axis=1, skipna=True)
    pivot["min_share_across_models"] = pivot[model_cols].min(axis=1, skipna=True)
    pivot["max_share_across_models"] = pivot[model_cols].max(axis=1, skipna=True)
    pivot["interpretation_stability"] = pd.cut(
        pivot["mean_share_across_models"],
        bins=[-0.001, 0.02, 0.10, 1.0],
        labels=["low_or_contextual", "moderate", "dominant"],
    )
    pivot = pivot.sort_values(["target", "mean_share_across_models"], ascending=[True, False])
    return top_groups, pivot


def dashboard_checklist() -> pd.DataFrame:
    rows = [
        ("Overview outcome composition", "implemented", "Use for thesis result screenshot; explains where strict distress, pressure, success, and ordinary observations fit."),
        ("Target coverage by year", "implemented", "Use to explain why labels have different denominators and why null targets are unknown."),
        ("Firm metrics selector", "implemented", "Use financial fields only; targets are separated into target timeline."),
        ("Macro comparison standardization", "implemented", "Default training-period baseline; caption explains z-score baseline."),
        ("Target timeline separated from firm metrics", "implemented", "Prevents target labels from being mixed with raw financial metrics."),
        ("Model metrics and top features", "implemented", "Use with caveat that feature importance is association, not causality."),
        ("Factor-group view", "implemented", "Preferred for thesis interpretation over isolated single features."),
        (
            "Artifact caveat panel",
            "implemented_with_caveats",
            "Includes explicit caveat controls and source-of-truth pointers; strict event-date provenance remains REVIEW.",
        ),
        ("Final screenshots", "implemented", "Screenshots already saved under reports/figures/dashboard/."),
    ]
    return pd.DataFrame(rows, columns=["item", "status", "thesis_use"])


def write_docs(
    event_policy: pd.DataFrame,
    duplicate_policy_df: pd.DataFrame,
    manifest: pd.DataFrame,
    stability: pd.DataFrame,
    dashboard: pd.DataFrame,
) -> None:
    verified = int((event_policy["final_policy"] == "include_as_source_verified_strict_distress").sum())
    review = int((event_policy["final_policy"] == "retain_only_with_explicit_review_caveat").sum())
    non_strict = int((event_policy["final_policy"] == "exclude_from_strict_distress_keep_context_only").sum())

    caveat_doc = f"""# Final Caveat Resolution Register

Updated: 2026-05-07

This file records how the remaining thesis caveats are handled. It is a control document: it does not silently change the production panel.

## Resolution Summary

| Caveat | Current action | Thesis-safe position |
| --- | --- | --- |
| Distress event-date provenance | {verified} source-verified strict rows; {review} strict rows retained only with explicit REVIEW caveat; {non_strict} near-distress/context rows excluded from strict distress. | Strict legal distress is a rare-event benchmark with disclosed provenance limitations. |
| SEC concept mapping | Row-level selected-fact provenance sidecar created under `reports/data_quality/sec_selected_fact_provenance.*`. | Accounting values are auditable to selected SEC tags and qtrs methods; not perfect taxonomy harmonization. |
| Duplicate/amended filings | Same-information-date duplicates are resolved deterministically in the build pipeline; later amended filings remain as distinct information dates. | Duplicate/amendment handling is disclosed and audited; no manual parquet editing is used. |
| Reproducibility/version freeze | Checksum manifest and GitHub release list created under `reports/reproducibility/`. | Final upload should use the frozen artifacts and exclude raw SEC ZIPs. |
| Dashboard presentation | Storyboard/checklist created and screenshots already exist. | Dashboard is a historical decision-support artifact, not a live oracle. |
| Model interpretation | Stability tables created for economic feature groups. | Interpret feature groups and associations, not causal single-feature claims. |
| Writing discipline | Safe/unsafe claims remain controlling. | No overclaiming of AutoML, causality, perfect SEC mapping, or full legal-event verification. |

## Distress Event Policy Counts

{markdown_table(event_policy["final_policy"].value_counts().rename_axis("final_policy").reset_index(name="rows"))}

## Duplicate/Amendment Policy Counts

{markdown_table(duplicate_policy_df["deterministic_policy"].value_counts().rename_axis("deterministic_policy").reset_index(name="rows"))}

## Reproducibility Manifest Status

{markdown_table(manifest["exists"].value_counts().rename_axis("exists").reset_index(name="files"))}

## Model Interpretation Stability

Use `reports/modeling/model_interpretation_stability_summary.csv` and `reports/modeling/model_interpretation_top_groups_by_target_model.csv`.

Top average feature-group shares:

{markdown_table(stability.head(15), ["target", "feature_group", "mean_share_across_models", "interpretation_stability"])}

## Dashboard Storyboard Status

{markdown_table(dashboard)}
"""
    (DOCS / "FINAL_CAVEAT_RESOLUTION_REGISTER.md").write_text(caveat_doc)

    repro_doc = f"""# Reproducibility Freeze 2026-05-07

This freeze records the core files that should be uploaded or referenced for the final thesis artifact.

## Main Package Files

- `data/github/firm_panel_v2.parquet`
- `data/github/firm_panel_v2.csv.gz`
- `data/github/firm_panel_v2_schema.csv`
- `app/dashboard.py`
- `requirements.txt`
- `README.md`
- current source-of-truth docs and final reports listed in `reports/reproducibility/freeze_manifest_20260507.csv`

## Raw Data Policy

Raw SEC ZIP files are not included in GitHub because they are large. They stay local under `data/raw/sec_fsd_zips/` or are redownloaded from SEC. FRED raw series stay local or can be regenerated from the FRED catalog.

## Smoke Commands

```bash
python3 scripts/project_audit/clean_venv_smoke_check.py
python3 scripts/project_audit/final_scientific_validity_qa.py
python3 -m streamlit run app/dashboard.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
```

## Manifest

The checksum manifest is:

```text
reports/reproducibility/freeze_manifest_20260507.csv
```

All listed files should have `exists = True` before final GitHub upload.
"""
    (DOCS / "REPRODUCIBILITY_FREEZE_20260507.md").write_text(repro_doc)

    dashboard_doc = f"""# Dashboard Thesis Storyboard

Updated: 2026-05-07

The dashboard should tell the thesis story in this order:

1. Dataset and target composition: what is in the panel and how strict distress, broader failure pressure, success/resilience, and ordinary observations differ.
2. Data coverage and missingness: why nulls are preserved and how feature families differ.
3. Models: strict distress as rare-event benchmark, broader failure pressure as main failure-factor target, success/resilience as counterpart.
4. Target lab and factor groups: feature groups are the preferred economic interpretation layer.
5. Firm explorer: firm fundamentals, ratios, deterioration, macro context, and target timeline are separated so scales and labels are not confused.
6. Artifact notes: scope, reproducibility, caveats, and safe/unsafe claims.

## Checklist

{markdown_table(dashboard)}
"""
    (DOCS / "DASHBOARD_THESIS_STORYBOARD.md").write_text(dashboard_doc)

    model_doc = f"""# Model Interpretation Stability Note

Updated: 2026-05-07

This note supports thesis writing by comparing feature-group importance across saved production model outputs. It does not add new model results.

The thesis should emphasize stable economic groups, not isolated single features. Missingness indicators are excluded from economic shares.

## Stability Summary

{markdown_table(stability.head(30), ["target", "feature_group", "mean_share_across_models", "min_share_across_models", "max_share_across_models", "interpretation_stability"])}

## Interpretation Rule

Use dominant or moderate groups as thesis evidence of association. Do not claim causality. Do not interpret missingness indicators as economic mechanisms.
"""
    (DOCS / "MODEL_INTERPRETATION_STABILITY_NOTE.md").write_text(model_doc)


def main() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    DASHBOARD_REPORTS.mkdir(parents=True, exist_ok=True)
    panel = pd.read_parquet(ROOT / "data/processed/panel_v2/firm_panel_v2.parquet")

    event_policy = event_verification_policy()
    write_csv(DATA_QUALITY / "distress_event_final_policy.csv", event_policy)

    duplicate_policy_df, duplicate_detail = duplicate_policy(panel)
    write_csv(DATA_QUALITY / "duplicate_amendment_deterministic_policy.csv", duplicate_policy_df)
    write_csv(DATA_QUALITY / "duplicate_ticker_period_prediction_detail.csv", duplicate_detail)

    manifest = freeze_manifest()
    write_csv(REPRO / "freeze_manifest_20260507.csv", manifest)
    release_list = github_release_file_list(manifest)
    write_csv(REPRO / "github_release_file_list_20260507.csv", release_list)

    top_groups, stability = interpretation_stability()
    write_csv(MODELING / "model_interpretation_top_groups_by_target_model.csv", top_groups)
    write_csv(MODELING / "model_interpretation_stability_summary.csv", stability)

    dashboard = dashboard_checklist()
    write_csv(DASHBOARD_REPORTS / "dashboard_polish_checklist.csv", dashboard)

    write_docs(event_policy, duplicate_policy_df, manifest, stability, dashboard)

    summary = pd.DataFrame(
        [
            {"area": "distress_event_policy", "artifact": "reports/data_quality/distress_event_final_policy.csv", "status": "created"},
            {"area": "duplicate_policy", "artifact": "reports/data_quality/duplicate_amendment_deterministic_policy.csv", "status": "created"},
            {"area": "reproducibility_freeze", "artifact": "reports/reproducibility/freeze_manifest_20260507.csv", "status": "created"},
            {"area": "dashboard_storyboard", "artifact": "docs/DASHBOARD_THESIS_STORYBOARD.md", "status": "created"},
            {"area": "model_interpretation", "artifact": "docs/MODEL_INTERPRETATION_STABILITY_NOTE.md", "status": "created"},
            {"area": "caveat_register", "artifact": "docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md", "status": "created"},
        ]
    )
    write_csv(PROJECT_AUDIT / "final_polish_caveat_package_summary.csv", summary)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
