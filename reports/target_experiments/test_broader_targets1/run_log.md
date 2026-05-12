# test_broader_targets1: Loose broad economic pressure

## Definitions

- Failure target: `failure_pressure_loose_next_4obs`.
- Failure definition: formal distress OR repeated future losses OR repeated future unhealthy state.
- Success target: `success_composite_loose_next_4obs`.
- Success definition: at least two of profitability, resilience, and quality components; blocked by failure pressure.

## Integrity Actions

- Post-event rows are excluded before target construction.
- Rows with fewer than 3 future observations are kept as unknown for future-financial labels unless formal distress is known.
- Success labels are blocked when the same row qualifies as the same-experiment failure-pressure label.
- Unknown labels are not filled; they are removed only from the model fit for that target.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_loose_next_4obs | all | 29141 | 27652 | 1489 | 7902 | 0.2858 | 366 |
| failure_pressure_loose_next_4obs | train | 17197 | 17197 | 0 | 4418 | 0.2569 | 282 |
| failure_pressure_loose_next_4obs | validation | 6059 | 6043 | 16 | 2086 | 0.3452 | 275 |
| failure_pressure_loose_next_4obs | test | 5885 | 4412 | 1473 | 1398 | 0.3169 | 218 |
| success_composite_loose_next_4obs | all | 29141 | 27526 | 1615 | 11287 | 0.4100 | 325 |
| success_composite_loose_next_4obs | train | 17197 | 17164 | 33 | 7108 | 0.4141 | 288 |
| success_composite_loose_next_4obs | validation | 6059 | 6012 | 47 | 2360 | 0.3925 | 258 |
| success_composite_loose_next_4obs | test | 5885 | 4350 | 1535 | 1819 | 0.4182 | 239 |

## Best Test Runs By PR-AUC

| target | model | seed | rows | positives | roc_auc | pr_auc | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| success_composite_loose_next_4obs | random_forest | 42 | 4350 | 1819 | 0.9731 | 0.9541 | 0.8952 | 0.9346 | 0.9145 |
| failure_pressure_loose_next_4obs | random_forest | 202 | 4412 | 1398 | 0.9504 | 0.9192 | 0.7970 | 0.8763 | 0.8348 |

## Inconsistency Audit

| check | value | integrity_action |
| --- | --- | --- |
| rows_with_less_than_3_future_observations | 1615 | future-financial target rows set to unknown unless strict formal distress is known |
| post_event_rows_in_experiment_frame | 0 | post-event rows excluded before target construction |
| failure_success_overlap_rows | 0 | success target is explicitly blocked by same-experiment failure target |
| strict_distress_not_captured_by_failure_rows | 0 | formal distress is forced into every experimental failure target |
| rows_with_unknown_failure_target | 1489 | unknown kept as null and removed from model fitting for that target |
| rows_with_unknown_success_target | 1615 | unknown kept as null and removed from model fitting for that target |
