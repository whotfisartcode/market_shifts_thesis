# Final Caveat Resolution Register

Updated: 2026-05-09

This file records how the remaining thesis caveats are handled. It is a control document: production changes are made through deterministic rebuild logic, not manual parquet edits.

## Resolution Summary

| Caveat | Current action | Thesis-safe position |
| --- | --- | --- |
| Distress event-date provenance | 44 source-verified strict rows; 0 strict rows retained only with explicit REVIEW caveat; 6 near-distress/context rows excluded from strict distress. | Strict legal distress is a rare-event benchmark with disclosed provenance limitations. |
| SEC concept mapping | Row-level selected-fact provenance sidecar created as `reports/data_quality/sec_selected_fact_provenance.parquet`, `reports/data_quality/sec_selected_fact_provenance.csv.gz`, and `reports/data_quality/sec_selected_fact_provenance_summary.csv`; sign/null policies are documented in the build and validation reports. | Accounting values are auditable to selected SEC tags and qtrs methods; not perfect taxonomy harmonization. |
| Duplicate/amended filings | Same-information-date duplicates are resolved deterministically in the build pipeline; later amended filings remain as distinct information dates. | Duplicate/amendment handling is disclosed and audited; no manual parquet editing is used. |
| Reproducibility/version freeze | Checksum manifest and GitHub release list created under `reports/reproducibility/`. | Final upload should use the frozen artifacts and exclude raw SEC ZIPs. |
| Dashboard presentation | Storyboard/checklist created and screenshots already exist. | Dashboard is a historical decision-support artifact, not a live oracle. |
| Model interpretation | Stability tables created for economic feature groups. | Interpret feature groups and associations, not causal single-feature claims. |
| Writing discipline | Safe/unsafe claims remain controlling. | No overclaiming of AutoML, causality, perfect SEC mapping, or full legal-event verification. |

## Current Accounting/Panel Caveat Counts

| check | current result |
| --- | --- |
| Production panel rows | 31,702 |
| Same ticker/period/prediction duplicate groups | 0 |
| Same-information-date amended rows dropped by builder | 15 |
| Non-positive `total_assets` rows | 0 |
| Negative `total_revenue` rows | 10 |
| Unresolved negative-revenue mapping rows | 0 |
| Selected-value mismatches above tolerance | 0 |
| Documented selected-fact panel exclusions | 371 |

## Distress Event Policy Counts

| final_policy | rows |
| --- | --- |
| include_as_source_verified_strict_distress | 44 |
| exclude_from_strict_distress_keep_context_only | 6 |

## Duplicate/Amendment Policy Counts

| deterministic_policy | rows |
| --- | --- |
| keep_distinct_prediction_dates | 322 |
| review_universe_or_metadata_duplication_no_financial_manual_drop | 1 |
| future_rebuild_choose_deterministic_single_row_within_same_cik_period_prediction | 1 |
| review_ticker_alias_or_same_date_amendment_do_not_drop_manually | 1 |

## Reproducibility Manifest Status

| exists | files |
| --- | --- |
| True | 57 |

## Model Interpretation Stability

Use `reports/modeling/model_interpretation_stability_summary.csv` and `reports/modeling/model_interpretation_top_groups_by_target_model.csv`.

Top average feature-group shares:

| target | feature_group | mean_share_across_models | interpretation_stability |
| --- | --- | --- | --- |
| distress_next_4q | Accounting fundamentals | 0.35214842631160853 | dominant |
| distress_next_4q | Firm trend / deterioration | 0.25027501437318334 | dominant |
| distress_next_4q | Financial ratios | 0.21489696175323938 | dominant |
| distress_next_4q | Macro conditions | 0.1599299540561395 | dominant |
| distress_next_4q | Industry / sector | 0.0760596281912088 | moderate |
| failure_pressure_conservative_v2_next_4obs | Accounting fundamentals | 0.3717751134602249 | dominant |
| failure_pressure_conservative_v2_next_4obs | Macro conditions | 0.22757131601133385 | dominant |
| failure_pressure_conservative_v2_next_4obs | Firm trend / deterioration | 0.21158567086334726 | dominant |
| failure_pressure_conservative_v2_next_4obs | Financial ratios | 0.1529727591557171 | dominant |
| failure_pressure_conservative_v2_next_4obs | Industry / sector | 0.10512302507101183 | dominant |
| failure_pressure_conservative_v2_next_4obs | Macro regime / time | 0.0204876623264287 | moderate |
| success_resilience_next_4q | Financial ratios | 0.3973216828589973 | dominant |
| success_resilience_next_4q | Accounting fundamentals | 0.30556098126074654 | dominant |
| success_resilience_next_4q | Firm trend / deterioration | 0.18261741431845813 | dominant |
| success_resilience_next_4q | Industry / sector | 0.09240784872381297 | moderate |

## Dashboard Storyboard Status

| item | status | thesis_use |
| --- | --- | --- |
| Overview outcome composition | implemented | Use for thesis result screenshot; explains where strict distress, pressure, success, and ordinary observations fit. |
| Target coverage by year | implemented | Use to explain why labels have different denominators and why null targets are unknown. |
| Firm metrics selector | implemented | Use financial fields only; targets are separated into target timeline. |
| Macro comparison standardization | implemented | Default training-period baseline; caption explains z-score baseline. |
| Target timeline separated from firm metrics | implemented | Prevents target labels from being mixed with raw financial metrics. |
| Model metrics and top features | implemented | Use with caveat that feature importance is association, not causality. |
| Factor-group view | implemented | Preferred for thesis interpretation over isolated single features. |
| Artifact caveat panel | implemented_with_caveats | Includes explicit caveat controls and source-of-truth pointers; strict event-date provenance is PASS for current formal rows. |
| Final screenshots | implemented | Screenshots already saved under reports/figures/dashboard/. |
