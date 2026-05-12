# Thesis Project Audit Review 2026-05-12

Scope: full local workspace review of `/Users/whotfisart/codex/Thesis work`, with the current production package treated as `market_shifts_clean/`.

## Executive Verdict

The technical empirical package is thesis-ready with disclosed caveats. The core panel, audit outputs, model outputs, documentation references, bibliography package, and dashboard evidence are internally consistent after the 2026-05-10 validated-secondary target promotion and the 2026-05-12 final QA refresh.

The main remaining risk is not a model/data blocker. It is submission discipline: choose the correct manuscript file, add the required title page/front matter, refresh the final freeze manifest, and avoid stale historical counts or overclaims in the written thesis.

## Current Accepted Facts

- Production panel: 31,702 rows x 190 columns.
- Identifiers: 540 SEC CIKs and 540 ticker/display IDs.
- Period range: 2009-03-31 to 2026-02-28.
- Prediction timestamp range: 2009-04-15 to 2026-03-31.
- Prediction-date policy: `prediction_date = filed_date` for all rows.
- Primary targets:
  - `distress_next_4q`: 31,702 known, 207 positives, 0 missing.
  - `failure_pressure_conservative_v2_next_4obs`: 29,805 known, 3,003 positives, 1,897 missing.
  - `success_resilience_next_4q`: 20,152 known, 12,519 positives, 11,550 missing.
- Validated secondary production outcomes:
  - `industry_relative_resilience_next_4obs`;
  - `stress_resilience_next_4obs`;
  - `recovery_next_4obs`;
  - `quality_success_cashflow_next_4obs`.

## Verification Performed

- Reran `scripts/project_audit/full_project_audit.py`.
- Reran `scripts/data_quality/run_p0_audits.py`.
- Reran `scripts/project_audit/clean_venv_smoke_check.py`.
- Reran `scripts/project_audit/final_scientific_validity_qa.py`.
- Loaded and checked the production Parquet panel directly.
- Reviewed key source-of-truth docs, target docs, dashboard docs, bibliography docs, requirement inputs, and external review PDFs.
- Extracted and structurally checked both thesis DOCX drafts.

## Audit Results

Latest full-project audit:

- 2,998 files in `market_shifts_clean`.
- 56 Python files compile.
- 32 JSON/notebook files parse.
- 1,317 CSV files quick-load.
- 962 Parquet files load.
- 69 SEC ZIPs quick-load.
- 7 production model-output consistency checks pass.
- 8 model feature-list leakage blacklist checks pass.
- 0 broken documentation references after filtering.
- 6 required config files present.

Latest P0 audit:

- `prediction_timestamp`: PASS.
- `distress_event_dates`: PASS.
- `leakage`: PASS, 0 violations.
- `macro_lag`: PASS, 0 violations.
- `global_event_timing`: PASS, 0 violations.
- `post_event_rows`: PASS, 0 violations.

Direct panel checks:

- Shape: `(31702, 190)`.
- `prediction_date_source`: `{'filed_date': 31702}`.
- Duplicate ticker/period/prediction rows: 0.
- Duplicate CIK/period/prediction rows: 0.
- Post-event rows retained for history: 409.

Package smoke check:

- Required imports pass: pandas, numpy, pyarrow, altair, sklearn, streamlit, xgboost, lightgbm.
- Core and GitHub panels load as `(31702, 190)`.
- Core/GitHub panel equality: PASS.
- Scripts and dashboard compile: PASS.

Scientific-validity summary:

- Structural readiness: PASS.
- Prediction timing: PASS.
- Leakage control: PASS.
- Strict distress event dates: PASS.
- Validated secondary targets: PASS.
- SEC concept mapping: PASS_WITH_CAVEATS.
- Missingness: PASS_WITH_CAVEATS.
- Model validity: PASS_WITH_CAVEATS.
- Dashboard evidence: PASS_WITH_CAVEATS.

## Model Soundness

The model story is coherent if written with target discipline.

- Strict legal distress is clean but rare. Best baseline: gradient boosting, test PR-AUC 0.104, F1 0.182, 96 test positives. It should be a benchmark, not the headline performance claim.
- Broader failure pressure is the main failure-factor target. Best baseline: random forest, test PR-AUC 0.758, F1 0.725, 575 test positives.
- Success/resilience is the main upside target. Best baseline: random forest, test PR-AUC 0.975, F1 0.938, 2,648 test positives.
- Validated secondary targets have strong metrics but should remain dimensional outcomes, not replacements for the three primary targets.
- Feature interpretation should be phrased as association/model behavior, not causality.

## Data Soundness

Strengths:

- SEC selected facts now require `ddate == period`, preventing prior-year comparative facts from being selected as current-period facts.
- Selected-fact provenance has 700,844 selected rows, 0 `ddate != period`, and 0 selected-value mismatches above tolerance.
- Same-information-date amendment duplicates are resolved deterministically in the builder.
- PCG/PGNPQ duplicate-CIK alias handling is resolved by keeping one CIK history and preserving alias metadata for event lookup.
- Core/GitHub processed panels are exactly equal.

Residual caveats:

- SEC concept mapping is conservative and audited, but not perfect taxonomy harmonization.
- Missingness is material and must remain disclosed.
- Accounting identity sanity is good but not perfect; the documentation correctly treats it as plausibility evidence, not perfect reconciliation.
- Strict distress is source-curated and rare, not a universal legal bankruptcy database.

## Manuscript Readiness

The current thesis-writing assets are strong enough to assemble the thesis:

- `docs/thesis_academic_manuscript_no_title_page.docx`: about 16,620 words and 126,672 characters including tables.
- `docs/thesis_first_draft_no_title_page.docx`: older parallel draft, about 16,438 words.
- Bibliography: 75 BibTeX entries, no duplicate keys, all with DOI/URL metadata.
- Bibliography audit: 58 academic journal articles, 62 peer-reviewed sources, 27 recent 2020+ sources.

Manuscript risks:

- There are two DOCX thesis drafts. The current-looking one is `docs/thesis_academic_manuscript_no_title_page.docx`; the older `docs/thesis_first_draft_no_title_page.docx` should not be the submission source unless deliberately chosen.
- Both thesis DOCX files are explicitly `no_title_page`. HSE requirements include a title page, so final submission needs a title page/front matter package.
- DOCX visual QA could not be completed in this environment because LibreOffice/`soffice` is unavailable.
- The manuscript should include exact target-threshold definitions for the broader failure-pressure target if those thresholds are quoted or defended.

## Release/Repository Risks

- The current workspace root is not a Git repository.
- `last_years_thesis_data/` contains a separate old `.git` project and 2.6 GB of historical material. It must not be mixed into the current release.
- The package-level `.gitignore` is useful only if the repository root is `market_shifts_clean/`. If Git is initialized at `/Users/whotfisart/codex/Thesis work`, add a root-level ignore or upload only `market_shifts_clean/`.
- The reproducibility freeze manifest is still named `freeze_manifest_20260507.csv` and contains stale checksums for files updated after May 7. Refresh it before final upload/archive.
- `requirements.txt` is unpinned. This is acceptable for local work but weak for long-term reproducibility; freeze exact versions before final archival.
- Full raw SEC ZIP rebuild reproducibility is Level 2 only: the raw ZIPs are local and intentionally excluded from GitHub.

## Priority Fix List

1. Select one manuscript file, preferably `docs/thesis_academic_manuscript_no_title_page.docx`, and retire or clearly mark the older draft.
2. Add the official HSE title page and final front matter.
3. Open/render the DOCX in Word/LibreOffice and visually inspect all tables, page breaks, headers/footers, and references.
4. Refresh a final freeze manifest/checksum set after manuscript and dashboard wording are locked.
5. Decide the Git root. Prefer `market_shifts_clean/`, not the whole `Thesis work/` directory.
6. Freeze dependency versions or at least capture `pip freeze`/environment metadata for the final archive.
7. In the thesis methodology, state exact broader failure-pressure thresholds or explicitly cite the code/report appendix where they are defined.
8. Keep the final claims aligned with `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`: no AutoGluon, no causal feature-importance claims, no complete bankruptcy-database claim, no perfect SEC-taxonomy claim.

## Final Recommendation

Move into thesis writing and submission packaging. Do not add new empirical scope unless a blocking factual error is found. The technical project is sufficiently sound; the main work now is manuscript discipline, final visual QA, and release freeze.
