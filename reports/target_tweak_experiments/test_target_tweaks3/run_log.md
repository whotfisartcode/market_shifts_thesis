# test_target_tweaks3: Balance and liquidity stress pressure

Summary: Tests whether balance-sheet/liquidity stress is learnable separately from profitability failure.

## Failure Definition

`failure_pressure_balance_liquidity_next_4obs`: formal distress OR repeated future loss/unhealthy observations with repeated leverage, current-ratio, or cash stress.

## Success Definition

`success_stable_balance_next_4obs`: repeated leverage/liquidity health plus positive profitability and non-negative future ROA.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_balance_liquidity_next_4obs | all | 29141 | 27652 | 1489 | 5655 | 0.2045 | 299 |
| failure_pressure_balance_liquidity_next_4obs | train | 17197 | 17197 | 0 | 3146 | 0.1829 | 216 |
| failure_pressure_balance_liquidity_next_4obs | validation | 6059 | 6043 | 16 | 1457 | 0.2411 | 212 |
| failure_pressure_balance_liquidity_next_4obs | test | 5885 | 4412 | 1473 | 1052 | 0.2384 | 166 |
| success_stable_balance_next_4obs | all | 29141 | 27526 | 1615 | 7604 | 0.2762 | 288 |
| success_stable_balance_next_4obs | train | 17197 | 17164 | 33 | 4839 | 0.2819 | 244 |
| success_stable_balance_next_4obs | validation | 6059 | 6012 | 47 | 1577 | 0.2623 | 200 |
| success_stable_balance_next_4obs | test | 5885 | 4350 | 1535 | 1188 | 0.2731 | 183 |

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
| failure_pressure_balance_liquidity_next_4obs | all_features | random_forest | 2 | 1052.0000 | 0.2384 | 0.9557 | 0.9060 | 0.8392 | 0.7890 | 0.8133 |
| success_stable_balance_next_4obs | all_features | gradient_boosting | 2 | 1188.0000 | 0.2731 | 0.9609 | 0.8829 | 0.7661 | 0.9209 | 0.8364 |
