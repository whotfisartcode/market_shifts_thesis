# Scientific Validity And Limitations Note

Updated: 2026-05-10

This note separates structural readiness from empirical validity.

## Structural Readiness

Structural readiness means the project files load, scripts compile, panels match, dependencies import, and feature blacklist checks pass. The full structural audit is useful, but it does not prove that every empirical claim is true.

## Scientific Validity Layer

The empirical validity case rests on these controls:

- Prediction-date alignment: the production panel uses `prediction_date = filed_date`.
- Temporal validation: models are evaluated on later periods instead of random row splits.
- Leakage control: target and metadata leakage columns are excluded through `config/model_feature_blacklist.csv`.
- P0 audit status:
- `prediction_timestamp`: `PASS`.
- `distress_event_dates`: `PASS`.
- `leakage`: `PASS`.
- `macro_lag`: `PASS`.
- `global_event_timing`: `PASS`.
- `post_event_rows`: `PASS`.
- Target hierarchy: strict legal distress, broader failure pressure, success/resilience, and four validated secondary production outcomes are separated rather than collapsed into one success/failure label.
- Missingness policy: nulls are not invented as zeros; missingness indicators may help prediction but are excluded from economic-factor interpretation.
- Robustness: baseline models, controlled tuning, XGBoost/LightGBM benchmarks, ablations, and factor-group summaries exist.
- SEC concept mapping: concept-map coverage and accounting sanity checks are now reported in `docs/SEC_CONCEPT_MAPPING_AUDIT.md`.

## What Is Proven

- The current package is internally consistent enough to support thesis writing.
- The GitHub-ready panel currently matches the core processed panel.
- The model feature lists do not include blacklisted leakage columns.
- Macro/event variables are aligned to prediction dates by the current audit outputs.
- The four validated secondary production targets passed construction, leakage, temporal-validation, calibration/ranking, and model-output consistency checks.

## What Is Tested But Not Proven As Causal Truth

- Feature importance and factor groups indicate association under the modeling setup, not causal mechanisms.
- Macro/regime/event features provide market-shift context, but current results do not show they dominate firm fundamentals.
- Broader failure pressure is a deterioration/pressure target, not legal bankruptcy.
- The validated secondary production targets support dimensional factor analysis, not replacement of the three primary outcomes.

## What Remains Caveated

- `distress_event_dates` is PASS for the current formal event rows, but strict distress remains a rare-event benchmark rather than a complete legal bankruptcy database.
- SEC concept mapping is conservative and documented, not perfect cross-firm accounting harmonization.
- Success and secondary target coverage is incomplete because future horizons are not always observable.
- Dashboard screenshots must be used with the screenshot capture caveats recorded in `reports/project_audit/dashboard_screenshot_capture.csv`.

## Thesis-Safe Sentence

The project passed structural and reproducibility-readiness checks; empirical validity is assessed through prediction-date alignment, leakage controls, SEC concept-mapping audits, target-validity review, temporal validation, ablation and robustness tests, missingness policy, and explicit limitations.
