# Literature Matrix

Last updated: 2026-05-06

The full machine-readable matrix is in `reports/literature/literature_matrix.csv`. It records what each source actually supports, its limitation, and how it should be used in the thesis.

## Bucket Coverage

| Bucket | References |
| --- | --- |
| Classical firm failure and financial distress prediction | 11 |
| Design science, dashboard, and decision-support artifact framing | 5 |
| Emerging-market and Russia-specific distress prediction context | 5 |
| Firm fundamentals, financial ratios, and deterioration features | 7 |
| Interpretability and explainable ML | 7 |
| Machine learning, rare-event evaluation, and temporal validation | 15 |
| Macroeconomic conditions, credit cycles, and market-shift/default context | 7 |
| Missing data, data integrity, and accounting-data limitations | 4 |
| Official data sources and empirical context | 8 |
| Strategic management and resilience framing | 6 |

## Matrix Preview

| Key | Year | Bucket | Contribution | Thesis Use |
| --- | --- | --- | --- | --- |
| beaver1966financial | 1966 | Classical firm failure and financial distress prediction | Shows that accounting ratios can contain early warning information before business failure. | Historical foundation for ratio-based failure signals. |
| altman1968financial | 1968 | Classical firm failure and financial distress prediction | Introduces the Z-score logic that combines multiple ratios into a failure-risk score. | Benchmark for classical bankruptcy prediction. |
| altman1997international | 1997 | Classical firm failure and financial distress prediction | Shows that failure prediction is an international, mature field with many country-specific model variants. | Prevents overclaiming novelty in bankruptcy prediction itself. |
| ohlson1980financial | 1980 | Classical firm failure and financial distress prediction | Moves bankruptcy prediction toward probabilistic modeling with accounting variables. | Supports logistic benchmark and probability framing. |
| zmijewski1984methodological | 1984 | Classical firm failure and financial distress prediction | Highlights sample selection and estimation problems in distress modeling. | Supports explicit audit and label-construction discussion. |
| merton1974pricing | 1974 | Classical firm failure and financial distress prediction | Provides a structural market-based theory of default risk. | Future-work comparator only, not an implemented model. |
| hillegeist2004assessing | 2004 | Classical firm failure and financial distress prediction | Compares accounting-score approaches with market-based probability estimates. | Supports limitation/future-work discussion about market-based features. |
| shumway2001forecasting | 2001 | Classical firm failure and financial distress prediction | Argues that bankruptcy prediction should use time-varying panel logic rather than one static observation per firm. | Supports firm-period panel and temporal framing. |
| duffie2007multi | 2007 | Macroeconomic conditions, credit cycles, and market-shift/default context | Links corporate default prediction to time-varying firm and macro-financial covariates. | Supports dynamic macro-context variables and forward horizons. |
| campbell2008distress | 2008 | Classical firm failure and financial distress prediction | Shows distress risk is related to profitability, leverage, market conditions, and dynamic firm characteristics. | Supports profitability/leverage/deterioration signal interpretation. |
| bharath2008forecasting | 2008 | Classical firm failure and financial distress prediction | Evaluates structural distance-to-default ideas against simpler default forecasting inputs. | Future-work and limitation source. |
| bauer2014hazard | 2014 | Classical firm failure and financial distress prediction | Tests whether hazard approaches outperform traditional models under comparable settings. | Supports methodological caution and model-comparison framing. |
| tinoco2013financial | 2013 | Macroeconomic conditions, credit cycles, and market-shift/default context | Directly supports combining accounting, market, and macroeconomic variables for listed-company distress prediction. | Core support for the SEC plus FRED design. |
| tian2017financial | 2017 | Firm fundamentals, financial ratios, and deterioration features | Shows ratio signals can generalize across countries, while still requiring local validation. | Supports ratio families and warns against country-blind generalization. |
| alaminos2016global | 2016 | Firm fundamentals, financial ratios, and deterioration features | Demonstrates interest in broader, cross-country bankruptcy-prediction models. | Supports discussion of scope limits and future international extensions. |
| taffler1983assessment | 1983 | Firm fundamentals, financial ratios, and deterioration features | Reinforces the long-standing link between solvency, performance, and accounting data. | Background support for solvency and performance indicators. |
| platt1994bankruptcy | 1994 | Firm fundamentals, financial ratios, and deterioration features | Broadens the distress-prediction feature discussion beyond pure financial-ratio sets. | Supports using richer firm-period attributes and context variables. |
| billios2024power | 2024 | Firm fundamentals, financial ratios, and deterioration features | Recent review evidence that numerical financial indicators and cash-flow information remain useful for bankruptcy prediction. | Modern support that accounting/numerical indicators remain relevant. |
| valaskova2023postpandemic | 2023 | Firm fundamentals, financial ratios, and deterioration features | Shows renewed post-pandemic interest in firm failure prediction and financial-health monitoring. | Recent context for why distress/resilience analysis remains current after large market shocks. |
| bragoli2022industrial | 2022 | Firm fundamentals, financial ratios, and deterioration features | Directly motivates industry metadata and sector-aware analysis. | Supports inclusion of industry metadata and sector summaries. |

## Usage Rule

When writing the thesis, use the `main_limitation_or_critique` column. The literature review should not read like a list of summaries; it should explain what each stream contributes and where it remains insufficient for the current research problem.
