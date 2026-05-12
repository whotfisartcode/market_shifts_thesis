# Broader Target Experiment Comparison

Each `test_broader_targetsN` folder contains its own target profile, model metrics, plots, predictions, and run log.

## Best Rows By Target

| experiment | target | model | runs | positives | positive_share | roc_auc_mean | roc_auc_std | pr_auc_mean | pr_auc_std | precision_mean | recall_mean | f1_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test_broader_targets1 | success_composite_loose_next_4obs | random_forest | 3 | 1819.0000 | 0.4182 | 0.9731 | 0.0001 | 0.9537 | 0.0004 | 0.8880 | 0.9410 | 0.9137 |
| test_broader_targets2 | success_composite_balanced_next_4obs | random_forest | 3 | 1385.0000 | 0.3184 | 0.9665 | 0.0004 | 0.9200 | 0.0010 | 0.8068 | 0.9172 | 0.8584 |
| test_broader_targets1 | failure_pressure_loose_next_4obs | random_forest | 3 | 1398.0000 | 0.3169 | 0.9506 | 0.0003 | 0.9189 | 0.0003 | 0.8141 | 0.8650 | 0.8386 |
| test_broader_targets4 | success_composite_strict_next_4obs | gradient_boosting | 3 | 788.0000 | 0.1811 | 0.9617 | 0.0001 | 0.8126 | 0.0015 | 0.7203 | 0.8498 | 0.7797 |
| test_broader_targets3 | success_composite_sector_relative_next_4obs | gradient_boosting | 3 | 740.0000 | 0.1701 | 0.9469 | 0.0000 | 0.7754 | 0.0001 | 0.6763 | 0.8189 | 0.7408 |
| test_broader_targets4 | failure_pressure_conservative_next_4obs | random_forest | 3 | 514.0000 | 0.1165 | 0.9365 | 0.0015 | 0.7412 | 0.0029 | 0.6328 | 0.7964 | 0.7047 |
| test_broader_targets3 | failure_pressure_sector_relative_next_4obs | random_forest | 3 | 1134.0000 | 0.2570 | 0.8530 | 0.0012 | 0.7213 | 0.0016 | 0.6091 | 0.6925 | 0.6480 |
| test_broader_targets2 | failure_pressure_balanced_next_4obs | random_forest | 3 | 990.0000 | 0.2244 | 0.8315 | 0.0024 | 0.6402 | 0.0028 | 0.5365 | 0.6801 | 0.5978 |

## Integrity Note

The experiments preserve null/unknown target states for rows without enough future observations. They do not forward-fill missing fundamentals or add invented data.
