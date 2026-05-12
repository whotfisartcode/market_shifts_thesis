# Technical QA Resolution 2026-05-09

This note records the post-freeze technical QA cleanup performed after the factual freeze. It does not change the empirical scope, targets, or panel rows.

Current status note, 2026-05-12: the final acceptance checkpoint supersedes the numeric audit counts in this note where later reruns expanded the audit inventory. Use `docs/FINAL_ACCEPTANCE_REPORT_20260512.md` and `reports/project_audit/audit_summary_metrics.csv` for current acceptance counts.

## Documentation Reference QA

- `scripts/project_audit/full_project_audit.py` now filters local references more conservatively, ignoring code fences, archived redundant docs, generated reference TODO files, command text, README directory descriptions, and URL fragments.
- `reports/project_audit/doc_reference_audit.csv` has no actionable missing local references.
- `reports/project_audit/doc_reference_audit_clean.csv` has no actionable missing local references.
- `reports/project_audit/doc_reference_todo.md` states that no actionable missing local references remain.
- `reports/project_audit/audit_summary_metrics.csv` records `doc_references_BROKEN = 0`.

## Dashboard QA

- `app/dashboard.py` now renders charts through explicit Altair wrappers instead of Streamlit native chart wrappers.
- `requirements.txt`, the package smoke test, clean-venv smoke check, and project audit dependency checks now include `altair`.
- `reports/project_audit/dashboard_screenshot_capture.csv` records PASS for all screenshot views and PASS for the console row.
- The console row retains known benign Vega-Lite render warnings for transparency; these are visual-library render warnings, not browser error-level failures and not scientific-validity limitations.
- Remaining dashboard caveats are presentation-density issues on narrow/mobile views and long sidebar controls.

## Manual Logic QA

- `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md` has been regenerated against the current 31,702-row production panel.
- Target recomputation passed for the three primary production targets at this QA checkpoint:
  - `distress_next_4q`;
  - `failure_pressure_conservative_v2_next_4obs`;
  - `success_resilience_next_4q`.
- Later model-output consistency checks pass for all seven production targets after validated-secondary target promotion.
- Formula recomputation still has 229 small REVIEW mismatches. These arise because the manual audit recomputes raw arithmetic formulas while the production builder applies null-preserving extreme-value cleanup. This remains a disclosed accounting/data-quality caveat, not timing leakage or target leakage.

## Current QA Status

- P0 audits: PASS.
- Python compile audit: PASS for 56 files after the final consistency refresh.
- CSV quick audit: PASS for 1,317 files after the final consistency refresh.
- Parquet audit: PASS for 962 files.
- ZIP quick audit: PASS for 69 files.
- Model-output consistency audit: PASS for all seven production targets.
- Feature blacklist audit: PASS.
- Required config audit: PASS.

## Thesis Position

The project is technically usable as an audited empirical artifact. The remaining scientific caveats are substantive and should be disclosed: conservative SEC concept mapping, material missingness, rare strict-distress events, formula-review differences caused by production cleanup policy, and dashboard presentation density. None of these require reopening the empirical panel or changing the target hierarchy.
