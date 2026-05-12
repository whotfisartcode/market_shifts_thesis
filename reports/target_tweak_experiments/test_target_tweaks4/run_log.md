# test_target_tweaks4: Sector-adjusted strict pressure

Summary: Uses sector-relative future ROA thresholds to reduce bias against low-margin industries.

## Failure Definition

`failure_pressure_sector_strict_next_4obs`: formal distress OR bottom-quartile future ROA within sector plus repeated losses or deterioration.

## Success Definition

`success_sector_quality_next_4obs`: sector-above-median future ROA plus profitability and balance health.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_sector_strict_next_4obs | all | 29141 | 27652 | 1489 | 4704 | 0.1701 | 363 |
| failure_pressure_sector_strict_next_4obs | train | 17197 | 17197 | 0 | 2557 | 0.1487 | 272 |
| failure_pressure_sector_strict_next_4obs | validation | 6059 | 6043 | 16 | 1269 | 0.2100 | 235 |
| failure_pressure_sector_strict_next_4obs | test | 5885 | 4412 | 1473 | 878 | 0.1990 | 206 |
| success_sector_quality_next_4obs | all | 29141 | 27526 | 1615 | 4256 | 0.1546 | 231 |
| success_sector_quality_next_4obs | train | 17197 | 17164 | 33 | 2599 | 0.1514 | 189 |
| success_sector_quality_next_4obs | validation | 6059 | 6012 | 47 | 917 | 0.1525 | 138 |
| success_sector_quality_next_4obs | test | 5885 | 4350 | 1535 | 740 | 0.1701 | 131 |

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
| success_sector_quality_next_4obs | all_features | gradient_boosting | 2 | 740.0000 | 0.1701 | 0.9471 | 0.7766 | 0.6766 | 0.8257 | 0.7438 |
| failure_pressure_sector_strict_next_4obs | all_features | gradient_boosting | 2 | 878.0000 | 0.1990 | 0.8757 | 0.7137 | 0.6071 | 0.7118 | 0.6553 |
