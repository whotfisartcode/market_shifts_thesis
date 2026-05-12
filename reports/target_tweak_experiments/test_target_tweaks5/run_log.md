# test_target_tweaks5: Component-score targets

Summary: Uses explicit component scores for dashboard-friendly success/failure drivers.

## Failure Definition

`failure_pressure_score3_next_4obs`: formal distress OR at least 3 of 5 failure-pressure components.

## Success Definition

`success_score3_next_4obs`: at least 3 of 5 success-quality components and no score-based failure.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_score3_next_4obs | all | 29141 | 27652 | 1489 | 3760 | 0.1360 | 297 |
| failure_pressure_score3_next_4obs | train | 17197 | 17197 | 0 | 1994 | 0.1160 | 205 |
| failure_pressure_score3_next_4obs | validation | 6059 | 6043 | 16 | 1047 | 0.1733 | 196 |
| failure_pressure_score3_next_4obs | test | 5885 | 4412 | 1473 | 719 | 0.1630 | 152 |
| success_score3_next_4obs | all | 29141 | 27526 | 1615 | 15067 | 0.5474 | 431 |
| success_score3_next_4obs | train | 17197 | 17164 | 33 | 9623 | 0.5607 | 394 |
| success_score3_next_4obs | validation | 6059 | 6012 | 47 | 3190 | 0.5306 | 365 |
| success_score3_next_4obs | test | 5885 | 4350 | 1535 | 2254 | 0.5182 | 329 |

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
| success_score3_next_4obs | all_features | random_forest | 2 | 2254.0000 | 0.5182 | 0.9205 | 0.9137 | 0.8073 | 0.9155 | 0.8580 |
| failure_pressure_score3_next_4obs | all_features | gradient_boosting | 2 | 719.0000 | 0.1630 | 0.8922 | 0.6876 | 0.6269 | 0.6822 | 0.6534 |
