# Target And Feature Tweak Experiments

This second pass tests small target-definition tweaks and feature-set sensitivity.

## Best Target-Definition Rows

| target | feature_set | model | runs | positives | positive_share | roc_auc_mean | pr_auc_mean | precision_mean | recall_mean | f1_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| success_resilience_quality_v2_next_4obs | all_features | random_forest | 2 | 1449.0000 | 0.3331 | 0.9694 | 0.9289 | 0.8429 | 0.9106 | 0.8754 |
| success_score3_next_4obs | all_features | random_forest | 2 | 2254.0000 | 0.5182 | 0.9205 | 0.9137 | 0.8073 | 0.9155 | 0.8580 |
| failure_pressure_balance_liquidity_next_4obs | all_features | random_forest | 2 | 1052.0000 | 0.2384 | 0.9557 | 0.9060 | 0.8392 | 0.7890 | 0.8133 |
| success_stable_balance_next_4obs | all_features | gradient_boosting | 2 | 1188.0000 | 0.2731 | 0.9609 | 0.8829 | 0.7661 | 0.9209 | 0.8364 |
| success_sector_quality_next_4obs | all_features | gradient_boosting | 2 | 740.0000 | 0.1701 | 0.9471 | 0.7766 | 0.6766 | 0.8257 | 0.7438 |
| failure_pressure_conservative_v2_next_4obs | all_features | random_forest | 2 | 514.0000 | 0.1165 | 0.9356 | 0.7389 | 0.6352 | 0.7928 | 0.7053 |
| failure_pressure_sector_strict_next_4obs | all_features | gradient_boosting | 2 | 878.0000 | 0.1990 | 0.8757 | 0.7137 | 0.6071 | 0.7118 | 0.6553 |
| failure_pressure_score3_next_4obs | all_features | gradient_boosting | 2 | 719.0000 | 0.1630 | 0.8922 | 0.6876 | 0.6269 | 0.6822 | 0.6534 |
| failure_pressure_profit_roa_next_4obs | all_features | random_forest | 2 | 591.0000 | 0.1340 | 0.9108 | 0.6823 | 0.5969 | 0.7022 | 0.6452 |
| success_quality_growth_next_4obs | all_features | random_forest | 2 | 352.0000 | 0.0809 | 0.9522 | 0.5836 | 0.5708 | 0.7500 | 0.6482 |

## Best Feature-Set Rows

| target | feature_set | model | runs | positives | positive_share | roc_auc_mean | pr_auc_mean | precision_mean | recall_mean | f1_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| success_resilience_quality_v2_next_4obs | firm_core | random_forest | 1 | 1449.0000 | 0.3331 | 0.9697 | 0.9307 | 0.8363 | 0.9165 | 0.8745 |
| success_composite_strict_next_4obs | firm_core | gradient_boosting | 1 | 788.0000 | 0.1811 | 0.9621 | 0.8140 | 0.7097 | 0.8655 | 0.7799 |
| failure_pressure_conservative_next_4obs | firm_core | random_forest | 1 | 514.0000 | 0.1165 | 0.9333 | 0.7397 | 0.6225 | 0.7860 | 0.6948 |
| failure_pressure_conservative_v2_next_4obs | firm_core | random_forest | 1 | 514.0000 | 0.1165 | 0.9333 | 0.7397 | 0.6225 | 0.7860 | 0.6948 |
| failure_pressure_profit_roa_next_4obs | all_features | random_forest | 1 | 591.0000 | 0.1340 | 0.9085 | 0.6831 | 0.5887 | 0.7073 | 0.6426 |
| success_quality_growth_next_4obs | ratios_trends_only | gradient_boosting | 1 | 352.0000 | 0.0809 | 0.9536 | 0.5991 | 0.5572 | 0.7330 | 0.6331 |

## Interpretation Prompt

A target is more thesis-ready when it is predictive, has a defensible economic interpretation, has enough positives in the temporal test split, and does not rely on filling unknown future labels.
