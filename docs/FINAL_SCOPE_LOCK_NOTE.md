# Final Scope Lock Note

Updated: 2026-05-12

Current status note: this scope-lock decision remains active, but the panel facts below have been refreshed after the 2026-05-09 caveat-resolution rebuild, 2026-05-10 validated-secondary target promotion, and 2026-05-12 final technical acceptance check. For the complete final checkpoint, use `docs/FINAL_ACCEPTANCE_REPORT_20260512.md` and `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`.

## Decision

The main thesis scope is now locked.

The project will not add new core data sources before submission. The empirical core is:

- SEC Financial Statement Data Sets;
- FRED macro-financial data;
- curated global-event calendar;
- manually curated distress-event dates;
- Streamlit dashboard artifact;
- final reports, figures, and model outputs generated from the local pipeline.

## Why Scope Is Locked

The project is technically strong enough to write if the claims remain disciplined.

Adding RFSD, Hong Kong, Japan, paid data, large-scale NLP, or a live global-event feed would create new data-lineage, cleaning, licensing, validation, and writing risks. These ideas can be discussed as future research, but they should not enter the main empirical model before submission.

## Current Frozen State

Production panel:

```text
data/processed/panel_v2/firm_panel_v2.parquet
data/processed/panel_v2/firm_panel_v2.csv.gz
data/github/firm_panel_v2.parquet
data/github/firm_panel_v2.csv.gz
data/github/firm_panel_v2_schema.csv
```

Current shape:

- 31,702 rows;
- 190 columns;
- 540 SEC CIKs;
- 540 tickers / firm display IDs;
- period range: 2009-03-31 to 2026-02-28;
- prediction timestamp range: 2009-04-15 to 2026-03-31;
- strict `distress_next_4q` positives: 207;
- `prediction_date_source = filed_date` for all rows.

Universe:

- 546 universe rows before duplicate-CIK alias collapse;
- 254 core large-cap universe rows;
- 100 additional-control universe rows;
- 42 distress/near-distress candidate rows;
- 75 event-review expansion firms;
- 75 matched-control expansion firms.

## Locked Claims

Safe claims:

- The panel is reproducible from SEC/FSD, FRED, curated global events, and documented event labels.
- `prediction_date = filed_date` protects temporal validity.
- Strict legal distress is a clean but rare benchmark.
- Broader financial-pressure targets are better suited for factor analysis.
- Missing-aware success/resilience targets are defensible.
- Firm fundamentals, ratios, and deterioration features dominate empirical signal.
- Macro regimes and global events support market-shift context, sector comparison, and dashboard analysis.

Unsafe claims:

- The +150 expansion added 75 confirmed bankrupt firms.
- Strict bankruptcy prediction improved after the +150 expansion.
- Missing total liabilities is an economic cause of success or failure.
- Macro variables alone predict firm failure.
- The dashboard is a real-time bankruptcy prediction system.
- Global-event flags are a complete automated event database.
- The thesis explains every possible cause of company success or failure.

## Remaining Open Items Inside Scope

The following are inside the locked scope:

1. Final thesis manuscript writing and integration.
2. Final documentation consistency review before submission.
3. Final dashboard review in the presentation environment.
4. Final Git or archive freeze with manifest/checksums.
5. GitHub upload after thesis-facing files and claims are locked.

## Version Protection

The current folder is not a Git repository. Therefore no git commit has been made.

Until a GitHub repository is created or Git is initialized, protection means:

- preserve the current `data/processed/panel_v2/` and `data/github/` outputs;
- preserve `reports/RUN_STATUS_FINAL.md`;
- avoid manual edits to production data files;
- run changes through scripts only;
- document every substantial change in `docs/PROJECT_CHRONICLE.md`.
