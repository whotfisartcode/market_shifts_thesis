# Full Manual Logic, UI, And Backend Audit - 2026-05-08

This audit combines manual code reading with a fixed hand-reviewable panel sample and recomputation checks. It does not rebuild or edit the production panel.

Current status note, 2026-05-12: this manual audit remains evidence for the high-risk logic/UI/backend review, but its panel-width snapshot predates the 2026-05-10 validated-secondary target-label promotion. The current production panel is 31,702 rows x 190 columns and is accepted in `docs/FINAL_ACCEPTANCE_REPORT_20260512.md`. The manual audit's core timing, duplicate-CIK, target-recompute, formula-review, and dashboard findings remain historical QA evidence.

## Executive Result

- The project is scientifically usable for the thesis, but it should be presented as an audited empirical artifact with explicit caveats, not as a perfect corporate-default database.
- The highest-risk timing, target-leakage, SEC period-alignment, duplicate-CIK, and target-recompute checks pass in the rebuilt panel. The remaining risks are accounting concept imperfections, source outlier rows, duplicate/amended filings, material missingness, and dashboard visual-density caveats.
- Formula recomputation still has `229` small REVIEW mismatches because the audit recomputes raw formulas while the production builder applies extreme-value cleaning/null preservation. These are disclosed rather than silently overwritten.
- Dashboard static backend checks have `0` REVIEW rows after the current polish pass; readable event context is now surfaced separately from numeric macro charts.

## Panel Snapshot

- Rows: `31,702`
- Columns at this manual-audit checkpoint: `186`; current production columns after validated-secondary target promotion: `190`
- CIKs: `540`
- Ticker/display IDs: `540`
- Prediction dates: `2009-04-15` to `2026-03-31`
- Numeric null share: `13.372%`
- Duplicate ticker-period-prediction rows: `0`
- CIKs mapped to multiple ticker/display IDs: `0`
- Negative revenue rows: `10`
- Non-positive asset rows: `0`

## P0 Audit Status

| audit | status | violations |
| --- | --- | --- |
| prediction_timestamp | PASS |  |
| distress_event_dates | PASS |  |
| leakage | PASS | 0.0 |
| macro_lag | PASS | 0.0 |
| global_event_timing | PASS | 0.0 |
| post_event_rows | PASS | 0.0 |

## Manual Row Sample

A fixed review sample of `375` rows was written to `reports/project_audit/manual_panel_row_audit_sample_20260508.csv`. It intentionally over-samples distress, broader failure pressure, success/resilience, neutral observations, unknown horizons, duplicates, outliers, event-context rows, stress-regime rows, test-window rows, and anchor tickers.

| audit_category | rows | firms | first_prediction | last_prediction |
| --- | --- | --- | --- | --- |
| failure_pressure_without_strict_distress | 45 | 40 | 2009-11-06 | 2024-08-08 |
| global_event_context_present | 35 | 35 | 2010-10-21 | 2024-08-05 |
| known_anchor_tickers | 60 | 7 | 2009-10-27 | 2026-02-18 |
| market_stress_regime | 30 | 28 | 2009-05-07 | 2022-10-21 |
| negative_revenue_outlier | 10 | 7 | 2011-04-28 | 2022-04-28 |
| neutral_surviving_known_outcome | 35 | 33 | 2010-09-02 | 2024-10-29 |
| strict_distress_positive | 45 | 30 | 2010-10-20 | 2023-12-18 |
| success_resilience_positive | 45 | 39 | 2011-02-14 | 2025-04-22 |
| temporal_test_window | 35 | 34 | 2022-02-03 | 2024-10-31 |
| unknown_future_horizon_or_missing_target | 35 | 33 | 2010-06-25 | 2026-02-06 |

## Highest-Risk Manual Row Finding

- The prior `PCG`/`PGNPQ` duplicate-CIK issue is resolved in the current rebuilt panel: no CIK maps to multiple ticker/display IDs.
- Target recomputation had zero mismatches across the three primary production targets at this manual-audit checkpoint. Current model-output consistency checks pass for all seven production targets after validated-secondary target promotion.

## Formula Recompute Checks

| area | column | rows_checked | mismatches | status |
| --- | --- | --- | --- | --- |
| ratio_recompute | leverage_assets | 31702 | 1 | REVIEW |
| ratio_recompute | equity_assets | 31702 | 1 | REVIEW |
| ratio_recompute | current_ratio | 31702 | 0 | PASS |
| ratio_recompute | cash_assets | 31702 | 0 | PASS |
| ratio_recompute | net_margin | 31702 | 39 | REVIEW |
| ratio_recompute | operating_margin | 31702 | 39 | REVIEW |
| ratio_recompute | gross_margin | 31702 | 0 | PASS |
| ratio_recompute | roa | 31702 | 1 | REVIEW |
| ratio_recompute | r_and_d_intensity | 31702 | 15 | REVIEW |
| ratio_recompute | inventory_assets | 31702 | 1 | REVIEW |
| ratio_recompute | receivables_assets | 31702 | 0 | PASS |
| trend_recompute | roa_lag1 | 31702 | 0 | PASS |
| trend_recompute | leverage_assets_lag1 | 31702 | 0 | PASS |
| trend_recompute | current_ratio_lag1 | 31702 | 0 | PASS |
| trend_recompute | cash_assets_lag1 | 31702 | 0 | PASS |
| trend_recompute | net_margin_lag1 | 31702 | 0 | PASS |
| trend_recompute | operating_margin_lag1 | 31702 | 0 | PASS |
| trend_recompute | gross_margin_lag1 | 31702 | 0 | PASS |
| trend_recompute | total_revenue_growth_4obs | 31702 | 6 | REVIEW |
| trend_recompute | total_assets_growth_4obs | 31702 | 11 | REVIEW |
| trend_recompute | cash_equivalents_growth_4obs | 31702 | 61 | REVIEW |
| trend_recompute | total_liabilities_growth_4obs | 31702 | 12 | REVIEW |
| trend_recompute | current_assets_growth_4obs | 31702 | 22 | REVIEW |
| trend_recompute | current_liabilities_growth_4obs | 31702 | 17 | REVIEW |
| trend_recompute | roa_change_4obs | 31702 | 0 | PASS |
| trend_recompute | leverage_assets_change_4obs | 31702 | 0 | PASS |
| trend_recompute | current_ratio_change_4obs | 31702 | 0 | PASS |
| trend_recompute | cash_assets_change_4obs | 31702 | 0 | PASS |
| trend_recompute | net_margin_change_4obs | 31702 | 2 | REVIEW |
| trend_recompute | operating_margin_change_4obs | 31702 | 1 | REVIEW |
| trend_recompute | gross_margin_change_4obs | 31702 | 0 | PASS |
| trend_recompute | net_income_negative_count_prior_4obs | 31702 | 0 | PASS |
| sec_fact_provenance | ddate_period_aligned | 700844 | 0 | PASS |

Formula mismatches are small relative to the full panel and mostly reflect the difference between raw arithmetic recomputation and the production builder's null-preserving extreme-value cleanup. This is not timing leakage or target leakage; it remains a disclosed accounting/data-quality caveat.

## Target Recompute Checks

| target | known_observed | positives_observed | mismatches | status |
| --- | --- | --- | --- | --- |
| distress_next_4q | 31702 | 207 | 0 | PASS |
| failure_pressure_conservative_v2_next_4obs | 29805 | 3003 | 0 | PASS |
| success_resilience_next_4q | 20152 | 12519 | 0 | PASS |

## Model Logic Checks

| area | status | evidence |
| --- | --- | --- |
| feature_list | PASS | features=116; missing=[]; blacklist_overlap=[] |
| temporal_split_distress_next_4q | PASS | train: rows=17145, positives=58, years=2009-2018; validation: rows=6045, positives=53, years=2019-2021; test: rows=5872, positives=96, years=2022-2024; key_overlaps=[] |
| saved_metrics_distress_next_4q | PASS | best_test_model=gradient_boosting; roc_auc=0.8159328471260388; pr_auc=0.1043138859696451; f1=0.1818181818181818; positives=96 |
| saved_feature_blacklist_distress_next_4q | PASS | listed_features=116; blacklist_overlap=[] |
| temporal_split_failure_pressure_conservative_v2_next_4obs | PASS | train: rows=17145, positives=1555, years=2009-2018; validation: rows=6029, positives=834, years=2019-2021; test: rows=5734, positives=575, years=2022-2024; key_overlaps=[] |
| saved_metrics_failure_pressure_conservative_v2_next_4obs | PASS | best_test_model=random_forest; roc_auc=0.9540138186720593; pr_auc=0.7578791892959569; f1=0.7250996015936254; positives=575 |
| saved_feature_blacklist_failure_pressure_conservative_v2_next_4obs | PASS | listed_features=116; blacklist_overlap=[] |
| temporal_split_success_resilience_next_4q | PASS | train: rows=11058, positives=7029, years=2009-2018; validation: rows=4190, positives=2414, years=2019-2021; test: rows=4046, positives=2647, years=2022-2024; key_overlaps=[] |
| saved_metrics_success_resilience_next_4q | PASS | best_test_model=random_forest; roc_auc=0.9665813841997628; pr_auc=0.974648887771459; f1=0.9376303317535546; positives=2648 |
| saved_feature_blacklist_success_resilience_next_4q | PASS | listed_features=116; blacklist_overlap=[] |
| sklearn_tuning | PASS_WITH_CAVEAT | summary_exists=True; candidate_failure_rows=0 |
| advanced_boosting | PASS_WITH_CAVEAT | summary_exists=True; candidate_failure_rows=0 |

## Dashboard Static Backend Checks

| area | status | evidence |
| --- | --- | --- |
| financial_dashboard_coverage | PASS | dashboard=63; schema_usable=63; missing=[] |
| macro_dashboard_coverage | PASS | dashboard_chartable=68; schema_chartable=68; missing=[] |
| global_event_names_text_context | PASS | `global_event_names` is treated as readable text context, not as a numeric chart metric. |
| target_separation | PASS | Targets are shown in a separate timeline tab; firm metrics use FIRM_METRIC_GROUPS. |
| standardization_disclosure | PASS | Dashboard exposes selected-window, filtered-panel, and training-period standardization baselines. |
| artifact_caveats | PASS | Artifact tab contains thesis story and caveat controls. |

## Dashboard Rendered Browser Checks

| area | status | evidence |
| --- | --- | --- |
| page_identity | PASS | Browser opened http://127.0.0.1:8501/; title was Market Shifts Distress Dashboard; app heading rendered as Market Shifts: Firm Distress and Resilience. |
| not_blank | PASS | Overview, Firm Explorer, and Macro Compare rendered meaningful dashboard content. |
| framework_overlay | PASS | No Streamlit/framework error overlay appeared during desktop or mobile smoke checks. |
| console_health | PASS | Current screenshot capture marks the console row PASS: only known benign Vega-Lite render warnings were captured, and no browser error-level app failures were found. |
| overview_logic | PASS_WITH_CAVEAT | Overview now separates outcome composition, target coverage, independent positive rates, and unknown/neutral rows. The default sidebar year filter is 2009-2024, so visible row counts differ from the full 2026 panel by design. |
| firm_explorer_logic | PASS | Firm metrics, macro comparison, target timeline, and recent rows are separated. Default ticker is AAPL when present. |
| desktop_visual | PASS_WITH_CAVEAT | Desktop layout is usable; long sidebar multiselect chips may truncate visually, but firm-level sector/cohort values no longer use cramped metric widgets. |
| macro_compare_logic | PASS | Macro comparison exposes raw separate scales, one raw metric, and standardized comparison with selected-window, filtered-panel, and training-period baselines. |
| mobile_visual | PASS_WITH_CAVEAT | Mobile viewport renders without crashing and tabs remain usable, but content is long/scroll-heavy and sidebar/filter density is high. |
| event_context_ui | PASS | Numeric global-event count/severity fields are chartable, and `global_event_names` is surfaced as readable event context in the Firm Explorer. |

## Manual Code-Reading Findings

1. `scripts/sec_fsd/build_panel_v2.py` uses `ddate == period`, excludes dimensional segment/coreg facts, filters units, standardizes flow values, then computes ratios, lags, macro/event context, and forward labels. This is the correct structure for avoiding look-ahead from filing-period accounting values.
2. The flow-standardization logic is reasonable but not equivalent to a full accountant-grade XBRL mapping audit. The thesis should say selected facts are mapped and audited, not that every possible SEC tag across all firms is perfectly represented.
3. `prediction_date = filed_date` is correctly used as the information-availability date. This is one of the strongest parts of the empirical design.
4. `scripts/modeling/train_panel_v2_models.py` uses train `<= 2018`, validation `2019-2021`, and test `2022-2024`, with threshold selection on validation. This is defensible and better than random split for the thesis.
5. The model feature list excludes target/event-date metadata by blacklist, but imputer-generated missingness indicators exist inside pipelines. They must remain predictive auxiliaries and must not be interpreted as economic causes.
6. The dashboard separates firm metrics from target timelines and includes standardization baseline controls. This directly addresses the earlier issue where raw metrics and targets were visually mixed.
7. `scripts/data_quality/audit_data_integrity_caveats.py` previously had one stale generated-report sentence about event-date provenance; it has been patched so future reruns align with the current PASS status for formal strict-distress event provenance.

## Remaining Weaknesses

- SEC concept mapping is strong enough for thesis use but still relies on a selected concept map and priority rules. This is normal for FSD work, but it must be disclosed.
- Accounting sign/outlier rows remain real review items. Do not delete them silently; either disclose or source-correct if time allows.
- The prior `PCG`/`PGNPQ` duplicate-CIK mapping has been resolved in the rebuilt panel; keep the alias-resolution note with the final package.
- Duplicate/amended-filing rows remain small in count but need explicit policy wording.
- Missingness is material. The panel should stay null-preserving; model imputation should stay inside pipelines.
- Strict legal distress is source-curated and rare. It is a benchmark, not a complete bankruptcy universe.
- Dashboard screenshots and console triage now pass; remaining dashboard caveats are presentation-density issues on narrow/mobile views, not empirical validity issues.

## Audit Artifacts

- `reports/project_audit/manual_panel_row_audit_sample_20260508.csv`
- `reports/project_audit/manual_panel_row_audit_sample_summary_20260508.csv`
- `reports/project_audit/manual_formula_recompute_audit_20260508.csv`
- `reports/project_audit/manual_target_recompute_audit_20260508.csv`
- `reports/project_audit/manual_model_logic_audit_20260508.csv`
- `reports/project_audit/manual_dashboard_static_audit_20260508.csv`
- `reports/project_audit/manual_dashboard_rendered_audit_20260508.csv`
