# Panel Data Architecture and Expansion

Updated: 2026-05-09

## Answer: One Dataset, Not Two

The thesis should use one modeling dataset: a firm-period panel where each row is one SEC filing-period observation for one firm.

Primary dataset:

```text
data/processed/panel_v2/firm_panel_v2.parquet
data/processed/panel_v2/firm_panel_v2.csv.gz
```

GitHub-ready copies:

```text
data/github/firm_panel_v2.parquet
data/github/firm_panel_v2.csv.gz
data/github/firm_panel_v2_schema.csv
```

The schema file includes `feature_family`, so the GitHub dataset can be inspected by category instead of as a flat unexplained list of columns.

Current shape after the macro, trend-feature, global-event, missing-aware target, +150 firm universe expansion, 2026-05-07 SEC `ddate == period` selector rebuild, 2026-05-08 alias-collapse rebuild, 2026-05-09 SEC mapping polish, 2026-05-09 accounting/duplicate caveat-resolution rebuild, and 2026-05-10 validated-secondary target promotion:

- 31,702 rows
- 190 columns
- 540 SEC CIKs
- 540 tickers / firm display IDs
- period dates: 2009-03-31 to 2026-02-28
- prediction dates: 2009-04-15 to 2026-03-31
- `prediction_date_source = filed_date` for all rows

This is the right structure because the models need one rectangular table. Raw SEC accounting fields, financial ratios, firm trend variables, macro variables, regime indicators, global event context, industry metadata, and target labels all attach to the same firm-period row.

Plain-language field definitions are maintained in:

```text
docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md
```

## Feature Families

### 1. Filing and firm identifiers

Examples:

- `adsh`
- `cik`
- `ticker`
- `period_date`
- `filed_date`
- `prediction_date`
- `prediction_date_source`
- `form`
- `afs`
- `sec_zip`

Purpose:

- identifies the SEC submission and time period;
- supports temporal splitting;
- helps reproduce the data build.

Important time-field policy:

- `period_date` is the accounting period end date.
- `filed_date` is the date the SEC filing became available.
- `prediction_date` is the model's information date.
- In the current panel, `prediction_date = filed_date` for all rows.
- The panel builder has a `period_date` fallback only for missing filing dates, but the current panel does not use it.

This prevents look-ahead leakage. The model cannot use a December 31 filing-period observation as if the filing were known on December 31 when it was actually filed later.

### 2. Raw accounting fundamentals

Examples:

- `total_assets`
- `total_liabilities`
- `current_assets`
- `current_liabilities`
- `cash_equivalents`
- `total_equity`
- `total_revenue`
- `gross_profit`
- `operating_income`
- `net_income`
- `cash_flow_operating`
- `capex`

Purpose:

- preserves SEC-reported facts;
- makes the dataset auditable;
- supports model features and ratio construction.

Important wording for the thesis:

> These are accounting fundamentals extracted from SEC Financial Statement Data Sets. They are not manually typed balance-sheet values.

Flow-variable treatment:

- balance-sheet variables use point-in-time values (`qtrs=0`);
- flow variables use single-period values;
- when SEC reports only cumulative year-to-date flow values (`qtrs=2`, `qtrs=3`, or `qtrs=4`), the panel derives the single-period value by subtracting the prior cumulative value within the same firm, fiscal year, and variable;
- if the prior cumulative value is unavailable, the field remains null.

This is documented in:

```text
docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md
reports/data_quality/sec_fsd_variable_source_audit.csv
reports/data_quality/panel_v2_key_missingness_by_form_fp.csv
```

### 3. Financial ratios

Examples:

- `roa`
- `leverage_assets`
- `equity_assets`
- `current_ratio`
- `cash_assets`
- `net_margin`
- `operating_margin`
- `gross_margin`
- `r_and_d_intensity`
- `inventory_assets`
- `receivables_assets`

Purpose:

- makes firm condition comparable across firm sizes;
- gives interpretable predictors for distress and resilience.

Important wording:

> ROA is not a raw SEC line item. It is an engineered accounting ratio derived from net income and total assets.

This is acceptable and normal in financial distress prediction, as long as the ratio is computed only from information available at the observation date.

### 4. Firm trend and deterioration features

Examples:

- `roa_lag1`
- `leverage_assets_lag1`
- `cash_assets_lag1`
- `net_margin_lag1`
- `total_revenue_growth_4obs`
- `total_assets_growth_4obs`
- `total_liabilities_growth_4obs`
- `roa_change_4obs`
- `leverage_assets_change_4obs`
- `net_income_negative_count_prior_4obs`

Purpose:

- captures deterioration before distress;
- improves rare-event signal without needing another external dataset;
- is defensible because all values use current or prior firm observations, not future data.

First result before the SEC flow-standardization pass:

- after adding trend features and expanded macro data, the primary random-forest failure model test PR-AUC improved from about 0.152 to about 0.168;
- ablation random forest with firm + macro + regime features reached about 0.173 PR-AUC.

This is a modest but useful improvement. It should not be overstated.

After the SEC flow-standardization and missingness-indicator pass, firm fundamentals and firm deterioration became even more clearly dominant. The strongest ablation by test PR-AUC is currently the firm-only random forest.

### 5. Macro variables

Existing and newly added FRED variables are cataloged in:

```text
config/fred_series_catalog.csv
```

Newly added series:

- `T10Y2Y`: 10-year minus 2-year Treasury spread
- `T10Y3M`: 10-year minus 3-month Treasury spread
- `DCOILWTICO`: WTI crude oil price
- `DTWEXBGS`: broad nominal U.S. dollar index
- `CPIAUCSL`: CPI
- `PPIACO`: PPI all commodities
- `PAYEMS`: total nonfarm payrolls
- `RSAFS`: retail sales
- `HOUST`: housing starts
- `BUSLOANS`: commercial and industrial loans
- `DRTSCILM`: bank tightening standards for C&I loans to large and middle-market firms

Derived year-over-year macro changes are also added for selected level/index series:

- `INDPRO_yoy_pct`
- `M2SL_yoy_pct`
- `DCOILWTICO_yoy_pct`
- `DTWEXBGS_yoy_pct`
- `CPIAUCSL_yoy_pct`
- `PPIACO_yoy_pct`
- `PAYEMS_yoy_pct`
- `RSAFS_yoy_pct`
- `HOUST_yoy_pct`
- `BUSLOANS_yoy_pct`

Purpose:

- creates macro-market context for the phrase "market shifts";
- improves the thesis fit without changing the title;
- allows industry/regime comparisons in the dashboard and discussion.

### 6. Regime indicators

Regimes are binary context flags. They do not replace macro variables. They convert macro levels into interpretable market states.

Current regime indicators:

- `high_rate_regime`: federal funds rate >= 4%
- `market_stress_regime`: VIX >= 25
- `tight_financial_conditions`: NFCI > 0
- `credit_spread_stress_regime`: high-yield spread >= 5 percentage points
- `yield_curve_inversion_regime`: `T10Y2Y` or `T10Y3M` below 0
- `inflation_pressure_regime`: CPI YoY >= 4%
- `oil_shock_regime`: WTI oil YoY >= 30%
- `strong_dollar_regime`: broad dollar index YoY >= 5%
- `demand_slowdown_regime`: retail sales YoY < 0
- `credit_tightening_regime`: positive net share of banks tightening C&I lending standards
- `crisis_regime`: 2009, 2020, 2022, or 2023

Plain explanation:

> A regime is a market environment. For example, high interest rates, inverted yield curve, oil-price shock, or tight credit conditions. These indicators let the thesis test whether firm failure and success drivers differ across market states.

Regime indicators are useful for interpretation and dashboard storytelling even when they are not the strongest raw predictors.

### 7. Industry metadata

Examples:

- `Sector`
- `Industry`
- `sic`
- `sic_sector`
- `exchange`

Purpose:

- supports cross-industry comparison;
- answers the thesis title's "across industries" requirement;
- allows sector plots and dashboard filters.

### 8. Global event context

Global events are cataloged in:

```text
config/global_event_calendar_seed.csv
```

Current event types:

- `financial_crisis`
- `sovereign_debt`
- `natural_disaster`
- `commodity_oil`
- `financial_market`
- `political_policy`
- `trade_policy`
- `pandemic`
- `supply_chain`
- `monetary_inflation`
- `geopolitical_war`
- `banking_stress`

Examples of generated panel columns:

- `global_event_count`
- `global_event_severity_sum`
- `global_event_pandemic_count`
- `global_event_supply_chain_count`
- `global_event_geopolitical_war_count`
- `global_event_names`

Purpose:

- gives the dashboard a historical event-analysis layer;
- lets the thesis compare sector resilience and distress across discrete market-shift windows;
- keeps event data interpretable instead of introducing an unmanaged raw news/NLP project.

Current output:

```text
reports/modeling/panel_v2_global_event_sector_summary.csv
reports/figures/modeling/panel_v2_distress_share_by_global_event_type.png
```

## Rare-Event Strategy

Failure remains rare:

- primary target `distress_next_4q`: 207 positive rows overall;
- 96 positives in the 2022-2024 test period after the +150 firm expansion and source-verified event-date update.

This means accuracy is the wrong metric. The thesis should emphasize:

- PR-AUC / average precision;
- recall at usable alert thresholds;
- confusion matrices;
- temporal validation;
- feature contribution and case interpretation.

The rare-event problem should be improved through four channels:

1. Better event labels.
   Exact or near-exact bankruptcy/distress dates matter more than adding ten more generic macro variables.

2. Broader but transparent target variants.
   Use `distress_next_4q` as primary and `broad_distress_next_4q`, `distress_next_2q`, and `distress_next_8q` as robustness checks.

3. Firm trend features.
   Deterioration in profitability, margins, liquidity, and leverage is empirically stronger than raw macro context alone.

4. More distressed firms only if they have SEC coverage.
   Randomly adding small firms is risky. The better approach is to add firms with known distress events plus matched controls.

## Qualitative Data Decision

Qualitative data is possible but should not become the main empirical rebuild before the deadline.

Reasonable optional additions:

- add a small case-study table for 5-8 distressed firms;
- cite SEC 8-K or 10-K language around bankruptcy, going concern, or restructuring;
- use it in discussion/dashboard annotations, not as a new NLP model.

Not recommended before the deadline:

- full 10-K text scraping and sentiment modeling;
- large-scale risk-factor NLP;
- paid datasets that require new cleaning and licensing work.

## Current Empirical Takeaway

The current data architecture is defensible:

- one firm-period panel;
- SEC accounting fundamentals;
- engineered financial ratios;
- firm deterioration features;
- FRED macro variables;
- interpretable regime indicators;
- curated global event context;
- industry metadata;
- multiple forward-looking success/failure targets.

The strongest honest thesis claim is:

> Firm-level accounting condition and deterioration dominate prediction of future distress and resilience, while macro-market regimes and global event windows provide contextual and sometimes incremental information for ranking rare distress events across industries.
