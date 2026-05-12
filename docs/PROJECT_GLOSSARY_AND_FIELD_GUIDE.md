# Project Glossary And Field Guide

Updated: 2026-05-09

This document explains the main project terms in plain language. Use it as the first reference when reading the panel, the dashboard, model outputs, or thesis notes.

## Core Idea

The project builds one firm-period panel from SEC Financial Statement Data Sets, FRED macro data, curated global-event windows, and manually maintained distress-event labels.

Each row means:

> One company, one reported accounting period, observed from the date the SEC filing became available.

The thesis should describe the artifact as a historical early-warning and decision-support dashboard for firm distress, financial pressure, and resilience across industries and market environments.

## Key Time Fields

### `period_date`

The accounting period end date.

Example: a firm's fiscal quarter ended on 2023-12-31.

This is the date the financial statements describe. It is not always the date the market or model could know those numbers.

### `filed_date`

The SEC filing date.

Example: a firm files its 10-Q or 10-K on 2024-02-15.

This is when the information becomes publicly available through the SEC data source.

### `prediction_date`

The date from which the model is allowed to make a prediction.

In the current production panel:

```text
prediction_date = filed_date
prediction_date_source = filed_date for all 31,702 rows
```

This is one of the most important integrity choices in the project. It prevents look-ahead leakage. The model should not act as if it knew a filing on the fiscal quarter-end date if the filing was published weeks later.

The panel builder has a fallback to use `period_date` if `filed_date` is missing, but the current built panel does not use that fallback.

### Why This Matters

If the model uses `period_date`, it may accidentally pretend that December 31 financials were known on December 31. In reality, many filings are submitted in February, March, or later.

Using `prediction_date = filed_date` makes the thesis more defensible because targets, macro context, global-event context, and temporal train/test splits are aligned to the date when the information was knowable.

## What Is A Regime?

A regime is a market-environment flag derived from macro data.

It is not a company fact, not a target, and not a separate dataset that replaces the firm panel. It is an engineered context indicator attached to each firm-period row.

Plain example:

> If the federal funds rate is at least 4 percent on the prediction date, `high_rate_regime = 1`; otherwise it is 0.

Regime indicators make the phrase "market shifts" concrete. They let the thesis compare whether firm distress and resilience factors differ during high-rate periods, market-stress periods, inflation-pressure periods, credit-tightening periods, and similar states.

## Current Regime Indicators

| Column | Meaning |
| --- | --- |
| `high_rate_regime` | Federal funds rate is at least 4.0 percent. |
| `market_stress_regime` | VIX is at least 25. |
| `tight_financial_conditions` | NFCI is above 0, meaning tighter-than-average financial conditions. |
| `credit_spread_stress_regime` | High-yield spread is at least 5.0 percentage points. |
| `yield_curve_inversion_regime` | `T10Y2Y` or `T10Y3M` is below 0. |
| `inflation_pressure_regime` | CPI year-over-year inflation is at least 4.0 percent. |
| `oil_shock_regime` | WTI oil year-over-year change is at least 30.0 percent. |
| `strong_dollar_regime` | Broad U.S. dollar index year-over-year change is at least 5.0 percent. |
| `demand_slowdown_regime` | Retail sales year-over-year change is below 0. |
| `credit_tightening_regime` | Bank lending-standards tightening measure is positive. |
| `crisis_regime` | Prediction year is 2009, 2020, 2022, or 2023. |

These thresholds are simple and interpretable. They are useful for dashboard filters, sector comparisons, and thesis discussion. They should not be overstated as perfect economic regime definitions.

## Key Identifier Fields

### `adsh`

SEC accession/submission identifier. It identifies the exact SEC submission used in the SEC Financial Statement Data Sets.

### `cik`

Central Index Key. This is the stable SEC company identifier and is more reliable than ticker for historical data.

### `ticker`

Ticker or display identifier used for readability. Some historical expansion firms may have display IDs rather than current live tickers.

### `cohort`

The source bucket that explains why a firm is in the universe.

Current cohort types:

- `core_large_cap`
- `additional_controls`
- `distress_candidates`
- `expansion_event_review`
- `expansion_matched_controls`

`cohort` is useful for audit and dataset description. It should not be used as a predictive model feature because it leaks sampling logic.

## Target Fields

A target is the outcome being predicted or analyzed.

Examples:

- `distress_next_4q`: strict formal distress event in the next roughly four quarters.
- `failure_pressure_conservative_v2_next_4obs`: production broader failure-pressure target. It captures strict formal distress plus repeated future profitability weakness with serious balance-stress, deterioration, or unhealthy-future signals. It is not a legal bankruptcy label.
- `success_resilience_next_4q`: future profitability/resilience target with missing-aware logic.
- other broader failure-pressure targets: diagnostic/experimental definitions of serious financial pressure, not the same thing as legal bankruptcy.

Important rule:

> A target must use future information only to label the outcome, never as a model input feature.

## Event Fields

### `event_date`

The known or manually curated date of a formal distress event.

This field is still marked as REVIEW in the audit because the source file is an initial seed and event-review expansion firms still need manual verification.

### `post_event_flag`

Marks rows where `prediction_date` is on or after a formal event date.

These rows remain in the panel for historical/dashboard analysis but are excluded from primary forward-looking model training.

### `days_to_event`

Number of days from the `prediction_date` to a known event date.

It is used to create forward-looking distress labels and event-timing diagnostics.

## Feature Families

### Raw SEC Accounting Fundamentals

Examples:

- `total_assets`
- `total_liabilities`
- `total_revenue`
- `net_income`
- `operating_income`
- `cash_flow_operating`
- `capex`

These are SEC-derived accounting facts after standardized extraction logic. Missing values are not invented.

### Engineered Financial Ratios

Examples:

- `roa`
- `leverage_assets`
- `equity_assets`
- `current_ratio`
- `net_margin`
- `operating_margin`
- `gross_margin`

These are calculated from SEC fundamentals. This is normal in financial distress and business analytics research. For example, ROA is not directly a raw SEC line item; it is an engineered ratio based on net income and assets.

### Firm Trend And Deterioration Features

Examples:

- lagged ratios;
- four-observation growth/change variables;
- prior negative-income counts.

These measure whether the firm is improving or deteriorating over time.

### Macro Variables

FRED variables such as rates, spreads, inflation, oil, dollar, labor, demand, housing, credit, and lending standards.

They describe the external economic environment at the `prediction_date`.

### Regime Indicators

Binary macro-context flags such as high-rate, inflation-pressure, oil-shock, credit-tightening, and crisis regimes.

### Global Event Context

Curated historical event-window fields such as event counts, event severity, event type counts, and event names.

These are not a full news database. They are a transparent historical context layer.

### Industry Metadata

Sector, industry, SIC, SIC sector, and exchange fields used for cross-industry comparison and dashboard filters.

## Missing Values

Missing values do not have one universal meaning.

They can mean:

- the company did not report the item;
- the item was not applicable;
- the item was reported under another accounting concept;
- the SEC fact had dimensions that were excluded from the standardized panel;
- cumulative flow derivation was impossible because a prior cumulative value was missing;
- the field was genuinely unavailable for that filing.

The main panel does not invent these values. Model pipelines may impute values internally for algorithms, but imputed values are model-processing artifacts, not new facts.

## Missingness Indicators

A missingness indicator is a model-created flag showing whether a field had to be imputed.

Example:

```text
missingindicator_total_liabilities
```

This is not a raw SEC variable. It may help model prediction, but it should not be interpreted as an economic factor like leverage, ROA, or profitability.

## Train, Validation, And Test Splits

The core firm panel should not store a permanent train/test split as a factual data column.

The modeling scripts derive temporal splits from `prediction_date`:

- train: prediction years up to 2018;
- validation: 2019-2021;
- test: 2022-2024.

This is better than a random split because it tests whether the model generalizes forward in time.

## Current Production Panel Snapshot

Current production panel:

```text
data/processed/panel_v2/firm_panel_v2.parquet
data/processed/panel_v2/firm_panel_v2.csv.gz
```

Current GitHub-ready copies:

```text
data/github/firm_panel_v2.parquet
data/github/firm_panel_v2.csv.gz
data/github/firm_panel_v2_schema.csv
```

Current shape:

- 31,702 rows;
- 190 columns;
- 540 SEC CIKs;
- 540 tickers / display IDs;
- period dates: 2009-03-31 to 2026-02-28;
- prediction dates: 2009-04-15 to 2026-03-31;
- `prediction_date_source = filed_date` for all rows.

## What The Dashboard Artifact Is

The dashboard should be framed as:

> A historical decision-support and early-warning analytics artifact for exploring firm distress, financial pressure, resilience, industries, and macro-market regimes.

It should not be framed as:

- a real-time bankruptcy oracle;
- a live trading system;
- a complete event/news intelligence platform;
- a guaranteed prediction system.

The defensible artifact is the reproducible panel plus an interactive dashboard that exposes data coverage, target definitions, model results, firm histories, factor groups, sector comparisons, regime comparisons, and event-window context.
