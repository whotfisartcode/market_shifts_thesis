# Factor Analysis and Data Integrity Position

Updated: 2026-05-07

## Main Position

The thesis does not need to be sold as a pure forecasting project.

Better framing:

> Predictive analytics is used to identify and compare success and failure factors across industries and market-shift contexts. The early-warning model is one artifact, while the main empirical contribution is the structured panel, factor analysis, sector/event comparisons, and dashboard.

This fits the fixed title:

> Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries

## What "Predictive" Means Here

Predictive analytics can mean:

- estimating forward-looking distress and resilience labels;
- ranking firms by risk/resilience using latest available filings;
- identifying which accounting, trend, macro, event, and industry features separate future-success and future-failure observations;
- comparing how industries behave under different market regimes and global event windows.

It does not have to mean:

- real-time stock-price prediction;
- daily bankruptcy prediction;
- claiming the model can forecast global events;
- claiming firm fundamentals update daily.

## Current Analytical Questions

Primary empirical questions:

1. Which firm-level financial factors are most associated with forward distress?
2. Which firm-level financial factors are most associated with forward resilience/success?
3. Do these factors differ across industries?
4. Do macro regimes and global event windows change sector outcomes?
5. Does adding macro/event context improve the analysis beyond firm fundamentals?

Recommended thesis wording:

> The model is evaluated as an early-warning and factor-discovery tool rather than as a standalone automated prediction engine.

## Factual Data Lineage

No financial values in the panel are manually invented.

Source families:

- SEC Financial Statement Data Sets: accounting fundamentals from structured XBRL filings.
- FRED: macroeconomic and financial market variables.
- SEC/company metadata and SIC codes: firm and industry metadata.
- Curated event calendar: manually selected global event windows with source URLs.
- Distress event date file: manually curated bankruptcy/distress dates; still needs final verification.

Important distinction:

- raw accounting values come from SEC data;
- ratios are calculated from SEC values;
- trend features are calculated from current/prior firm observations;
- macro year-over-year changes are calculated from FRED series;
- event flags are calculated from event-calendar date windows;
- target labels are calculated from event dates and future firm observations.

## Null Values

The exported dataset preserves nulls.

Current audit:

```text
reports/data_quality/panel_v2_null_treatment_audit.csv
```

Current result:

- numeric cells in exported panel: 4,977,214;
- numeric null cells preserved: 661,300;
- overall numeric null share: about 13.3%.

This means missing values are not filled inside the dataset.

Model treatment:

- numeric nulls are imputed inside the sklearn pipeline using training-split medians;
- explicit missingness indicators are added inside the pipeline;
- the persisted CSV/Parquet panel remains null-preserving.

Interpretation:

> Imputation is a model-estimation step, not a data-fabrication step.

## Why a Value Is Null

A null value does not have one universal meaning.

Possible reasons:

1. The firm did not report that line item separately.
2. The item is not applicable or not material for that firm.
3. The value is embedded in another line item.
4. The firm used a tag outside the current concept map.
5. A dimensional/segment value existed but was excluded because the panel keeps consolidated entity-level facts.
6. A cumulative flow value could not be converted into a single-period value because the prior cumulative value was unavailable.
7. In some balance-sheet cases, the value may have stayed unchanged and therefore was not separately disclosed, but this cannot be proven from absence alone.

Policy:

- do not treat null as zero by default;
- do not treat null as unchanged by default;
- do not forward-fill the main dataset;
- use missingness indicators during modeling;
- use longitudinal missingness audits to explain whether a variable is never reported, intermittently missing, or has prior/future values nearby.

Audit outputs:

```text
reports/data_quality/panel_v2_longitudinal_missingness_summary.csv
reports/data_quality/panel_v2_longitudinal_missingness_by_firm.csv
```

Current examples:

- `r_and_d_expense` is missing in about 75.9% of rows, and about 69.6% of firms never report it in the selected panel. This is mostly structural/reporting absence, not a quarter-to-quarter unchanged-value issue.
- `gross_profit` is missing in about 69.9% of rows, and about 65.6% of firms never report it separately. Many firms report revenue and cost lines differently.
- `cash_flow_operating` is missing in about 16.5% of rows, but every firm has at least some observed values. This is more plausibly intermittent filing/tagging or derivation limitation than total absence.
- `total_assets` is missing in about 0.2% of rows, so core balance-sheet coverage is strong.

## SEC Flow Variable Fix

The audit found an important issue:

- many cash-flow variables are filed as year-to-date values in Q2 and Q3;
- the earlier parser only accepted `qtrs=1` and `qtrs=4` for flow variables;
- this made Q2/Q3 CapEx and cash-flow coverage look much worse than it really was.

Fix implemented:

- SEC flow variables now accept `qtrs=1`, `qtrs=2`, `qtrs=3`, and `qtrs=4`;
- if a current-period value is directly reported, it is used;
- if only a cumulative value is reported, the single-period value is derived by subtracting the prior cumulative value within the same firm, fiscal year, and variable;
- if the prior cumulative value is unavailable, the field remains null.

This is not invented data. It is a derived accounting value from reported cumulative filings.

Coverage improvement:

- `capex` missingness improved from about 63.8% to about 33.3%;
- `cash_flow_operating` missingness improved from about 55.6% to about 15.7%;
- `cash_flow_investing` missingness improved from about 55.6% to about 15.6%;
- `cash_flow_financing` missingness improved from about 55.5% to about 15.5%.

Audit outputs:

```text
reports/data_quality/sec_fsd_variable_source_audit.csv
reports/data_quality/panel_v2_key_missingness_by_form_fp.csv
reports/data_quality/panel_v2_missingness_by_feature_family.csv
```

## Current Factor Findings

Economic feature-group interpretation should use:

```text
reports/modeling/panel_v2_feature_contribution_economic_groups.csv
```

This excludes missingness indicators from economic-factor shares so reporting gaps are not confused with financial mechanisms.

Current strict legal-distress benchmark:

- target: `distress_next_4q`;
- best post-rebuild baseline model: random forest;
- test positives: 96;
- random forest test ROC-AUC: about 0.798;
- random forest test PR-AUC: about 0.157;
- random forest test precision: about 0.147;
- random forest test recall: about 0.146;
- random forest test F1: about 0.147.

Current main broader failure-pressure target:

- target: `failure_pressure_conservative_v2_next_4obs`;
- best post-rebuild baseline model: random forest;
- test positives: 575;
- random forest test ROC-AUC: about 0.955;
- random forest test PR-AUC: about 0.764;
- random forest test precision: about 0.679;
- random forest test recall: about 0.793;
- random forest test F1: about 0.731.

Current main success/resilience target:

- target: `success_resilience_next_4q`;
- best post-rebuild baseline model: random forest;
- test positives: 2,648;
- random forest test ROC-AUC: about 0.966;
- random forest test PR-AUC: about 0.973;
- random forest test precision: about 0.938;
- random forest test recall: about 0.946;
- random forest test F1: about 0.942.

Current ablation result:

- after the +150 firm expansion, source-verified event-date additions, and 2026-05-07 SEC period-alignment rebuild, strict legal-distress support is 96 test positives and remains a difficult rare-event benchmark;
- broader financial-pressure targets perform much better and are useful for factor analysis;
- macro/regime/event context remains useful for explanation and dashboard views, but does not dominate firm fundamentals.

Interpretation:

> Firm fundamentals and deterioration carry the strongest predictive signal. Macro regimes and global event windows are better used to explain market-shift context and industry reactions than to replace accounting-based firm analysis.

## Dashboard Implication

The dashboard should have two roles:

1. Historical factor analyzer.
   Compare success/failure factors across sectors, macro regimes, and global event windows.

2. Latest-filing early-warning view.
   Score firms using the latest available filing and current macro/event context.

Correct limitation:

> Firm accounting scores update when new filings become available. Macro and event context can update more frequently, but the dashboard is not a daily accounting prediction system.

## P0 Audit Position

The peer-review P0 audit path is now implemented.

Current combined status:

```text
reports/data_quality/p0_audit_status.csv
```

Results:

- prediction timestamp audit: `PASS`;
- leakage audit: `PASS`;
- macro lag audit: `PASS`;
- global-event timing audit: `PASS`;
- post-event row audit: `PASS`;
- distress event-date audit: `PASS`.

The previous event-date provenance caveat has been resolved for the current package. All 44 formal strict-distress event rows now have source-provenance records in `config/distress_event_source_provenance.csv`; the 6 near-distress rows remain context only and are not strict legal distress labels.
