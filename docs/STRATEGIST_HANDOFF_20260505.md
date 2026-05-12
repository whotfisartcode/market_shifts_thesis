# Strategist Handoff 2026-05-05

> Superseded status note, 2026-05-10: this file is retained as a historical strategist handoff. It contains stale panel dimensions and model numbers from an earlier rebuild. For current production facts, use `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`, `docs/FACTUAL_FREEZE_20260509.md`, `docs/CURRENT_STATUS.md`, and `reports/RUN_STATUS_FINAL.md`.

Purpose: concise state package for strategic review by GPT-5.5 Pro / external strategist. It has been refreshed after the 2026-05-08 alias-collapse rebuild and post-rebuild model/interpretation rerun, and should be used together with `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`, `reports/RUN_STATUS_FINAL.md`, and `docs/PROJECT_CHRONICLE.md`.

## 2026-05-08 Post-Rebuild Model Update

Some detailed tables in this handoff originated before the final alias-collapse rebuild. The current source-of-truth model numbers are `reports/RUN_STATUS_FINAL.md`, `docs/CURRENT_STATUS.md`, and `reports/modeling/post_rebuild_model_summary_20260508.csv`.

- `distress_next_4q`: strict rare-event benchmark; baseline random forest test PR-AUC 0.157, F1 0.147; XGBoost robustness gives the highest threshold F1 at 0.241 with lower PR-AUC 0.121.
- `failure_pressure_conservative_v2_next_4obs`: main failure-factor target; baseline random forest test PR-AUC 0.764, F1 0.731.
- `success_resilience_next_4q`: success/resilience counterpart; baseline random forest test PR-AUC 0.973, F1 0.942; LightGBM robustness PR-AUC 0.974, F1 0.938.

## Source Of Truth

Use these files as current references:

- `docs/STRATEGIST_HANDOFF_20260505.md` — consolidated current-state handoff.
- `reports/data_quality/readiness_table_20260505.csv` — compact PASS / REVIEW / TODO readiness table.
- `reports/RUN_STATUS_FINAL.md` — current run/audit/model status.
- `docs/FINAL_TARGET_HIERARCHY.md` — final target hierarchy and wording guardrails.
- `docs/PROJECT_CHRONICLE.md` — full decision log and reasoning trail.
- `docs/BIBLIOGRAPHY.md` and `docs/references.bib` — curated references.
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md` — model-tuning, XGBoost/LightGBM benchmark, and AutoGluon positioning.

Older experiment notes remain useful as historical evidence, but the files above should control current decisions.

## Current Project Position

The thesis is viable without changing the topic or adding new core data sources. The empirical core is now a U.S. public-company SEC/FRED/global-event panel with temporal prediction dates, model outputs, dashboard artifact, audit reports, and a curated bibliography.

Current production panel:

- rows: 31,716;
- columns: 185;
- SEC CIKs: 540;
- ticker/display IDs: 540;
- accounting period range: 2009-03-31 to 2026-02-28;
- prediction timestamp range: 2009-04-15 to 2026-03-31;
- prediction-date policy: `prediction_date = filed_date` for all rows.

Current audit status:

- prediction timestamp: PASS;
- leakage: PASS;
- macro lag: PASS;
- global-event timing: PASS;
- post-event rows: PASS;
- distress event dates: PASS.

The remaining integrity risks are accounting-mapping caveats, accounting outlier disclosure, duplicate/amendment disclosure, material missingness disclosure, dashboard warning disclosure, and final GitHub packaging. The SEC selected-fact period-alignment code has been fixed; formal strict-distress event-date provenance is source-verified for the current package; the panel, provenance sidecar, P0 audits, target profiles, integrity audits, models, tuning/boosting reports, feature interpretation, dashboard screenshots, and rendered UI/project QA have been regenerated or refreshed after the 2026-05-08 alias-collapse rebuild.

## Dataset And Dashboard Coverage

Panel feature families:

- 30 SEC accounting fundamentals;
- 11 financial ratios;
- 21 firm trend/deterioration features;
- 31 macro variables;
- 11 macro regime indicators;
- 27 global-event context columns;
- 10 target labels;
- metadata and event-audit fields.

Final verification:

- no infinite numeric values were found;
- all 62 usable financial fields are exposed in the dashboard Firm Explorer;
- all 68 chartable macro/regime/global-event fields are exposed in the dashboard;
- model feature lists have zero intersection with `config/model_feature_blacklist.csv`.

Dashboard artifact:

- Streamlit app: `app/dashboard.py`;
- local URL: `http://localhost:8501`;
- current views: Overview, Data Coverage, Models, Target Lab, Firm Explorer, Artifact Notes;
- Overview now separates mutually exclusive outcome composition from independent target rates;
- Firm Explorer now separates firm financial metrics, macro comparison, target timeline, and recent rows;
- macro comparisons show explicit standardization baseline.

Final screenshot plan:

- Overview outcome composition and target coverage;
- Firm Explorer financial metrics;
- Macro Compare with training-period baseline;
- Models tab with target-specific metrics and top features;
- Target Lab with factor groups / target experiments.

Screenshots have been saved under `reports/figures/dashboard/`; the capture report records all requested screenshots as PASS plus non-blocking chart-library warnings for review.

## Target Hierarchy

Use a target hierarchy, not one overloaded target.

1. Strict legal benchmark: `distress_next_4q`
   - production column;
   - 207 full-panel positives;
   - 96 temporal test positives;
   - use as clean legal distress benchmark and robustness anchor;
   - do not use as headline model-performance claim.

2. Main failure-factor target: `failure_pressure_conservative_v2_next_4obs`
   - production column;
   - 29,819 known labels;
   - 3,007 full-panel positives;
   - 575 temporal test positives;
   - use as the main broader financial-pressure outcome.

3. Main success/resilience target: `success_resilience_next_4q`
   - production column;
   - 20,160 known labels;
   - 12,525 full-panel positives;
   - 2,648 temporal test positives;
   - use as success/resilience counterpart.

4. Diagnostic / robustness targets:
   - `failure_pressure_balance_liquidity_next_4obs`;
   - `success_resilience_quality_v2_next_4obs`.
   These remain experiment-output targets unless separately productionized.

## Model Results

These model results are the post-2026-05-08 alias-collapse rebuild outputs.

Strict legal distress, `distress_next_4q`:

- best baseline model: random forest;
- test rows: 5,873;
- test positives: 96;
- ROC-AUC: 0.798;
- PR-AUC: 0.157;
- precision: 0.147;
- recall: 0.146;
- F1: 0.147.

Broader failure pressure, `failure_pressure_conservative_v2_next_4obs`:

- best model by PR-AUC/F1: random forest;
- test rows: 5,735;
- test positives: 575;
- ROC-AUC: 0.955;
- PR-AUC: 0.764;
- precision: 0.679;
- recall: 0.793;
- F1: 0.731.

Success/resilience, `success_resilience_next_4q`:

- best model: random forest;
- test rows: 4,047;
- test positives: 2,648;
- ROC-AUC: 0.966;
- PR-AUC: 0.973;
- precision: 0.938;
- recall: 0.946;
- F1: 0.942.

Interpretation position:

- strict legal distress is too rare to be the headline performance story;
- broader failure pressure is the defensible failure-factor analysis target;
- success/resilience is empirically strong;
- feature-group conclusions should be emphasized over isolated individual features;
- missingness indicators may help prediction but must not be described as economic causes.

## Model Tuning Robustness Pass

A controlled tuning/seed robustness pass now supplements the production models. It did not overwrite `models/panel_v2/`.

Protocol:

- 35 candidate configurations per production target;
- 105 candidate configurations total;
- train through 2018, validation 2019-2021, test 2022-2024;
- candidate choice and thresholds use validation data only;
- candidate failures: 0.

Validation-selected tuned candidates:

- `distress_next_4q`: `extra_trees_cfg3_seed777`, test PR-AUC 0.144, F1 0.195.
- `failure_pressure_conservative_v2_next_4obs`: `hist_gradient_boosting_cfg2`, test PR-AUC 0.745, F1 0.710.
- `success_resilience_next_4q`: `random_forest_cfg1_seed42`, test PR-AUC 0.972, F1 0.941.

Interpretation:

- tuning improves strict distress threshold F1 but does not make strict legal distress a strong headline target;
- tuning supports broader failure-pressure robustness, while the baseline random forest remains stronger on test PR-AUC/F1;
- the success/resilience result is stable across baseline and tuning models;
- AutoGluon was not installed or used, so do not claim exhaustive AutoML optimization.

Advanced XGBoost/LightGBM benchmark:

- 24 candidate configurations per target, 72 total;
- candidate failures: 0;
- `distress_next_4q`: validation-selected XGBoost, test PR-AUC 0.121, F1 0.241;
- `failure_pressure_conservative_v2_next_4obs`: validation-selected XGBoost, test PR-AUC 0.744, F1 0.713;
- `success_resilience_next_4q`: validation-selected LightGBM, test PR-AUC 0.974, F1 0.938.

Interpretation:

- XGBoost/LightGBM provide boosted-tree robustness evidence; XGBoost improves strict-distress threshold F1, while random forest remains stronger for the broader failure-pressure headline metrics;
- production random forest still remains the strongest success/resilience headline model by F1, while LightGBM is slightly higher by PR-AUC;
- describe these as advanced boosted-tree robustness benchmarks, not AutoML.

## Results Interpretation

Current feature-group evidence supports the thesis story:

- strict distress: firm trend/deterioration, accounting fundamentals, and ratios dominate;
- broader failure pressure: profitability, prior losses, ROA, margins, and balance stress are central;
- success/resilience: equity/assets, leverage/assets, profitability, and prior loss history dominate;
- macro/regime/event variables are useful context and dashboard dimensions, but not the dominant predictive factor group in the current models.

Recommended wording:

- "macro-regime-aware" is defensible because macro/regime/event variables are present, audited, dashboarded, and evaluated;
- do not claim that macro variables dominate firm fundamentals;
- do not claim causal effects from feature importance;
- do not call broader pressure "bankruptcy" or "formal distress."

## Remaining Risks

REVIEW:

- Some event-review expansion firms may be M&A, ticker-change, coverage-ending, or ordinary exits, not formal distress.
- Strict legal distress results remain weak because formal events are rare.
- Amendment/duplicate filing rows are audited but not manually removed; methodology must disclose the policy.
- Dashboard screenshots exist, but screenshot capture reports non-blocking chart-library warnings.

Do not do before submission:

- no RFSD, Hong Kong, Russia, paid data, NLP, or live event-feed expansion in the main model;
- no random firm expansion;
- no market-price features unless handled as future work;
- no manual edits to production panel files;
- no claims that target labels are complete legal truth without event-date provenance caveats.

## Thesis Substance And 85-Page Feasibility

There is enough material for an 85-page thesis if written as a research-format empirical artifact:

1. Introduction and research problem.
2. Literature review: distress prediction, business analytics, XAI, missing data, dashboard/design-science artifact.
3. Data and panel construction: SEC FSD, FRED, global events, universe expansion, prediction-date logic.
4. Target construction and integrity controls: strict distress, broader pressure, success/resilience, missing-aware logic.
5. Modeling methodology: temporal split, models, imbalance handling, PR-AUC/ROC-AUC/F1, leakage controls.
6. Results: target balance, model comparison, feature groups, sector/regime/event context.
7. Dashboard artifact: practical decision-support value, screenshots, reproducibility.
8. Limitations and future research: event verification, market data, international/Russian comparison, automated event feeds.

Appendices should include:

- data dictionary and feature-family table;
- P0 audit summary;
- missingness tables;
- model metrics;
- feature-group contribution tables;
- dashboard screenshots;
- GitHub/reproducibility notes.

## Final Scientific-Validity QA Addendum

Updated 2026-05-07:

- Scientific-validity note: `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`.
- SEC concept mapping audit: `docs/SEC_CONCEPT_MAPPING_AUDIT.md`.
- Amendment/duplicate handling note: `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md`.
- Thesis claim guardrails: `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`.
- Package smoke test: `reports/project_audit/package_smoke_test_report.md`.
- Clean virtualenv smoke test: `reports/project_audit/clean_venv_smoke_test_results.csv`.
- Dashboard screenshots: `reports/figures/dashboard/`.
- Appendix evidence index: `reports/final_thesis_appendix_pack/README.md`.

Current QA position:

- structural readiness: PASS;
- prediction timing: PASS;
- leakage control: PASS;
- SEC concept mapping: PASS with caveats;
- missingness: PASS with caveats;
- model validity: PASS with caveats;
- dashboard evidence: PASS with caveats;
- strict distress event dates: PASS.

## Recommended Next Actions

1. Consolidate docs before strategist review.
   - Trust the source-of-truth files listed above.
   - Treat older target-experiment notes as historical unless marked current.

2. Keep event-date provenance frozen unless adding new evidence.
   - Current formal strict-distress rows are source-verified.
   - Continue event-review firm classification only if new firms are being considered for strict legal-distress labeling.

3. Use captured dashboard screenshots.
   - Source folder: `reports/figures/dashboard/`.
   - Screenshot report: `reports/project_audit/dashboard_screenshot_capture.csv`.

4. Start writing from the actual outputs.
   - Use `docs/PROJECT_CHRONICLE.md` for reasoning.
   - Use `reports/RUN_STATUS_FINAL.md` and this handoff for current metrics.
   - Use `docs/BIBLIOGRAPHY.md` for citation placement.

5. Keep scope frozen.
   - Further data expansion should be future research, not a main-model change.
