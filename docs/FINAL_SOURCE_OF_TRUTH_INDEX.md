# Final Source Of Truth Index

Last updated: 2026-05-10

Use this file to decide which project documents are authoritative during thesis writing.

Final technical acceptance checkpoint: `docs/FINAL_ACCEPTANCE_REPORT_20260512.md`.

Final documentation/dashboard consistency checkpoint: `docs/FINAL_CONSISTENCY_REVIEW_20260512.md`.

## Current Panel Metrics

These metrics describe the current rebuilt panel after the `ddate == period` selector patch, 2026-05-08 alias-collapse rebuild, 2026-05-09 SEC concept-map polish, 2026-05-09 accounting/duplicate caveat-resolution rebuild, and 2026-05-10 controlled promotion of four validated secondary production outcomes. Provenance, audits, baseline models, calibration/ranking, feature interpretation, target profiles, and descriptive analysis outputs have been rerun for the promoted target state.

Important: dashboard screenshots and the full rendered UI/project audit have been refreshed. The screenshot report marks the console row PASS and records only known benign Vega-Lite render warnings.

- Production panel rows: 31,702.
- Production panel columns: 190.
- SEC CIKs: 540.
- Ticker/display IDs: 540.
- Period range: 2009-03-31 to 2026-02-28.
- Prediction timestamp range: 2009-04-15 to 2026-03-31.
- Prediction-date policy: `prediction_date = filed_date`.

Current rebuilt target counts:

- `distress_next_4q`: 31,702 known rows; 207 positives; 0 missing.
- `failure_pressure_conservative_v2_next_4obs`: 29,805 known rows; 3,003 positives; 1,897 missing.
- `success_resilience_next_4q`: 20,152 known rows; 12,519 positives; 11,550 missing.
- `industry_relative_resilience_next_4obs`: 20,039 known rows; 8,093 positives; 11,663 missing.
- `stress_resilience_next_4obs`: 5,901 known rows; 3,707 positives; 25,801 missing.
- `recovery_next_4obs`: 11,375 known rows; 5,578 positives; 20,327 missing.
- `quality_success_cashflow_next_4obs`: 16,767 known rows; 9,852 positives; 14,935 missing.

## Target Hierarchy

- Strict legal benchmark: `distress_next_4q`.
- Main failure-factor target: `failure_pressure_conservative_v2_next_4obs`.
- Main success/resilience target: `success_resilience_next_4q`.
- Validated secondary production outcomes: `industry_relative_resilience_next_4obs`, `stress_resilience_next_4obs`, `recovery_next_4obs`, and `quality_success_cashflow_next_4obs`.
- Robustness-extension targets, not production targets: `persistent_resilience_next_6obs` and `sector_relative_improvement_next_4obs`.
- Diagnostic targets only: `failure_pressure_balance_liquidity_next_4obs`, `success_resilience_quality_v2_next_4obs`, and exploratory `deterioration_next_4obs`.

## Files To Trust

- `docs/MANUAL_HIGH_RISK_AUDIT_20260507.md` for the latest manual high-risk audit and SEC period-alignment blocker.
- `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md` for manual row/model/dashboard audit evidence and the `PCG`/`PGNPQ` duplicate-CIK finding/resolution. Its 186-column snapshot predates the 2026-05-10 validated-secondary target-label promotion; use `docs/FINAL_ACCEPTANCE_REPORT_20260512.md` for current panel width.
- `docs/STRATEGIST_HANDOFF_20260505.md` for historical strategist-facing context only; do not use it for current panel counts or current extension status.
- `reports/RUN_STATUS_FINAL.md` for production run metrics.
- `docs/FACTUAL_FREEZE_20260509.md` for the current compact factual table used to refresh package-facing docs.
- `docs/TECHNICAL_QA_RESOLUTION_20260509.md` for post-freeze technical QA cleanup: documentation references, dashboard screenshot/console triage, and manual logic audit refresh.
- `reports/data_quality/readiness_table_20260505.csv` for readiness status.
- `docs/FINAL_TARGET_HIERARCHY.md` for target roles.
- `docs/PROJECT_CHRONICLE.md` for reasoning history and decisions.
- `docs/BIBLIOGRAPHY.md` and `docs/references.bib` for citations.
- `reports/literature/literature_matrix.csv` for source-to-claim usage.
- `docs/REFERENCE_CRITICAL_EVALUATION.md` and `reports/literature/reference_critical_evaluation.csv` for source descriptions, critiques, evaluations, and unknown/access-limited flags.
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`, `reports/model_tuning/`, and `reports/model_tuning_advanced/` for controlled model tuning and advanced boosted-tree robustness passes.
- `docs/DOCUMENT_ORGANIZATION.md` for the current document map and redundant archive location.
- `reports/project_audit/` for current project/file audit CSV outputs. `reports/project_audit/FULL_PROJECT_REVIEW_20260506.md` is a historical narrative audit and should not override the 2026-05-09 factual freeze.
- `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md` for the difference between structural readiness and empirical validity.
- `docs/SEC_CONCEPT_MAPPING_AUDIT.md` and `reports/data_quality/sec_concept_mapping_summary.csv` for accounting concept-map QA.
- `docs/SEC_MAPPING_POLISH_20260509.md` for the final SEC mapping improvement pass and deliberately rejected shortcuts.
- `docs/SEC_HARMONIZATION_HARDENING_REVIEW_20260512.md`, `reports/data_quality/sec_harmonization_candidate_tag_audit.csv`, and `reports/data_quality/sec_harmonization_candidate_summary.csv` for the non-mutating review of unmapped SEC tags near thesis-critical accounting concepts. This review did not change the production panel or concept map.
- `reports/data_quality/sec_selected_fact_provenance.parquet`, `reports/data_quality/sec_selected_fact_provenance_summary.csv`, and `reports/data_quality/sec_selected_fact_panel_validation.csv` for row-level selected SEC fact provenance.
- `config/distress_event_source_provenance.csv`, `docs/DISTRESS_EVENT_DATE_PROVENANCE.md`, and `reports/data_quality/event_date_scientific_validity_summary.csv` for strict distress event-date source verification.
- `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md` and `reports/data_quality/amendment_duplicate_summary.csv` for duplicate/amendment policy evidence.
- `docs/PCG_PGNPQ_DUPLICATE_CIK_NOTE.md` for the duplicate-CIK ticker/display issue found on 2026-05-08 and its implemented alias-collapse rebuild.
- `docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md` for final caveat handling and thesis-safe wording.
- `docs/REPRODUCIBILITY_FREEZE_20260507.md` and `reports/reproducibility/freeze_manifest_20260507.csv` for historical GitHub/release freeze checksums; refresh before actual upload/commit.
- `docs/DASHBOARD_THESIS_STORYBOARD.md` and `reports/dashboard/dashboard_polish_checklist.csv` for dashboard presentation logic.
- `docs/MODEL_INTERPRETATION_STABILITY_NOTE.md` and `reports/modeling/model_interpretation_stability_summary.csv` for stable feature-group interpretation.
- `reports/project_audit/package_smoke_test_report.md` and `reports/project_audit/clean_venv_smoke_test_results.csv` for processed-panel package reproducibility checks.
- `reports/figures/dashboard/` and `reports/project_audit/dashboard_screenshot_capture.csv` for dashboard screenshot evidence.
- `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md` for final claim guardrails.
- `docs/FINAL_ACCEPTANCE_REPORT_20260512.md` for the final technical acceptance decision, current panel/target/model/dashboard status, remaining caveats, and freeze-stage next steps.
- `docs/FINAL_CONSISTENCY_REVIEW_20260512.md` for the final documentation/dashboard consistency review and stale-fact classification.
- `reports/target_lab/validated_secondary_target_promotion_audit_summary.md`, `docs/CONTROLLED_EXTENSION_DECISION_REPORT.md`, `docs/CALIBRATION_AND_RANKING_NOTE.md`, and `reports/target_lab/validation_extension_gate_summary.md` for the controlled secondary-target promotion, calibration/ranking, and validated-secondary-outcome decisions.
- `reports/target_lab/robustness_extension_target_audit_summary.md` and `reports/target_lab/robustness_extension_target_audit.csv` for reproducible invariant checks on the two robustness-extension targets.

## Literature Package Metrics

- Total verified references: 67.
- Academic journal articles: 51.
- Peer-reviewed sources including conference papers: 56.
- Sources from 2020 onward: 21.
- Verified DOI, official page, publisher page, or official report URL: 67/67.
- Unknown or access-limited notes are explicitly labeled in `reports/literature/reference_critical_evaluation.csv`.

## Files To Treat As Historical

- Earlier target-experiment folders are useful evidence but not current production status.
- Older notes that discuss whether to promote the broader target are historical. The current production broader failure-pressure target is already promoted.
- Any old reference to a 180-column, 181-column, 185-column, or 186-column production panel is historical. The current production panel has 190 columns after four validated secondary production outcomes were promoted.
- Superseded planning/review/target/universe documents now live under `docs/_redundant/`.

## Remaining Review Risk

- Manual audit on 2026-05-07 found a critical SEC selected-fact period-alignment issue: selected facts often matched the panel but could use prior-year `ddate` values inside the filing. The selector code has now been patched to require `ddate == period`, `firm_panel_v2` has been rebuilt, selected-fact provenance was regenerated, and the downstream audit/model/interpretation chain was rerun.
- Selected-fact provenance now has 700,844 selected rows, zero selected rows with `ddate != period`, zero selected-value mismatches above tolerance, and 371 documented panel-comparison exclusions explained by deterministic duplicate drops, invalid timestamp exclusions, and source-aware accounting nulls.
- Strict event-date provenance is resolved for the current package: `distress_event_dates = PASS`, 44/44 formal strict-distress rows are source-verified, and 6 near-distress rows remain context only.
- Event-review firms must not be described as legal distress cases unless source-verified and added to `config/distress_event_dates.csv`.
- AutoGluon was not installed or used in the production workflow. XGBoost and LightGBM were installed and tested as advanced boosted-tree benchmarks. The current defensible claim is controlled temporal-validation tuning/benchmarking, not exhaustive AutoML.
- Same-information-date amendment duplicates are resolved in the production builder. The current panel has 0 duplicate ticker/period/prediction groups, and 15 dropped amended rows are recorded in `reports/data_quality/dropped_duplicate_filing_rows.csv`.
- Accounting sign/outlier caveats are now reduced: non-positive `total_assets` rows are 0; negative `total_revenue` rows are 10; unresolved negative-revenue mapping rows are 0. Remaining negative revenue cases are source-reported and disclosed.
- The 2026-05-08 manual audit found one duplicate CIK ticker/display mapping: `CIK 1004980` appeared as both `PCG` and `PGNPQ`, duplicating the same SEC filings with different strict-distress labels. The 2026-05-08 rebuild now keeps one `PCG` history and preserves `PGNPQ` as event-source alias metadata.
- The 2026-05-08 manual audit also found a derived-feature cleaning-order caveat. The 2026-05-08 rebuild now cleans derived ratios before trend features and records cleanup audit files under `reports/data_quality/`.
- Dashboard screenshots have been refreshed; the screenshot capture report marks the console row PASS and records only known benign Vega-Lite render warnings.
- SEC mapping was polished on 2026-05-09 with conservative debt, receivables, R&D, and revenue fallback tags. `LiabilitiesAndStockholdersEquity` and risky `Assets - Equity` filling were deliberately not used as silent `total_liabilities` substitutes.
- GitHub packaging/version-freeze has been refreshed by the final polish script, but it should still be checked immediately before the actual upload/commit.
