# Controlled Extension Decision Report

Last updated: 2026-05-10

This report records the controlled extension, validation gate, and 2026-05-10 promotion decision. The first four validated secondary outcomes now alter the production panel by adding target-label columns only; robustness-extension and diagnostic targets remain outside the production panel.

Controlling production facts remain:

- `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`
- `docs/FACTUAL_FREEZE_20260509.md`

## Extension Layer Added

Implemented in `scripts/modeling/run_exploratory_target_lab.py`:

- exploratory target lab with five forward-looking labels;
- cash-flow and financial-quality features from existing SEC fields;
- market-health v2 scores from already available FRED variables;
- temporal exploratory model diagnostics;
- target profiles, year-sector profiles, feature-group importance, audits, and figures.

Validated in `scripts/modeling/run_validation_extension_gate.py`:

- validation-only model selection;
- validation-only probability calibration;
- holdout test calibration metrics;
- ranking diagnostics at top 1%, 5%, and 10%;
- detailed exploratory feature-level importance;
- direction-of-effect diagnostics;
- reason-code summaries;
- robustness-extension diagnostics for `sector_relative_improvement_next_4obs` and `persistent_resilience_next_6obs`.

## Key Outputs

- `reports/target_lab/validated_secondary_target_promotion_audit.csv`
- `reports/target_lab/validated_secondary_target_promotion_audit_summary.md`
- `reports/target_lab/exploratory_target_profiles.csv`
- `reports/target_lab/exploratory_model_metrics.csv`
- `reports/target_lab/exploratory_feature_group_importance.csv`
- `reports/target_lab/validation_extension_gate_summary.md`
- `reports/modeling/calibration_model_selection.csv`
- `reports/modeling/calibration_metrics.csv`
- `reports/modeling/threshold_ranking_metrics.csv`
- `reports/target_lab/exploratory_feature_level_importance.csv`
- `reports/target_lab/exploratory_feature_direction_effects.csv`
- `reports/target_lab/exploratory_permutation_importance.csv`
- `reports/target_lab/exploratory_reason_code_summary.csv`
- `reports/target_lab/robustness_extension_target_audit.csv`
- `reports/target_lab/robustness_extension_target_audit_summary.md`
- `reports/data_quality/financial_quality_feature_audit.csv`
- `reports/data_quality/market_health_v2_timing_audit.csv`
- `reports/data_quality/market_health_v2_component_coverage.csv`

## Target Decisions After Validation Gate

| Target | Decision | Basis |
| --- | --- | --- |
| `industry_relative_resilience_next_4obs` | Promoted to validated secondary production outcome | Broad coverage, calibrated test PR-AUC 0.844, top-decile precision 0.951, interpretable sector-relative resilience factors. |
| `stress_resilience_next_4obs` | Promoted to validated secondary production outcome with stress-gate caveat | Calibrated test PR-AUC 0.969 and Brier 0.061; high positive base rate means ranking lift is modest. |
| `recovery_next_4obs` | Promoted to validated secondary production outcome with leverage-sensitivity caveat | Calibrated test PR-AUC 0.968 and strong ranking; feature interpretation is dominated by leverage/assets because current weakness and healthy-future definitions include leverage. |
| `quality_success_cashflow_next_4obs` | Promoted to validated secondary production outcome | Calibrated test PR-AUC 0.949; cash-flow quality appears in detailed feature evidence, though leverage and profitability remain stronger drivers. |
| `deterioration_next_4obs` | Diagnostic only | First-pass test PR-AUC was materially weaker and positives are rarer; do not headline it. |
| `sector_relative_improvement_next_4obs` | Robustness extension only | Calibrated test PR-AUC 0.639, top-decile precision 0.767, and 2.51x lift. Useful dynamic catch-up target, but materially weaker than the validated secondary outcomes. |
| `persistent_resilience_next_6obs` | Strong robustness extension | Calibrated test PR-AUC 0.955 and top-decile precision 0.985. Useful long-horizon sensitivity result, but not a replacement for the four-observation production success target. |

The first four are now production panel target columns and should be used as validated secondary production outcomes in thesis discussion and dashboard Target Lab views. The two robustness-extension targets should be used for sensitivity and dimensional discussion, not production or headline replacement claims.

## Calibration Decision

The calibration/ranking gate is now complete for the three primary production targets, the four validated secondary production outcomes, and the two robustness-extension targets. All selected models use validation-fitted isotonic calibration. The test period remains a holdout.

Safe probability wording: validation-calibrated model probability or calibrated model score. Unsafe wording: true live event probability.

## Feature Interpretation Decision

Detailed factor evidence now exists for the four validated secondary production outcomes:

- feature-level native importance;
- raw-feature permutation importance by PR-AUC drop;
- test-split direction-of-effect diagnostics;
- reason-code summaries.

Interpret these as associations in model behavior, not causal effects. Missingness indicators remain data-availability signals, not economic mechanisms.

Detailed factor evidence also exists for the two robustness-extension outcomes. For `persistent_resilience_next_6obs`, balance-sheet leverage/liquidity and firm momentum dominate. For `sector_relative_improvement_next_4obs`, firm momentum, profitability/efficiency, macro price/policy conditions, and cash-flow quality are visible, but the target remains weaker and should not be promoted without further validation.

## Market-Health V2 Decision

Market-health v2 is finalized as an audited stress-regime layer for target construction, validation, and dashboard context.

Policy:

- allowed for target-lab analysis and dashboard stress/regime context;
- allowed as current-row features in secondary-outcome validation models;
- `stress_elevated_v2` is primarily a stress-gate variable for the production target `stress_resilience_next_4obs`;
- the v2 score columns are not promoted as production panel feature columns;
- not a replacement for the existing production macro variables unless the additional FRED-series gate and full rebuild are completed.

The current v2 implementation does not include `STLFSI4`, `ANFCI`, `CFNAI`, `BAMLC0A4CBBB`, or `BAMLC0A0CM`. `USEPUINDXD` is already present.

## Safe Claims After This Gate

- The production panel is now 31,702 rows x 190 columns after controlled promotion of four validated secondary target labels.
- The target lab adds secondary outcome dimensions beyond binary success/failure.
- Four secondary targets pass profile, temporal model sanity, calibration, ranking, interpretation checks, and production-promotion audit.
- `deterioration_next_4obs` remains diagnostic.
- `persistent_resilience_next_6obs` is a strong robustness/sensitivity result for durable success.
- `sector_relative_improvement_next_4obs` is a useful dynamic catch-up robustness result, but weaker than the validated secondary outcomes.
- Cash-flow-supported success is useful for separating accounting success from operating cash-flow-supported success.
- Market-health v2 is an audited stress/regime layer using currently available FRED variables; its score columns are not production panel features.

## Unsafe Claims After This Gate

- Do not claim the two robustness-extension targets are final production targets.
- Do not claim the two robustness-extension targets are validated secondary production outcomes.
- Do not claim causal effects from feature importance, permutation importance, or reason codes.
- Do not claim calibrated scores are live deployment probabilities.
- Do not claim market-health v2 includes missing FRED series until those are downloaded, merged, audited, and documented.
- Do not cite 31,702 x 186 as current; the current production panel is 31,702 x 190 after target-label promotion.

## Robustness Extension Gate

The two creative robustness targets have now been implemented and evaluated:

- `sector_relative_improvement_next_4obs`
- `persistent_resilience_next_6obs`

Decision: keep both as robustness-extension targets. `persistent_resilience_next_6obs` is strong enough for long-horizon sensitivity analysis. `sector_relative_improvement_next_4obs` is useful for dynamic peer catch-up discussion, but not strong enough to promote beyond exploratory robustness.

## Robustness Extension Target Audit

`scripts/modeling/audit_robustness_extension_targets.py` now writes a reproducible target-construction audit:

- `reports/target_lab/robustness_extension_target_audit.csv`
- `reports/target_lab/robustness_extension_target_audit_summary.md`

Audit result: PASS. No blocking invariant violations were found. The audit verifies that the two robustness-extension labels are not production-panel columns, do not enter the model feature list, are not assigned on post-event rows, preserve missingness, and respect strict-distress override rules.

Scientific caveats remain:

- `sector_relative_improvement_next_4obs` uses an OR rule over ROA and net margin, not a formal composite index;
- 68 known sector-relative improvement rows use sector-year peer groups with fewer than 10 rows, and 86 use groups with fewer than 20 rows;
- `persistent_resilience_next_6obs` strongly overlaps with `success_resilience_next_4q` and should be used as durability confirmation rather than a separate primary outcome.
