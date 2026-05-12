# Broader Target Experiments

Updated: 2026-05-05

## Purpose

The strict `distress_next_4q` target is legally clean but very rare. These experiments test broader success/failure definitions that better match the thesis title:

> Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries

The goal is not to inflate metrics artificially. The goal is to separate:

- strict legal failure;
- broader economic failure pressure;
- high-quality future success/resilience.

## Experiment Outputs

All experiment artifacts are in:

```text
reports/target_experiments/
```

Each folder contains:

- target definitions;
- target profile;
- inconsistency audit;
- overlap audit;
- model metrics;
- model comparison plots;
- PR/ROC plots for the best run;
- best test predictions;
- `run_log.md`.

Folders:

- `test_broader_targets1`: loose broad economic pressure.
- `test_broader_targets2`: balanced two-of-three pressure.
- `test_broader_targets3`: sector-relative underperformance.
- `test_broader_targets4`: conservative quality gate.

## Integrity Rules Applied

The experiment runner applies these rules before modeling:

- post-event rows are excluded;
- rows with fewer than three future observations are not forced to 0;
- unknown future-financial labels remain null and are removed only from that target's model fit;
- every experimental failure target includes strict `distress_next_4q`;
- success targets are blocked when the same row qualifies for same-experiment failure pressure;
- missing fundamentals are not forward-filled or invented.

The inconsistency audit passed for all four experiment folders:

- failure/success overlap rows: 0;
- post-event rows in experiment frame: 0;
- strict distress rows missed by experimental failure target: 0.

Rows with fewer than three future observations:

- 1,165 rows.

These are treated as unknown for future-financial target components, except where formal distress is already known.

## Result Summary

Best failure-side results by test PR-AUC:

| Experiment | Target | Best model | Test positives | Positive share | Test PR-AUC | Test F1 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `test_broader_targets1` | `failure_pressure_loose_next_4obs` | random forest | 830 | 25.5% | 0.912 | 0.839 |
| `test_broader_targets4` | `failure_pressure_conservative_next_4obs` | random forest | 255 | 7.8% | 0.693 | 0.677 |
| `test_broader_targets3` | `failure_pressure_sector_relative_next_4obs` | random forest | 777 | 23.9% | 0.691 | 0.624 |
| `test_broader_targets2` | `failure_pressure_balanced_next_4obs` | gradient boosting | 565 | 17.4% | 0.546 | 0.506 |

Best success-side results by test PR-AUC:

| Experiment | Target | Best model | Test positives | Positive share | Test PR-AUC | Test F1 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `test_broader_targets1` | `success_composite_loose_next_4obs` | random forest | 1,483 | 46.1% | 0.965 | 0.929 |
| `test_broader_targets2` | `success_composite_balanced_next_4obs` | random forest | 1,159 | 36.1% | 0.940 | 0.879 |
| `test_broader_targets4` | `success_composite_strict_next_4obs` | gradient boosting | 687 | 21.4% | 0.847 | 0.813 |
| `test_broader_targets3` | `success_composite_sector_relative_next_4obs` | gradient boosting | 613 | 19.1% | 0.806 | 0.743 |

## Interpretation

`test_broader_targets1` produces the strongest metrics, but it is too broad to call "failure" without careful wording. It is better interpreted as a broad financial-pressure label.

`test_broader_targets4` is the best defensible failure upgrade. It captures:

- formal distress; or
- repeated future losses plus balance stress, deterioration, or repeated unhealthy state.

It is much more learnable than strict legal distress, but it is not as loose as labeling any future weakness as failure.

For success, `success_composite_strict_next_4obs` is the cleanest "three-in-one" target because it requires:

- profitability;
- resilience;
- quality.

Its metrics are lower than the loose target, but the interpretation is stronger.

## Recommendation

Use three target levels in the thesis:

1. Strict failure benchmark:
   - `distress_next_4q`.

2. Broader economic failure-pressure target:
   - recommended: `failure_pressure_conservative_next_4obs`.

3. Composite high-quality success target:
   - recommended: `success_composite_strict_next_4obs`.

The loose and balanced targets should be treated as robustness/sensitivity checks, not as the main thesis target.

## Thesis Wording

Recommended wording:

> In addition to a strict formal-distress benchmark, the study tests broader economic failure-pressure and composite success targets. This avoids reducing "failure" only to legal bankruptcy and allows the empirical artifact to identify factors associated with deteriorating financial condition, resilience, and high-quality future performance.

