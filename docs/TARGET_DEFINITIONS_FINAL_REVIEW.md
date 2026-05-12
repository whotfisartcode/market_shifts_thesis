# Target Definitions Final Review

Last updated: 2026-05-09

## Production Panel Status

The production panel has been rebuilt with missing-aware forward success targets, the 2026-05-07 SEC `ddate == period` selector fix, the 2026-05-08 `PCG`/`PGNPQ` alias-collapse fix, the 2026-05-09 SEC mapping polish, the 2026-05-09 accounting/duplicate caveat-resolution controls, and the 2026-05-10 validated-secondary target promotion. Post-rebuild provenance, P0, panel integrity, caveat audit, target profiles, models, tuning, advanced boosting, calibration/ranking, feature interpretation, dashboard screenshots, and rendered UI audit have been rerun/refreshed where directly affected.

Panel:

- rows: 31,702;
- columns: 190;
- CIKs: 540;
- tickers / firm display IDs: 540;
- prediction timestamp policy: `prediction_date = filed_date`;
- model rows exclude `post_event_flag = 1`.

## Primary Targets

### `distress_next_4q`

Strict legal distress target. Positive when a formal distress event occurs after `prediction_date` and within 456 days.

Final count:

- full-panel known rows: 31,702;
- positive rows: 207;
- temporal model rows after date and post-event filters: 29,062;
- temporal test rows after filters: 5,872;
- temporal test positives: 96.

Post-caveat-resolution baseline model:

- gradient boosting;
- test ROC-AUC: 0.816;
- test PR-AUC: 0.104;
- test precision: 0.120;
- test recall: 0.375;
- test F1: 0.182.

Interpretation:

This remains the clean legal early-warning benchmark. It is hard because formal distress is rare.

### `failure_pressure_conservative_v2_next_4obs`

Broader conservative failure-pressure target. Positive when strict formal distress occurs within the target horizon, or when future observations show repeated serious financial pressure. It is not a bankruptcy label.

Missing-aware rule:

- post-event rows are left null;
- strict formal distress overrides positive;
- otherwise at least three future observations are required;
- positive cases require repeated future profitability weakness plus at least one serious balance-stress, deterioration, or unhealthy-future signal;
- unknown future components remain unknown rather than becoming automatic negatives.

Final count:

- full-panel known rows: 29,805;
- full-panel unknown rows: 1,897;
- positive rows among known rows: 3,003;
- temporal model rows after date and post-event filters: 28,923;
- temporal test rows after filters: 5,735;
- temporal test positives: 575.

Post-caveat-resolution baseline models:

- random forest test ROC-AUC: 0.955;
- random forest test PR-AUC: 0.758;
- random forest test precision: 0.669;
- random forest test recall: 0.791;
- random forest test F1: 0.725;
- gradient boosting test ROC-AUC: 0.941;
- gradient boosting test PR-AUC: 0.721;
- gradient boosting test precision: 0.661;
- gradient boosting test recall: 0.736;
- gradient boosting test F1: 0.696.

Interpretation:

This is now the main production failure-factor target. It should be described as broader financial pressure or deterioration, not formal bankruptcy.

### `success_resilience_next_4q`

Forward success/resilience target. Positive when at least three of the next four future observations have positive net income, positive ROA, acceptable leverage/assets, and the firm is not a formal distress firm.

Missing-aware rule:

- future net income, ROA, and leverage/assets must be observed in at least three future observations;
- otherwise the target remains null;
- missing future leverage/liability values are not treated as automatic non-success.

Final count:

- full-panel known rows: 20,152;
- full-panel unknown rows: 11,550;
- positive rows among known rows: 12,519;
- temporal model rows used after date and post-event filters: 19,303;
- temporal test rows used in model: 4,047;
- temporal test positives: 2,648.

Post-caveat-resolution baseline model:

- random forest;
- test ROC-AUC: 0.966;
- test PR-AUC: 0.975;
- test precision: 0.941;
- test recall: 0.934;
- test F1: 0.938.

Interpretation:

This is a defensible primary success/resilience target after the missingness fix. The class is much less rare than formal distress, so metrics should not be compared mechanically to the distress target.

## Secondary Targets

`success_profitability_next_4q` and `success_quality_next_4q` are also missing-aware in the rebuilt panel.

Final counts after the 2026-05-09 caveat-resolution rebuild:

- `success_profitability_next_4q`: 29,962 known, 1,740 unknown, 24,950 positives.
- `success_quality_next_4q`: 20,152 known, 11,550 unknown, 8,685 positives.

Broader target experiments remain useful for thesis robustness:

- legal failure benchmark: `distress_next_4q`;
- production general economic failure pressure: `failure_pressure_conservative_v2_next_4obs`;
- balance/liquidity diagnostic: `failure_pressure_balance_liquidity_next_4obs`;
- composite success candidate: `success_resilience_quality_v2_next_4obs`;
- strict quality/growth success: `success_quality_growth_next_4obs`.

All broader targets except `failure_pressure_conservative_v2_next_4obs` remain experiment outputs unless promoted into the production panel later.

## Final Caveats

- Formal strict-distress event dates are source-verified for the current package: 44/44 formal rows have source-provenance records. Several events naturally occur after the last available pre-event filing, which affects label coverage but not source verification.
- Null values are preserved in the dataset and treated as unknown, not zero.
- Missingness indicators are predictive auxiliaries only and are excluded from economic factor interpretation.
- Macro/regime/global-event variables are context and comparison features; firm fundamentals, ratios, and deterioration features remain the empirical core.
