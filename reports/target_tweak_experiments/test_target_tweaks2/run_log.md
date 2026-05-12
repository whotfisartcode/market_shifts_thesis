# test_target_tweaks2: Profitability and ROA decline pressure

Summary: Focuses on profitability failure plus average future ROA or operating-margin weakness.

## Failure Definition

`failure_pressure_profit_roa_next_4obs`: formal distress OR repeated future losses with weak future ROA/operating margin and at least one pressure signal.

## Success Definition

`success_quality_growth_next_4obs`: positive profitability, quality ROA/operating margin, acceptable leverage, and non-negative revenue or asset growth.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_profit_roa_next_4obs | all | 29141 | 27652 | 1489 | 3189 | 0.1153 | 280 |
| failure_pressure_profit_roa_next_4obs | train | 17197 | 17197 | 0 | 1694 | 0.0985 | 192 |
| failure_pressure_profit_roa_next_4obs | validation | 6059 | 6043 | 16 | 904 | 0.1496 | 175 |
| failure_pressure_profit_roa_next_4obs | test | 5885 | 4412 | 1473 | 591 | 0.1340 | 124 |
| success_quality_growth_next_4obs | all | 29141 | 27526 | 1615 | 2230 | 0.0810 | 140 |
| success_quality_growth_next_4obs | train | 17197 | 17164 | 33 | 1390 | 0.0810 | 109 |
| success_quality_growth_next_4obs | validation | 6059 | 6012 | 47 | 488 | 0.0812 | 86 |
| success_quality_growth_next_4obs | test | 5885 | 4350 | 1535 | 352 | 0.0809 | 70 |

## Logic Audit

| check | value |
| --- | --- |
| post_event_rows | 0 |
| failure_success_overlap_rows | 0 |
| strict_distress_missed_by_failure_rows | 0 |
| future_observation_count_lt3_rows | 1615 |
| unknown_failure_rows | 1489 |
| unknown_success_rows | 1615 |

## Best Target-Scan Rows

| target | feature_set | model | runs | positives | positive_share | roc_auc_mean | pr_auc_mean | precision_mean | recall_mean | f1_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_profit_roa_next_4obs | all_features | random_forest | 2 | 591.0000 | 0.1340 | 0.9108 | 0.6823 | 0.5969 | 0.7022 | 0.6452 |
| success_quality_growth_next_4obs | all_features | random_forest | 2 | 352.0000 | 0.0809 | 0.9522 | 0.5836 | 0.5708 | 0.7500 | 0.6482 |
