# Strategic Next Steps Review Assessment

Updated: 2026-05-05

Source reviewed:

```text
/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/strategic_next_steps_20260505.json
```

## Verdict

The review is mostly right and should be accepted as the strategic direction, with several important corrections and guardrails.

The strongest recommendation is correct:

> Freeze the scope, stop adding new core data sources, verify event dates, finalize a small target hierarchy, refine the dashboard, and start writing from the actual reports.

This is the right direction because the project now has enough empirical substance to support a thesis, and the biggest remaining risk is overclaiming or destabilizing the pipeline.

## Claims That Checked Out

The review's main factual project-state claims matched the local data and reports at the time of assessment. The later source-verified event-date merge changed the current strict-distress and success metrics; use `docs/CURRENT_STATUS.md` and `reports/RUN_STATUS_FINAL.md` for current numbers.

- production panel: 31,786 rows and 181 columns after the later broader-target promotion;
- SEC CIKs: 540;
- tickers / display IDs: 541;
- period range: 2009-03-31 to 2026-02-28;
- prediction timestamp range: 2009-04-15 to 2026-03-31;
- `prediction_date_source = filed_date` for all current panel rows;
- universe rows: 546;
- +150 expansion split: 75 `expansion_event_review` and 75 `expansion_matched_controls`;
- P0 status: all PASS except distress event dates, which remain REVIEW;
- strict `distress_next_4q` expanded-panel best model: gradient boosting, test rows 5,897, positives 64, ROC-AUC about 0.749, PR-AUC about 0.060, F1 about 0.098;
- `success_resilience_next_4q` expanded-panel best model: random forest, test rows 4,048, positives 2,481, ROC-AUC about 0.959, PR-AUC about 0.967, F1 about 0.928;
- missing-aware success target status: 20,169 known rows, 11,617 unknown rows, 12,157 positive rows among known rows;
- broader target experiment results matched the compact target-tweak reports at the time:
  - `failure_pressure_conservative_v2_next_4obs`: PR-AUC about 0.736, F1 about 0.702;
  - `failure_pressure_balance_liquidity_next_4obs`: PR-AUC about 0.907, F1 about 0.816.

The review is also right that strict legal distress should be a clean benchmark, not the headline performance story.

## Corrections And Guardrails

### 1. Broader Pressure Target Status Changed After This Review

The review was correct that broader targets were strategically needed. After the later controlled production pass, `failure_pressure_conservative_v2_next_4obs` was promoted into:

```text
data/processed/panel_v2/firm_panel_v2.parquet
```

Current production panel contains:

- `failure_pressure_conservative_v2_next_4obs`.

Current production panel does not contain the remaining diagnostic/experimental targets:

- `failure_pressure_balance_liquidity_next_4obs`;
- `success_resilience_quality_v2_next_4obs`;
- `success_composite_strict_next_4obs`.

Decision:

- use them now as documented experiment outputs;
- promote only selected final targets into `scripts/sec_fsd/build_panel_v2.py` if time allows and if we rerun all audits and final reports afterward;
- do not write as if they are production-panel columns until promotion happens.

### 2. Event-Review Firms Are Not Distress Firms

The review's first event-verification candidate list is useful, but potentially misleading.

The local universe marks these firms as `expansion_event_review` because SEC coverage ended or changed materially. That does not mean they are distressed.

Examples from the review list that must be treated as classification checks, not presumed distress:

- Activision Blizzard;
- VMware;
- Pioneer Natural Resources;
- Hawaiian Holdings;
- Six Flags Entertainment.

These may be acquisition, merger, ordinary delisting, or restructuring cases rather than formal distress. They should not enter `distress_next_4q` unless source verification proves formal distress.

Decision:

- classify each event-review firm as formal distress, near distress, M&A/transaction, normal exit, missing evidence, or exclude;
- add only verified formal distress events to `config/distress_event_dates.csv`;
- document non-distress coverage endings separately if useful for the dashboard or appendix.

### 3. Git Commit Is Conditional

The review recommends creating a git commit or local backup. That is good practice, but the current local workspace is not a Git repository.

Decision:

- do not pretend a commit exists;
- use a local snapshot/backup unless a Git repo is initialized or the GitHub deliverable repo is created;
- document current file versions in `reports/RUN_STATUS_FINAL.md` and the scope-lock note.

### 4. Grade Estimate Is Not Evidence

The review's "7.5-8.0/10" assessment is a useful sanity estimate, but it is subjective.

Decision:

- do not cite or rely on that number in the thesis;
- use it only as informal project-risk feedback.

### 5. Dashboard Recommendation Is Correct, But Current Dashboard Only Partly Meets It

The dashboard already has:

- overview;
- data coverage;
- model metrics;
- Target Lab;
- firm explorer;
- artifact notes.

It still needs to be more thesis-ready:

- clearer target hierarchy;
- sector/regime/global-event comparison;
- factor-group interpretation separated from missingness indicators;
- data-quality and caveat page;
- screenshot-ready layout and saved screenshots.

Decision:

- dashboard refinement is a P2 task after scope lock, event-date review, and final target decision.

### 6. The Review Source List Is Slightly Incomplete

The JSON lists 11 source documents. The project documentation set also includes other updated status/scope files such as `DATA_MANIFEST.md` and `TOPIC_RELEVANCE_AND_SCOPE_NOTE.md`.

This is not a substantive error, but it means the review should be treated as strategic guidance, not a complete documentation audit.

## Accepted Strategy

Accepted:

- freeze scope;
- do not add RFSD, Japan, Hong Kong, NLP, paid data, or live event feeds into the main model before submission;
- keep U.S. SEC/FRED/global-event panel as the empirical core;
- verify distress event dates;
- use strict legal distress as benchmark;
- use broader financial pressure for main factor analysis if promoted or clearly documented as experiment output;
- use missing-aware success/resilience as the success side;
- keep missingness indicators out of economic interpretation;
- frame macro/regime/global-event variables as market-shift context and sector comparison, not the main predictive engine.

Rejected or modified:

- no automatic claim that the +150 expansion added formal distress firms;
- no claim that strict bankruptcy prediction improved after expansion;
- no assumption that coverage-ended event-review firms are failures;
- no claim that final broader targets are production-panel fields until code promotion happens;
- no git-commit claim while the folder is not a Git repository.

## Final Strategic Position

The thesis should now be positioned as:

> A reproducible SEC/FRED firm-period panel and Streamlit decision-support dashboard for analyzing forward-looking legal distress, broader financial pressure, and resilience across industries under macro-regime and global-event market shifts.

The main empirical story:

1. Strict legal distress is clean but rare and difficult.
2. Broader financial-pressure targets capture meaningful deterioration better.
3. Success/resilience is strong after missing-aware target repair.
4. Firm fundamentals, ratios, and deterioration features dominate the predictive signal.
5. Macro regimes and global events provide context for market shifts, sector comparison, and dashboard interpretation.

## Next-Step Decision

Priority order from here:

1. Freeze scope and record the final working state.
2. Verify event dates and classify event-review firms.
3. Finalize and possibly productionize the target hierarchy.
4. Rerun audits and final model/figure/table generation.
5. Refine dashboard and capture screenshots.
6. Write the thesis from saved reports, figures, and the chronicle.
