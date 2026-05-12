# Distress Event Date Provenance

Updated: 2026-05-10

This note records the current scientific-validity status of strict distress event dates.

## Current Status

- Formal distress rows: 44.
- Source-verified formal distress rows: 44.
- Formal distress rows still requiring source review: 0.
- Near-distress/context rows not used as strict distress: 6.
- Output audit: `reports/data_quality/final_distress_event_date_audit.csv`.
- Source evidence table: `config/distress_event_source_provenance.csv`.

## Interpretation

All formal strict-distress event dates in `config/distress_event_dates.csv` have source-provenance records in `config/distress_event_source_provenance.csv`.

Near-distress rows are context labels only and are not treated as strict legal distress.

Panel-coverage notes can still appear when an event occurs before the first available prediction row or after the last available SEC filing row for that firm. Those notes affect how many pre-event rows can be labeled; they are not evidence that the event date itself is unverified.

## Thesis Wording

Use: "Strict distress events were source-curated and separately audited. All formal strict-distress event dates used in the current event configuration have source-provenance records; non-strict near-distress rows are retained only as context."

Do not use: "The strict distress target is a complete legal bankruptcy database for the U.S. market."

