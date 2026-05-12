# Master Data, Model, and Target Explainer

Generated: 2026-05-07

This file is the thesis-ready master explanation of the empirical system behind the project. It is intended for direct use in methodology, data, target-definition, modeling, dashboard-artifact, limitations, and appendix sections.

## Source Boundary

This explainer uses the current source-of-truth project materials and saved reports. It does not introduce new data sources, new targets, or new model results.

Source materials used:

- `docs/CURRENT_STATUS.md`
- `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`
- `docs/PROJECT_CHRONICLE.md`
- `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md`
- `docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md`
- `docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md`
- `docs/FINAL_TARGET_HIERARCHY.md`
- `docs/TARGET_DEFINITIONS_FINAL_REVIEW.md`
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`
- `docs/MISSINGNESS_INDICATOR_POLICY.md`
- `docs/MARKET_HEALTH_INDEX_NOTE.md`
- `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md`
- `docs/DISTRESS_EVENT_DATE_PROVENANCE.md`
- `docs/BIBLIOGRAPHY.md`
- `docs/references.bib`
- `reports/modeling/`
- `reports/model_tuning/`
- `reports/data_quality/`
- `reports/data_quality/sec_selected_fact_provenance.parquet`
- `reports/data_quality/sec_selected_fact_panel_validation.csv`
- `data/github/firm_panel_v2_schema.csv`

When the source material does not document a detail precisely, this file states `not documented / requires review`.

## 1. Project Overview

The thesis topic is:

> Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries

The empirical contribution is a reproducible firm-period analytics system for U.S. public companies. The project builds one structured panel from SEC Financial Statement Data Sets, FRED macroeconomic variables, curated global-event context, manually maintained distress-event labels, and industry metadata. The final production panel has 31,702 rows, 190 columns, 540 SEC CIKs, and 540 ticker/display identifiers. Its accounting periods run from 2009-03-31 to 2026-02-28, and its prediction timestamps run from 2009-04-15 to 2026-03-31.

The practical artifact is an interactive Streamlit dashboard plus a GitHub-ready dataset package. The dashboard is best described as a historical decision-support and early-warning analytics artifact. It exposes panel coverage, target composition, model results, firm-level histories, sector comparisons, macro/regime context, global-event windows, and data-quality caveats. It should not be described as a live trading engine, daily bankruptcy oracle, or complete news-intelligence system.

The final scope is deliberately U.S. SEC/FRED/global-event public-company data. HR, ESG, NLP, international datasets, Russian RFSD, Hong Kong/Japan data, paid data, market-price models, and live event feeds are not used in the production panel. They were considered as possible extensions, but they were excluded before submission because they would require new data-cleaning systems, licensing review, cross-country accounting harmonization, language processing, or market microstructure assumptions. The locked scope is stronger for the thesis because it is reproducible, auditable, and already aligned to the title: firm success and failure factors across industries and market shifts.

The core empirical story is not that a model perfectly predicts bankruptcy. The correct story is that predictive analytics is used to identify and compare forward-looking distress, broader financial pressure, and resilience factors. Strict legal distress is retained as a clean rare-event benchmark. Broader failure pressure is the main failure-factor target. Success/resilience is the main positive-outcome counterpart. Firm fundamentals, ratios, and deterioration features carry the strongest economic signal, while macro variables, regime indicators, and global events provide market-shift context and dashboard interpretability.

## Caveat Handling Plan

The caveats are not ignored. They are handled as explicit validity controls:

| Caveat | Handling rule | Thesis position |
| --- | --- | --- |
| Strict event-date provenance remains `REVIEW` | Use strict legal distress only as a rare-event benchmark; continue source-verifying remaining initial-seed events; do not silently upgrade unverified rows. | Safe with disclosure; do not claim a complete verified legal bankruptcy database. |
| SEC concept mapping is conservative, not perfect | Use documented SEC concept mapping, qtrs handling, missingness tables, accounting identity sanity checks, and outlier review. | Safe as audited SEC-FSD extraction; unsafe to claim perfect accounting harmonization. |
| Nulls have multiple meanings | Preserve raw panel nulls; impute only inside model pipelines; keep missing future target components as unknown. | Safe as null-preserving empirical panel; unsafe to treat null as zero or unchanged by default. |
| Missingness indicators can be predictive | Keep indicators only as model auxiliaries after diagnosis; exclude them from economic factor interpretation. | Safe for prediction; unsafe as economic causal claims. |
| Duplicate/amended filing keys exist | Disclose amendment/duplicate audit; no manual panel edits were made. A deterministic rebuild policy is needed if rows are to be dropped. | Safe with disclosure; not a blocker for thesis writing. |
| Structural audit PASS is not scientific proof | Separate structural readiness from empirical validity; rely on prediction-date alignment, leakage audits, temporal validation, target review, robustness, and limitations. | Safe if written as association and decision support, not causal truth. |
| Dashboard screenshot warnings | Use captured screenshots; record chart-library warnings as non-blocking evidence caveats. | Safe as artifact evidence; not a scientific limitation by itself. |
| GitHub/version freeze incomplete | Before final upload, freeze the exact panel, docs, README, requirements, and reproduction instructions. | TODO before submission package, not a reason to change empirical scope. |

## 2. Panel Architecture

Each row means:

> One company, one reported accounting period, observed from the date the SEC filing became available.

The panel is a firm-period table. It does not store disconnected accounting, macro, event, and target datasets separately because the models and dashboard need a single rectangular observation unit. Raw SEC accounting fundamentals, ratios, trend features, macro variables, regime indicators, global-event context, industry metadata, event metadata, and target labels attach to the same firm-period row.

The key time fields are:

- `period_date`: the accounting period end date described by the filing.
- `filed_date`: the date when the SEC filing became available.
- `prediction_date`: the information date from which prediction is allowed.

The production panel uses:

```text
prediction_date = filed_date
prediction_date_source = filed_date for all rows
```

This prevents look-ahead leakage. A filing for a quarter ending on December 31 is often not filed until weeks later. If the model were allowed to use the accounting period end date as the prediction date, it could accidentally behave as if it knew the financial statement before it was publicly available. Using `filed_date` as `prediction_date` aligns the firm information, macro context, event context, target windows, and temporal train/validation/test splits to the date when the information was knowable.

The core panel should not contain a permanent train/test split as a factual column. Modeling scripts derive temporal splits from `prediction_date`: train through 2018, validation from 2019 to 2021, and test from 2022 to 2024. This is more defensible than random row splitting because it evaluates forward-time generalization.

Current feature-family counts:

| feature_family | columns |
| --- | --- |
| sec_accounting_fundamental | 31 |
| macro_variable | 31 |
| global_event_context | 27 |
| identifier_or_time | 24 |
| firm_trend_or_deterioration | 21 |
| target_label | 14 |
| financial_ratio | 11 |
| macro_regime_indicator | 11 |
| event_metadata | 11 |
| industry_or_universe_metadata | 9 |

Current P0 audit status:

| audit | status | violations |
| --- | --- | --- |
| prediction_timestamp | PASS |  |
| distress_event_dates | PASS |  |
| leakage | PASS | 0.0 |
| macro_lag | PASS | 0.0 |
| global_event_timing | PASS | 0.0 |
| post_event_rows | PASS | 0.0 |

## 3. Full Column Dictionary

The full machine-readable dictionary is also saved at:

```text
reports/documentation/master_column_dictionary.csv
```

`can_use_in_current_models = yes` means the column appears in the saved current model feature lists under `reports/data_quality/model_feature_lists/`. A `no` does not mean the variable could never be used in future research; it means it is not part of the current documented production feature set, or it is a target/metadata/audit field that must not be used as a predictor.

| column | feature_family | plain_english_meaning | source | can_use_in_current_models | metadata_or_audit_only | missingness_caveat |
| --- | --- | --- | --- | --- | --- | --- |
| adsh | identifier_or_time | SEC accession/submission identifier for the filing observation. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| cik | identifier_or_time | SEC Central Index Key, used as the stable firm identifier. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| name | identifier_or_time | SEC company name from the filing/submission metadata. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| sic | industry_or_universe_metadata | SEC SIC industry code. | metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| afs | identifier_or_time | SEC accelerated-filer status metadata. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| form | identifier_or_time | SEC filing form, mainly 10-K, 10-K/A, 10-Q, and 10-Q/A. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| period | identifier_or_time | SEC filing period end date in numeric YYYYMMDD form. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| fy | identifier_or_time | Fiscal year reported in the SEC filing metadata. | SEC metadata | no | yes | Schema missing share: 0.0%. Identifier/time metadata missingness should be reviewed before using the field operationally. |
| fp | identifier_or_time | Fiscal period code from SEC metadata, such as FY, Q1, Q2, or Q3. | SEC metadata | no | yes | Schema missing share: 0.0%. Identifier/time metadata missingness should be reviewed before using the field operationally. |
| filed | identifier_or_time | SEC filing date in numeric YYYYMMDD form. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| sec_zip | identifier_or_time | SEC FSD ZIP/source package from which the filing was parsed. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| accounts_receivable | sec_accounting_fundamental | Accounts receivable, usually current receivables net of allowances. | SEC | no | no | Schema missing share: 24.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| capex | sec_accounting_fundamental | Capital expenditure, primarily payments to acquire property, plant, and equipment. | SEC | yes | no | Schema missing share: 35.2%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| cash_equivalents | sec_accounting_fundamental | Cash and cash equivalents, including restricted cash when mapped by the SEC concept map. | SEC | yes | no | Schema missing share: 4.3%. Low to moderate missingness; nulls are preserved. |
| cash_flow_financing | sec_accounting_fundamental | Net cash provided by or used in financing activities. | SEC | no | no | Schema missing share: 16.6%. Low to moderate missingness; nulls are preserved. |
| cash_flow_investing | sec_accounting_fundamental | Net cash provided by or used in investing activities. | SEC | no | no | Schema missing share: 16.6%. Low to moderate missingness; nulls are preserved. |
| cash_flow_operating | sec_accounting_fundamental | Net cash provided by or used in operating activities. | SEC | yes | no | Schema missing share: 16.6%. Low to moderate missingness; nulls are preserved. |
| cost_of_revenue | sec_accounting_fundamental | Cost of revenue, cost of goods sold, or cost of sales according to mapped SEC tags. | SEC | no | no | Schema missing share: 48.4%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| current_assets | sec_accounting_fundamental | Current assets. | SEC | yes | no | Schema missing share: 17.9%. Low to moderate missingness; nulls are preserved. |
| current_liabilities | sec_accounting_fundamental | Current liabilities. | SEC | yes | no | Schema missing share: 18.0%. Low to moderate missingness; nulls are preserved. |
| depreciation_amortization | sec_accounting_fundamental | Depreciation, depletion, and amortization expense. | SEC | no | no | Schema missing share: 35.9%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| eps_basic | sec_accounting_fundamental | Basic earnings per share. | SEC | no | no | Schema missing share: 9.6%. Low to moderate missingness; nulls are preserved. |
| eps_diluted | sec_accounting_fundamental | Diluted earnings per share. | SEC | no | no | Schema missing share: 9.6%. Low to moderate missingness; nulls are preserved. |
| gross_profit | sec_accounting_fundamental | Gross profit where separately reported. | SEC | yes | no | Schema missing share: 69.8%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| inventory | sec_accounting_fundamental | Inventory, net. | SEC | no | no | Schema missing share: 46.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| long_term_debt | sec_accounting_fundamental | Long-term debt where separately reported. | SEC | yes | no | Schema missing share: 27.1%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| net_income | sec_accounting_fundamental | Net income or loss. | SEC | yes | no | Schema missing share: 0.5%. Low to moderate missingness; nulls are preserved. |
| noncurrent_liabilities | sec_accounting_fundamental | Noncurrent liabilities where separately reported. | SEC | no | no | Schema missing share: 87.2%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| operating_income | sec_accounting_fundamental | Operating income or loss. | SEC | yes | no | Schema missing share: 25.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| ppe_net | sec_accounting_fundamental | Property, plant, and equipment, net. | SEC | no | no | Schema missing share: 16.7%. Low to moderate missingness; nulls are preserved. |
| pretax_income | sec_accounting_fundamental | Income or loss before income taxes, extraordinary items, and noncontrolling interest where mapped. | SEC | no | no | Schema missing share: 50.5%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| r_and_d_expense | sec_accounting_fundamental | Research and development expense. | SEC | no | no | Schema missing share: 73.0%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| retained_earnings | sec_accounting_fundamental | Retained earnings or accumulated deficit. | SEC | no | no | Schema missing share: 5.6%. Low to moderate missingness; nulls are preserved. |
| sg_and_a | sec_accounting_fundamental | Selling, general, and administrative expense. | SEC | no | no | Schema missing share: 50.9%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| shares_outstanding | sec_accounting_fundamental | Common shares outstanding. | SEC | no | no | Schema missing share: 46.4%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| short_term_debt | sec_accounting_fundamental | Short-term borrowings or current debt. | SEC | yes | no | Schema missing share: 39.0%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| total_assets | sec_accounting_fundamental | Total assets. | SEC | yes | no | Schema missing share: 0.2%. Low to moderate missingness; nulls are preserved. |
| total_equity | sec_accounting_fundamental | Stockholders' equity, including noncontrolling interest where mapped. | SEC | yes | no | Schema missing share: 1.6%. Low to moderate missingness; nulls are preserved. |
| total_liabilities | sec_accounting_fundamental | Total liabilities. | SEC | yes | no | Schema missing share: 32.7%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| total_revenue | sec_accounting_fundamental | Revenue, sales, or revenue from contracts with customers according to mapped SEC tags. | SEC | yes | no | Schema missing share: 10.7%. Low to moderate missingness; nulls are preserved. |
| wavg_shares_basic | sec_accounting_fundamental | Weighted average basic shares outstanding. | SEC | no | no | Schema missing share: 25.0%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| wavg_shares_diluted | sec_accounting_fundamental | Weighted average diluted shares outstanding. | SEC | no | no | Schema missing share: 27.4%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| ticker | identifier_or_time | Ticker or display identifier used for readability. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| firm_id | identifier_or_time | Internal firm identifier used to join firm-level observations. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| shortname | identifier_or_time | Short readable firm name. | SEC metadata | no | yes | Schema missing share: 18.8%. Identifier/time metadata missingness should be reviewed before using the field operationally. |
| sec_name | identifier_or_time | Company name from SEC metadata. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| exchange | industry_or_universe_metadata | Listing exchange or exchange metadata where available. | metadata | no | yes | Schema missing share: 4.8%. Metadata missingness affects description/filtering and should not be invented. |
| Sector | industry_or_universe_metadata | Broad sector label used for industry comparisons and current model categorical encoding. | metadata | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| Industry | industry_or_universe_metadata | More detailed industry label used for dashboard and descriptive analysis. | metadata | no | yes | Schema missing share: 23.7%. Metadata missingness affects description/filtering and should not be invented. |
| cohort | industry_or_universe_metadata | Universe-selection bucket explaining why the firm is included. | metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| include_status | industry_or_universe_metadata | Universe inclusion status metadata. | metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| notes | industry_or_universe_metadata | Free-form universe note; contents are not standardized for modeling. | metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| ticker_aliases | identifier_or_time | not documented / requires review | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| event_lookup_tickers | identifier_or_time | not documented / requires review | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| duplicate_cik_alias_count | industry_or_universe_metadata | not documented / requires review | metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| period_date | identifier_or_time | Accounting period end date described by the filing. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| filed_date | identifier_or_time | Date when the SEC filing became available. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| prediction_date | identifier_or_time | Information date for modeling; equals filed_date in the production panel. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| prediction_date_source | identifier_or_time | Audit field showing which date source produced prediction_date. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| calendar_year | identifier_or_time | Calendar year of the accounting period. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| calendar_quarter | identifier_or_time | Calendar quarter of the accounting period. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| prediction_year | identifier_or_time | Calendar year of prediction_date, used for temporal validation splits. | SEC metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| prediction_quarter | identifier_or_time | Calendar quarter of prediction_date; current model feature for filing-season context. | SEC metadata | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| sic_sector | industry_or_universe_metadata | Sector grouping derived from SIC metadata. | metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| leverage_assets | financial_ratio | Calculated leverage ratio showing how much of assets are financed by liabilities. Formula: total liabilities divided by total assets. | calculated ratio | yes | no | Schema missing share: 32.7%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| equity_assets | financial_ratio | Calculated capitalization ratio showing book equity relative to assets. Formula: total equity divided by total assets. | calculated ratio | yes | no | Schema missing share: 1.7%. Low to moderate missingness; nulls are preserved. |
| current_ratio | financial_ratio | Calculated liquidity ratio for short-term balance-sheet coverage. Formula: current assets divided by current liabilities. | calculated ratio | yes | no | Schema missing share: 18.0%. Low to moderate missingness; nulls are preserved. |
| cash_assets | financial_ratio | Calculated liquidity buffer relative to firm size. Formula: cash and equivalents divided by total assets. | calculated ratio | yes | no | Schema missing share: 4.4%. Low to moderate missingness; nulls are preserved. |
| net_margin | financial_ratio | Calculated profitability margin after all expenses. Formula: net income divided by total revenue. | calculated ratio | yes | no | Schema missing share: 11.1%. Low to moderate missingness; nulls are preserved. |
| operating_margin | financial_ratio | Calculated operating profitability margin. Formula: operating income divided by total revenue. | calculated ratio | yes | no | Schema missing share: 30.2%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| gross_margin | financial_ratio | Calculated gross profitability margin where gross profit is available. Formula: gross profit divided by total revenue. | calculated ratio | yes | no | Schema missing share: 70.2%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| roa | financial_ratio | Calculated return on assets; it is an engineered ratio, not a raw SEC line item. Formula: net income divided by total assets. | calculated ratio | yes | no | Schema missing share: 0.7%. Low to moderate missingness; nulls are preserved. |
| r_and_d_intensity | financial_ratio | Calculated innovation/intangible-investment intensity where R&D is reported. Formula: R&D expense divided by total revenue. | calculated ratio | yes | no | Schema missing share: 73.8%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| inventory_assets | financial_ratio | Calculated inventory exposure relative to assets. Formula: inventory divided by total assets. | calculated ratio | yes | no | Schema missing share: 46.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| receivables_assets | financial_ratio | Calculated receivables exposure relative to assets. Formula: accounts receivable divided by total assets. | calculated ratio | yes | no | Schema missing share: 24.9%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| roa_lag1 | firm_trend_or_deterioration | One-observation lag of roa, using prior firm observation only. | trend feature | yes | no | Schema missing share: 2.4%. Low to moderate missingness; nulls are preserved. |
| leverage_assets_lag1 | firm_trend_or_deterioration | One-observation lag of leverage_assets, using prior firm observation only. | trend feature | yes | no | Schema missing share: 34.0%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| current_ratio_lag1 | firm_trend_or_deterioration | One-observation lag of current_ratio, using prior firm observation only. | trend feature | yes | no | Schema missing share: 19.4%. Low to moderate missingness; nulls are preserved. |
| cash_assets_lag1 | firm_trend_or_deterioration | One-observation lag of cash_assets, using prior firm observation only. | trend feature | yes | no | Schema missing share: 6.1%. Low to moderate missingness; nulls are preserved. |
| net_margin_lag1 | firm_trend_or_deterioration | One-observation lag of net_margin, using prior firm observation only. | trend feature | yes | no | Schema missing share: 12.7%. Low to moderate missingness; nulls are preserved. |
| operating_margin_lag1 | firm_trend_or_deterioration | One-observation lag of operating_margin, using prior firm observation only. | trend feature | yes | no | Schema missing share: 31.4%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| gross_margin_lag1 | firm_trend_or_deterioration | One-observation lag of gross_margin, using prior firm observation only. | trend feature | yes | no | Schema missing share: 70.8%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| total_revenue_growth_4obs | firm_trend_or_deterioration | Four-observation growth feature for total_revenue: current value versus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 17.6%. Low to moderate missingness; nulls are preserved. |
| total_assets_growth_4obs | firm_trend_or_deterioration | Four-observation growth feature for total_assets: current value versus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 7.2%. Low to moderate missingness; nulls are preserved. |
| cash_equivalents_growth_4obs | firm_trend_or_deterioration | Four-observation growth feature for cash_equivalents: current value versus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 11.6%. Low to moderate missingness; nulls are preserved. |
| total_liabilities_growth_4obs | firm_trend_or_deterioration | Four-observation growth feature for total_liabilities: current value versus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 37.9%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| current_assets_growth_4obs | firm_trend_or_deterioration | Four-observation growth feature for current_assets: current value versus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 23.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| current_liabilities_growth_4obs | firm_trend_or_deterioration | Four-observation growth feature for current_liabilities: current value versus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 23.9%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| roa_change_4obs | firm_trend_or_deterioration | Four-observation change feature for roa: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 7.8%. Low to moderate missingness; nulls are preserved. |
| leverage_assets_change_4obs | firm_trend_or_deterioration | Four-observation change feature for leverage_assets: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 37.9%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| current_ratio_change_4obs | firm_trend_or_deterioration | Four-observation change feature for current_ratio: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 23.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| cash_assets_change_4obs | firm_trend_or_deterioration | Four-observation change feature for cash_assets: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 11.6%. Low to moderate missingness; nulls are preserved. |
| net_margin_change_4obs | firm_trend_or_deterioration | Four-observation change feature for net_margin: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 18.0%. Low to moderate missingness; nulls are preserved. |
| operating_margin_change_4obs | firm_trend_or_deterioration | Four-observation change feature for operating_margin: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 35.8%. Moderate missingness; nulls are preserved and imputed only inside modeling pipelines. |
| gross_margin_change_4obs | firm_trend_or_deterioration | Four-observation change feature for gross_margin: current value minus value four prior observations earlier. | trend feature | yes | no | Schema missing share: 72.6%. High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation. |
| net_income_negative_count_prior_4obs | firm_trend_or_deterioration | Count of prior four firm observations with negative net income. | trend feature | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| BAMLH0A0HYM2 | macro_variable | High-yield corporate bond spread. | FRED | yes | no | Schema missing share: 0.1%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| FEDFUNDS | macro_variable | Federal funds rate. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| GDPC1 | macro_variable | Real GDP. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| GS10 | macro_variable | 10-year Treasury yield. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| INDPRO | macro_variable | Industrial production index. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| INDPRO_yoy_pct | macro_variable | Industrial production year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| M2SL | macro_variable | M2 money supply. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| M2SL_yoy_pct | macro_variable | M2 money supply year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| NFCI | macro_variable | Chicago Fed National Financial Conditions Index. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| UNRATE | macro_variable | Unemployment rate. | FRED | yes | no | Schema missing share: 0.7%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| USEPUINDXD | macro_variable | U.S. economic policy uncertainty index. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| VIXCLS | macro_variable | VIX volatility index. | FRED | yes | no | Schema missing share: 0.1%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| T10Y2Y | macro_variable | 10-year minus 2-year Treasury spread. | FRED | yes | no | Schema missing share: 0.1%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| T10Y3M | macro_variable | 10-year minus 3-month Treasury spread. | FRED | yes | no | Schema missing share: 0.1%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| DCOILWTICO | macro_variable | WTI crude oil price. | FRED | yes | no | Schema missing share: 0.1%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| DCOILWTICO_yoy_pct | macro_variable | WTI crude oil year-over-year percent change. | FRED | yes | no | Schema missing share: 1.7%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| DTWEXBGS | macro_variable | Broad nominal U.S. dollar index. | FRED | yes | no | Schema missing share: 0.5%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| DTWEXBGS_yoy_pct | macro_variable | Broad dollar index year-over-year percent change. | FRED | yes | no | Schema missing share: 3.5%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| CPIAUCSL | macro_variable | Consumer price index. | FRED | yes | no | Schema missing share: 0.7%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| CPIAUCSL_yoy_pct | macro_variable | CPI year-over-year percent change. | FRED | yes | no | Schema missing share: 0.7%. Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation. |
| PPIACO | macro_variable | Producer price index for all commodities. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| PPIACO_yoy_pct | macro_variable | PPI year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| PAYEMS | macro_variable | Total nonfarm payroll employment. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| PAYEMS_yoy_pct | macro_variable | Payroll employment year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| RSAFS | macro_variable | Retail sales. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| RSAFS_yoy_pct | macro_variable | Retail sales year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| HOUST | macro_variable | Housing starts. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| HOUST_yoy_pct | macro_variable | Housing starts year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| BUSLOANS | macro_variable | Commercial and industrial loans. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| BUSLOANS_yoy_pct | macro_variable | Commercial and industrial loans year-over-year percent change. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| DRTSCILM | macro_variable | Bank lending standards for C&I loans to large and middle-market firms. | FRED | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| high_rate_regime | macro_regime_indicator | Federal funds rate is at least 4 percent. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| market_stress_regime | macro_regime_indicator | VIX is at least 25. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| tight_financial_conditions | macro_regime_indicator | NFCI is above 0, meaning tighter-than-average financial conditions. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| credit_spread_stress_regime | macro_regime_indicator | High-yield spread is at least 5 percentage points. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| yield_curve_inversion_regime | macro_regime_indicator | T10Y2Y or T10Y3M is below 0. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| inflation_pressure_regime | macro_regime_indicator | CPI year-over-year inflation is at least 4 percent. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| oil_shock_regime | macro_regime_indicator | WTI oil year-over-year change is at least 30 percent. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| strong_dollar_regime | macro_regime_indicator | Broad U.S. dollar index year-over-year change is at least 5 percent. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| demand_slowdown_regime | macro_regime_indicator | Retail sales year-over-year change is below 0. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| credit_tightening_regime | macro_regime_indicator | Bank lending-standards tightening measure is positive. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| crisis_regime | macro_regime_indicator | Prediction year is 2009, 2020, 2022, or 2023. | regime | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_count | global_event_context | Count of curated global event windows active on the prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_severity_sum | global_event_context | Sum of severity scores for curated global event windows active on the prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_banking_stress_count | global_event_context | Count of active curated banking stress event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_banking_stress_severity | global_event_context | Severity sum for active curated banking stress event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_commodity_oil_count | global_event_context | Count of active curated commodity oil event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_commodity_oil_severity | global_event_context | Severity sum for active curated commodity oil event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_financial_crisis_count | global_event_context | Count of active curated financial crisis event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_financial_crisis_severity | global_event_context | Severity sum for active curated financial crisis event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_financial_market_count | global_event_context | Count of active curated financial market event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_financial_market_severity | global_event_context | Severity sum for active curated financial market event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_geopolitical_war_count | global_event_context | Count of active curated geopolitical war event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_geopolitical_war_severity | global_event_context | Severity sum for active curated geopolitical war event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_monetary_inflation_count | global_event_context | Count of active curated monetary inflation event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_monetary_inflation_severity | global_event_context | Severity sum for active curated monetary inflation event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_natural_disaster_count | global_event_context | Count of active curated natural disaster event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_natural_disaster_severity | global_event_context | Severity sum for active curated natural disaster event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_pandemic_count | global_event_context | Count of active curated pandemic event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_pandemic_severity | global_event_context | Severity sum for active curated pandemic event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_political_policy_count | global_event_context | Count of active curated political policy event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_political_policy_severity | global_event_context | Severity sum for active curated political policy event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_sovereign_debt_count | global_event_context | Count of active curated sovereign debt event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_sovereign_debt_severity | global_event_context | Severity sum for active curated sovereign debt event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_supply_chain_count | global_event_context | Count of active curated supply chain event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_supply_chain_severity | global_event_context | Severity sum for active curated supply chain event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_trade_policy_count | global_event_context | Count of active curated trade policy event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_trade_policy_severity | global_event_context | Severity sum for active curated trade policy event windows at prediction_date. | global event | yes | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| global_event_names | global_event_context | Readable names of active curated global events attached to the prediction_date. | global event | no | no | Schema missing share: 25.9%. Names can be null when no curated event name is active; numeric count/severity fields should be used for analysis. |
| event_year | event_metadata | Year of a curated distress event for firms with event metadata. | target/audit metadata | no | yes | Schema missing share: 94.9%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| event_source_ticker | event_metadata | not documented / requires review | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| event_date | event_metadata | Curated formal distress event date where available. | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| event_type | event_metadata | Curated distress/near-distress event type. | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| event_label | event_metadata | Readable event label for the curated event. | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| verification_status | event_metadata | Manual/source verification status for the event-date row. | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| formal_distress_firm | event_metadata | Firm-level flag for a formal distress event in the event metadata. | target/audit metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| near_distress_firm | event_metadata | Firm-level flag for near-distress or context cases not used as strict legal distress. | target/audit metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| days_from_period_to_event | event_metadata | Days from accounting period end to the curated event date. | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| days_to_event | event_metadata | Days from prediction_date to the curated event date. | target/audit metadata | no | yes | Schema missing share: 93.6%. Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row. |
| post_event_flag | event_metadata | Flag for rows on or after a formal event date; excluded from primary forward-looking model training. | target/audit metadata | no | yes | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| distress_next_2q | target_label | Strict formal distress within the shorter forward horizon; exact day horizon is not documented / requires review. | target | no | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| distress_next_4q | target_label | Strict formal distress event after prediction_date and within 456 days. | target | no | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| distress_next_8q | target_label | Strict formal distress within the longer forward horizon; exact day horizon is not documented / requires review. | target | no | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| broad_distress_next_4q | target_label | Earlier broad distress target retained as a secondary label; exact current rule is not documented / requires review. | target | no | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| healthy_current | target_label | Current-period healthy-firm indicator; exact rule is not documented / requires review. | target | no | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| resilient_profitability | target_label | Current or historical profitability/resilience indicator; exact rule is not documented / requires review. | target | no | no | Schema missing share: 0.0%. No missing values observed in the schema snapshot. |
| failure_pressure_conservative_v2_next_4obs | target_label | Main production broader failure-pressure target: formal distress or repeated future profitability weakness with serious balance-stress, deterioration, or unhealthy-future signals. | target | no | no | Schema missing share: 6.0%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| success_profitability_next_4q | target_label | Missing-aware forward profitability target with 29,977 known rows and 24,963 positives. | target | no | no | Schema missing share: 5.5%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| success_resilience_next_4q | target_label | Main production success/resilience target requiring enough observed future net income, ROA, and leverage/assets components. | target | no | no | Schema missing share: 36.4%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| success_quality_next_4q | target_label | Missing-aware future success-quality target with 20,161 known rows and 8,691 positives. | target | no | no | Schema missing share: 36.4%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| industry_relative_resilience_next_4obs | target_label | not documented / requires review | target | no | no | Schema missing share: 36.8%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| stress_resilience_next_4obs | target_label | not documented / requires review | target | no | no | Schema missing share: 81.4%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| recovery_next_4obs | target_label | not documented / requires review | target | no | no | Schema missing share: 64.1%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |
| quality_success_cashflow_next_4obs | target_label | not documented / requires review | target | no | no | Schema missing share: 47.1%. Null target labels mean unknown future outcome or insufficient future information, not automatic zero. |

## 4. SEC Accounting Fundamentals and Ratios

The SEC accounting fundamentals are extracted from SEC Financial Statement Data Sets using a documented concept map. They are not manually typed balance-sheet values. Balance-sheet variables use point-in-time values. Flow variables use single-period values where directly available; when SEC filings report cumulative year-to-date values for Q2, Q3, or Q4, the build logic derives a single-period flow by subtracting the prior cumulative value within the same firm, fiscal year, and variable. If the prior cumulative value is unavailable, the field remains null.

This is important because Q2 and Q3 flow variables are often reported as cumulative values. The flow-standardization pass improved coverage without inventing values. Reported improvements include CapEx missingness falling from about 63.8 percent to about 33.3 percent, operating cash-flow missingness from about 55.6 percent to about 15.7 percent, investing cash-flow missingness from about 55.6 percent to about 15.6 percent, and financing cash-flow missingness from about 55.5 percent to about 15.5 percent.

The current SEC concept-mapping audit is thesis-safe but caveated. It documents mapped tags, qtrs patterns, missingness, accounting identity plausibility, and extreme values. It does not prove perfect harmonization across all firms, years, industries, and accounting practices.

The final polish pass adds row-level selected-fact provenance as a sidecar rather than widening the production panel. `reports/data_quality/sec_selected_fact_provenance.parquet` and `.csv.gz` record the SEC accession number, CIK, standardized variable, selected SEC/XBRL tag, selected value, raw reported value, qtrs value, unit, segment/coreg filters, direct-or-derived `value_method`, and source ZIP. The validation report shows 661,533 selected fact rows, 0 selected-value mismatches above tolerance, and 24 documented exclusions belonging to one invalid timestamp row already excluded from the production panel.

Accounting fundamentals:

| field | plain meaning | statement type | missing share |
| --- | --- | --- | --- |
| accounts_receivable | Accounts receivable, usually current receivables net of allowances. | balance/share | 24.8% |
| capex | Capital expenditure, primarily payments to acquire property, plant, and equipment. | flow | 35.2% |
| cash_equivalents | Cash and cash equivalents, including restricted cash when mapped by the SEC concept map. | balance/share | 4.3% |
| cash_flow_financing | Net cash provided by or used in financing activities. | flow | 16.6% |
| cash_flow_investing | Net cash provided by or used in investing activities. | flow | 16.6% |
| cash_flow_operating | Net cash provided by or used in operating activities. | flow | 16.6% |
| cost_of_revenue | Cost of revenue, cost of goods sold, or cost of sales according to mapped SEC tags. | flow | 48.4% |
| current_assets | Current assets. | balance/share | 17.9% |
| current_liabilities | Current liabilities. | balance/share | 18.0% |
| depreciation_amortization | Depreciation, depletion, and amortization expense. | flow | 35.9% |
| eps_basic | Basic earnings per share. | flow | 9.6% |
| eps_diluted | Diluted earnings per share. | flow | 9.6% |
| gross_profit | Gross profit where separately reported. | flow | 69.8% |
| inventory | Inventory, net. | balance/share | 46.8% |
| long_term_debt | Long-term debt where separately reported. | balance/share | 27.1% |
| net_income | Net income or loss. | flow | 0.5% |
| noncurrent_liabilities | Noncurrent liabilities where separately reported. | balance/share | 87.2% |
| operating_income | Operating income or loss. | flow | 25.8% |
| ppe_net | Property, plant, and equipment, net. | balance/share | 16.7% |
| pretax_income | Income or loss before income taxes, extraordinary items, and noncontrolling interest where mapped. | flow | 50.5% |
| r_and_d_expense | Research and development expense. | flow | 73.0% |
| retained_earnings | Retained earnings or accumulated deficit. | balance/share | 5.6% |
| sg_and_a | Selling, general, and administrative expense. | flow | 50.9% |
| shares_outstanding | Common shares outstanding. | balance/share | 46.4% |
| short_term_debt | Short-term borrowings or current debt. | balance/share | 39.0% |
| total_assets | Total assets. | balance/share | 0.2% |
| total_equity | Stockholders' equity, including noncontrolling interest where mapped. | balance/share | 1.6% |
| total_liabilities | Total liabilities. | balance/share | 32.7% |
| total_revenue | Revenue, sales, or revenue from contracts with customers according to mapped SEC tags. | flow | 10.7% |
| wavg_shares_basic | Weighted average basic shares outstanding. | flow | 25.0% |
| wavg_shares_diluted | Weighted average diluted shares outstanding. | flow | 27.4% |

Financial ratios:

| ratio | formula | meaning | missing share |
| --- | --- | --- | --- |
| leverage_assets | total liabilities divided by total assets | Calculated leverage ratio showing how much of assets are financed by liabilities. | 32.7% |
| equity_assets | total equity divided by total assets | Calculated capitalization ratio showing book equity relative to assets. | 1.7% |
| current_ratio | current assets divided by current liabilities | Calculated liquidity ratio for short-term balance-sheet coverage. | 18.0% |
| cash_assets | cash and equivalents divided by total assets | Calculated liquidity buffer relative to firm size. | 4.4% |
| net_margin | net income divided by total revenue | Calculated profitability margin after all expenses. | 11.1% |
| operating_margin | operating income divided by total revenue | Calculated operating profitability margin. | 30.2% |
| gross_margin | gross profit divided by total revenue | Calculated gross profitability margin where gross profit is available. | 70.2% |
| roa | net income divided by total assets | Calculated return on assets; it is an engineered ratio, not a raw SEC line item. | 0.7% |
| r_and_d_intensity | R&D expense divided by total revenue | Calculated innovation/intangible-investment intensity where R&D is reported. | 73.8% |
| inventory_assets | inventory divided by total assets | Calculated inventory exposure relative to assets. | 46.8% |
| receivables_assets | accounts receivable divided by total assets | Calculated receivables exposure relative to assets. | 24.9% |

Interpretation of ratios must be precise. ROA, margins, leverage/assets, equity/assets, current ratio, cash/assets, R&D intensity, inventory/assets, and receivables/assets are not raw SEC line items. They are engineered ratios derived from SEC fundamentals. This is standard in financial distress and business analytics research, as long as ratios are computed from current or prior information available at the prediction date.

Nulls are preserved. A missing CapEx, R&D, gross profit, debt, inventory, or receivables field does not automatically mean zero. It may reflect non-reporting, non-applicability, concept mapping limits, dimensional facts excluded from consolidated extraction, or unresolved cumulative-flow derivation.

## 5. Firm Trend and Deterioration Features

Trend features are engineered from current and prior firm observations. They are important because distress and resilience are dynamic: a firm that is deteriorating quickly can be riskier than a firm with the same current-level ratio but stable history.

The main trend feature classes are:

- Lag features: `x_lag1 = x` from the prior firm observation.
- Four-observation growth features: `x_growth_4obs = (current x - x from four prior observations) / abs(x from four prior observations)`, where calculable from available values. Exact denominator safeguards are not documented / require review.
- Four-observation change features: `x_change_4obs = current x - x from four prior observations`.
- Prior loss counts: `net_income_negative_count_prior_4obs` counts how many of the prior four firm observations had negative net income.

These features are forward-safe because they use current or prior observations, not future values. They improve the empirical fit because repeated losses, declining profitability, shrinking revenue/assets, rising leverage, worsening liquidity, and margin compression are economically plausible signs of deterioration.

The current factor analysis reports recurring drivers such as ROA, net income, prior negative-income count, net margin and lagged net margin, leverage/assets, equity/assets, total liabilities, lagged leverage, and operating margin. Feature-group interpretation should be preferred over isolated one-feature claims.

## 6. Macro Variables and Regimes

Macro variables come from FRED and are aligned to `prediction_date`. Year-over-year fields use prior-year comparisons. The macro lag audit is `PASS`, so current documentation supports the claim that these values are used as prediction-date context and not as future macro information.

Macro variables:

| variable | what it measures | why it belongs | expected relationship | alignment | dashboard/modeling |
| --- | --- | --- | --- | --- | --- |
| BAMLH0A0HYM2 | High-yield corporate bond spread | Credit stress and risky financing conditions | Higher spreads are expected to be associated with more distress pressure and lower resilience. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| FEDFUNDS | Federal funds rate | Monetary policy and rate pressure | Higher rates may increase financing pressure, especially for leveraged firms. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| GDPC1 | Real GDP | Aggregate economic activity | Weaker growth is expected to be associated with lower firm resilience. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| GS10 | 10-year Treasury yield | Long-term rate environment | Higher yields may raise discount rates and financing costs. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| INDPRO | Industrial production index | Production-side economic activity | Weaker industrial activity may pressure cyclical sectors. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| INDPRO_yoy_pct | Industrial production year-over-year percent change | Growth-rate version of industrial activity | Lower growth is expected to signal demand weakness. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| M2SL | M2 money supply | Liquidity and monetary conditions | Liquidity contraction or slower money growth may coincide with tighter conditions. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| M2SL_yoy_pct | M2 money supply year-over-year percent change | Liquidity growth rate | Lower growth may indicate less supportive liquidity conditions. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| NFCI | Chicago Fed National Financial Conditions Index | Broad financial conditions | Higher values mean tighter conditions and may be associated with pressure. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| UNRATE | Unemployment rate | Labor-market weakness | Higher unemployment can proxy demand stress and macro weakness. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| USEPUINDXD | U.S. economic policy uncertainty index | Policy uncertainty | Higher uncertainty may reduce investment and increase risk. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| VIXCLS | VIX volatility index | Market volatility and risk appetite | Higher volatility is expected to coincide with risk stress. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| T10Y2Y | 10-year minus 2-year Treasury spread | Yield-curve slope | Lower or inverted spread can signal future macro stress. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| T10Y3M | 10-year minus 3-month Treasury spread | Yield-curve slope | Lower or inverted spread can signal future macro stress. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| DCOILWTICO | WTI crude oil price | Commodity and energy cost shock | Higher or volatile oil prices may affect sectors differently. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| DCOILWTICO_yoy_pct | WTI crude oil year-over-year percent change | Oil shock pressure | Large increases may pressure input costs and consumers while helping some energy firms. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| DTWEXBGS | Broad nominal U.S. dollar index | Dollar strength and external competitiveness | A stronger dollar may pressure exporters and firms with foreign revenue exposure. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| DTWEXBGS_yoy_pct | Broad dollar index year-over-year percent change | Dollar-strength shock | Higher growth may indicate exchange-rate pressure. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| CPIAUCSL | Consumer price index | Consumer inflation level | Higher inflation can increase cost and rate pressure. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| CPIAUCSL_yoy_pct | CPI year-over-year percent change | Inflation pressure | Higher inflation may raise costs and monetary-policy pressure. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| PPIACO | Producer price index for all commodities | Input-cost inflation level | Higher producer prices may pressure margins. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| PPIACO_yoy_pct | PPI year-over-year percent change | Input-cost inflation pressure | Higher growth may pressure cost structures. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| PAYEMS | Total nonfarm payroll employment | Labor-market activity | Weaker employment conditions can signal demand weakness. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| PAYEMS_yoy_pct | Payroll employment year-over-year percent change | Labor-market growth | Lower growth may signal weakening demand conditions. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| RSAFS | Retail sales | Consumer demand | Lower retail sales may pressure consumer-facing firms. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| RSAFS_yoy_pct | Retail sales year-over-year percent change | Consumer-demand growth | Lower growth is expected to weaken resilience in demand-sensitive sectors. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| HOUST | Housing starts | Rate-sensitive real-economy activity | Lower housing starts may indicate rate-sensitive demand weakness. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| HOUST_yoy_pct | Housing starts year-over-year percent change | Housing activity growth | Lower growth can indicate pressure on housing-linked sectors. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| BUSLOANS | Commercial and industrial loans | Business credit availability | Weak loan growth can indicate tighter credit or weaker demand. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| BUSLOANS_yoy_pct | Commercial and industrial loans year-over-year percent change | Business-credit growth | Lower growth may signal tighter credit availability. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |
| DRTSCILM | Bank lending standards for C&I loans to large and middle-market firms | Credit tightening | Higher tightening standards are expected to increase financing pressure. | Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values. | Available as dashboard context and current model feature. |

Regime indicators convert macro variables into interpretable market states. A regime is a market environment flag, not a target and not a separate dataset. Regimes make the phrase "market shifts" concrete by identifying high-rate, market-stress, tight-credit, inflation-pressure, oil-shock, strong-dollar, demand-slowdown, and crisis-year conditions.

Regime indicators:

| regime | meaning | expected relationship | alignment | dashboard/modeling |
| --- | --- | --- | --- | --- |
| high_rate_regime | Federal funds rate is at least 4 percent. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| market_stress_regime | VIX is at least 25. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| tight_financial_conditions | NFCI is above 0, meaning tighter-than-average financial conditions. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| credit_spread_stress_regime | High-yield spread is at least 5 percentage points. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| yield_curve_inversion_regime | T10Y2Y or T10Y3M is below 0. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| inflation_pressure_regime | CPI year-over-year inflation is at least 4 percent. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| oil_shock_regime | WTI oil year-over-year change is at least 30 percent. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| strong_dollar_regime | Broad U.S. dollar index year-over-year change is at least 5 percent. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| demand_slowdown_regime | Retail sales year-over-year change is below 0. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| credit_tightening_regime | Bank lending-standards tightening measure is positive. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |
| crisis_regime | Prediction year is 2009, 2020, 2022, or 2023. | Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof. | Derived from prediction-date-aligned macro values. | Available as dashboard filter/context and current model feature. |

The market-health index is a reporting/dashboard layer built from existing prediction-date-aligned macro, regime, and global-event context. It does not modify the production panel and is not a target. It contains components such as `credit_stress_score`, `rate_pressure_score`, `inflation_pressure_score`, `demand_weakness_score`, `market_volatility_score`, `event_stress_score`, `market_stress_score`, `market_health_score`, and `market_health_regime`. Higher market-stress score means more stressful macro/event conditions. Higher market-health score means healthier macro/event conditions.

The market-health index uses training-period standardization from prediction years 2009-2018. Its latest documented output has 3,319 unique prediction-date rows, 18 audit rows, and `production panel modified: False`. It should be used for dashboard context, sector/regime comparison, and thesis interpretation, not as causal proof that macro conditions dominate firm fundamentals.

### Market-Health Indicator Selection Logic

The market-health indicator was developed iteratively as a compact representation of the macro-financial environment surrounding each firm observation. The first version used a continuous standardized index. Prediction-date-aligned macro and event variables were standardized against the 2009-2018 training period, direction-adjusted so that higher transformed values represented greater stress, clipped to limit outlier influence, and averaged into component scores such as credit stress, rate pressure, inflation pressure, demand weakness, market volatility, and event stress.

That first version preserved continuous variation in macro conditions, but it was less transparent for thesis interpretation and dashboard use. A score from the standardized index represented an average of transformed z-scores rather than a directly observable economic condition. Movement in the score could also reflect offsetting changes across several components, which made it harder to explain why a particular date was classified as healthier or more stressed.

For this reason, the final market-health v2 layer was simplified into a threshold-based stress indicator. Instead of asking how far each macro variable was from its training-period mean, the revised version asks whether economically interpretable stress conditions are active at the prediction date. These conditions include high market volatility, elevated high-yield spreads, tight financial conditions, tightening lending standards, yield-curve inversion, high inflation, oil-price shock, dollar-strength pressure, negative retail-sales growth, weak industrial production, weak payroll growth, and weak housing activity.

The resulting market-stress score is easier to interpret because it represents the share of selected stress conditions active at the prediction date, while the market-health score is its complement. This design sacrifices some continuous detail, but it improves auditability, dashboard communication, and thesis defensibility. Each component can be traced to a visible macroeconomic rule, and all inputs remain aligned to information available at the prediction date.

The final choice therefore prioritizes interpretability, temporal validity, and economic transparency over statistical smoothness. The market-health indicator should not be interpreted as a causal explanation of firm failure or success. It is a contextual market-shift layer that allows firm outcomes, target definitions, dashboard views, and model outputs to be compared across different macro-financial environments.

## 7. Global-Event Context

The global-event layer is a curated historical event calendar, not a full news/NLP database. It is merged into the production panel as `global_event_context` fields. The current panel has 27 global-event context columns.

Current event types are:

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

For each prediction date, the panel records active event-window counts and severity sums. The fields include total event count, total severity, type-specific counts, type-specific severities, and `global_event_names`.

The event layer is used as historical market-shift context. It supports questions such as whether sectors behave differently during pandemic, supply-chain, oil, banking-stress, or geopolitical-war windows. It should not be described as live event prediction. The dashboard can update macro/event context more often than SEC filings, but firm fundamentals update only when new filings arrive.

Current evidence says event features are useful for explanation and dashboard analysis, but firm fundamentals, ratios, and deterioration remain the dominant predictive signal. That is a strength, not a failure: the title is about navigating market shifts through predictive insights into success and failure factors, not proving that event labels alone predict bankruptcy.

## 8. Targets

Targets use future information only to label outcomes. They must never be used as model input features. The final thesis uses a target hierarchy because strict formal distress is clean but rare, while success/failure-factor analysis is broader than bankruptcy alone.

Production targets:

| target | role | definition | known/positive | model result | limitation |
| --- | --- | --- | --- | --- | --- |
| distress_next_4q | Strict legal distress benchmark | Positive when a formal distress event occurs after prediction_date and within 456 days. | 31,702 known; 207 positives. | Gradient boosting test PR-AUC 0.104; F1 0.182. | Strict legal distress is source-verified for current formal rows but remains rare. |
| failure_pressure_conservative_v2_next_4obs | Main broader failure-factor target | Formal distress, or repeated future profitability weakness with serious balance-stress, deterioration, or unhealthy-future signal; at least three future observations required unless formal distress overrides. | 29,805 known; 3,003 positives; 1,897 unknown. | Random forest test PR-AUC 0.758; F1 0.725. | Not a legal bankruptcy label; exact component thresholds are not fully exposed in the current prose docs / require review if quoted. |
| success_resilience_next_4q | Main success/resilience target | Positive when at least three of the next four future observations have positive net income, positive ROA, acceptable leverage/assets, and no formal distress. | 20,152 known; 12,519 positives; 11,550 unknown. | Random forest test PR-AUC 0.975; F1 0.938. | Unknown future components remain null; metrics are not comparable mechanically to rare strict distress. |
| industry_relative_resilience_next_4obs | Validated secondary production outcome | Positive when future profitability is above sector-year peer medians in at least three future observations, leverage is not in the sector-year worst quartile, and no formal distress occurs. | 20,039 known; 8,093 positives; 11,663 unknown. | Gradient boosting baseline test PR-AUC 0.855; F1 0.787; calibrated gate test PR-AUC 0.844. | Sector-year thresholds support relative benchmarking, not causal peer effects. |
| stress_resilience_next_4obs | Validated secondary production outcome | Evaluated only under elevated current market stress; positive when at least three of the next four observations remain financially healthy and no formal distress occurs. | 5,901 known; 3,707 positives; 25,801 unknown. | Random forest baseline test PR-AUC 0.974; F1 0.937; calibrated gate test PR-AUC 0.969. | Stress-gated target has narrower coverage and a high positive base rate, so ranking lift is modest. |
| recovery_next_4obs | Validated secondary production outcome | Evaluated only for currently weak firms; positive when future observations improve to healthy status repeatedly and no formal distress occurs. | 11,375 known; 5,578 positives; 20,327 unknown. | Random forest baseline test PR-AUC 0.977; F1 0.915; calibrated gate test PR-AUC 0.968. | Interpretation is leverage-sensitive because current weakness and future health definitions include leverage/assets. |
| quality_success_cashflow_next_4obs | Validated secondary production outcome | Positive when at least three future observations show positive net income, positive ROA, positive operating cash flow, acceptable leverage/assets, and no formal distress. | 16,767 known; 9,852 positives; 14,935 unknown. | Gradient boosting baseline test PR-AUC 0.953; F1 0.920; calibrated gate test PR-AUC 0.949. | Cash-flow support adds quality information, but leverage and profitability remain stronger model drivers. |

Why the targets are forward-looking:

- `distress_next_4q` looks for a formal event after `prediction_date` and within the forward window.
- `failure_pressure_conservative_v2_next_4obs` examines future firm observations after the current row.
- `success_resilience_next_4q` examines the next four future observations after the current row.

Why missing labels remain null:

- A missing future component means the future outcome is not sufficiently observed.
- Treating unknown future leverage, liability, ROA, or net income as zero or failure would contaminate targets.
- The missingness fix made future success labels missing-aware, so insufficient future information stays null rather than becoming automatic non-success.

Preferred and rejected positioning:

- `distress_next_4q` is preferred as the strict legal benchmark, but rejected as the headline performance target because it is too rare and still has event-date provenance caveats.
- `failure_pressure_conservative_v2_next_4obs` is preferred as the main failure-factor target because it is conservative, learnable, and economically interpretable.
- `success_resilience_next_4q` is preferred as the production success/resilience counterpart because it is missing-aware and empirically strong.
- `industry_relative_resilience_next_4obs`, `stress_resilience_next_4obs`, `recovery_next_4obs`, and `quality_success_cashflow_next_4obs` are validated secondary production outcomes. They add relative resilience, stress resilience, recovery, and cash-flow-supported success dimensions without replacing the three primary targets.
- `failure_pressure_balance_liquidity_next_4obs`, `success_resilience_quality_v2_next_4obs`, `deterioration_next_4obs`, `persistent_resilience_next_6obs`, and `sector_relative_improvement_next_4obs` are useful diagnostic or robustness targets but are not current production panel columns according to the target hierarchy.
- Older random-split and superseded broader-target results must not be cited as final model results.

## 9. Models and Tuning

The modeling workflow uses temporal validation rather than random splitting. Train rows are prediction years through 2018, validation rows are 2019-2021, and test rows are 2022-2024. Candidate choice and threshold selection use validation data only; test metrics are observed after validation selection and should not be used for further tuning.

Production best-model summary:

| target | best_model | test_rows | test_positives | roc_auc | pr_auc | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| distress_next_4q | gradient_boosting | 5872 | 96 | 0.816 | 0.104 | 0.120 | 0.375 | 0.182 |
| failure_pressure_conservative_v2_next_4obs | random_forest | 5735 | 575 | 0.954 | 0.758 | 0.669 | 0.791 | 0.725 |
| success_resilience_next_4q | random_forest | 4047 | 2648 | 0.967 | 0.975 | 0.941 | 0.934 | 0.938 |
| industry_relative_resilience_next_4obs | gradient_boosting | 4098 | 1678 | 0.900 | 0.855 | 0.710 | 0.883 | 0.787 |
| stress_resilience_next_4obs | random_forest | 3028 | 1920 | 0.966 | 0.974 | 0.896 | 0.982 | 0.937 |
| recovery_next_4obs | random_forest | 2419 | 1199 | 0.976 | 0.977 | 0.917 | 0.912 | 0.915 |
| quality_success_cashflow_next_4obs | gradient_boosting | 3998 | 2458 | 0.945 | 0.953 | 0.897 | 0.944 | 0.920 |

Model intuition:

- Logistic regression estimates a linear relationship between features and the log-odds of the target. It is interpretable and useful as a benchmark. The tuning pass varied L2 regularization strength `C`.
- Random forest averages many decision trees trained with randomization. It captures nonlinear effects and interactions. Key hyperparameters include number of trees, maximum depth, minimum samples per leaf, maximum feature sampling, and random seed.
- Extra trees are a randomized tree ensemble used in tuning robustness. They add more randomization in split selection and can improve rare-event ranking.
- Gradient boosting builds trees sequentially, where each new tree focuses on correcting prior errors. Key hyperparameters include number of estimators, learning rate, tree depth, and subsampling.
- Histogram gradient boosting is an efficient boosted-tree implementation using binned features. Key hyperparameters include learning rate, max iterations, max leaf nodes, and L2 regularization.
- XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks. They are not described as AutoGluon or exhaustive AutoML.

Baseline versus controlled tuning:

| target | baseline | baseline PR-AUC/F1 | validation-selected tuned | tuned PR-AUC/F1 | interpretation |
| --- | --- | --- | --- | --- | --- |
| distress_next_4q | gradient_boosting | 0.104 / 0.182 | extra_trees_cfg3_seed777 | 0.143 / 0.237 | Validation selected; test observed once and not used for further tuning. |
| failure_pressure_conservative_v2_next_4obs | random_forest | 0.758 / 0.725 | hist_gradient_boosting_cfg4 | 0.748 / 0.685 | Validation selected; test observed once and not used for further tuning. |
| success_resilience_next_4q | random_forest | 0.975 / 0.938 | random_forest_cfg1_seed202 | 0.974 / 0.943 | Validation selected; test observed once and not used for further tuning. |

Advanced XGBoost/LightGBM robustness:

| target | advanced candidate | family | advanced PR-AUC/F1 | positioning |
| --- | --- | --- | --- | --- |
| distress_next_4q | xgboost_cfg1_seed42 | XGBoost | 0.088 / 0.140 | Robustness benchmark from docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md, not production overwrite. |
| failure_pressure_conservative_v2_next_4obs | lightgbm_cfg3_seed42 | LightGBM | 0.760 / 0.686 | Robustness benchmark from docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md, not production overwrite. |
| success_resilience_next_4q | xgboost_cfg4_seed777 | XGBoost | 0.962 / 0.919 | Robustness benchmark from docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md, not production overwrite. |

Metric interpretation:

- ROC-AUC measures ranking quality across thresholds, but it can look optimistic for rare events.
- PR-AUC is more informative for rare positives because it focuses on precision-recall tradeoffs.
- Precision measures how many predicted positives are actually positive.
- Recall measures how many actual positives are found.
- F1 balances precision and recall at the selected threshold.

Strict distress is the rare-event benchmark because it has 207 full-panel positives and 96 test positives. Broader failure pressure is the main failure-factor target because it has enough positives for stable factor analysis and remains economically meaningful. Success/resilience is the success counterpart and should be interpreted separately because it is much less rare.

## 10. Missingness and Imputation

The raw panel preserves null values. The documented null-treatment audit reports 4,863,258 numeric cells, 680,419 preserved numeric null cells, and an overall numeric null share of about 14.0 percent.

Missingness by feature family:

| feature_family | columns | average_missing_share | max_missing_share | columns_over_50pct_missing |
| --- | --- | --- | --- | --- |
| event_metadata | 11 | 0.6818095789769502 | 0.9494669106050092 | 8 |
| sec_accounting_fundamental | 31 | 0.2872404508924846 | 0.8723108952116586 | 5 |
| financial_ratio | 11 | 0.2858810169705381 | 0.7376190776607154 | 2 |
| firm_trend_or_deterioration | 21 | 0.2410062757044019 | 0.7258532584694972 | 2 |
| target_label | 10 | 0.0843385275376947 | 0.3643303261623872 | 0 |
| industry_or_universe_metadata | 9 | 0.0317014699388051 | 0.2368935713835089 | 0 |
| global_event_context | 27 | 0.0096056563787306 | 0.2593527222257271 | 0 |
| identifier_or_time | 24 | 0.0078846234727567 | 0.1884739133177717 | 0 |
| macro_variable | 31 | 0.0027361660300255 | 0.0352028263201059 | 0 |
| macro_regime_indicator | 11 | 0.0 | 0.0 | 0 |

The correct missingness policy is:

- do not treat null as zero by default;
- do not treat null as unchanged by default;
- do not forward-fill the main panel;
- use model-pipeline imputation only inside estimation;
- use missingness indicators as predictive auxiliaries, not economic causes;
- keep unknown future target components as null labels.

Sklearn pipelines may impute numeric missing values with training-split medians and create missingness indicators such as `missingindicator_total_liabilities`. These indicators are model-engineering artifacts. They are not raw SEC variables and are excluded from economic factor interpretation.

The total-liabilities missingness diagnosis found that the old success target was vulnerable: missing future leverage/liability values could become automatic non-success. This was fixed. The rebuilt `success_resilience_next_4q` target has 20,161 known rows, 11,556 unknown rows, and 12,526 positives among known rows. Rows currently zero but revised missing-aware logic says unknown: 0. Known current/revised disagreements: 0.

## 11. Interpretation and Factor Analysis

Feature importance and contribution tables are tools for association-based interpretation. They do not prove causality. They should be read as evidence about which current and prior features help separate future pressure, strict distress, or resilience under the documented modeling setup.

The safest interpretation level is economic feature groups:

- accounting fundamentals;
- financial ratios;
- firm trend/deterioration;
- macro conditions;
- regimes;
- global-event context;
- industry/sector;
- missingness indicators, separated and not economically interpreted.

The current feature-group interpretation excludes missingness indicators from economic-factor shares. The recurring substantive drivers across model outputs include profitability, net income, prior loss counts, margins, leverage/assets, equity/assets, total liabilities, lagged leverage, and operating margin. The thesis should emphasize that firm fundamentals and deterioration dominate, while macro/regime/event features mainly contextualize market shifts and sector behavior.

Permutation or SHAP-style explanations are only thesis-ready if saved outputs exist and are described in the current reports. The current source set includes saved permutation output for success, but not a full SHAP package across all targets. Therefore, if SHAP is mentioned, it should be labeled not documented / requires review unless additional verified outputs are created.

Across industries, regimes, and event windows, the dashboard should be used to compare patterns rather than claim universal laws. For example, oil shocks can have different implications for energy firms than consumer firms. High-rate regimes can matter more for leveraged firms. Event labels provide context, while firm fundamentals determine much of the observed model signal.

## 12. Safe Thesis Claims and Unsafe Claims

Safe claims:

- The project constructs a reproducible U.S. public-company firm-period panel from SEC FSD, FRED macro variables, curated global-event context, distress-event labels, and industry metadata.
- The production panel has 31,702 rows, 190 columns, 540 SEC CIKs, and 540 ticker/display IDs.
- The panel uses `prediction_date = filed_date`, which reduces look-ahead leakage by aligning observations to the date filings became available.
- The project uses temporal validation rather than random splitting for final model claims.
- Strict legal distress is a clean but rare benchmark, not the headline performance target.
- Broader conservative failure pressure is the main failure-factor target.
- Success/resilience is the main positive-outcome counterpart.
- Nulls are preserved in the raw panel and imputed only inside modeling pipelines.
- Missingness indicators may help prediction but are not interpreted as economic causes.
- Firm accounting fundamentals, ratios, and deterioration features provide the strongest current empirical signal.
- Macro variables, regimes, and curated global events provide market-shift context and support dashboard/sector analysis.
- XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks; AutoGluon was not used in production.
- The dashboard is a historical decision-support and early-warning artifact based on latest available filings and aligned macro/event context.

Unsafe claims:

- All strict distress labels are fully verified bankruptcy events.
- The model perfectly predicts bankruptcy.
- The broader failure-pressure target is the same thing as legal bankruptcy.
- The market-health index proves macro conditions cause bankruptcy.
- Macro or global-event variables dominate firm fundamentals in the current results.
- Null accounting values mean zero or unchanged values.
- Missing total liabilities causes success or failure.
- The production workflow used HR, ESG, NLP, market-price features, Russian RFSD, Hong Kong/Japan data, paid datasets, or live event feeds.
- Exhaustive AutoML or AutoGluon optimization was performed.
- SEC tags are perfectly harmonized across all firms, sectors, and years.
- Dashboard visuals alone validate scientific accuracy.

## Appendix Pointers

Use these files as appendix evidence:

- `reports/documentation/master_column_dictionary.csv` for the complete column dictionary.
- `data/github/firm_panel_v2_schema.csv` for schema, dtypes, feature families, and missing shares.
- `reports/data_quality/p0_audit_status.csv` for P0 audit status.
- `reports/data_quality/sec_concept_mapping_summary.csv` for SEC concept coverage.
- `reports/data_quality/panel_v2_missingness_by_feature_family.csv` for missingness by feature family.
- `reports/modeling/*_model_metrics.csv` for model metrics.
- `reports/model_tuning/baseline_vs_tuned_comparison.csv` for controlled tuning.
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md` for XGBoost/LightGBM robustness.
- `docs/BIBLIOGRAPHY.md` and `docs/references.bib` for the curated bibliography.
