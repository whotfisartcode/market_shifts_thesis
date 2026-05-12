# test_broader_targets4: Conservative quality gate

## Definitions

- Failure target: `failure_pressure_conservative_next_4obs`.
- Failure definition: formal distress OR repeated losses plus either balance stress, deterioration, or unhealthy future state.
- Success target: `success_composite_strict_next_4obs`.
- Success definition: all three success components: profitability, resilience, and quality; blocked by failure pressure.

## Integrity Actions

- Post-event rows are excluded before target construction.
- Rows with fewer than 3 future observations are kept as unknown for future-financial labels unless formal distress is known.
- Success labels are blocked when the same row qualifies as the same-experiment failure-pressure label.
- Unknown labels are not filled; they are removed only from the model fit for that target.

## Target Profile

| target | split | rows | known_rows | unknown_rows | positives | positive_share_known | firms_with_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| failure_pressure_conservative_next_4obs | all | 29141 | 27652 | 1489 | 2830 | 0.1023 | 221 |
| failure_pressure_conservative_next_4obs | train | 17197 | 17197 | 0 | 1529 | 0.0889 | 147 |
| failure_pressure_conservative_next_4obs | validation | 6059 | 6043 | 16 | 787 | 0.1302 | 133 |
| failure_pressure_conservative_next_4obs | test | 5885 | 4412 | 1473 | 514 | 0.1165 | 104 |
| success_composite_strict_next_4obs | all | 29141 | 27526 | 1615 | 5063 | 0.1839 | 214 |
| success_composite_strict_next_4obs | train | 17197 | 17164 | 33 | 3272 | 0.1906 | 180 |
| success_composite_strict_next_4obs | validation | 6059 | 6012 | 47 | 1003 | 0.1668 | 139 |
| success_composite_strict_next_4obs | test | 5885 | 4350 | 1535 | 788 | 0.1811 | 130 |

## Best Test Runs By PR-AUC

| target | model | seed | rows | positives | roc_auc | pr_auc | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| success_composite_strict_next_4obs | gradient_boosting | 202 | 4350 | 788 | 0.9618 | 0.8142 | 0.7201 | 0.8490 | 0.7793 |
| failure_pressure_conservative_next_4obs | random_forest | 777 | 4412 | 514 | 0.9382 | 0.7438 | 0.6093 | 0.8191 | 0.6988 |

## Inconsistency Audit

| check | value | integrity_action |
| --- | --- | --- |
| rows_with_less_than_3_future_observations | 1615 | future-financial target rows set to unknown unless strict formal distress is known |
| post_event_rows_in_experiment_frame | 0 | post-event rows excluded before target construction |
| failure_success_overlap_rows | 0 | success target is explicitly blocked by same-experiment failure target |
| strict_distress_not_captured_by_failure_rows | 0 | formal distress is forced into every experimental failure target |
| rows_with_unknown_failure_target | 1489 | unknown kept as null and removed from model fitting for that target |
| rows_with_unknown_success_target | 1615 | unknown kept as null and removed from model fitting for that target |
