# Run Status

Last updated: 2026-05-12

Current status note: this run-status file has been refreshed for the final acceptance state. The final technical checkpoint is `docs/FINAL_ACCEPTANCE_REPORT_20260512.md`.

## 2026-05-09 SEC Mapping And Caveat-Resolution Status

The SEC concept map has been conservatively improved, same-information-date duplicates are resolved in the builder, and source-aware accounting outlier controls have been applied.

Implemented mapping changes:

- expanded long-term debt coverage with `LongTermDebtNoncurrent` and `LongTermDebtAndCapitalLeaseObligations`;
- expanded short-term/current debt coverage with `DebtCurrent`, `LongTermDebtCurrent`, and `LongTermDebtAndCapitalLeaseObligationsCurrent`, while retaining `ShortTermBorrowings` as a fallback;
- added `LiabilitiesNoncurrent` as a separate `noncurrent_liabilities` accounting field;
- expanded receivables with `ReceivablesNetCurrent` and `AccountsReceivableNet`;
- expanded R&D with `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost`;
- added `RevenueFromContractWithCustomerIncludingAssessedTax` as a low-priority revenue fallback.

Rejected mapping shortcuts:

- `LiabilitiesAndStockholdersEquity` was not mapped to `total_liabilities`;
- `total_liabilities` was not silently filled from `Assets - Equity`;
- component inventory/capex/revenue tags were not blindly mapped into total fields.

Current production panel:

- rows: 31,702;
- columns: 190;
- SEC CIKs: 540;
- ticker/display IDs: 540;
- processed and GitHub panel copies match exactly.

Current target counts:

- `distress_next_4q`: 31,702 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,805 known rows, 3,003 positives, 1,897 missing;
- `success_resilience_next_4q`: 20,152 known rows, 12,519 positives, 11,550 missing.
- `industry_relative_resilience_next_4obs`: 20,039 known rows, 8,093 positives, 11,663 missing;
- `stress_resilience_next_4obs`: 5,901 known rows, 3,707 positives, 25,801 missing;
- `recovery_next_4obs`: 11,375 known rows, 5,578 positives, 20,327 missing;
- `quality_success_cashflow_next_4obs`: 16,767 known rows, 9,852 positives, 14,935 missing.

Current provenance/audit status:

- P0 audits: all PASS;
- selected SEC facts: 700,844;
- selected facts with `ddate != period`: 0;
- selected-value mismatches above tolerance: 0;
- documented panel-comparison exclusions: 371, explained by deterministic duplicate drops, invalid timestamp exclusions, and accounting-quality nulls;
- numeric infinities: 0.

Accounting/duplicate caveat status:

- same-information-date duplicate amended rows dropped deterministically: 15;
- current duplicate ticker/period/prediction groups: 0;
- non-positive `total_assets` rows: 0;
- negative `total_revenue` rows: 10;
- unresolved negative-revenue mapping rows: 0.

Post-polish model metrics:

- `distress_next_4q`: baseline gradient boosting test PR-AUC 0.104, F1 0.182; validation-selected ExtraTrees test PR-AUC 0.143, F1 0.237; advanced XGBoost test PR-AUC 0.142, F1 0.201.
- `failure_pressure_conservative_v2_next_4obs`: baseline random forest test PR-AUC 0.758, F1 0.725; validation-selected HistGradientBoosting test PR-AUC 0.748, F1 0.685; advanced LightGBM test PR-AUC 0.739, F1 0.718.
- `success_resilience_next_4q`: baseline random forest test PR-AUC 0.975, F1 0.938; validation-selected random forest test PR-AUC 0.974, F1 0.943; advanced XGBoost test PR-AUC 0.974, F1 0.935.
- `industry_relative_resilience_next_4obs`: baseline gradient boosting test PR-AUC 0.855, F1 0.787; validation-calibrated gate PR-AUC 0.844.
- `stress_resilience_next_4obs`: baseline random forest test PR-AUC 0.974, F1 0.937; validation-calibrated gate PR-AUC 0.969.
- `recovery_next_4obs`: baseline random forest test PR-AUC 0.977, F1 0.915; validation-calibrated gate PR-AUC 0.968.
- `quality_success_cashflow_next_4obs`: baseline gradient boosting test PR-AUC 0.953, F1 0.920; validation-calibrated gate PR-AUC 0.949.

Interpretation:

- mapping quality and debt-field coverage are materially improved;
- the headline target hierarchy keeps the first three targets primary and adds four validated secondary production outcomes;
- the baseline random forest remains the main interpretable model for failure pressure and success/resilience;
- strict legal distress remains a rare-event benchmark.

Dashboard artifact after mapping polish:

- financial field coverage: 63/63;
- macro/regime/event chartable coverage: 68/68;
- screenshots refreshed under `reports/figures/dashboard/`;
- screenshot console row is PASS; only known benign Vega-Lite render warnings are recorded.

## 2026-05-08 Alias-Collapse Rebuild Status

The `PCG`/`PGNPQ` duplicate-CIK issue and the derived-feature cleaning-order issue have now been materialized into the production panel exports.

Step-2 rerun status:

- `scripts/sec_fsd/build_panel_v2.py` rebuilt the production and GitHub panel exports;
- `scripts/sec_fsd/build_sec_selected_fact_provenance.py` rebuilt selected-fact provenance;
- `scripts/data_quality/run_p0_audits.py` was patched to match distress events through `event_lookup_tickers`, then rerun;
- target profile, panel integrity, and caveat audits were rerun;
- processed and GitHub panel copies match exactly.

Important downstream note:

- baseline model metrics, controlled sklearn tuning, XGBoost/LightGBM robustness, feature-set ablation, descriptive analysis outputs, and feature-group interpretation have now been rerun after the 2026-05-08 alias-collapse rebuild;
- dashboard screenshots and the full rendered UI/project audit have now been refreshed after the 2026-05-08 alias-collapse rebuild.

## 2026-05-08 Step-4 Dashboard Artifact Refresh

- Dashboard code was polished for artifact presentation: AAPL default firm selection, readable `global_event_names` context, non-finite chart guards, and cleaner long-text display for sector/cohort/prediction-window values.
- Static dashboard audit: PASS for 62/62 usable financial fields and 68/68 chartable macro/regime/global-event fields.
- Rendered browser interaction check: PASS for page load, Firm Explorer, Macro Compare, AAPL default selection, and training-period baseline visibility.
- Browser error-level failures: 0 during rendered interaction check.
- Dashboard screenshots regenerated under `reports/figures/dashboard/`.
- Screenshot capture report: `reports/project_audit/dashboard_screenshot_capture.csv`.
- Screenshot console status: PASS; known benign Vega-Lite render warnings are retained in the report for transparency.

## Manual Audit Override

`docs/MANUAL_HIGH_RISK_AUDIT_20260507.md` found a critical SEC selected-fact period-alignment issue. That issue has now been addressed by filtering selected SEC facts to `ddate == period`, rebuilding `firm_panel_v2`, regenerating selected-fact provenance, rerunning audits, retraining the final-target models, rerunning tuning/boosting robustness, regenerating feature-group interpretation, refreshing dashboard screenshots, and rerunning project QA.

Code status:

- `scripts/sec_fsd/build_panel_v2.py` now filters candidate SEC facts to `ddate == period` before selecting accounting values.
- `scripts/sec_fsd/build_sec_selected_fact_provenance.py` mirrors the same selector and records `ddate_period_aligned`.
- Both scripts passed `python3 -m py_compile`.
- A targeted AAPL FY2022 check now selects the 2022 current-period revenue fact and derives Q4 revenue from 2022 cumulative values.
- `firm_panel_v2` has been rebuilt from the patched selector.
- At the 2026-05-08 checkpoint, selected-fact provenance showed 660,989 selected rows, zero `ddate != period` selected rows, zero selected-value mismatches above tolerance, and 24 documented panel-comparison exclusions. The current post-polish provenance status is reported above: 700,844 selected facts, zero `ddate != period` selected rows, zero selected-value mismatches above tolerance, and 371 documented panel-comparison exclusions.

## Completed

- Rebuilt SEC/FRED/global-event panel with missing-aware forward success targets.
- Expanded the universe by 150 rule-selected firms.
- Reran P0 audits.
- Reran panel integrity audit.
- Reran target profile reports.
- Reran missing-liabilities/missing-indicator investigation after the target fix.
- Retrained `distress_next_4q` and `success_resilience_next_4q` production models.
- Regenerated dashboard analysis outputs.
- Regenerated final feature interpretation and feature-group contribution tables.
- Reran target/factor tweak experiments for the expanded panel.
- Assessed `_external_inputs/02_ai_reviews_and_strategy_plans/strategic_next_steps_20260505.json`.
- Added scope-lock and final target-hierarchy documentation.
- Assessed and accepted `_external_inputs/02_ai_reviews_and_strategy_plans/final_codex_decision_plan_20260505_1.json` as the controlling final direction.
- Created event-date provenance and event-review classification scaffolds.
- Source-verified 8 event-review formal distress candidates and added them to `config/distress_event_dates.csv`.
- Rebuilt the production panel after the event-date update.
- Reran P0 audits, integrity audit, target profiles, production models, ablation, analysis outputs, feature contributions, broader target experiments, and target-tweak experiments.
- Generated the market-health index context layer from existing prediction-date-aligned macro/regime/global-event fields.
- Promoted `failure_pressure_conservative_v2_next_4obs` into the production panel builder as the main broader failure-pressure target.
- Rebuilt the panel and GitHub-ready copies after broader-target promotion.
- Retrained production models for `distress_next_4q`, `failure_pressure_conservative_v2_next_4obs`, and `success_resilience_next_4q`.
- Updated the Streamlit dashboard to expose strict distress, broader failure pressure, and success/resilience as separate target views.
- Created `docs/BIBLIOGRAPHY.md` and `docs/references.bib`.
- Created `docs/STRATEGIST_HANDOFF_20260505.md`.
- Created `reports/data_quality/readiness_table_20260505.csv`.
- Ran controlled model-tuning and seed-robustness experiments for the three production targets.
- Created `scripts/modeling/run_model_tuning_experiments.py`, `reports/model_tuning/`, and `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`.
- Installed XGBoost and LightGBM, installed macOS OpenMP runtime `libomp`, and ran advanced boosted-tree benchmarks.
- Created `scripts/modeling/run_advanced_boosting_experiments.py` and `reports/model_tuning_advanced/`.

## Current Audit Status

- prediction timestamp: PASS;
- leakage: PASS;
- macro lag: PASS;
- global event timing: PASS;
- post-event rows: PASS;
- distress event dates: PASS.

Event-review scaffold:

- existing strict event-date rows: 50;
- event-review expansion firms: 75;
- source-verified formal distress candidates outside config: 0;
- source-verified formal distress cases in config: 44;
- provisional unverified formal distress candidates: 0;
- likely merger/transaction candidates: 11.

Market-health index:

- date-level output rows: 3,319;
- audit rows: 18;
- production panel modified: no.

Historical 2026-05-08 production panel before the 2026-05-09 SEC mapping polish:

- rows: 31,716;
- columns: 185;
- CIKs: 540;
- tickers / display IDs: 540.

Historical 2026-05-08 target counts before the 2026-05-09 SEC mapping polish:

- `distress_next_4q`: 31,716 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,819 known rows, 3,007 positives, 1,897 missing;
- `success_resilience_next_4q`: 20,160 known rows, 12,525 positives, 11,556 missing.

## Historical 2026-05-08 Best Models

`distress_next_4q`:

- best baseline model by test PR-AUC: random forest;
- test rows: 5,873;
- test positives: 96;
- ROC-AUC: 0.798;
- PR-AUC: 0.157;
- precision: 0.147;
- recall: 0.146;
- F1: 0.147;
- strongest threshold F1 across advanced robustness checks: XGBoost `xgboost_cfg1_seed777`, F1 0.241, PR-AUC 0.121.

`success_resilience_next_4q`:

- best model: random forest;
- test rows: 4,047;
- test positives: 2,648;
- ROC-AUC: 0.966;
- PR-AUC: 0.973;
- precision: 0.938;
- recall: 0.946;
- F1: 0.941.

`failure_pressure_conservative_v2_next_4obs`:

- production status: production panel column;
- best model by PR-AUC/F1: random forest;
- test rows: 5,735;
- test positives: 575;
- ROC-AUC: 0.955;
- PR-AUC: 0.764;
- precision: 0.679;
- recall: 0.793;
- F1: 0.731.

Broader target experiments retained for robustness:

- `failure_pressure_balance_liquidity_next_4obs`: random forest, test positives 1,052, PR-AUC 0.906, F1 0.813.
- `success_resilience_quality_v2_next_4obs`: random forest, test positives 1,449, PR-AUC 0.929, F1 0.875.

## Controlled Tuning Robustness Pass

This pass did not overwrite the production models.

- candidate configurations: 35 per target, 105 total;
- split-metric rows: 315;
- candidate failures: 0;
- split policy: train through 2018, validation 2019-2021, test 2022-2024;
- candidate selection and thresholds used validation data only.

Validation-selected tuned candidates:

- `distress_next_4q`: `extra_trees_cfg3_seed777`, test PR-AUC 0.144, F1 0.195.
- `failure_pressure_conservative_v2_next_4obs`: `hist_gradient_boosting_cfg2`, test PR-AUC 0.745, F1 0.710.
- `success_resilience_next_4q`: `random_forest_cfg1_seed42`, test PR-AUC 0.972, F1 0.941.

Interpretation:

- strict legal distress remains a rare-event benchmark rather than the thesis headline model;
- broader failure pressure remains strong; tuning supports robustness, while the baseline random forest remains slightly stronger on test PR-AUC/F1;
- the success/resilience result remains stable across baseline and tuning runs;
- AutoGluon was not installed or used, so the thesis should not claim exhaustive AutoML optimization.

## Advanced Boosting Robustness Pass

This pass did not overwrite the production models.

- candidate configurations: 24 per target, 72 total;
- split-metric rows: 216;
- candidate failures: 0;
- families: XGBoost and LightGBM;
- split policy: train through 2018, validation 2019-2021, test 2022-2024.

Validation-selected advanced candidates:

- `distress_next_4q`: `xgboost_cfg1_seed777`, test PR-AUC 0.121, F1 0.241.
- `failure_pressure_conservative_v2_next_4obs`: `xgboost_cfg4_seed42`, test PR-AUC 0.744, F1 0.713.
- `success_resilience_next_4q`: `lightgbm_cfg3_seed202`, test PR-AUC 0.974, F1 0.938.

Interpretation:

- advanced boosting improves strict-distress threshold F1 versus the baseline model but does not change its rare-event caveat;
- advanced boosting confirms the broader failure-pressure and success/resilience stories, without replacing the baseline random forest as the main interpretable production model;
- the thesis can now state that XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks.

## Final Scientific-Validity QA Layer

This pass did not manually edit the production panel.

- pre-QA snapshot: `reports/project_audit/pre_qa_snapshot_manifest.csv`;
- scientific validity note: `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`;
- scientific validity summary: `reports/project_audit/scientific_validity_summary.csv`;
- SEC concept mapping audit: `docs/SEC_CONCEPT_MAPPING_AUDIT.md`;
- duplicate/amendment note: `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md`;
- package smoke test: `reports/project_audit/package_smoke_test_report.md`;
- clean virtualenv smoke test: `reports/project_audit/clean_venv_smoke_test_results.csv`;
- clean doc-reference audit: `reports/project_audit/doc_reference_audit_clean.csv`;
- dashboard screenshots: `reports/figures/dashboard/`;
- final claim guardrails: `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`;
- appendix evidence pack index: `reports/final_thesis_appendix_pack/README.md`.

Current scientific-validity summary:

- structural readiness: PASS;
- prediction timing: PASS;
- leakage control: PASS;
- strict distress event dates: PASS;
- SEC concept mapping: PASS with caveats;
- missingness: PASS with caveats;
- model validity: PASS with caveats;
- dashboard evidence: PASS with caveats.

## Final Polish Caveat-Resolution Layer

This pass did not manually edit the production panel.

- selected SEC fact provenance sidecar: `reports/data_quality/sec_selected_fact_provenance.parquet` and `.csv.gz`;
- selected fact rows: 660,989;
- selected facts with `ddate != period`: 0;
- selected-value mismatches against production panel above tolerance: 0;
- selected facts missing from production panel comparison: 24, all documented as belonging to one invalid timestamp row already excluded from the production panel;
- final distress-event policy: `reports/data_quality/distress_event_final_policy.csv`;
- deterministic duplicate/amendment policy: `reports/data_quality/duplicate_amendment_deterministic_policy.csv`;
- reproducibility freeze manifest: `reports/reproducibility/freeze_manifest_20260507.csv`;
- GitHub release file list: `reports/reproducibility/github_release_file_list_20260507.csv`;
- dashboard storyboard/checklist: `docs/DASHBOARD_THESIS_STORYBOARD.md` and `reports/dashboard/dashboard_polish_checklist.csv`;
- model interpretation stability: `docs/MODEL_INTERPRETATION_STABILITY_NOTE.md` and `reports/modeling/model_interpretation_stability_summary.csv`;
- final caveat register: `docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md`;
- dashboard Artifact Notes tab now includes thesis story and caveat controls.

## Remaining Review Items

- Keep `config/distress_event_source_provenance.csv` with the final package as evidence for the now source-verified formal strict-distress dates.
- Continue manual verification for the remaining `expansion_event_review` firms before claiming strict legal-distress improvement.
- Classify event-review firms carefully; coverage-ended/M&A-style firms must not be labeled as formal distress without source evidence.
- Continue using `failure_pressure_conservative_v2_next_4obs` as the main production broader failure-pressure target.
- Keep `failure_pressure_balance_liquidity_next_4obs` and `success_resilience_quality_v2_next_4obs` as robustness/diagnostic targets unless there is time for another controlled promotion.
- Use captured dashboard screenshots from `reports/figures/dashboard/`; the screenshot report records non-blocking chart warnings.
- Disclose the duplicate/amendment audit policy; no manual production-panel edits were made.
- Refresh the GitHub/version-freeze manifest after Step-4 dashboard/docs changes, then complete final upload packaging.
- Start writing thesis chapters from the chronicle and final reports.

## Scope-Lock Status

Scope is locked as of 2026-05-05:

- no new core data sources before submission;
- U.S. SEC/FRED/global-event panel remains the empirical core;
- RFSD, Hong Kong, Japan, NLP, paid datasets, and live event feeds are future research or appendix ideas only;
- production panel files should not be manually edited.

Supporting docs:

- `docs/FINAL_SCOPE_LOCK_NOTE.md`
- `docs/FINAL_TARGET_HIERARCHY.md`
- `docs/BIBLIOGRAPHY.md`
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`
- `docs/DOCUMENT_ORGANIZATION.md`
- `reports/model_tuning_advanced/ADVANCED_BOOSTING_PROTOCOL.md`
- `reports/project_audit/FULL_PROJECT_REVIEW_20260506.md`
- `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`
- `docs/SEC_CONCEPT_MAPPING_AUDIT.md`
- `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`
