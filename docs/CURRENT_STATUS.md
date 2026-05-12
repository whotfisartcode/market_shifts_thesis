# Current Status

Updated: 2026-05-12

Latest final technical acceptance checkpoint: `docs/FINAL_ACCEPTANCE_REPORT_20260512.md`. It accepts the technical project for thesis writing and presentation with disclosed caveats; remaining work is final manuscript writing, documentation consistency review, dashboard presentation review, and Git/GitHub freeze.

## 2026-05-10 Validated Secondary Target Promotion

This is the current controlling production state.

The production panel now includes four validated secondary target labels in addition to the three primary production targets:

- `industry_relative_resilience_next_4obs`;
- `stress_resilience_next_4obs`;
- `recovery_next_4obs`;
- `quality_success_cashflow_next_4obs`.

The promotion was implemented by `scripts/modeling/promote_validated_secondary_targets.py`, which copies only the four validated secondary labels into the production panel. It does not promote `deterioration_next_4obs`, `sector_relative_improvement_next_4obs`, or `persistent_resilience_next_6obs`.

Current production panel after promotion:

- 31,702 rows;
- 190 columns;
- 540 SEC CIKs;
- 540 ticker/display IDs;
- `prediction_date = filed_date` for every row;
- processed and GitHub panel copies match exactly.

Promoted secondary target counts:

- `industry_relative_resilience_next_4obs`: 20,039 known rows, 8,093 positives, 11,663 missing;
- `stress_resilience_next_4obs`: 5,901 known rows, 3,707 positives, 25,801 missing;
- `recovery_next_4obs`: 11,375 known rows, 5,578 positives, 20,327 missing;
- `quality_success_cashflow_next_4obs`: 16,767 known rows, 9,852 positives, 14,935 missing.

Promotion/audit status:

- P0 audits: all PASS after promotion;
- `reports/target_lab/validated_secondary_target_promotion_audit.csv`: PASS;
- `reports/project_audit/core_panel_audit.csv`: PASS with 31,702 rows and 190 columns;
- `reports/project_audit/model_output_consistency_audit.csv`: PASS for all seven production model targets;
- `reports/project_audit/scientific_validity_summary.csv`: PASS or PASS_WITH_CAVEATS; no blocking failure.

Validated secondary calibration/ranking:

- `industry_relative_resilience_next_4obs`: calibrated test PR-AUC 0.844, Brier 0.127, ECE 0.030;
- `stress_resilience_next_4obs`: calibrated test PR-AUC 0.969, Brier 0.061, ECE 0.019;
- `recovery_next_4obs`: calibrated test PR-AUC 0.968, Brier 0.065, ECE 0.019;
- `quality_success_cashflow_next_4obs`: calibrated test PR-AUC 0.949, Brier 0.078, ECE 0.036.

Scientific positioning:

- the first three targets remain the primary thesis targets;
- the four promoted targets are validated secondary production outcomes for dimensional factor analysis;
- `deterioration_next_4obs` remains diagnostic only;
- `persistent_resilience_next_6obs` and `sector_relative_improvement_next_4obs` remain robustness-extension outcomes, not production panel columns.

## 2026-05-09 SEC Mapping And Caveat-Resolution Rebuild

This is the current controlling SEC/FRED rebuild state before the 2026-05-10 secondary-target promotion.

Implemented SEC concept-map polish:

- added high-coverage debt mappings:
  - `LongTermDebtNoncurrent`;
  - `LongTermDebtAndCapitalLeaseObligations`;
  - `DebtCurrent`;
  - `LongTermDebtCurrent`;
  - `LongTermDebtAndCapitalLeaseObligationsCurrent`;
  - retained `ShortTermBorrowings` as a lower-priority current-debt fallback;
- added `LiabilitiesNoncurrent` as a separate `noncurrent_liabilities` field, not as a substitute for total liabilities;
- added `ReceivablesNetCurrent` and `AccountsReceivableNet` as receivables fallbacks;
- added `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost` as an R&D fallback;
- added `RevenueFromContractWithCustomerIncludingAssessedTax` as a low-priority revenue fallback;
- did not map `LiabilitiesAndStockholdersEquity` to total liabilities and did not silently fill total liabilities as assets minus equity.

Additional caveat-resolution controls now implemented in the build pipeline:

- same-`CIK + period_date + prediction_date` amendment duplicates are resolved before ratios, trends, and targets are built;
- same-information-date duplicate policy keeps the non-amended filing first, then stable accession-number order;
- negative `SalesRevenue*` sign-convention values are normalized to positive revenue;
- negative derived quarterly revenue from inconsistent cumulative annual/YTD comparisons is left null;
- non-positive `total_assets` rows have impossible zero core accounting values nulled rather than treated as economic zeros.

Current production panel after this rebuild:

- 31,702 rows;
- 186 columns before secondary-target promotion; 190 columns after promotion;
- 540 SEC CIKs;
- 540 ticker/display IDs;
- `prediction_date = filed_date` for every row;
- processed and GitHub panel copies match exactly.

Coverage improvements after the concept-map polish:

- `long_term_debt` missingness improved to 27.1%;
- `short_term_debt` missingness improved to 39.0%;
- `accounts_receivable` missingness improved to 24.8%;
- `r_and_d_expense` missingness improved to 73.0%;
- `total_revenue` missingness improved to 10.6%.

Current rebuilt target counts:

- `distress_next_4q`: 31,702 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,805 known rows, 3,003 positives, 1,897 missing;
- `success_resilience_next_4q`: 20,152 known rows, 12,519 positives, 11,550 missing.

Current SEC/provenance audit:

- P0 audits: all PASS;
- selected SEC fact provenance: 700,844 selected facts;
- selected facts with `ddate != period`: 0;
- selected-value mismatches above tolerance: 0;
- documented panel-comparison exclusions: 371, explained by deterministic duplicate drops, invalid timestamp exclusions, and source-aware accounting nulls.

Current post-polish model story:

- `distress_next_4q` remains a strict rare-event benchmark: baseline gradient boosting test PR-AUC 0.104 and F1 0.182; validation-selected ExtraTrees improves test PR-AUC to 0.143 and F1 to 0.237;
- `failure_pressure_conservative_v2_next_4obs` remains the main failure-factor target: baseline random forest test PR-AUC 0.758 and F1 0.725;
- `success_resilience_next_4q` remains strong and stable: baseline random forest test PR-AUC 0.975 and F1 0.938.

Current post-polish dashboard status:

- dashboard financial coverage: 63/63 usable financial fields;
- macro/regime/event chartable coverage: 68/68 fields;
- dashboard screenshots refreshed under `reports/figures/dashboard/`;
- screenshot capture marks the console row PASS; only known benign Vega-Lite render warnings are retained for transparency.

Current controlled-extension status:

- the production panel is now 31,702 rows x 190 columns after promotion of the four validated secondary target labels;
- calibration/ranking diagnostics now exist for the three primary production targets, four validated secondary production outcomes, and two robustness-extension targets;
- four former exploratory targets are now validated secondary production outcomes: `industry_relative_resilience_next_4obs`, `stress_resilience_next_4obs`, `recovery_next_4obs`, and `quality_success_cashflow_next_4obs`;
- `deterioration_next_4obs` remains diagnostic only;
- `persistent_resilience_next_6obs` is a strong robustness-extension target for long-horizon resilience sensitivity analysis;
- `sector_relative_improvement_next_4obs` is a useful but weaker robustness-extension target for dynamic peer catch-up analysis;
- detailed factor evidence now exists through feature-level importance, direction-of-effect, permutation importance, and reason-code reports;
- market-health v2 remains an audited stress-regime layer used to construct and validate the stress-resilience outcome; the target label is production, while the v2 score columns are not promoted as production panel features.

Current extension outputs:

- `docs/CALIBRATION_AND_RANKING_NOTE.md`;
- `docs/CONTROLLED_EXTENSION_DECISION_REPORT.md`;
- `reports/target_lab/validation_extension_gate_summary.md`;
- `reports/modeling/calibration_metrics.csv`;
- `reports/modeling/threshold_ranking_metrics.csv`;
- `reports/target_lab/exploratory_reason_code_summary.csv`.
- `reports/target_lab/robustness_extension_target_audit_summary.md`.

Current robustness-extension audit status:

- `scripts/modeling/audit_robustness_extension_targets.py` passes;
- zero blocking target-construction invariant violations;
- the two robustness-extension labels are not production-panel columns and do not enter the model feature list;
- scientific caveats remain documented: OR-based peer catch-up logic, tiny peer-group edge cases for sector-relative improvement, and high overlap between persistent resilience and the production success/resilience target.

Current data-integrity caveat status:

- SEC values are auditable to selected tags but not perfect taxonomy harmonization;
- strict distress is rare and should stay a benchmark, not the headline model;
- total liabilities are not filled from risky accounting-identity inference;
- same-information-date amendment duplicates are now resolved in the builder: 15 amended rows dropped, 0 duplicate ticker/period/prediction groups remain;
- non-positive `total_assets` rows are now 0 after source-aware nulling of BKR/VICI zero-asset source rows;
- negative `total_revenue` rows are now 10; unresolved negative-revenue mapping rows are 0 because remaining cases are source-reported negative revenue in stress-sector contexts;
- structured missingness remains a disclosed caveat.

## 2026-05-08 Alias-Collapse Rebuild And Step-2 Audit

Step-2 rebuild artifacts:

- `data/processed/panel_v2/firm_panel_v2.csv.gz`
- `data/processed/panel_v2/firm_panel_v2.parquet`
- `data/github/firm_panel_v2.csv.gz`
- `data/github/firm_panel_v2.parquet`
- `reports/data_quality/sec_selected_fact_provenance.parquet`
- `reports/data_quality/sec_selected_fact_panel_validation.csv`
- `reports/data_quality/p0_audit_status.csv`
- `reports/modeling/panel_v2_target_overall.csv`
- `reports/data_quality/data_integrity_caveat_audit_20260508.csv`
- `reports/data_quality/target_missingness_summary_20260508.csv`
- `reports/data_quality/failure_pressure_missingness_reasons_20260508.csv`
- `reports/data_quality/success_resilience_missingness_reasons_20260508.csv`

Historical 2026-05-08 rebuilt panel before the 2026-05-09 SEC mapping polish:

- 31,716 rows;
- 185 columns;
- 540 SEC CIKs;
- 540 ticker/display IDs;
- 0 duplicated CIK/submission rows;
- processed and GitHub panel copies match exactly.

Historical 2026-05-08 rebuilt target counts before the 2026-05-09 SEC mapping polish:

- `distress_next_4q`: 31,716 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,819 known rows, 3,007 positives, 1,897 missing;
- `success_resilience_next_4q`: 20,160 known rows, 12,525 positives, 11,556 missing.

Step-2 audit status:

- P0 audits: all PASS;
- SEC selected-fact provenance: 660,989 selected facts, 0 `ddate != period` rows, 0 selected-value mismatches, 24 documented panel-comparison exclusions;
- numeric integrity: 0 infinite numeric values;
- structured missingness remains a disclosed caveat, not an integrity failure;
- accounting sign/outlier sanity remains REVIEW: 18 negative revenue rows and 2 non-positive asset rows are preserved for source-aware review rather than silently deleted;
- duplicate same-ticker/period/prediction groups remain REVIEW: 30 rows across 15 groups under the existing deterministic disclosure policy.

Target-missingness interpretation:

- `distress_next_4q` has 0 missing labels because strict legal distress is encoded as a rare sourced event benchmark for every row;
- `failure_pressure_conservative_v2_next_4obs` has 1,897 missing labels: 1,488 rows lack at least three future filing observations and 409 rows are post-event rows excluded from primary prediction;
- `success_resilience_next_4q` has 11,556 missing labels: 1,620 rows lack at least three future filing observations and 9,936 rows have future filings but fewer than three future rows with net income, ROA, and leverage/assets all available;
- the success/resilience missingness is mainly driven by missing future `total_liabilities` / `leverage_assets` availability, so these rows remain null rather than being forced into non-success labels.

`PCG`/`PGNPQ` resolution:

- `CIK 1004980` now appears once in the production panel, under primary ticker `PCG`;
- `PGNPQ` is preserved in `ticker_aliases`, `event_lookup_tickers`, and `event_source_ticker`;
- the source-verified `PGNPQ` 2019 bankruptcy event attaches to the single `PCG`/CIK history;
- `reports/data_quality/duplicate_cik_alias_resolution.csv` records the alias-collapse policy.

Step-3 post-rebuild modeling status:

- baseline temporal models were rerun for all three production targets;
- controlled sklearn tuning was rerun for all three production targets;
- XGBoost and LightGBM advanced boosting benchmarks were rerun;
- feature-group interpretation, interpretation-stability tables, target profiles, descriptive sector/regime/event outputs, and feature-set ablation outputs were refreshed;
- P0 audits and model feature leakage guardrails still PASS after model feature-list regeneration;
- dashboard screenshots and the rendered UI/project audit have now been refreshed in the Step-4 artifact pass.

Current post-rebuild model story:

- `distress_next_4q` remains a strict rare-event legal benchmark: best baseline test PR-AUC is 0.157 with random forest, while XGBoost gives the strongest threshold F1 at 0.241 but lower PR-AUC;
- `failure_pressure_conservative_v2_next_4obs` remains the main failure-factor target: baseline random forest test PR-AUC is 0.764 and F1 is 0.731;
- `success_resilience_next_4q` remains strong and stable: baseline random forest test PR-AUC is 0.973 and F1 is 0.942; LightGBM has slightly higher PR-AUC at 0.974 but lower F1.

## 2026-05-08 Step-4 Dashboard Artifact Refresh

Step-4 dashboard/artifact outputs:

- `app/dashboard.py`;
- `scripts/project_audit/capture_dashboard_screenshots.py`;
- `reports/figures/dashboard/`;
- `reports/project_audit/dashboard_screenshot_capture.csv`;
- `reports/project_audit/manual_dashboard_static_audit_20260508.csv`;
- `reports/project_audit/manual_dashboard_rendered_audit_20260508.csv`;
- `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md`.

Step-4 result:

- dashboard static/backend coverage is PASS: 62/62 usable financial fields and 68/68 chartable macro/regime/global-event fields are exposed;
- `global_event_names` is now surfaced as readable firm-level event context rather than treated as a numeric chart metric;
- Firm Explorer now defaults to `AAPL` when available and separates long text values such as sector/cohort from metric widgets;
- chart helpers now drop non-finite chart values and show an explanation when a selection has no chartable numeric observations;
- nine thesis screenshot files were regenerated under `reports/figures/dashboard/`;
- rendered browser interaction check passed for app load, Firm Explorer, AAPL default selection, Macro Compare, and training-period standardization baseline visibility;
- no browser error-level app failures were found;
- non-fatal Streamlit/Vega chart-library warnings remain in the console report and should be disclosed as artifact caveats, not treated as scientific failures.

## 2026-05-08 Full Manual Logic/UI/Backend Audit

Current audit artifact:

- `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md`
- `reports/project_audit/manual_panel_row_audit_sample_20260508.csv`
- `reports/project_audit/manual_dashboard_rendered_audit_20260508.csv`

Manual audit result:

- the project remains scientifically usable for thesis writing, but it must be presented with explicit data-construction caveats;
- P0 timing/leakage/event audits remain PASS;
- selected SEC fact provenance remains PASS for current-period alignment (`ddate != period` selected rows: 0);
- model feature lists still have no target/metadata blacklist overlap;
- dashboard rendered in browser on desktop and mobile without a fatal app error.

High-risk finding and fix status:

- the original manual audit found that `CIK 1004980` appeared under two ticker/display IDs, `PCG` and `PGNPQ`;
- code-level alias-collapse handling was added to `scripts/sec_fsd/build_panel_v2.py` and materialized into the production panel exports;
- the current rebuilt panel has 0 CIKs mapped to multiple ticker/display IDs;
- target recomputation now has 0 mismatches across the three production targets.

Additional audit caveats:

- formula recomputation mismatches are tiny relative to the full panel and mostly reflect the difference between raw arithmetic recomputation and the production builder's extreme-value cleanup/null-preservation policy;
- code-level derived-feature cleaning now runs after ratio construction, after trend construction, and after target construction, and the rebuilt production panel reflects this fix;
- production target recomputation now passes for strict distress, failure pressure, and success/resilience;
- dashboard static coverage is good for chartable fields: 62/62 financial fields and 68/68 chartable macro/regime/event fields;
- `global_event_names` is now surfaced in readable Firm Explorer event context, not charted as a numeric metric;
- rendered dashboard console has repeated non-fatal Streamlit/Vega chart-library warnings, but no browser error-level app failures;
- long sector/cohort values no longer use cramped metric widgets in Firm Explorer.

## Critical Manual Audit Update

`docs/MANUAL_HIGH_RISK_AUDIT_20260507.md` supersedes the earlier "SEC mapping structurally passed" interpretation.

Manual inspection found that the selected SEC facts are reproducible against the panel, but not always economically period-aligned. The sidecar validation confirms that panel values match the selected facts; it does not prove that every selected fact has `ddate == period`. Targeted checks found prior-year comparative facts selected as current-period values, including AAPL FY2022 `total_revenue = -7.942B` and BKR 2017 Q2 `total_assets = 0`.

Current implication:

- the old period-alignment caveat has been addressed in code and by a full downstream rerun;
- strict legal distress event-date provenance has been source-verified for all 44 formal event rows;
- accounting variables, ratios, deterioration features, success/failure-pressure targets, GitHub dataset, model metrics, tuning outputs, feature interpretation, dashboard screenshots, and rendered UI audit now refer to the rebuilt `ddate == period` panel plus the later 2026-05-08 alias-collapse rebuild.

Implementation status:

- code-level period filtering has been added to `scripts/sec_fsd/build_panel_v2.py`;
- the provenance sidecar builder `scripts/sec_fsd/build_sec_selected_fact_provenance.py` now uses the same current-period filter and records `ddate_period_aligned`;
- syntax checks passed for both scripts;
- a targeted AAPL FY2022 check now selects the current-period 2022 revenue fact and derives Q4 revenue from 2022 cumulative values rather than mixing in a 2020 comparative fact;
- BKR 2017 Q2 still has a current-period zero-assets raw SEC fact in the targeted check, so that row remains an outlier-review item after rebuild;
- `firm_panel_v2` has been rebuilt from the patched selector and later alias-collapse fix:
  - 31,716 rows;
  - 185 columns;
  - 540 SEC CIKs;
  - 540 ticker/display IDs;
  - `distress_next_4q`: 207 positives across 31,716 known rows;
  - `failure_pressure_conservative_v2_next_4obs`: 3,007 positives across 29,819 known rows;
  - `success_resilience_next_4q`: 12,525 positives across 20,160 known rows;
- selected-fact provenance was regenerated:
  - 660,989 selected fact rows;
  - `ddate != period` selected rows: 0;
  - selected-value mismatches against the production panel above tolerance: 0;
  - 24 documented exclusions where selected facts do not compare to a production panel value;
- P0 audits were rerun: all PASS, including `distress_event_dates`;
- formal distress source verification was completed:
  - 44 formal event rows have source-provenance records;
  - 0 formal event rows remain `initial_seed`;
  - 6 near-distress rows remain non-strict context only;
  - source evidence is recorded in `config/distress_event_source_provenance.csv`;
- temporal baseline models, controlled tuning, XGBoost/LightGBM robustness, feature-group interpretation, target profiles, ablation, descriptive outputs, P0 audits, caveat audits, dashboard screenshots, and rendered UI/project audit have now been rerun/refreshed after the 2026-05-08 alias-collapse rebuild.

## Current Source Of Truth For Strategist Review

Use these as current-state files:

- `docs/MANUAL_HIGH_RISK_AUDIT_20260507.md`
- `docs/STRATEGIST_HANDOFF_20260505.md`
- `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`
- `reports/data_quality/readiness_table_20260505.csv`
- `reports/RUN_STATUS_FINAL.md`
- `docs/FINAL_TARGET_HIERARCHY.md`
- `docs/PROJECT_CHRONICLE.md`
- `docs/BIBLIOGRAPHY.md`
- `docs/references.bib`
- `reports/literature/literature_matrix.csv`
- `reports/literature/reference_critical_evaluation.csv`
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`
- `reports/model_tuning/`
- `reports/project_audit/FULL_PROJECT_REVIEW_20260506.md`
- `reports/project_audit/`
- `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`
- `docs/SEC_CONCEPT_MAPPING_AUDIT.md`
- `reports/data_quality/sec_selected_fact_provenance.parquet`
- `reports/data_quality/sec_selected_fact_panel_validation.csv`
- `config/distress_event_source_provenance.csv`
- `reports/data_quality/distress_event_source_verification_summary_20260507.md`
- `reports/data_quality/event_date_scientific_validity_summary.csv`
- `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md`
- `docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md`
- `docs/REPRODUCIBILITY_FREEZE_20260507.md`
- `reports/reproducibility/freeze_manifest_20260507.csv`
- `docs/DASHBOARD_THESIS_STORYBOARD.md`
- `docs/MODEL_INTERPRETATION_STABILITY_NOTE.md`
- `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`
- `reports/figures/dashboard/`
- `reports/final_thesis_appendix_pack/README.md`

Older experiment notes remain useful historical evidence, but the files above control current target status, model positioning, and next steps.

## Completed

- Reinstatement submitted by user.
- Clean workspace created at `market_shifts_clean/`.
- Thesis requirements extracted and converted into checklist.
- SEC FSD ZIPs collected from 2009q1 through 2026q1.
- SEC submission coverage indexed.
- Expanded universe built:
  - 254 core large-cap universe rows,
  - 100 additional-control universe rows,
  - 42 distress/near-distress candidates included,
  - 75 event-review expansion firms added,
  - 75 matched-control expansion firms added,
  - 546 universe rows total.
- SEC/FRED panel built:
  - `data/processed/panel_v2/firm_panel_v2.csv.gz`,
  - `data/processed/panel_v2/firm_panel_v2.parquet`,
  - `data/github/firm_panel_v2.csv.gz`,
  - `data/github/firm_panel_v2.parquet`,
  - 31,716 rows,
  - 185 columns,
  - 540 SEC CIKs,
  - 540 tickers / firm display IDs,
  - period range 2009-03-31 to 2026-02-28,
  - prediction timestamp range 2009-04-15 to 2026-03-31,
  - 207 `distress_next_4q` positive rows after source-verified event-date refinement and prediction-date retargeting.
- Macro and trend-feature expansion added:
  - FRED catalog at `config/fred_series_catalog.csv`,
  - downloader at `scripts/data/download_fred_series.py`,
  - yield-curve, oil, dollar, inflation, labor, demand, housing, bank-credit, and lending-standards variables,
  - firm deterioration features such as lagged ratios, 4-observation growth/change variables, and prior loss counts.
- Global-event context layer added:
  - curated seed calendar at `config/global_event_calendar_seed.csv`,
  - strategy note at `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md`,
  - event-sector summary at `reports/modeling/panel_v2_global_event_sector_summary.csv`,
  - event figure at `reports/figures/modeling/panel_v2_distress_share_by_global_event_type.png`.
- Data-integrity and null-treatment pass completed:
  - integrity note at `docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md`,
  - audit script at `scripts/data_quality/audit_panel_integrity.py`,
  - source/qtrs audit at `reports/data_quality/sec_fsd_variable_source_audit.csv`,
  - form/fiscal-period missingness audit at `reports/data_quality/panel_v2_key_missingness_by_form_fp.csv`,
  - longitudinal missingness audit at `reports/data_quality/panel_v2_longitudinal_missingness_summary.csv`,
  - null-treatment audit at `reports/data_quality/panel_v2_null_treatment_audit.csv`.
- P0 peer-review audit path implemented:
  - prediction timestamp audit at `reports/data_quality/prediction_timestamp_audit.csv`,
  - event-date audit at `reports/data_quality/distress_event_date_audit.csv`,
  - leakage audit at `reports/data_quality/leakage_audit.csv`,
  - macro lag audit at `reports/data_quality/macro_lag_audit.csv`,
  - global-event timing audit at `reports/data_quality/global_event_timing_audit.csv`,
  - post-event row audit at `reports/data_quality/post_event_row_audit.csv`,
  - combined status at `reports/data_quality/p0_audit_status.csv`.
- Broader success/failure target experiments completed:
  - runner at `scripts/modeling/run_broader_target_experiments.py`,
  - results root at `reports/target_experiments/`,
  - historical explanation archived at `docs/_redundant/03_superseded_target_notes/BROADER_TARGET_EXPERIMENTS.md`,
  - four experiment folders from `test_broader_targets1` through `test_broader_targets4`,
  - each folder contains target profile, inconsistency audit, model metrics, plots, best predictions, and `run_log.md`.
- Second-pass target and feature tweak experiments completed:
  - runner at `scripts/modeling/run_target_feature_tweak_experiments.py`,
  - results root at `reports/target_tweak_experiments/`,
  - historical assessment archived at `docs/_redundant/03_superseded_target_notes/TARGET_AND_FACTOR_TWEAK_ASSESSMENT.md`,
  - five target-tweak folders from `test_target_tweaks1` through `test_target_tweaks5`,
  - feature-set ablation at `reports/target_tweak_experiments/feature_set_ablation/`,
  - dashboard compact tables at `reports/target_tweak_experiments/dashboard_best_target_rows.csv`, `dashboard_feature_set_performance.csv`, and `dashboard_factor_group_best_models.csv`.
- Prediction-time policy implemented:
  - `prediction_date = filed_date`,
  - `period_date` fallback is available but currently unused in the panel,
  - macro variables and global-event windows are now aligned to `prediction_date`,
  - distress labels use event dates strictly after `prediction_date`,
  - post-event rows are flagged and excluded from primary model training.
- SEC flow variables standardized:
  - Q2/Q3 year-to-date flow values are converted into single-period values when prior cumulative values are available,
  - missing values remain missing when derivation is not possible,
  - CapEx missingness improved from about 63.8% to about 33.3%,
  - operating cash-flow missingness improved from about 55.6% to about 15.7%.
- GitHub dataset package created:
  - `data/github/firm_panel_v2.csv.gz`,
  - `data/github/firm_panel_v2.parquet`,
  - `data/github/firm_panel_v2_schema.csv` with feature-family labels,
  - `data/github/README.md`.
- First temporal-validation models trained:
  - logistic regression,
  - random forest,
  - gradient boosting.
- Multiple target definitions added:
  - `distress_next_2q`,
  - `distress_next_4q`,
  - `distress_next_8q`,
  - `broad_distress_next_4q`,
  - `healthy_current`,
  - `success_profitability_next_4q`,
  - `success_resilience_next_4q`,
  - `success_quality_next_4q`.
- Leakage issues found and fixed:
  - `cohort` was removed from model features.
  - `form` and `afs` were removed from model features because they are filing metadata.
  - final model feature lists are saved in `reports/data_quality/model_feature_lists/`.
- Streamlit dashboard artifact created:
  - `app/dashboard.py`,
  - `app/README.md`.
- Dashboard updated to use `prediction_date` for filtering, ordering, and firm time series.
- Dashboard updated with a `Target Lab` tab for target experiment summaries, feature-set ablation, and factor-group importance.
- Dashboard server starts on `http://localhost:8501`.
- VS Code tasks added in `.vscode/tasks.json`.
- Strategic next-steps review assessed:
  - source file: `/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/strategic_next_steps_20260505.json`,
  - historical assessment archived at `docs/_redundant/02_superseded_strategy_reviews/STRATEGIC_NEXT_STEPS_20260505_REVIEW.md`,
  - scope lock: `docs/FINAL_SCOPE_LOCK_NOTE.md`,
  - target hierarchy: `docs/FINAL_TARGET_HIERARCHY.md`.
- Final decision plan accepted and implemented conservatively:
  - source file: `/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/final_codex_decision_plan_20260505_1.json`,
  - historical decision record archived at `docs/_redundant/02_superseded_strategy_reviews/FINAL_DECISION_PLAN_20260505.md`,
  - event-date provenance note: `docs/DISTRESS_EVENT_DATE_PROVENANCE.md`,
  - market-health index note: `docs/MARKET_HEALTH_INDEX_NOTE.md`,
  - event-review scaffold: `reports/data_quality/event_review_firm_classification_scaffold.csv`,
  - event-review summary: `reports/data_quality/event_review_scaffold_summary.csv`,
  - market-health date output: `reports/modeling/market_health_index_by_prediction_date.csv`,
  - market-health sector/regime output: `reports/modeling/market_health_by_year_regime_sector.csv`,
  - 44 formal distress events are now source-verified in `config/distress_event_dates.csv`,
  - detailed event-source evidence is recorded in `config/distress_event_source_provenance.csv`,
  - production panel rebuilt and full audit/model/report chain rerun.
- Mandatory literature sprint completed:
  - generator at `scripts/docs/generate_literature_package.py`,
  - source-of-truth index at `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`,
  - curated bibliography at `docs/BIBLIOGRAPHY.md`,
  - BibTeX file at `docs/references.bib`,
  - literature search strategy at `docs/LITERATURE_SEARCH_STRATEGY.md`,
  - literature matrix at `docs/LITERATURE_MATRIX.md` and `reports/literature/literature_matrix.csv`,
  - critical source evaluation at `docs/REFERENCE_CRITICAL_EVALUATION.md` and `reports/literature/reference_critical_evaluation.csv`,
  - reference quality audit at `docs/BIBLIOGRAPHY_AUDIT.md` and `reports/literature/reference_quality_audit.csv`,
  - source-to-claim map at `reports/literature/source_to_claim_map.csv`,
  - research-gap synthesis at `reports/literature/research_gap_synthesis.csv`,
  - literature review outline at `docs/LITERATURE_REVIEW_OUTLINE.md`,
  - literature review draft at `docs/LITERATURE_REVIEW_DRAFT.md`,
  - introduction/research-gap draft at `docs/INTRODUCTION_RESEARCH_GAP_DRAFT.md`,
  - theoretical positioning note at `docs/THESIS_THEORETICAL_POSITIONING.md`.
- Literature audit counts:
  - 67 total verified references,
  - 51 academic journal articles,
  - 56 peer-reviewed sources,
  - 21 sources from 2020 onward,
  - all 67 entries have a DOI, official page, publisher page, or official report URL,
  - 56 sources are explicitly marked with unknown or access-limited notes, mostly because metadata was verified but full-text access was not assumed.
- Controlled model tuning and robustness pass completed:
  - runner at `scripts/modeling/run_model_tuning_experiments.py`,
  - outputs at `reports/model_tuning/`,
  - protocol note at `reports/model_tuning/MODEL_TUNING_PROTOCOL.md`,
  - interpretation note at `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`,
  - 35 candidate configurations per production target,
  - 105 candidate configurations across the three production targets,
  - 315 split-metric rows in `reports/model_tuning/all_candidate_metrics.csv`,
  - no candidate failures.
- Advanced XGBoost/LightGBM benchmark completed:
  - runner at `scripts/modeling/run_advanced_boosting_experiments.py`,
  - outputs at `reports/model_tuning_advanced/`,
  - 24 candidate configurations per production target,
  - 72 candidate configurations across the three production targets,
  - 216 split-metric rows in `reports/model_tuning_advanced/all_candidate_metrics.csv`,
  - no candidate failures.
- Document organization pass completed:
  - current document map at `docs/DOCUMENT_ORGANIZATION.md`,
  - redundant archive at `docs/_redundant/`,
  - external uploaded inputs organized at `../_external_inputs/`,
  - top-level `docs/` reduced to current source-of-truth, writing, methodology, and artifact notes.
- Full project audit completed:
  - audit runner at `scripts/project_audit/full_project_audit.py`,
  - audit outputs at `reports/project_audit/`,
  - full review at `reports/project_audit/FULL_PROJECT_REVIEW_20260506.md`,
  - 2,759 files inventoried after the final scientific-validity QA layer,
  - Python, JSON/notebook, CSV, Parquet, ZIP, dependency, model-output, required-config, and feature-blacklist checks passed,
  - remaining review risks are strict-distress rarity, duplicate/amendment policy disclosure, accounting outlier disclosure, missing accounting fields, and GitHub packaging.
- Final scientific-validity QA layer completed:
  - runner at `scripts/project_audit/final_scientific_validity_qa.py`,
  - pre-QA snapshot at `reports/project_audit/pre_qa_snapshot_manifest.csv`,
  - scientific validity note at `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`,
  - scientific validity summary at `reports/project_audit/scientific_validity_summary.csv`,
  - SEC concept mapping audit at `docs/SEC_CONCEPT_MAPPING_AUDIT.md`,
  - SEC concept tables at `reports/data_quality/sec_concept_mapping_summary.csv` and `reports/data_quality/sec_concept_coverage_by_year_form_sector.csv`,
  - accounting sanity checks at `reports/data_quality/accounting_identity_sanity_summary.csv`,
  - amendment/duplicate audit at `reports/data_quality/amendment_duplicate_audit.csv`,
  - amendment/duplicate summary at `reports/data_quality/amendment_duplicate_summary.csv`,
  - package smoke test at `reports/project_audit/package_smoke_test_report.md`,
  - clean virtualenv smoke test at `reports/project_audit/clean_venv_smoke_test_results.csv`,
  - clean doc-reference audit at `reports/project_audit/doc_reference_audit_clean.csv`,
  - dashboard screenshots at `reports/figures/dashboard/`,
  - claim guardrails at `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`,
  - appendix evidence index at `reports/final_thesis_appendix_pack/README.md`.
- Final polish caveat-resolution layer completed:
  - selected SEC fact provenance sidecar at `reports/data_quality/sec_selected_fact_provenance.parquet` and `.csv.gz`;
  - selected SEC fact summary at `reports/data_quality/sec_selected_fact_provenance_summary.csv`;
  - selected SEC fact validation at `reports/data_quality/sec_selected_fact_panel_validation.csv`;
  - validation result: 660,989 selected fact rows, 0 selected rows with `ddate != period`, 0 selected-value mismatches above tolerance, and 24 documented panel-comparison exclusions;
  - final distress-event policy at `reports/data_quality/distress_event_final_policy.csv`;
  - deterministic duplicate/amendment policy at `reports/data_quality/duplicate_amendment_deterministic_policy.csv`;
  - reproducibility checksum manifest at `reports/reproducibility/freeze_manifest_20260507.csv`;
  - GitHub release file list at `reports/reproducibility/github_release_file_list_20260507.csv`;
  - model interpretation stability tables at `reports/modeling/model_interpretation_stability_summary.csv` and `reports/modeling/model_interpretation_top_groups_by_target_model.csv`;
  - dashboard polish checklist at `reports/dashboard/dashboard_polish_checklist.csv`;
  - caveat register at `docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md`;
  - dashboard storyboard at `docs/DASHBOARD_THESIS_STORYBOARD.md`;
  - model interpretation stability note at `docs/MODEL_INTERPRETATION_STABILITY_NOTE.md`;
  - dashboard Artifact Notes tab updated with thesis story and caveat controls;
  - dashboard screenshots refreshed under `reports/figures/dashboard/`.

## Project Vocabulary

The plain-language glossary is maintained in:

```text
docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md
```

Key terms:

- `regime` means a macro-market environment flag derived from FRED data, such as high rates, market stress, oil shock, inflation pressure, credit tightening, or crisis years.
- `prediction_date` means the date from which the model is allowed to make a prediction. In the current panel it equals the SEC filing date for every row.
- `period_date` means the accounting period end date. It is not used as the current model information date.
- `cohort` explains why a firm is in the universe. It is audit metadata, not a model feature.
- train/validation/test split is derived in modeling scripts from `prediction_date`; it is not a factual field that belongs inside the core panel.
- event-review expansion firms are not formal distress cases until manually verified and added to `config/distress_event_dates.csv`.

## Current Best Model

Current strict legal distress benchmark after the +150 firm expansion, flow-standardization, prediction-date retargeting, post-event exclusion, SEC period-alignment fix, and leakage audit:

- Target: `distress_next_4q`
- Model: random forest
- Test period: 2022-2024
- Test rows: 5,873
- Test positives: 96
- ROC-AUC: 0.798
- PR-AUC: 0.157
- Precision: 0.147
- Recall: 0.146
- F1: 0.147

Interpretation:

- strict legal distress is still a rare-event benchmark, not the headline model;
- the expansion is still useful for broader financial-pressure and resilience analysis;
- do not claim complete bankruptcy prediction until event-review firms are manually verified.

Current primary success model:

- Target: `success_resilience_next_4q`
- Best model: random forest
- Test period: 2022-2024
- Test rows: 4,047
- Test positives: 2,648
- ROC-AUC: 0.966
- PR-AUC: 0.973
- Precision: 0.938
- Recall: 0.946
- F1: 0.942

Current broader failure-pressure status:

- `failure_pressure_conservative_v2_next_4obs` has been promoted into the production panel and is the main broader failure-factor target.
- Current production model: random forest, test PR-AUC 0.764, F1 0.731.
- Controlled tuning selected `hist_gradient_boosting_cfg2` on validation for this target; observed test PR-AUC 0.745 and F1 0.710. This supports robustness but does not beat the production random forest on test PR-AUC/F1.
- `failure_pressure_balance_liquidity_next_4obs` remains a diagnostic experiment-output target: PR-AUC 0.906, F1 0.813.

## Model Tuning And AutoGluon Status

The project now has a controlled hyperparameter/seed robustness pass, not only one or two baseline model runs.

Tuning summary:

- `distress_next_4q`: validation-selected `extra_trees_cfg3_seed777`, test PR-AUC 0.144, F1 0.195. This improves threshold F1 versus the baseline strict-distress model, but strict legal distress remains too rare to be the headline performance target.
- `failure_pressure_conservative_v2_next_4obs`: validation-selected `hist_gradient_boosting_cfg2`, test PR-AUC 0.745, F1 0.710. This supports the target as the main failure-factor target, while the baseline random forest remains stronger on test PR-AUC/F1.
- `success_resilience_next_4q`: validation-selected `random_forest_cfg1_seed42`, test PR-AUC 0.972, F1 0.941. This confirms the success/resilience story is stable.

AutoGluon status:

- AutoGluon is not installed in the current environment.
- XGBoost 3.2.0 and LightGBM 4.6.0 are installed and were tested as advanced boosted-tree benchmarks.
- CatBoost is not installed.
- AutoGluon should be described only as an optional future extension unless deliberately installed, rerun, validated, and documented.
- Current thesis-safe wording is controlled scikit-learn tuning plus XGBoost/LightGBM advanced benchmarks under temporal validation, not exhaustive AutoML.

Advanced benchmark summary:

- `distress_next_4q`: validation-selected `xgboost_cfg1_seed777`, test PR-AUC 0.121, F1 0.241. Threshold F1 improved versus the baseline strict-distress model, but strict legal distress remains too rare to be the headline target.
- `failure_pressure_conservative_v2_next_4obs`: validation-selected `xgboost_cfg4_seed42`, test PR-AUC 0.744, F1 0.713. This supports boosted-tree robustness, while the baseline random forest remains stronger on test PR-AUC/F1.
- `success_resilience_next_4q`: validation-selected `lightgbm_cfg3_seed202`, test PR-AUC 0.974, F1 0.938. The production random forest remains stronger on F1 and essentially tied on PR-AUC.

## Earlier Broader Target Experiment Recommendation

These earlier broader target experiment results are historical evidence. The current production broader failure-pressure target is `failure_pressure_conservative_v2_next_4obs`, documented in `docs/FINAL_TARGET_HIERARCHY.md` and `reports/RUN_STATUS_FINAL.md`.

Best defensible broader failure target:

- Target: `failure_pressure_conservative_next_4obs`
- Folder: `reports/target_experiments/test_broader_targets4/`
- Best model: random forest
- Test positives: 255
- Test positive share: 7.8%
- Test ROC-AUC: 0.947
- Test PR-AUC: 0.693
- Test precision: 0.610
- Test recall: 0.762
- Test F1: 0.677

Best high-integrity composite success target:

- Target: `success_composite_strict_next_4obs`
- Folder: `reports/target_experiments/test_broader_targets4/`
- Best model by PR-AUC: gradient boosting
- Test positives: 687
- Test positive share: 21.4%
- Test ROC-AUC: 0.964
- Test PR-AUC: 0.847
- Test precision: 0.773
- Test recall: 0.856
- Test F1: 0.813

Important interpretation:

- `test_broader_targets1` achieved the highest raw scores, but it is too loose to be the main failure target.
- `test_broader_targets4` is the strongest defensible recommendation because it requires severe repeated loss plus stress/deterioration unless formal distress is present.

## Second-Pass Target And Factor Findings

The second-pass tests confirm the dataset is useful for factor conclusions when framed correctly.

Best raw second-pass failure target:

- Target: `failure_pressure_balance_liquidity_next_4obs`
- Expanded-panel test positives: 1,052
- Expanded-panel test positive share: 23.8%
- Best model: random forest
- Test ROC-AUC: 0.956
- Test PR-AUC: 0.906
- Test F1: 0.813
- Interpretation: strong diagnostic target for leverage/liquidity pressure, but too specific to replace the general failure target.

Stable general broader failure target:

- Target: `failure_pressure_conservative_next_4obs` / `failure_pressure_conservative_v2_next_4obs`
- Expanded-panel test positives: 514
- Expanded-panel test positive share: 11.7%
- Best model: random forest
- Test PR-AUC: about 0.739
- Test F1: about 0.705
- Interpretation: best defensible production candidate for broader economic failure pressure.

Best second-pass success target:

- Target: `success_resilience_quality_v2_next_4obs`
- Expanded-panel test positives: 1,450
- Expanded-panel test positive share: 33.3%
- Best model: random forest
- Test ROC-AUC: 0.970
- Test PR-AUC: 0.929
- Test F1: 0.876
- Interpretation: best main composite success target.

Feature-set conclusion:

- Firm core features match or beat all-features models on the recommended targets.
- Ratios and trend features are almost as strong as full firm-core models.
- Raw accounting alone is useful but weaker.
- Macro/event-only models are weak predictively.
- Therefore, macro/regime/global-event variables should be used mainly for context, sector/regime/event analysis, and dashboard filtering rather than as the main predictive signal.

Dominant factor groups:

- financial ratios,
- firm trend/deterioration,
- accounting fundamentals.

Recurring individual drivers:

- ROA,
- net income,
- prior negative-income count,
- net margin and lagged net margin,
- leverage/assets,
- equity/assets,
- total liabilities,
- lagged leverage,
- operating margin.

## Caveats

- The current panel is a filing-period panel with explicit prediction timestamps, not a fully refined strict fiscal-quarter panel.
- Flow variables are now standardized to single-period values where SEC cumulative filings allow derivation; unresolved cases remain null.
- Distress labels now use `config/distress_event_dates.csv`, and the P0 audit now marks event dates as `PASS`.
- All 44 formal strict-distress event rows are source-verified in `config/distress_event_dates.csv`; the source evidence table is `config/distress_event_source_provenance.csv`.
- The 6 near-distress rows remain context markers only and are not strict legal distress labels.
- This is a strong first-pass empirical artifact, but the methodology chapter must disclose these choices carefully unless refined.
- Macro and global-event additions are valuable for explaining market-shift and sector context. The strongest economic signal remains firm fundamentals, ratios, and deterioration; strict distress improved after adding eight source-verified events but remains a rare-event benchmark rather than the headline performance claim.
- Global event flags are currently a curated historical layer. They are useful for dashboard explanation and sector-event analysis, but should not be presented as a fully automated event database yet.
- Null values do not have one universal meaning. They may represent non-reporting, non-applicability, aggregation into another line item, excluded dimensional facts, unresolved cumulative-flow derivation, or occasionally unchanged values. The main panel does not forward-fill them.
- The old `success_resilience_next_4q` target was vulnerable to missingness contamination through future leverage/liability fields. This was fixed on 2026-05-05; unknown future success components now remain null.

## 2026-05-05 Missingness Fix And Final Model Rerun

The `missingindicator_total_liabilities` audit confirmed that the feature is generated by sklearn imputation, not by the SEC panel. It also exposed a target-definition problem in the old success target: missing future leverage/liability values could become automatic non-success.

Actions completed:

- patched `scripts/sec_fsd/build_panel_v2.py` so forward success targets are missing-aware;
- rebuilt `data/processed/panel_v2/firm_panel_v2.csv.gz` and `.parquet`;
- reran P0 audits, panel integrity audit, target profile reports, model training, and feature contribution summaries;
- created `docs/MISSINGNESS_INDICATOR_POLICY.md`;
- created `docs/TARGET_DEFINITIONS_FINAL_REVIEW.md`;
- created `docs/TOPIC_RELEVANCE_AND_SCOPE_NOTE.md`;
- created `reports/RUN_STATUS_FINAL.md`.

Post-fix success target check before the later +150 expansion:

- `success_resilience_next_4q` known rows: 14,526;
- unknown rows: 8,187;
- positive rows: 9,567;
- rows currently `0` but missing-aware audit says unknown: 0;
- known current/revised disagreements: 0.

Production models at that pre-expansion checkpoint:

- `distress_next_4q`: random forest, test ROC-AUC 0.869, PR-AUC 0.112, F1 0.199.
- `success_resilience_next_4q`: random forest, test ROC-AUC 0.961, PR-AUC 0.976, F1 0.937.

Interpretation policy:

- missingness indicators may remain in predictive models only as diagnosed auxiliaries;
- missingness indicators are excluded from economic factor interpretation;
- economic conclusions should use `reports/modeling/final_model_feature_interpretation_table.csv` and `reports/modeling/final_feature_group_contribution_table.csv`.

## 2026-05-05 Universe Expansion By 150 Firms

The panel was expanded by 150 rule-selected firms:

- 75 `expansion_event_review` firms;
- 75 `expansion_matched_controls` firms.

This was not random sampling. The selector required SEC 10-K/10-Q coverage, U.S. business-address metadata, operating-company filters, sector balance, and minimum filing history.

Expanded panel after the 2026-05-08 alias-collapse rebuild:

- rows: 31,716;
- CIKs: 540;
- tickers / firm display IDs: 540.

Validation:

- all 150 selected additions parsed into the panel;
- P0 audits are PASS, including distress event dates after formal event source verification;
- one invalid timestamp row was dropped and saved to `reports/data_quality/invalid_prediction_timestamp_rows.csv`;
- missingness did not materially deteriorate.

Important interpretation:

- the 75 event-review additions are not automatically formal distress cases;
- strict `distress_next_4q` positives remain 207 after full formal event-date source verification;
- strict legal-distress model performance remains modest because formal legal distress is still rare in the temporal test split.

Historical production model status after the source-verified event update but before the 2026-05-07 SEC period-alignment rebuild:

- superseded by the current post-rebuild model results in the `Current Best Model` section above and `reports/RUN_STATUS_FINAL.md`.

Expanded broader target status:

- `failure_pressure_conservative_v2_next_4obs`: PR-AUC 0.739, F1 0.705.
- `failure_pressure_balance_liquidity_next_4obs`: PR-AUC 0.906, F1 0.813.

Conclusion:

- the expansion is useful for broader financial-pressure and resilience factor analysis;
- the expansion should be described as improving strict-event coverage modestly after source verification, not as solving the rare-event prediction problem.

## Historical Next Steps From 2026-05-05

The list below is retained as historical context. It has been superseded by the current 2026-05-10 status at the top of this document.

1. Keep scope frozen:
   - no RFSD/Hong Kong/Japan/NLP/live-event data in the main model before submission;
   - no manual edits to production panel files.
2. Treat strict event-date provenance as resolved for the current package:
   - 44/44 formal strict-distress event rows are source-verified;
   - 6 near-distress rows remain context only;
   - do not add new formal event rows unless they are source-verified first.
3. Keep `failure_pressure_conservative_v2_next_4obs` as the main production broader failure-pressure target.
4. Keep `failure_pressure_balance_liquidity_next_4obs` and `success_resilience_quality_v2_next_4obs` as robustness/diagnostic targets unless there is time for another controlled promotion.
5. Rerun model training, feature summaries, dashboard compact tables, dashboard screenshots, and full project audit after the 2026-05-08 rebuilt panel.
6. Refine dashboard around target hierarchy, factor-group panels, market-health context, sector/regime/event comparisons, data-quality caveats, and firm-level component views.
7. Refresh dashboard screenshots after dashboard/data rerun.
8. Start thesis writing from the actual pipeline, chronicle, final reports, saved figures, and curated bibliography once post-rebuild models and dashboard outputs are refreshed.

## 2026-05-05 Broader Failure-Pressure Production Promotion

The accepted final decision plan was implemented for the main broader failure target.

Actions completed:

- promoted `failure_pressure_conservative_v2_next_4obs` into `scripts/sec_fsd/build_panel_v2.py`;
- rebuilt `data/processed/panel_v2/firm_panel_v2.csv.gz`, `.parquet`, and the GitHub-ready panel copies;
- increased production panel width from 180 to 181 columns in the 2026-05-05 run; later rebuilds increased panel width to 186 columns; the 2026-05-10 validated-secondary target promotion increased the current production panel width to 190 columns;
- added the promoted target to the modeling blacklist as a target column;
- reran P0 audits, panel integrity audit, and target profile reports;
- retrained production models for `distress_next_4q`, `failure_pressure_conservative_v2_next_4obs`, and `success_resilience_next_4q`;
- regenerated analysis outputs, feature contribution summaries, market-health outputs, and event-review scaffolds;
- updated the Streamlit dashboard to separate strict distress, broader failure pressure, and success/resilience views;
- created `docs/BIBLIOGRAPHY.md` and `docs/references.bib`.

Promoted target counts:

- target: `failure_pressure_conservative_v2_next_4obs`;
- current full-panel known rows after 2026-05-08 rebuild: 29,819;
- current full-panel unknown rows after 2026-05-08 rebuild: 1,897;
- current full-panel positives after 2026-05-08 rebuild: 3,007;
- temporal model rows: 28,984;
- temporal test rows: 5,735;
- temporal test positives: 575 after the 2026-05-07 SEC period-alignment rebuild.

Promoted target model result:

- best model by PR-AUC/F1: random forest;
- test ROC-AUC: 0.955;
- test PR-AUC: 0.764;
- test precision: 0.679;
- test recall: 0.793;
- test F1: 0.731.

Updated production target hierarchy:

- strict legal benchmark: `distress_next_4q`;
- main broader failure-pressure target: `failure_pressure_conservative_v2_next_4obs`;
- main success/resilience target: `success_resilience_next_4q`;
- diagnostic/robustness targets remain in experiment reports.

## 2026-05-05 Firm Explorer Dashboard Refinement

The dashboard firm-level view was refined after the user identified that per-ticker charts were visually messy and mixed incompatible scales.

Changes completed:

- replaced the hard-coded single firm-ratio chart with grouped metric selectors;
- added firm metric groups: profitability, balance/liquidity, revenue/scale, trend signals, targets, and all numeric;
- added scale modes:
  - separate raw scales,
  - one raw metric,
  - standardized comparison;
- replaced the fixed five-variable macro chart with grouped macro selectors;
- added macro groups for rates/credit, money/inflation, labor/demand, markets/commodities, regime flags, global events, and all macro/regime/event fields;
- added a firm-vs-macro comparison view where one firm metric can be compared against selected macro/regime/event variables;
- added M2 money supply and oil-price series to the selectable macro workflow;
- moved recent firm rows into a separate tab and narrowed the default visible columns.

Validation:

- `app/dashboard.py` compiles;
- Streamlit dashboard restarted successfully;
- local HTTP smoke test returned 200 at `http://localhost:8501`.

## 2026-05-05 Firm Metric Semantics And Standardization Fix

The Firm Explorer was refined again after the user identified two methodological issues:

- standardized overlays needed an explicit, defensible baseline;
- target labels and calendar fields were appearing inside financial metric selectors.

Changes completed:

- removed target labels from the firm financial metric groups;
- added a separate `Target Timeline` tab for distress, failure-pressure, success, health, and post-event labels;
- replaced `All Numeric` with `All Financial Metrics`, which now includes only financial accounting fundamentals, ratios, and trend/deterioration fields;
- expanded financial selectors to the current usable financial set:
  - 30 SEC accounting fundamentals,
  - 11 financial ratios,
  - 21 firm trend/deterioration features;
- classified `accounts_receivable` under working capital/liquidity, not as a target or generic numeric field;
- added explicit standardization baselines:
  - selected firm window,
  - current sidebar-filtered panel/date baseline,
  - 2009-2018 training-period baseline;
- made macro/regime/event standardization date-level when panel-wide baselines are used, so repeated firm rows do not overweight the same macro date.

Validation:

- `app/dashboard.py` compiles;
- local dashboard smoke test returned 200 at `http://localhost:8501`.

## 2026-05-05 Overview Outcome Composition Fix

The Overview page was refined after the user noticed that success share, failure-pressure share, and strict-distress share did not add to 100%.

Reason:

- the previous chart mixed independent target rates with different denominators;
- strict distress had no nulls and used all rows;
- failure pressure used rows with known future pressure labels;
- success used only rows where the forward success target was observable;
- success, pressure, and strict distress are target labels, not a mutually exhaustive state taxonomy.

Changes completed:

- added a mutually exclusive `outcome_category` for dashboard display:
  - strict legal distress;
  - broader pressure, no legal distress;
  - success/resilience;
  - neutral/surviving;
  - unknown future horizon;
- added `Outcome Composition by Year`;
- added `Target Coverage by Year`;
- renamed confusing cards:
  - `Known failure-pressure labels` became `Failure target observed`;
  - `Known success labels` became `Success target observed`;
- added cards for `Neutral / surviving`, `Unknown outcome horizon`, and target coverage.

Default 2009-2024 outcome mix at the time of this change:

- success/resilience: 11,687 rows;
- broader pressure, no legal distress: 2,708 rows;
- strict legal distress: 207 rows;
- neutral/surviving: 5,521 rows;
- unknown future horizon: 9,388 rows.

Validation:

- `app/dashboard.py` compiles;
- local dashboard smoke test returned 200 at `http://localhost:8501`.
