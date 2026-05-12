# Full Project Review 2026-05-07

> Superseded historical report. Do not use the row/column counts in this file as current package facts. The current source of truth is `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md` and `docs/FACTUAL_FREEZE_20260509.md`, refreshed on 2026-05-10 for the 31,702 x 190 panel and seven-target production hierarchy.

This review summarizes the current post-rebuild project state. Detailed machine-readable audit outputs are in `reports/project_audit/`, `reports/data_quality/`, `reports/modeling/`, `reports/model_tuning/`, and `reports/model_tuning_advanced/`.

## Scope Audited

- Total files: 2,787.
- Total workspace size: 5.737 GB.
- Main data footprint: about 5.510 GB under `data/`.
- Model artifacts: about 310 MB under `models/`.
- Reports: about 47.7 MB under `reports/`.
- Current docs: 41 files; archived/superseded docs: 21 files.
- Python compile audit: PASS.
- JSON/notebook parse checks: PASS.
- CSV quick checks: PASS.
- Parquet checks: PASS.
- Package smoke test: PASS.
- Required dependency imports: PASS, including pandas, numpy, pyarrow, scikit-learn, Streamlit, XGBoost, and LightGBM.

## Audit Method Limitations

The audit is a strong structural/readiness check, not a proof that every empirical claim is true.

- CSV checks read sample rows, so they detect parse failures and obvious structural issues, not full-file semantic truth.
- SEC ZIP checks verify expected SEC FSD files exist, not that every accounting tag is economically perfect.
- Model-output consistency checks verify saved best-model JSON against saved metric tables; they do not prove causal validity.
- Dependency checks confirm imports in the current local environment, not every possible clean-machine installation scenario.
- Documentation reference checks are intentionally noisy; the current clean audit reports two broken raw SEC path-like references in `docs/MANUAL_HIGH_RISK_AUDIT_20260507.md`.
- Core-vs-GitHub panel equality should be repeated after the final GitHub packaging freeze.

## Current Production State

- Production panel: `data/processed/panel_v2/firm_panel_v2.parquet`.
- GitHub panel copy: `data/github/firm_panel_v2.parquet`.
- Rows: 31,783.
- Columns: 181.
- SEC CIKs: 540.
- Ticker/display IDs: 541.
- Period range: 2009-03-31 to 2026-02-28.
- Prediction-date range: 2009-04-15 to 2026-03-31.
- Prediction-date policy: `prediction_date = filed_date`.
- Core and GitHub panel shapes, columns, and content match.
- Core/GitHub content hash: `bf6ffd28bcbbb618b220e632e9b304cad644d30f05ad7757bd759cddf897ce5f`.
- Infinite numeric values: 0.

## SEC Period-Alignment Fix

The 2026-05-07 manual audit found that selected SEC facts could previously match panel values while still using comparative prior-period `ddate` facts inside a filing. The selector now filters selected SEC facts to `ddate == period`.

Post-rebuild selected-fact provenance:

- selected fact rows: 660,989;
- selected rows with `ddate != period`: 0;
- selected-value mismatches against panel above tolerance: 0;
- selected facts missing from production-panel comparison: 24 documented exclusions.

Spot checks:

- AAPL FY2022 revenue now uses current-period `20220930` and derives Q4 revenue from 2022 cumulative values.
- BKR 2017 Q2 remains a current-period zero-assets/zero-revenue SEC outlier, not a period-alignment bug.

## Target Hierarchy

Current production targets:

- Strict legal benchmark: `distress_next_4q`.
- Main broader failure-factor target: `failure_pressure_conservative_v2_next_4obs`.
- Main success/resilience target: `success_resilience_next_4q`.

Current target counts:

- `distress_next_4q`: 31,783 known rows; 207 positives; 0 missing.
- `failure_pressure_conservative_v2_next_4obs`: 29,883 known rows; 3,011 positives; 1,900 missing.
- `success_resilience_next_4q`: 20,160 known rows; 12,525 positives; 11,623 missing.

## Model Status

Production baseline models were rerun after the SEC period-alignment rebuild.

- `distress_next_4q`: random forest, test ROC-AUC 0.830, PR-AUC 0.105, F1 0.150.
- `failure_pressure_conservative_v2_next_4obs`: random forest, test ROC-AUC 0.950, PR-AUC 0.759, F1 0.730.
- `success_resilience_next_4q`: random forest, test ROC-AUC 0.966, PR-AUC 0.973, F1 0.941.

Controlled tuning robustness:

- 35 candidate configurations per target, 105 total.
- No candidate failures.
- Validation-selected strict distress: `random_forest_cfg2_seed42`, test PR-AUC 0.170, F1 0.178.
- Validation-selected failure pressure: `hist_gradient_boosting_cfg1`, test PR-AUC 0.745, F1 0.724.
- Validation-selected success/resilience: `random_forest_cfg1_seed42`, test PR-AUC 0.973, F1 0.940.

XGBoost/LightGBM robustness:

- 24 candidate configurations per target, 72 total.
- No candidate failures.
- Validation-selected strict distress: `xgboost_cfg1_seed777`, test PR-AUC 0.131, F1 0.197.
- Validation-selected failure pressure: `lightgbm_cfg3_seed777`, test PR-AUC 0.745, F1 0.712.
- Validation-selected success/resilience: `lightgbm_cfg3_seed202`, test PR-AUC 0.974, F1 0.933.

## What Is Strong

- The project has a defensible source-of-truth structure.
- The final target hierarchy is coherent and avoids overloading bankruptcy as the only outcome.
- Timing/leakage audits are strong: prediction timestamp, leakage, macro lag, global-event timing, and post-event row audits pass.
- Model feature lists have zero intersection with `config/model_feature_blacklist.csv`.
- The panel now uses `prediction_date`, not accounting period end, for model time.
- Missing-aware target repair fixed the old success-label contamination risk.
- The SEC selected-fact period-alignment issue has been fixed and provenance-audited.
- The dashboard exposes the final target hierarchy and firm/context views.
- Dashboard screenshots are captured under `reports/figures/dashboard/`.
- The bibliography package is enough for thesis writing.
- XGBoost/LightGBM are tested as robustness benchmarks, so the model section is not thin.

## Main Weaknesses And Hidden Stones

### 1. Strict Legal Distress Remains Source-Curated And Rare

- Current P0 audit status: `distress_event_dates = PASS`.
- Formal strict-distress event rows now have source-provenance records.
- Strict legal distress should still be used as a benchmark, not as a complete legal-bankruptcy database.
- Do not claim full U.S. legal-bankruptcy coverage.

### 2. Strict Legal Distress Remains Rare

- Test positives: 96.
- Best baseline PR-AUC: 0.105.
- Best validation-selected tuning PR-AUC: 0.170.
- Best advanced F1: 0.197.

Thesis implication: strict distress is a clean rare-event benchmark, not the main result.

### 3. Broader Failure Pressure Is Useful But Not Bankruptcy

`failure_pressure_conservative_v2_next_4obs` is strong enough for factor analysis, but it is a broader financial-pressure/deterioration target. Do not call it bankruptcy, legal distress, or actual firm failure.

### 4. Success Target Has High Missingness

- `success_resilience_next_4q` known rows: 20,160.
- Unknown rows: 11,623.
- Positive known rows: 12,525.

Strong success performance is real within known labels, but coverage must be disclosed.

### 5. Duplicate/Amendment Rows Need Disclosure

The duplicate/amendment audit documents deterministic handling and recommends disclosure rather than silent manual panel edits. This is small relative to 31,783 rows but must be mentioned in methodology/limitations.

### 6. Missingness Is Material In Accounting Fields

Average missingness by feature family:

- SEC accounting fundamentals: about 30.5%.
- Financial ratios: about 30.8%.
- Firm trend/deterioration: about 24.6%.
- Event metadata: about 65.7%, expected because not every firm has event metadata.

Thesis implication: do not treat missingness as random; keep missingness indicators separate from economic interpretation.

### 7. Macro/Event Features Are Context, Not Main Predictive Signal

Macro/regime/global-event fields are useful for market-shift context and dashboard comparison, but firm fundamentals, ratios, and deterioration features dominate factor conclusions.

### 8. Global Events Are Curated, Not A Full Event Database

The event layer is a curated historical context layer. Do not describe it as complete automated global-event coverage.

### 9. Current Folder Is Not A Git Repository

`git status` fails because `.git` is missing. Before final GitHub upload, initialize Git or copy the frozen deliverable folder.

### 10. Generated Junk And Local Artifacts Remain

System/junk files and local caches remain in the local workspace. `.gitignore` should exclude them from the GitHub package.

### 11. Dashboard Screenshots Are Captured, With Minor Chart Warnings

All requested dashboard screenshots passed capture. The browser run recorded non-blocking Vega/Altair warnings about empty/infinite chart extents in some views. Use the screenshots, but do not overstate visual QA as exhaustive UI testing.

## Missing Pieces

- Final thesis document body.
- Keep formal strict-distress source-provenance evidence in the final package.
- Final GitHub packaging/upload.
- README/package-facing re-check immediately before upload.
- Explicit methodology wording for amendment duplicates and missing labels.
- Final citation insertion from `docs/BIBLIOGRAPHY.md` and `docs/references.bib`.

## Recommended Next Steps

1. Keep scope frozen.
2. Do not add new core data sources.
3. Treat strict distress as a rare-event benchmark.
4. Use broader failure pressure and success/resilience as the main factor-analysis targets.
5. Use dashboard screenshots from `reports/figures/dashboard/`.
6. Re-check README/package-facing counts after the final packaging freeze.
7. Start thesis writing from `docs/MASTER_DATA_MODEL_TARGET_EXPLAINER.md`, `docs/PROJECT_CHRONICLE.md`, `reports/RUN_STATUS_FINAL.md`, and the bibliography package.
