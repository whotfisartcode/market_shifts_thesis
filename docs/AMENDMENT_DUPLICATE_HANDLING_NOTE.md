# Amendment And Duplicate Filing Handling Note

Updated: 2026-05-10

This note documents the duplicate/amendment audit for the production panel.

## Current Finding

- Current duplicate `(ticker, period_date, prediction_date)` groups: 0.
- Current duplicate extra rows under that key: 0.
- Exact duplicate full rows: 0.
- Deterministically dropped same-information-date rows recorded by the build/QA pipeline: 15.
- Audit output: `reports/data_quality/amendment_duplicate_audit.csv`.
- Dropped-row audit file: `reports/data_quality/dropped_duplicate_filing_rows.csv`.

## Policy

Same CIK/period/prediction-date duplicates are resolved in the build pipeline using deterministic information-date logic: prefer the original non-amended filing, then stable accession-number ordering. Original and amended filings with different prediction dates are not automatically collapsed, because they represent different information dates.

For thesis wording, state that same-information-date amendment duplicates were handled deterministically upstream and separately audited.

## Thesis Wording

Use: "A duplicate/amendment audit identified a very small number of repeated filing-period information dates. Same-information-date original/amended duplicates were resolved deterministically in the build pipeline, while amendments filed on later dates were retained as separate information events."

Do not use: "The panel is guaranteed to contain exactly one row per economic firm-period under every identifier definition."
