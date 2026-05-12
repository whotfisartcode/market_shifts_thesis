# Universe Expansion Plan

The thesis should add smaller and distressed firms, but the expansion must be rule-based. A random list of smaller companies would mostly add missing data and weaken the defense.

## Target Structure

Use three cohorts:

1. `core_large_cap`: the existing 255-firm defended-thesis panel.
2. `additional_controls`: the existing 100 extra tickers from `config/ticker100more.txt`, subject to SEC coverage checks.
3. `distress_candidates`: bankrupt, failed-bank, delisted, or severe near-distress public companies from `config/distress_candidate_seed.csv`, subject to SEC coverage checks.

This should produce a defensible final universe of about 350-450 firms after coverage filtering.

## Inclusion Rules

A company should enter the rebuilt panel only if it passes these checks:

- It has at least 8 quarterly or annual 10-Q/10-K observations in the downloaded SEC Financial Statement Data Set ZIPs.
- It has at least one usable pre-event observation if it is a distress case.
- Its core accounting tags are recoverable for assets, liabilities, revenue, net income, cash, operating cash flow, and shares/equity where available.
- It can be assigned a stable `firm_id`, preferably CIK, even if the ticker was delisted or changed.
- It is not included merely because it is famous; there must be data coverage and a clear label definition.

## Labeling Policy

Separate labels are cleaner than one vague "failure" label:

- `distress_event`: bankruptcy, bank failure, liquidation, or delisting-related distress.
- `near_distress`: severe distress without formal bankruptcy.
- `survivor_control`: no observed distress event in the thesis horizon.

For modeling, the strongest target should be forward-looking:

- `distress_next_4q`: 1 if a formal distress event occurs within the next four quarters.
- `success_next_4q`: 1 if profitability, margin, market-return, or Altman-style health stays above a defined threshold over the next four quarters.

## Why This Helps the Thesis

The old panel mainly contains surviving large U.S. companies. Adding a coverage-checked distressed cohort directly answers the defense criticism about lack of failure cases and makes the title more credible. Keeping matched controls prevents the sample from becoming only distressed anecdotes.

## Current Limitation

The downloaded SEC ZIPs currently start at 2019q1. That is enough for recent failures, but it weakens long-horizon analysis and omits clean pre-2019 histories for older distressed cases. For a thesis horizon near 2009-2025, download the SEC FSD ZIPs back to 2009q1.

## Current Draft Output

The generated draft universe is in `config/universe_v2_draft.csv`.

Current result from the downloaded ZIPs after adding the 2009-2018 SEC files:

- 254 core large-cap CIK rows. The old panel has 255 tickers, but `GOOG` and `GOOGL` collapse to the same SEC CIK.
- 100 additional-control tickers from `ticker100more.txt`.
- 42 distressed or near-distressed candidates with at least 8 SEC 10-K/10-Q submissions in the downloaded ZIPs.
- 1 additional control, `SW`, is pending because it has only 7 downloaded SEC submissions.

Generated support files:

- `data/interim/sec_submissions_index.csv`
- `reports/data_quality/sec_submission_coverage_by_cik.csv`
- `reports/data_quality/sec_submission_coverage_by_zip.csv`
- `reports/data_quality/distress_candidate_coverage.csv`

The matcher reads both `config/distress_candidate_seed.csv` and the older `config/distressed_candidates_seed.csv`, then resolves matches against the SEC submission coverage index.

Regenerate with:

```bash
python3 scripts/sec_fsd/index_submissions.py
python3 scripts/sec_fsd/match_distress_candidates.py
python3 scripts/sec_fsd/build_universe_v2.py
```
