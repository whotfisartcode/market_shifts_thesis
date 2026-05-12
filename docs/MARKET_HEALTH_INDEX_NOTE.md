# Market Health Index Note

Updated: 2026-05-05

## Decision

The project now includes a separate market-health index built from existing macro, regime, and global-event context.

This does not change the production firm panel. It is a reporting/dashboard layer that helps explain "market shifts" in a compact way.

Script:

```text
scripts/features/build_market_health_index.py
```

## Purpose

The thesis already has many macro variables. The index converts them into a smaller set of interpretable market-state components:

- `credit_stress_score`;
- `rate_pressure_score`;
- `inflation_pressure_score`;
- `demand_weakness_score`;
- `market_volatility_score`;
- `event_stress_score`;
- `market_stress_score`;
- `market_health_score`;
- `market_health_regime`.

Higher `market_stress_score` means more stressful macro/event conditions. Higher `market_health_score` means healthier macro/event conditions.

## Integrity Policy

- The index is computed only from values already aligned to `prediction_date`.
- Standardization uses the training-period window, prediction years 2009-2018.
- It is not a target and not a bankruptcy label.
- It is not presented as a causal proof that macro conditions dominate firm fundamentals.
- It should be used for dashboard context, sector/regime comparison, and thesis interpretation.

## Outputs

```text
reports/data_quality/market_health_index_audit.csv
reports/modeling/market_health_index_by_prediction_date.csv
reports/modeling/market_health_by_year_regime_sector.csv
reports/figures/modeling/market_health_index_timeseries.png
```

Latest run:

- 3,319 unique `prediction_date` market-health rows;
- 18 audit rows, one for each input component field;
- production panel modified: `False`;
- alignment policy: prediction-date values only, no future macro values.

Current regime labels in the generated output:

- `severe_stress`;
- `stressed`;
- `neutral`;
- `healthy`.

The exact counts can change if the production panel or macro/event inputs are rebuilt.

## Thesis Wording

Safe wording:

> A composite market-health index was constructed from existing FRED macro variables and curated event-context fields using training-period standardization. The index is used as an interpretable market-shift context marker for dashboard analysis and sector comparisons.

Unsafe wording:

> The market-health index proves that macro conditions cause bankruptcy.
