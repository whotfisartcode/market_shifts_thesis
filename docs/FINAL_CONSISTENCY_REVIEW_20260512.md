# Final Consistency Review 2026-05-12

This review checks whether the project documentation, package-facing files, dashboard evidence, and audit outputs are consistent with the final accepted technical state.

## Accepted Current Facts

Use these values in the thesis, README, dashboard discussion, defense answers, and GitHub package:

| Item | Current value |
| --- | --- |
| Production panel | 31,702 rows x 190 columns |
| SEC CIKs | 540 |
| Ticker/display IDs | 540 |
| Prediction-date policy | `prediction_date = filed_date` |
| Primary targets | `distress_next_4q`, `failure_pressure_conservative_v2_next_4obs`, `success_resilience_next_4q` |
| Validated secondary production outcomes | `industry_relative_resilience_next_4obs`, `stress_resilience_next_4obs`, `recovery_next_4obs`, `quality_success_cashflow_next_4obs` |
| Robustness-extension targets | `sector_relative_improvement_next_4obs`, `persistent_resilience_next_6obs` |
| Diagnostic-only target | exploratory `deterioration_next_4obs` |

Controlling documents:

- `docs/FINAL_ACCEPTANCE_REPORT_20260512.md`
- `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`
- `docs/FACTUAL_FREEZE_20260509.md`
- `reports/RUN_STATUS_FINAL.md`

## Review Scope

Reviewed:

- root `README.md`;
- `data/github/README.md`;
- current source-of-truth and status docs under `docs/`;
- package-facing methodology and caveat docs;
- dashboard wording in `app/dashboard.py`;
- dashboard screenshot report and regenerated screenshots;
- full project audit outputs;
- stale-number scans across `README.md`, `data/github/README.md`, `docs/`, `app/`, `reports/RUN_STATUS_FINAL.md`, and `reports/project_audit/`.

## Fixes Made

The review found several current-facing documents that could have caused a reviewer to cite stale pre-promotion facts. These were corrected or explicitly framed as historical:

| File | Consistency action |
| --- | --- |
| `docs/FINAL_SCOPE_LOCK_NOTE.md` | Refreshed current panel shape to 31,702 x 190 and replaced completed open items with remaining freeze-stage work. |
| `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md` | Refreshed panel dimensions to 31,702 x 190 and added a current-status note. |
| `docs/TECHNICAL_QA_RESOLUTION_20260509.md` | Added final-acceptance supersession note; updated audit counts to current 56 Python compile checks, 1,317 CSV checks, and seven-target model consistency. |
| `docs/PCG_PGNPQ_DUPLICATE_CIK_NOTE.md` | Clarified that the original target-recompute check covered the three primary targets at the alias-collapse checkpoint and that current consistency passes for seven production targets. |
| `reports/RUN_STATUS_FINAL.md` | Updated the date and clarified that older 660,989 selected-fact provenance figures were a 2026-05-08 checkpoint; current status is 700,844 selected facts and 371 documented exclusions. |
| `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md` | Added a current-status note explaining that the 186-column snapshot predates validated-secondary target promotion; current panel is 31,702 x 190. |
| `docs/CURRENT_STATUS.md` | Updated the document date to 2026-05-12 while preserving historical sections. |
| `docs/DOCUMENT_ORGANIZATION.md` | Added the final acceptance report to the current source-of-truth list and updated the date. |
| `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md` | Clarified the manual audit report's pre-promotion width and pointed to the final acceptance report for current panel width. |

## Remaining Stale-Number Matches

The final scan still finds old values such as 31,716, 31,717, 31,783, 31,786, 181 columns, and 186 columns in a few locations. These are acceptable because they fall into one of these categories:

- explicit historical sections in `docs/CURRENT_STATUS.md`;
- chronological build history in `docs/PROJECT_CHRONICLE.md`;
- superseded documents with top-of-file warnings, such as `docs/DATA_INTEGRITY_CAVEAT_AUDIT_20260507.md` and `docs/STRATEGIST_HANDOFF_20260505.md`;
- historical audit reports under `reports/project_audit/`;
- explicit warning text that says not to cite 31,702 x 186 as current;
- CSV numeric values where the digit sequence is part of an unrelated financial value.

These should not be used as current facts. The current facts are controlled by the accepted documents listed above.

## Dashboard Consistency

Dashboard evidence was refreshed during this review.

`reports/project_audit/dashboard_screenshot_capture.csv` reports PASS for:

- Overview;
- Data Coverage;
- Models: strict distress;
- Models: failure pressure;
- Models: success/resilience;
- Models: recovery secondary;
- Target Lab overview;
- Target Lab recovery reasons;
- Firm Explorer;
- Macro Compare;
- Artifact Notes;
- console row.

The console row records only known benign Vega-Lite warnings. No dashboard consistency blocker is open.

## Audit Status After Review

Latest project audit status:

| Audit area | Status |
| --- | --- |
| Python compile | PASS, 56 files |
| JSON/notebook parse | PASS, 32 checks |
| CSV quick audit | PASS, 1,317 files |
| Parquet audit | PASS, 962 files |
| ZIP quick audit | PASS, 69 files |
| Model-output consistency | PASS, 7 targets |
| Feature blacklist | PASS, 8 feature-list checks |
| Documentation references | PASS, 0 broken references |
| Required config files | PASS, 6 files |

## Consistency Decision

The package-facing and thesis-facing documentation is consistent enough for manuscript assembly and presentation preparation.

No current-facing document should be cited for 31,716, 31,717, 31,783, 31,786, 181 columns, 185 columns, 186 columns, or 541 ticker/display IDs as current facts.

Use the final accepted current state: 31,702 rows, 190 columns, 540 CIKs, 540 ticker/display IDs, three primary targets, four validated secondary production outcomes, two robustness-extension targets, and diagnostic-only deterioration.

## Next Step

Move to thesis manuscript assembly and final dashboard presentation review. Do not add new empirical scope before freeze unless a blocking factual error is found.
