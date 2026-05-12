# test_broader_targets3: Sector-relative underperformance

## Definitions

- Failure target: `failure_pressure_sector_relative_next_4obs`.
- Failure definition: formal distress OR bottom-quartile future ROA within sector-year plus pressure evidence.
- Success target: `success_composite_sector_relative_next_4obs`.
- Success definition: sector-year above-median future ROA plus profitability and balance resilience; blocked by failure pressure.

## Integrity Actions

- Post-event rows are excluded before target construction.
- Rows with fewer than 3 future observations are kept as unknown for future-financial labels unless formal distress is known.
- Success labels are blocked when the same row qualifies as the same-experiment failure-pressure label.
- Unknown labels are not filled; they are removed only from the model fit for that target.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_sector_relative_next_4obs | all | 29141 | 27652 | 1489 | 6222 | 0.2250 | 386 |
| failure_pressure_sector_relative_next_4obs | train | 17197 | 17197 | 0 | 3468 | 0.2017 | 302 |
| failure_pressure_sector_relative_next_4obs | validation | 6059 | 6043 | 16 | 1620 | 0.2681 | 277 |
| failure_pressure_sector_relative_next_4obs | test | 5885 | 4412 | 1473 | 1134 | 0.2570 | 239 |
| success_composite_sector_relative_next_4obs | all | 29141 | 27526 | 1615 | 4256 | 0.1546 | 231 |
| success_composite_sector_relative_next_4obs | train | 17197 | 17164 | 33 | 2599 | 0.1514 | 189 |
| success_composite_sector_relative_next_4obs | validation | 6059 | 6012 | 47 | 917 | 0.1525 | 138 |
| success_composite_sector_relative_next_4obs | test | 5885 | 4350 | 1535 | 740 | 0.1701 | 131 |

## Best Test Runs By PR-AUC

| target | model | seed | rows | positives | roc_auc | pr_auc | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| success_composite_sector_relative_next_4obs | gradient_boosting | 202 | 4350 | 740 | 0.9470 | 0.7755 | 0.6763 | 0.8189 | 0.7408 |
| failure_pressure_sector_relative_next_4obs | random_forest | 42 | 4412 | 1134 | 0.8534 | 0.7223 | 0.6234 | 0.6817 | 0.6512 |

## Inconsistency Audit

| check | value | integrity_action |
| --- | --- | --- |
| rows_with_less_than_3_future_observations | 1615 | future-financial target rows set to unknown unless strict formal distress is known |
| post_event_rows_in_experiment_frame | 0 | post-event rows excluded before target construction |
| failure_success_overlap_rows | 0 | success target is explicitly blocked by same-experiment failure target |
| strict_distress_not_captured_by_failure_rows | 0 | formal distress is forced into every experimental failure target |
| rows_with_unknown_failure_target | 1489 | unknown kept as null and removed from model fitting for that target |
| rows_with_unknown_success_target | 1615 | unknown kept as null and removed from model fitting for that target |
