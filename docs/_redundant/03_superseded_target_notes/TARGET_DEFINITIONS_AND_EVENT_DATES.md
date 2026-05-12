# Target Definitions and Event Dates

This thesis should not rely on one vague definition of "success" or "failure." The panel includes several target variants so the final paper can compare them and choose a primary specification.

## Failure / Distress Definitions

### `distress_next_2q`

Formal distress event occurs after the SEC filing becomes available and within roughly the next two quarters.

Definition:

- `formal_distress_firm = 1`
- `days_to_event = event_date - prediction_date`
- `0 < days_to_event <= 228`

Use:

- short-horizon early-warning target,
- stricter and more difficult.

### `distress_next_4q`

Formal distress event occurs after the SEC filing becomes available and within roughly the next four quarters.

Definition:

- `formal_distress_firm = 1`
- `days_to_event = event_date - prediction_date`
- `0 < days_to_event <= 456`

Use:

- primary failure target for the thesis.
- This is the best balance between practical early warning and enough positive examples.

### `distress_next_8q`

Formal distress event occurs after the SEC filing becomes available and within roughly the next eight quarters.

Definition:

- `formal_distress_firm = 1`
- `days_to_event = event_date - prediction_date`
- `0 < days_to_event <= 912`

Use:

- long-horizon robustness target.

### `broad_distress_next_4q`

Formal distress or near-distress marker occurs within roughly the next four quarters.

Definition:

- `formal_distress_firm = 1` or `near_distress_firm = 1`
- `days_to_event = event_date - prediction_date`
- `0 < days_to_event <= 456`

Use:

- broad stress target.
- More inclusive, but less legally clean than formal distress.

## Success / Resilience Definitions

### `healthy_current`

Current observation is financially healthy.

Definition:

- net income > 0,
- ROA > 0,
- leverage/assets between 0 and 0.85,
- no formal distress firm flag.

Use:

- descriptive health marker.
- Not the main prediction target because it is contemporaneous.

### `success_profitability_next_4q`

Firm reports positive net income in at least three of the next four reporting observations.

Missing-aware rule:

- at least three future net-income observations must be available;
- otherwise the target remains null.

Use:

- simple forward-looking profitability target.

### `success_resilience_next_4q`

Firm is financially healthy in at least three of the next four reporting observations and is not a formal distress firm.

Missing-aware rule added on 2026-05-05:

- at least three future observations must have net income, ROA, and leverage/assets available;
- otherwise the target remains null;
- missing future total-liabilities/leverage values are no longer converted into automatic non-success.

Use:

- recommended primary success/resilience target.
- Connects "success" to continued resilience rather than vague business success.

### `success_quality_next_4q`

Firm has positive income in at least three of the next four observations, average future ROA above 1%, leverage acceptable in at least three of the next four observations, and no formal distress flag.

Missing-aware rule:

- at least three future net-income, ROA, and leverage/assets observations must be available;
- otherwise the target remains null.

Use:

- stricter high-quality success target.

## Event Date Strategy

Event dates are stored in:

```text
config/distress_event_dates.csv
```

Current status:

- Dates are useful enough for modeling.
- They are marked `initial_seed`.
- They must be verified before final submission.
- P0 audit status is `REVIEW`, not `PASS`, until this verification is done.

Rows where `prediction_date >= event_date` are marked with `post_event_flag = 1`. These rows are kept in the exported panel for historical/dashboard analysis, but are excluded from primary model training and have zero forward-distress target positives.

Preferred verification hierarchy:

1. Company press release or investor relations announcement.
2. SEC 8-K or 10-K/10-Q disclosure.
3. Bankruptcy court/docket source.
4. Reputable financial news source.
5. Wikipedia or secondary summaries only as backup pointers, not final citation.

## Recommended Thesis Usage

Primary failure target:

- `distress_next_4q`

Primary broader economic failure-pressure candidate:

- `failure_pressure_conservative_next_4obs`
- Tested in `reports/target_experiments/test_broader_targets4/`
- Recommended for broader "failure factors" interpretation, but not yet promoted into the production panel.

Primary success target:

- `success_resilience_next_4q`

Primary three-in-one success candidate:

- `success_composite_strict_next_4obs`
- Tested in `reports/target_experiments/test_broader_targets4/`
- Combines profitability, resilience, and quality.

Robustness targets:

- `distress_next_2q`
- `distress_next_8q`
- `broad_distress_next_4q`
- `success_profitability_next_4q`
- `success_quality_next_4q`

Broader-target experiment note:

- Full experiment explanation is archived in `docs/_redundant/03_superseded_target_notes/BROADER_TARGET_EXPERIMENTS.md`.
- Strict legal failure should remain as a benchmark.
- Broader failure-pressure and composite success targets should be introduced as complementary target definitions, not as replacements that erase the legal-distress benchmark.
