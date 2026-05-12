# test_target_tweaks1: Conservative v2 with stronger deterioration threshold

Summary: Tightens deterioration threshold but allows one balance-stress signal with repeated losses.

## Failure Definition

`failure_pressure_conservative_v2_next_4obs`: formal distress OR at least 3 future loss observations plus at least one serious stress/deterioration signal.

## Success Definition

`success_resilience_quality_v2_next_4obs`: profitability and resilience, plus either ROA/operating quality or low-stress balance sheet.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_conservative_v2_next_4obs | all | 29141 | 27652 | 1489 | 2830 | 0.1023 | 221 |
| failure_pressure_conservative_v2_next_4obs | train | 17197 | 17197 | 0 | 1529 | 0.0889 | 147 |
| failure_pressure_conservative_v2_next_4obs | validation | 6059 | 6043 | 16 | 787 | 0.1302 | 133 |
| failure_pressure_conservative_v2_next_4obs | test | 5885 | 4412 | 1473 | 514 | 0.1165 | 104 |
| success_resilience_quality_v2_next_4obs | all | 29141 | 27526 | 1615 | 8928 | 0.3243 | 307 |
| success_resilience_quality_v2_next_4obs | train | 17197 | 17164 | 33 | 5651 | 0.3292 | 266 |
| success_resilience_quality_v2_next_4obs | validation | 6059 | 6012 | 47 | 1828 | 0.3041 | 219 |
| success_resilience_quality_v2_next_4obs | test | 5885 | 4350 | 1535 | 1449 | 0.3331 | 205 |

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
| success_resilience_quality_v2_next_4obs | all_features | random_forest | 2 | 1449.0000 | 0.3331 | 0.9694 | 0.9289 | 0.8429 | 0.9106 | 0.8754 |
| failure_pressure_conservative_v2_next_4obs | all_features | random_forest | 2 | 514.0000 | 0.1165 | 0.9356 | 0.7389 | 0.6352 | 0.7928 | 0.7053 |
