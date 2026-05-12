# Model Interpretation Stability Note

Updated: 2026-05-10

This note supports thesis writing by comparing feature-group importance across saved production model outputs. It does not add new model results.

The thesis should emphasize stable economic groups, not isolated single features. Missingness indicators are excluded from economic shares.

## Stability Summary

| target | feature_group | mean_share_across_models | min_share_across_models | max_share_across_models | interpretation_stability |
| --- | --- | --- | --- | --- | --- |
| distress_next_4q | Accounting fundamentals | 0.35214842631160853 | 0.2533023720294977 | 0.5323568893075066 | dominant |
| distress_next_4q | Firm trend / deterioration | 0.25027501437318334 | 0.1185780540714727 | 0.3528624782013377 | dominant |
| distress_next_4q | Financial ratios | 0.21489696175323938 | 0.1147874168549951 | 0.3633313157872435 | dominant |
| distress_next_4q | Macro conditions | 0.1599299540561395 | 0.0106329247296036 | 0.3092269833826754 | dominant |
| distress_next_4q | Industry / sector | 0.0760596281912088 | 0.0110535224986704 | 0.2041051736613588 | moderate |
| failure_pressure_conservative_v2_next_4obs | Accounting fundamentals | 0.3717751134602249 | 0.0744366196758048 | 0.6719510567050866 | dominant |
| failure_pressure_conservative_v2_next_4obs | Macro conditions | 0.22757131601133385 | 0.0230844895987312 | 0.4320581424239365 | dominant |
| failure_pressure_conservative_v2_next_4obs | Firm trend / deterioration | 0.21158567086334726 | 0.071109787219645 | 0.3457463971696767 | dominant |
| failure_pressure_conservative_v2_next_4obs | Financial ratios | 0.1529727591557171 | 0.041769544282836 | 0.2732252420611653 | dominant |
| failure_pressure_conservative_v2_next_4obs | Industry / sector | 0.10512302507101183 | 0.0120906967693747 | 0.2579842972310349 | dominant |
| failure_pressure_conservative_v2_next_4obs | Macro regime / time | 0.0204876623264287 | 0.0204876623264287 | 0.0204876623264287 | moderate |
| success_resilience_next_4q | Financial ratios | 0.3973216828589973 | 0.2079831252258661 | 0.5517717984505414 | dominant |
| success_resilience_next_4q | Accounting fundamentals | 0.30556098126074654 | 0.2529636770843582 | 0.4017517045544815 | dominant |
| success_resilience_next_4q | Firm trend / deterioration | 0.18261741431845813 | 0.0859253369571977 | 0.290658711633149 | dominant |
| success_resilience_next_4q | Industry / sector | 0.09240784872381297 | 0.0151636013228665 | 0.2380636147484998 | moderate |
| success_resilience_next_4q | Macro conditions | 0.0662762185139547 | 0.0662762185139547 | 0.0662762185139547 | moderate |

## Interpretation Rule

Use dominant or moderate groups as thesis evidence of association. Do not claim causality. Do not interpret missingness indicators as economic mechanisms.

## Secondary Outcome Interpretation Addendum

The May 10 validation extension gate adds detailed interpretation files for the four validated secondary production outcomes and two robustness-extension outcomes:

- `reports/target_lab/exploratory_feature_level_importance.csv`
- `reports/target_lab/exploratory_feature_direction_effects.csv`
- `reports/target_lab/exploratory_permutation_importance.csv`
- `reports/target_lab/exploratory_reason_code_summary.csv`

These reports answer the detailed "what factors/reasons matter?" question beyond broad feature groups. The most important interpretive patterns are:

| Target | Main detailed factors |
| --- | --- |
| `industry_relative_resilience_next_4obs` | Higher equity/assets, lower leverage/assets, stronger ROA, stronger margins, and favorable recent firm momentum. |
| `stress_resilience_next_4obs` | Lower leverage/assets, higher equity/assets, stronger ROA, fewer prior negative-income observations, and healthier firm momentum under stress. |
| `recovery_next_4obs` | Lower leverage/assets is the dominant factor, followed by higher equity/assets, positive ROA, and improving recent profitability. |
| `quality_success_cashflow_next_4obs` | Lower leverage/assets, higher equity/assets, stronger ROA, favorable momentum, and positive cash-flow quality through `cfo_assets`. |
| `persistent_resilience_next_6obs` | Balance-sheet leverage/liquidity and firm momentum dominate, followed by profitability/efficiency. |
| `sector_relative_improvement_next_4obs` | Firm momentum, profitability/efficiency, macro price/policy conditions, and cash-flow quality are visible, but the target remains a weaker robustness outcome. |

These are model-behavior associations on temporal validation/test splits. They are not causal explanations.
