# Universe Expansion 150 Assessment

Last updated: 2026-05-05

## Decision

The universe was expanded by 150 CIKs using a rule-based selection:

- 75 `expansion_event_review` firms with good SEC coverage until filings ended or changed materially;
- 75 `expansion_matched_controls` firms with long SEC coverage and current SEC ticker mapping.

This is not random data. The selector filters for SEC 10-K/10-Q coverage, U.S. business address, operating-company signals, sector balance, and minimum filing history.

Important caveat:

`expansion_event_review` firms are not automatically formal distress cases. They require manual event verification before being added to `config/distress_event_dates.csv`. Until then, they are useful for historical coverage and broader failure-pressure targets, but they do not increase strict legal-distress positives.

## Files

- Selector script: `scripts/sec_fsd/select_universe_expansion_150.py`
- Baseline universe backup: `config/universe_v2_pre_expansion_20260505.csv`
- Expanded universe: `config/universe_v2_draft.csv`
- Candidate report: `config/universe_expansion_150_candidates.csv`
- Baseline panel backup: `data/processed/panel_v2_pre_expansion_20260505/`
- Validation summary: `reports/data_quality/universe_expansion_150_validation_summary.csv`
- Cohort summary: `reports/data_quality/universe_expansion_150_cohort_summary.csv`
- Parse results: `reports/data_quality/universe_expansion_150_candidate_parse_results.csv`

## Panel Change

Pre-expansion:

- rows: 22,713;
- CIKs: 390;
- tickers: 391.

Expanded:

- rows: 31,786;
- CIKs: 540;
- tickers: 541.

Change:

- +9,073 rows;
- +150 CIKs;
- +150 tickers / firm display IDs.

All 150 selected additions parsed into the panel:

- event-review additions: 75 / 75 parsed;
- matched-control additions: 75 / 75 parsed.

## Cohort Summary

- `core_large_cap`: 15,133 rows, 250 CIKs.
- `additional_controls`: 5,978 rows, 99 CIKs.
- `distress_candidates`: 1,602 rows, 42 CIKs.
- `expansion_event_review`: 4,102 rows, 75 CIKs.
- `expansion_matched_controls`: 4,971 rows, 75 CIKs.

## Audit Status

P0 status after expansion:

- prediction timestamp: PASS;
- leakage: PASS;
- macro lag: PASS;
- global event timing: PASS;
- post-event rows: PASS;
- distress event dates: REVIEW.

One invalid timestamp row was dropped during build and written to:

`reports/data_quality/invalid_prediction_timestamp_rows.csv`

Reason:

- the row had `filed_date < period_date`, which is impossible for a prediction timestamp.

## Missingness Impact

The expansion did not materially damage core data quality.

Selected missingness changes:

- `total_assets`: 0.14% to 0.23%;
- `total_liabilities`: 32.39% to 32.85%;
- `net_income`: 0.35% to 0.52%;
- `total_revenue`: 10.56% to 12.71%;
- `operating_income`: 26.81% to 25.73%;
- `roa`: 0.47% to 0.66%;
- `leverage_assets`: 32.41% to 32.86%.

The missing-aware success target remains clean:

- current success positives after source-verified event-date update: 12,073;
- current unknown rows: 11,617;
- rows currently `0` but revised missing-aware target says unknown: 0;
- known current/revised disagreements: 0.

## Model Impact

This section records the immediate post-expansion result before the later source-verified event-date update. The current production results are better summarized in `docs/CURRENT_STATUS.md` and `reports/RUN_STATUS_FINAL.md`.

Strict legal distress became harder after expansion because the new firms added many non-labeled rows before event-review verification.

Pre-expansion `distress_next_4q`:

- best model: random forest;
- test rows: 4,318;
- test positives: 64;
- PR-AUC: 0.112;
- F1: 0.199.

Expanded `distress_next_4q`:

- best model: gradient boosting;
- test rows before source-verified update: 5,897;
- test positives before source-verified update: 64;
- PR-AUC before source-verified update: 0.060;
- F1 before source-verified update: 0.098.

Interpretation:

Do not use the immediate post-expansion strict-distress model as the current result. After adding eight source-verified event-review cases, current strict test positives are 96 and the best strict model has PR-AUC about 0.068 and F1 about 0.109.

Success/resilience remains strong:

- best model: random forest;
- current test rows: 4,047;
- current test positives: 2,475;
- current ROC-AUC: 0.958;
- current PR-AUC: 0.966;
- current F1: 0.925.

Broader failure-pressure target remains useful:

- `failure_pressure_conservative_v2_next_4obs`;
- current test positives: 514;
- current PR-AUC: 0.739;
- current F1: 0.705.

Diagnostic balance/liquidity failure-pressure target is strong:

- `failure_pressure_balance_liquidity_next_4obs`;
- current test positives: 1,052;
- current PR-AUC: 0.906;
- current F1: 0.813.

## Thesis Interpretation

Safe claim:

> The panel was expanded with 150 rule-selected firms to improve historical coverage and sector-balanced comparison. The expansion improves the usefulness of broader financial-pressure and resilience analysis, while strict legal-distress prediction still depends on verified event dates.

Unsafe claim:

> The expansion added 75 confirmed bankrupt firms.

That is not true yet. They are event-review firms until manually verified.

## Next Step

Manually verify event dates for the most important `expansion_event_review` firms. Good first candidates:

- Rite Aid;
- SunPower;
- Pioneer Natural Resources;
- Activision Blizzard;
- Hawaiian Holdings;
- Six Flags;
- VMware;
- Acorda Therapeutics;
- Pennsylvania Real Estate Investment Trust.

Verified formal distress cases should be added to `config/distress_event_dates.csv`. Mergers/acquisitions should not become formal distress labels, but can be documented as historical exit events.
