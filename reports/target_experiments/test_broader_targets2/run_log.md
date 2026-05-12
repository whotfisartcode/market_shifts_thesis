# test_broader_targets2: Balanced two-of-three pressure

## Definitions

- Failure target: `failure_pressure_balanced_next_4obs`.
- Failure definition: formal distress OR at least two of profitability failure, balance/liquidity stress, and deterioration.
- Success target: `success_composite_balanced_next_4obs`.
- Success definition: at least two of profitability, balance resilience, and operating/ROA quality; blocked by failure pressure.

## Integrity Actions

- Post-event rows are excluded before target construction.
- Rows with fewer than 3 future observations are kept as unknown for future-financial labels unless formal distress is known.
- Success labels are blocked when the same row qualifies as the same-experiment failure-pressure label.
- Unknown labels are not filled; they are removed only from the model fit for that target.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_balanced_next_4obs | all | 29141 | 27652 | 1489 | 5148 | 0.1862 | 447 |
| failure_pressure_balanced_next_4obs | train | 17197 | 17197 | 0 | 2723 | 0.1583 | 338 |
| failure_pressure_balanced_next_4obs | validation | 6059 | 6043 | 16 | 1435 | 0.2375 | 318 |
| failure_pressure_balanced_next_4obs | test | 5885 | 4412 | 1473 | 990 | 0.2244 | 282 |
| success_composite_balanced_next_4obs | all | 29141 | 27526 | 1615 | 8691 | 0.3157 | 305 |
| success_composite_balanced_next_4obs | train | 17197 | 17164 | 33 | 5519 | 0.3215 | 262 |
| success_composite_balanced_next_4obs | validation | 6059 | 6012 | 47 | 1787 | 0.2972 | 222 |
| success_composite_balanced_next_4obs | test | 5885 | 4350 | 1535 | 1385 | 0.3184 | 204 |

## Best Test Runs By PR-AUC

| target | model | seed | rows | positives | roc_auc | pr_auc | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| success_composite_balanced_next_4obs | random_forest | 202 | 4350 | 1385 | 0.9668 | 0.9209 | 0.8052 | 0.9220 | 0.8596 |
| failure_pressure_balanced_next_4obs | random_forest | 202 | 4412 | 990 | 0.8341 | 0.6421 | 0.5665 | 0.6414 | 0.6016 |

## Inconsistency Audit

| check | value | integrity_action |
| --- | --- | --- |
| rows_with_less_than_3_future_observations | 1615 | future-financial target rows set to unknown unless strict formal distress is known |
| post_event_rows_in_experiment_frame | 0 | post-event rows excluded before target construction |
| failure_success_overlap_rows | 0 | success target is explicitly blocked by same-experiment failure target |
| strict_distress_not_captured_by_failure_rows | 0 | formal distress is forced into every experimental failure target |
| rows_with_unknown_failure_target | 1489 | unknown kept as null and removed from model fitting for that target |
| rows_with_unknown_success_target | 1615 | unknown kept as null and removed from model fitting for that target |
