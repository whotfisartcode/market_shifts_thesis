# Target And Factor Tweak Assessment

Updated: 2026-05-05

## Purpose

This second pass tested whether the dataset can support stronger conclusions about success and failure factors, not just strict bankruptcy prediction.

The work tested:

- small target-definition tweaks;
- multiple success/failure composite definitions;
- feature-set ablations;
- factor-group stability;
- dashboard implications.

Outputs are in:

```text
reports/target_tweak_experiments/
```

Current expanded-panel compact metrics are in:

```text
reports/target_tweak_experiments/dashboard_best_target_rows.csv
reports/target_tweak_experiments/dashboard_feature_set_performance.csv
reports/target_tweak_experiments/dashboard_factor_group_best_models.csv
```

The expanded-panel rerun after source-verified event-date updates supersedes the earlier pre-expansion headline metrics in the strategic docs. Current headline results are:

- `failure_pressure_conservative_v2_next_4obs`: PR-AUC about 0.739, F1 about 0.705.
- `failure_pressure_balance_liquidity_next_4obs`: PR-AUC about 0.906, F1 about 0.813.
- `success_resilience_quality_v2_next_4obs`: PR-AUC about 0.929, F1 about 0.875.

## What Was Tested

Five target-tweak folders were created:

1. `test_target_tweaks1`
   - Failure: `failure_pressure_conservative_v2_next_4obs`
   - Success: `success_resilience_quality_v2_next_4obs`
   - Tweak: keeps the conservative idea but tests stronger deterioration thresholds.

2. `test_target_tweaks2`
   - Failure: `failure_pressure_profit_roa_next_4obs`
   - Success: `success_quality_growth_next_4obs`
   - Tweak: focuses on future losses, weak future ROA, operating weakness, and growth quality.

3. `test_target_tweaks3`
   - Failure: `failure_pressure_balance_liquidity_next_4obs`
   - Success: `success_stable_balance_next_4obs`
   - Tweak: isolates leverage/liquidity stress and balance-sheet stability.

4. `test_target_tweaks4`
   - Failure: `failure_pressure_sector_strict_next_4obs`
   - Success: `success_sector_quality_next_4obs`
   - Tweak: sector-relative future ROA thresholds to avoid punishing naturally lower-margin sectors.

5. `test_target_tweaks5`
   - Failure: `failure_pressure_score3_next_4obs`
   - Success: `success_score3_next_4obs`
   - Tweak: explicit component-score targets for dashboard-friendly scoring.

Feature-set ablation was then run for selected targets using:

- `firm_core`: accounting + ratios + trend + sector;
- `ratios_trends_only`: financial ratios + trend + sector;
- `raw_accounting_only`: raw accounting fundamentals + sector;
- `macro_event_only`: macro, regime, event, and sector context;
- `all_features`: full model feature list.

## Integrity Rules

These rules were preserved:

- post-event rows excluded;
- formal `distress_next_4q` captured inside every experimental failure target;
- future labels with fewer than three future observations left unknown, not forced to zero;
- missing accounting/macro values not forward-filled;
- success/failure overlap blocked;
- target components are derived only from future observed filings.

All second-pass logic audits show:

- post-event rows: 0;
- failure/success overlap: 0;
- strict distress missed by broader failure target: 0;
- future observations under threshold: 1,615 rows;
- unknown failure rows: 1,489;
- unknown success rows: 1,615.

## Key Target Results

Best second-pass failure target by raw metrics:

| Target | Model | Test positives | Positive share | PR-AUC | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| `failure_pressure_balance_liquidity_next_4obs` | random forest | 1,052 | 23.8% | 0.906 | 0.813 |

This target is highly learnable, but it is narrower conceptually: it is mostly a balance/liquidity stress detector. It is good for a dashboard view, but too specific to replace the main broader failure target.

Best defensible general failure-pressure target:

| Target | Model | Test positives | Positive share | PR-AUC | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| `failure_pressure_conservative_v2_next_4obs` | random forest | 514 | 11.7% | 0.739 | 0.705 |

This is effectively the same result as the first conservative target. The tweak did not materially change the label or performance. That is useful: it shows the conservative definition is stable to small threshold changes.

Best second-pass success target:

| Target | Model | Test positives | Positive share | PR-AUC | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| `success_resilience_quality_v2_next_4obs` | random forest | 1,449 | 33.3% | 0.929 | 0.875 |

This is strong, interpretable, and not as loose as the highest-scoring score target.

Best stricter success target:

| Target | Model | Test positives | Positive share | PR-AUC | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| `success_quality_growth_next_4obs` | random forest | 352 | 8.1% | 0.584 | 0.648 |

This is very strict. It is useful as a high-quality growth/resilience robustness target, but probably too narrow as the main success target.

## Feature-Set Findings

The dataset is useful. The signal is not random, but it is concentrated in firm-level data.

For `failure_pressure_conservative_next_4obs`:

- `firm_core` random forest PR-AUC: 0.690;
- `all_features` random forest PR-AUC: 0.689;
- `ratios_trends_only` random forest PR-AUC: 0.653;
- `raw_accounting_only` random forest PR-AUC: 0.606;
- `macro_event_only` random forest PR-AUC: 0.078.

For `success_composite_strict_next_4obs`:

- `ratios_trends_only` gradient boosting PR-AUC: 0.850;
- `firm_core` gradient boosting PR-AUC: 0.849;
- `all_features` gradient boosting PR-AUC: 0.849;
- `raw_accounting_only` random forest PR-AUC: 0.780;
- `macro_event_only` random forest PR-AUC: 0.273.

Interpretation:

> The strongest predictive information is in accounting fundamentals, financial ratios, and firm deterioration features. Macro/regime/global-event variables are useful for contextual interpretation and dashboard filtering, but they are not the primary predictive engine.

## Factor Findings

Across best all-feature models, dominant factor groups are:

- financial ratios;
- firm trend/deterioration;
- accounting fundamentals.

Examples:

- Conservative failure pressure:
  - firm trend: about 36.8% of grouped importance;
  - accounting fundamentals: about 30.7%;
  - financial ratios: about 30.0%.

- Profit/ROA failure pressure:
  - firm trend: about 40.5%;
  - financial ratios: about 28.0%;
  - accounting fundamentals: about 26.9%.

- Resilience-quality success:
  - firm trend: about 37.6%;
  - financial ratios: about 36.3%;
  - accounting fundamentals: about 25.0%.

- Quality/growth success:
  - financial ratios: about 77.1%;
  - firm trend: about 15.5%;
  - accounting fundamentals: about 6.8%.

Most recurring individual drivers:

- ROA;
- net income;
- prior negative-income count;
- net margin and lagged net margin;
- leverage/assets;
- equity/assets;
- total liabilities;
- lagged leverage;
- operating margin.

## Revised Recommendation

Use a target hierarchy, not one target:

1. Legal distress benchmark:
   - `distress_next_4q`.

2. General economic failure-pressure target:
   - `failure_pressure_conservative_next_4obs` or equivalent production version.
   - Keep this as the main broader failure target.

3. Diagnostic dashboard stress target:
   - `failure_pressure_balance_liquidity_next_4obs`.
   - Use this to show leverage/liquidity-specific warning.

4. Main composite success target:
   - `success_resilience_quality_v2_next_4obs`.

5. Strict high-quality growth/resilience target:
   - `success_quality_growth_next_4obs`.
   - Use as robustness and dashboard quality view.

## Dashboard Implications

The dashboard should not only show model metrics. It should become a factor-analysis console with:

- target selector:
  - legal distress;
  - economic failure pressure;
  - balance/liquidity pressure;
  - resilience-quality success;
  - strict quality/growth success;
- feature-set selector:
  - firm core;
  - ratios/trends;
  - raw accounting;
  - macro/event;
  - all features;
- factor group panel:
  - accounting fundamentals;
  - ratios;
  - trends;
  - macro/regime;
  - global events;
  - sector;
- sector/regime/event comparison views;
- firm explorer with latest filing, risk/success components, and historical trajectory;
- target-definition notes visible in a compact reference table.

The dashboard should emphasize:

> Firm fundamentals explain most of the model signal, while macro regimes and global events help interpret when and where those firm-level weaknesses matter.

## Bottom Line

The dataset is good enough for thesis conclusions if the claims are framed correctly.

Defensible conclusion:

> The panel supports robust factor analysis of future firm distress pressure and resilience. The strongest factors are profitability, leverage, balance-sheet structure, and deterioration in firm-level fundamentals. Macro and global-event indicators add useful historical context and dashboard interpretability, but they do not replace firm-level financial indicators as the main predictive signal.
