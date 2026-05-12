# Factual Freeze 2026-05-09

Use this compact table for README, GitHub package, thesis-results, and defense-prep wording unless the panel is rebuilt again. Updated on 2026-05-10 after controlled promotion of four validated secondary production outcomes.

## Current Panel

| Item | Current value |
| --- | ---: |
| Production rows | 31,702 |
| Production columns | 190 |
| SEC CIKs | 540 |
| Ticker/display IDs | 540 |
| Period range | 2009-03-31 to 2026-02-28 |
| Prediction timestamp range | 2009-04-15 to 2026-03-31 |
| Prediction-date policy | `prediction_date = filed_date` |
| Processed/GitHub panel equality | PASS |

## Production Targets

| Target | Known rows | Positives | Missing rows | Role |
| --- | ---: | ---: | ---: | --- |
| `distress_next_4q` | 31,702 | 207 | 0 | Strict legal distress benchmark |
| `failure_pressure_conservative_v2_next_4obs` | 29,805 | 3,003 | 1,897 | Main broader failure-pressure target |
| `success_resilience_next_4q` | 20,152 | 12,519 | 11,550 | Main success/resilience target |
| `industry_relative_resilience_next_4obs` | 20,039 | 8,093 | 11,663 | Validated secondary production outcome |
| `stress_resilience_next_4obs` | 5,901 | 3,707 | 25,801 | Validated secondary production outcome |
| `recovery_next_4obs` | 11,375 | 5,578 | 20,327 | Validated secondary production outcome |
| `quality_success_cashflow_next_4obs` | 16,767 | 9,852 | 14,935 | Validated secondary production outcome |

## Baseline Test Metrics

| Target | Best baseline model JSON | Test rows | Test positives | Test PR-AUC | Test F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| `distress_next_4q` | gradient boosting | 5,872 | 96 | 0.104 | 0.182 |
| `failure_pressure_conservative_v2_next_4obs` | random forest | 5,735 | 575 | 0.758 | 0.725 |
| `success_resilience_next_4q` | random forest | 4,047 | 2,648 | 0.975 | 0.938 |
| `industry_relative_resilience_next_4obs` | gradient boosting | 4,098 | 1,678 | 0.855 | 0.787 |
| `stress_resilience_next_4obs` | random forest | 3,028 | 1,920 | 0.974 | 0.937 |
| `recovery_next_4obs` | random forest | 2,419 | 1,199 | 0.977 | 0.915 |
| `quality_success_cashflow_next_4obs` | gradient boosting | 3,998 | 2,458 | 0.953 | 0.920 |

## Audit And Artifact Status

| Area | Status |
| --- | --- |
| P0 audits | PASS for prediction timestamp, distress event dates, leakage, macro lag, global-event timing, and post-event rows |
| Selected SEC fact provenance | 700,844 selected rows; 0 selected rows with `ddate != period`; 0 selected-value mismatches above tolerance |
| Deterministic duplicate handling | 15 same-information-date amended rows dropped; 0 duplicate ticker/period/prediction groups remain |
| Numeric infinities | 0 |
| Package smoke test | PASS; processed and GitHub panel copies load as `(31702, 190)` and match exactly |
| Validated secondary promotion audit | PASS; row count preserved, schema matches panel, all four promoted columns are `target_label`, post-event rows remain null |
| Dashboard screenshots | PASS for all screenshot views; console row PASS with only known benign Vega-Lite render warnings recorded |

Supporting artifacts:

- `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`
- `reports/RUN_STATUS_FINAL.md`
- `docs/DATA_INTEGRITY_CAVEAT_AUDIT_20260508.md`
- `reports/data_quality/p0_audit_status.csv`
- `reports/data_quality/target_missingness_summary_20260508.csv`
- `reports/project_audit/package_smoke_test_results.csv`
- `reports/project_audit/clean_venv_smoke_test_results.csv`
- `reports/project_audit/model_output_consistency_audit.csv`
- `reports/target_lab/validated_secondary_target_promotion_audit_summary.md`
- `reports/modeling/calibration_metrics.csv`
- `reports/modeling/threshold_ranking_metrics.csv`
- `reports/project_audit/dashboard_screenshot_capture.csv`
