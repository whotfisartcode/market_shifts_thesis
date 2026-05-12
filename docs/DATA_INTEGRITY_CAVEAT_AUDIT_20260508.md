# Data Integrity Caveat Audit 2026-05-10

This is the consolidated post-rebuild audit of data-integrity issues that previously carried caveats. It was refreshed after the 2026-05-10 validated-secondary target promotion.

## Status Summary

| status | areas |
| --- | --- |
| PASS | 8 |
| PASS_WITH_CAVEATS | 3 |
| PASS_WITH_DOCUMENTED_EXCLUSIONS | 1 |
| PASS_WITH_MISSINGNESS_CAVEAT | 1 |
| PASS_WITH_REVIEWED_EXCEPTIONS | 1 |

## Detailed Audit

| area | status | evidence | recommended_action |
| --- | --- | --- | --- |
| Core/GitHub panel equality | PASS | GitHub panel shape (31702, 190); processed panel shape (31702, 190); exact dataframe equality = True. | Repeat this after the final GitHub package freeze. |
| Panel dimensions | PASS | Panel shape is (31702, 190); CIKs=540; ticker/display IDs=540. | Use these counts in thesis/package docs unless the panel is rebuilt again. |
| Prediction timestamp | PASS | prediction_date_source counts: {'filed_date': 31702}. | Keep `prediction_date = filed_date` as the information-availability timestamp. |
| SEC selected-fact period alignment | PASS_WITH_DOCUMENTED_EXCLUSIONS | 700844 selected facts; ddate != period rows=0; unaligned flags=0; selected-value mismatches=0; documented exclusions=371. | Use the provenance sidecar as evidence; documented exclusions are deterministic duplicate drops, invalid timestamp exclusions, and source-aware accounting nulls. |
| Numeric null and infinity policy | PASS_WITH_MISSINGNESS_CAVEAT | numeric cells=5104022; numeric nulls=734026; null share=14.381%; infinite values=0. | Preserve nulls in the panel; impute only inside model pipelines. |
| Accounting sign/outlier sanity | PASS_WITH_REVIEWED_EXCEPTIONS | negative total_revenue rows=10; non-positive total_assets rows=0; negative total_assets rows=0; negative total_liabilities rows=0; unresolved negative-revenue mapping rows=0. | Use source-aware controls: invalid derived/sign-convention revenue and non-positive assets are nulled; remaining negative revenue is source-reported and disclosed. |
| Accounting identity sanity | PASS_WITH_CAVEATS | Balance-sheet identity within 5% of assets for 93.9% of checked rows. | Describe identity checks as plausibility checks, not perfect accounting reconciliation. |
| Duplicate amended-filing rows | PASS | 0 rows across 0 ticker-period-prediction groups. | Same-information-date amendment duplicates should be resolved in the builder; later amended filings with later prediction dates remain separate information events. |
| Structured missingness | PASS_WITH_CAVEATS | SEC accounting avg missing=28.7%; ratio avg missing=28.6%; trend avg missing=24.1%. | Treat missingness as a disclosed reporting/data-availability feature; exclude missingness indicators from economic causality claims. |
| Target label counts | PASS_WITH_CAVEATS | distress_next_4q: known=31702, positives=207, missing=0; failure_pressure_conservative_v2_next_4obs: known=29805, positives=3003, missing=1897; success_resilience_next_4q: known=20152, positives=12519, missing=11550; industry_relative_resilience_next_4obs: known=20039, positives=8093, missing=11663; stress_resilience_next_4obs: known=5901, positives=3707, missing=25801; recovery_next_4obs: known=11375, positives=5578, missing=20327; quality_success_cashflow_next_4obs: known=16767, positives=9852, missing=14935. | Use the first three as primary targets and the four promoted labels as validated secondary production outcomes. |
| P0 timing/leakage/event audits | PASS | prediction_timestamp=PASS; distress_event_dates=PASS; leakage=PASS; macro_lag=PASS; global_event_timing=PASS; post_event_rows=PASS | Keep timing/leakage claims; strict event-date provenance now passes. |
| Strict event-date provenance | PASS | formal_distress/VERIFIED=44; near_distress/REVIEW_NON_STRICT=6 | Use the source-provenance table as evidence; keep non-strict near-distress rows as context only. |
| Model feature leakage guardrail | PASS | No blacklist overlap in model feature lists. | Do not add target/event/date metadata into model feature lists. |
| GitHub schema coverage | PASS | schema rows=190; panel columns=190. | Keep schema with the GitHub package. |

## Interpretation

- The old SEC selected-fact period-alignment defect is closed for production selected facts.
- The panel remains null-preserving; missingness is material and must be disclosed.
- Same-information-date duplicate amended-filing rows are handled deterministically in the builder.
- Invalid derived/sign-convention revenue and non-positive assets are source-aware controls; remaining negative revenue is source-reported and disclosed.
- Strict legal distress event-date provenance now passes for formal distress rows; the remaining limitation is that strict distress is source-curated and rare, not a complete legal-bankruptcy database.
- The panel is scientifically usable for the thesis if these caveats are stated honestly.

## Detail Files

- `reports/data_quality/accounting_sign_outlier_detail_20260508.csv`
- `reports/data_quality/duplicate_amended_filing_rows_20260508.csv`
