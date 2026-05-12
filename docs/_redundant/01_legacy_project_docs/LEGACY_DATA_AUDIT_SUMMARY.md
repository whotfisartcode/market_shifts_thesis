# Legacy Data Audit Summary

This note summarizes the first-pass audit of the defended-thesis panel copied into `data/processed/legacy_2025/`.

## Panel Shape

- Rows: 14,104
- Columns: 58
- Firms: 255
- Date range: 2008-10-02 to 2025-05-09
- Duplicate ticker-date rows: 1

## Main Data Quality Risks

- `altman_z` is missing in about 93.5% of rows.
- `r_and_d_intensity`, `inventory_turnover`, `gross_margin`, and `Z_MVE_TL` are each missing in more than 82% of rows.
- `price` is missing in about 68.5% of rows.
- Several financial statement columns contain impossible or suspicious negative values.
- The old modeling notebook created targets outside the saved panel, so the panel itself does not preserve the thesis target definitions.
- The old model split was random, which is weak for a time-series/business-cycle thesis.

## Implication

The legacy panel is useful as a reference and partial baseline, but the thesis should be rebuilt around a cleaner firm-quarter panel with:

- stable SEC Financial Statement Data Set parsing,
- explicit forward-looking success/distress labels,
- macro variables lagged relative to the prediction date,
- temporal validation,
- explainable models and sensitivity checks.

Machine-readable audit outputs are in `reports/data_quality/`.
