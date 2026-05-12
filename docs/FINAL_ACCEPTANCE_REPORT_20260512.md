# Final Acceptance Report 2026-05-12

This report is the current technical acceptance checkpoint for the thesis project:

> Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries

It records the current empirical, modeling, dashboard, and documentation state after the 2026-05-10 validated secondary target promotion and the 2026-05-12 SEC harmonization hardening review.

## Acceptance Decision

The technical project is accepted for thesis writing and presentation with disclosed scientific caveats.

No production panel, target, model, dashboard, or concept-map blocker is currently open. The remaining work is final manuscript writing, final documentation consistency review, and final Git/GitHub freeze.

## Current Production Panel

| Item | Current value |
| --- | --- |
| Production rows | 31,702 |
| Production columns | 190 |
| SEC CIKs | 540 |
| Ticker/display IDs | 540 |
| Period range | 2009-03-31 to 2026-02-28 |
| Prediction timestamp range | 2009-04-15 to 2026-03-31 |
| Prediction-date policy | `prediction_date = filed_date` |
| Core/GitHub panel equality | PASS |
| Schema rows | 190 |

Direct check on 2026-05-12 loaded `data/processed/panel_v2/firm_panel_v2.parquet` as `(31702, 190)`.

## Production Target Hierarchy

| Role | Target | Known rows | Positives | Missing |
| --- | --- | ---: | ---: | ---: |
| Strict legal benchmark | `distress_next_4q` | 31,702 | 207 | 0 |
| Main failure-factor target | `failure_pressure_conservative_v2_next_4obs` | 29,805 | 3,003 | 1,897 |
| Main success/resilience target | `success_resilience_next_4q` | 20,152 | 12,519 | 11,550 |
| Validated secondary outcome | `industry_relative_resilience_next_4obs` | 20,039 | 8,093 | 11,663 |
| Validated secondary outcome | `stress_resilience_next_4obs` | 5,901 | 3,707 | 25,801 |
| Validated secondary outcome | `recovery_next_4obs` | 11,375 | 5,578 | 20,327 |
| Validated secondary outcome | `quality_success_cashflow_next_4obs` | 16,767 | 9,852 | 14,935 |

Robustness-extension targets remain non-production: `sector_relative_improvement_next_4obs` and `persistent_resilience_next_6obs`.

Diagnostic-only targets remain non-production, including exploratory `deterioration_next_4obs`.

## Technical Acceptance Gates

| Area | Status | Evidence |
| --- | --- | --- |
| P0 timing/leakage/event audits | PASS | `reports/data_quality/p0_audit_status.csv` |
| Prediction timestamp policy | PASS | `prediction_date = filed_date` |
| Distress event dates | PASS | strict formal event rows have source provenance |
| Macro lag policy | PASS | no future macro values in P0 audit |
| Global-event timing | PASS | no future global-event timing violation in P0 audit |
| Post-event rows | PASS | post-event controls pass |
| Feature blacklist leakage | PASS | 8 model feature-list checks, 0 blacklist overlaps |
| Model-output consistency | PASS | 7 production targets pass best-model consistency checks |
| Project audit | PASS | Python compile, notebooks, CSV, Parquet, ZIP, config, and model checks pass |
| Documentation references | PASS | 0 broken local references after audit refresh |
| Package smoke test | PASS | package loads, schema matches, dependency imports pass |
| Dashboard screenshots | PASS_WITH_CAVEATS | screenshots pass; only known benign Vega-Lite warnings recorded |
| SEC concept mapping | PASS_WITH_CAVEATS | conservative mapping, provenance, sanity checks; not perfect taxonomy |
| Missingness | PASS_WITH_CAVEATS | material missingness disclosed and preserved |
| Model validity | PASS_WITH_CAVEATS | temporal validation and robustness exist; no causal claim |

The full project audit refreshed on 2026-05-12 reports: `python_compile_PASS=56`, `csv_quick_PASS=1317`, `parquet_PASS=962`, `zip_quick_PASS=69`, `model_output_consistency_PASS=7`, `feature_blacklist_PASS=8`, `doc_references_BROKEN=0`, and `required_config_PASS=6`.

## Production Model State

| Target | Saved production best model | Test PR-AUC | Interpretation |
| --- | --- | ---: | --- |
| `distress_next_4q` | gradient boosting | 0.104 | Strict legal distress remains rare; use as benchmark, not headline model. |
| `failure_pressure_conservative_v2_next_4obs` | random forest | 0.758 | Main failure-pressure target; strong enough for factor analysis. |
| `success_resilience_next_4q` | random forest | 0.975 | Strong primary success/resilience outcome. |
| `industry_relative_resilience_next_4obs` | gradient boosting | 0.855 | Validated secondary outcome. |
| `stress_resilience_next_4obs` | random forest | 0.974 | Validated secondary outcome, stress-gated. |
| `recovery_next_4obs` | random forest | 0.977 | Validated secondary outcome. |
| `quality_success_cashflow_next_4obs` | gradient boosting | 0.953 | Validated secondary outcome. |

Controlled tuning and advanced boosted-tree checks support robustness, but they do not change the central interpretation. Tuning modestly improves strict-distress threshold behavior, while failure-pressure and success/resilience remain stable under alternative model families.

## Calibration And Ranking

Calibration and ranking diagnostics exist for the three primary production targets, the four validated secondary production outcomes, and the two robustness-extension targets.

Selection policy:

- Base models are selected using validation-period PR-AUC.
- Probability calibrators are fitted using the validation period.
- Test-period metrics are final holdout diagnostics and are not used for model or calibrator selection.

Current calibration evidence is in `reports/modeling/calibration_metrics.csv`, `reports/modeling/threshold_ranking_metrics.csv`, and `reports/target_lab/validation_extension_gate_summary.md`.

## Feature Interpretation

Feature interpretation is accepted for association and ranking evidence, not causality.

Available interpretation layers:

- feature-group contribution tables;
- feature-level importance tables;
- permutation importance outputs;
- direction-of-association diagnostics;
- reason-code summaries for validated secondary targets;
- dashboard Target Lab views.

Thesis-safe wording: firm fundamentals, ratios, balance-sheet leverage/liquidity, profitability, cash-flow quality, and trend/deterioration features are associated with the modeled outcomes under temporal validation. Do not claim causal mechanisms from feature importance alone.

## SEC Mapping And Harmonization

The SEC concept map is accepted as conservative and auditable, not perfect.

Current support:

- `ddate == period` current-period filtering is implemented.
- Row-level selected-fact provenance exists.
- SEC concept-map polish improved debt, receivables, R&D, and revenue fallback coverage.
- Risky substitutions remain rejected, including `LiabilitiesAndStockholdersEquity` as total liabilities and silent `Assets - Equity` filling.
- The 2026-05-12 hardening review scanned 7,350 unmapped tags near thesis-critical accounting concepts and accepted no automatic additions under strict rules.

Accepted thesis claim: accounting variables were mapped from SEC FSD tags using a documented, conservative concept map, filtered to current-period facts, audited with selected-fact provenance, and disclosed with missingness and taxonomy caveats.

Rejected thesis claim: all SEC/XBRL accounting tags are perfectly harmonized across all firms, industries, and years.

## Dashboard Acceptance

The dashboard is accepted as a thesis artifact for historical exploration, factor comparison, target interpretation, and decision-support demonstration.

Screenshot checks pass for:

- Overview;
- Data Coverage;
- Models for strict distress, failure pressure, success/resilience, and recovery;
- Target Lab overview;
- Target Lab recovery reason evidence;
- Firm Explorer;
- Macro comparison;
- Artifact Notes.

The console report records only known benign Vega-Lite warnings. These are not treated as scientific failures.

## Literature And Claims

The literature package remains sufficient for the thesis requirement baseline:

- 67 verified references;
- 51 academic journal articles;
- 56 peer-reviewed sources including conference papers;
- 21 sources from 2020 onward;
- 67/67 with DOI, official page, publisher page, or official report URL.

The thesis should use `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md` as the claim guardrail.

## Safe Claims

- The project builds an audited SEC/FRED/global-event firm-period panel.
- The panel uses SEC filing dates as prediction timestamps.
- Strict legal distress is a rare-event benchmark.
- Broader financial pressure is the main failure-factor target.
- Success/resilience is modeled separately from failure pressure.
- Four validated secondary production outcomes add dimensional analysis of resilience, stress resilience, recovery, and cash-flow-supported success.
- Models are evaluated under temporal validation, not random splitting.
- Calibration, ranking, tuning, and boosted-tree robustness diagnostics exist.
- The dashboard is a decision-support and exploratory artifact, not a live bankruptcy oracle.

## Unsafe Claims

- The model predicts bankruptcy well in a complete legal sense.
- Broader failure pressure equals bankruptcy.
- Feature importance proves causality.
- Macro variables dominate firm fundamentals.
- SEC taxonomy harmonization is perfect.
- Missingness indicators are direct economic causes.
- Robustness-extension targets are production targets.
- AutoGluon, RFSD, CHS/Merton, survival analysis, NLP, ESG, HR, Japan/Hong Kong data, or market-price default models were implemented in the final pipeline.

## Remaining Work Before Submission

Technical blockers: none currently open.

Required non-technical/freeze work:

1. Final thesis manuscript writing and integration.
2. Final documentation consistency review immediately before submission.
3. Final dashboard review in the presentation environment.
4. Final Git or archive freeze with manifest/checksums.
5. GitHub upload only after the thesis-facing files and claims are locked.

## Final Recommendation

Do not add new data sources, targets, features, or taxonomy mappings before submission unless a blocking factual error is found.

The project should now move from empirical development into manuscript assembly, final documentation consistency, and release freeze.
