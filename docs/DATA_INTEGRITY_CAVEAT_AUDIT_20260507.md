# Data Integrity Caveat Audit 2026-05-07

> Superseded status note, 2026-05-10: this audit is retained for history. It was superseded by the later 2026-05-09 SEC mapping and caveat-resolution rebuild. For current panel dimensions, target counts, and caveat status, use `docs/DATA_INTEGRITY_CAVEAT_AUDIT_20260508.md`, `docs/FACTUAL_FREEZE_20260509.md`, `docs/CURRENT_STATUS.md`, and `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`.

This is the consolidated post-rebuild audit of data-integrity issues that previously carried caveats.

## Status Summary

| status | areas |
| --- | --- |
| PASS | 6 |
| REVIEW | 4 |
| PASS_WITH_CAVEATS | 2 |
| PASS_WITH_DOCUMENTED_EXCLUSIONS | 1 |
| PASS_WITH_MISSINGNESS_CAVEAT | 1 |

## Detailed Audit

| area | status | evidence | recommended_action |
| --- | --- | --- | --- |
| Core/GitHub panel equality | PASS | GitHub panel shape (31716, 185); processed panel shape (31716, 185); exact dataframe equality = True. | Repeat this after the final GitHub package freeze. |
| Panel dimensions | REVIEW | Panel shape is (31716, 185); CIKs=540; ticker/display IDs=540. | Use these counts in thesis/package docs unless the panel is rebuilt again. |
| Prediction timestamp | PASS | prediction_date_source counts: {'filed_date': 31716}. | Keep `prediction_date = filed_date` as the information-availability timestamp. |
| SEC selected-fact period alignment | PASS_WITH_DOCUMENTED_EXCLUSIONS | 660989 selected facts; ddate != period rows=0; unaligned flags=0; selected-value mismatches=0; documented exclusions=24. | Use the provenance sidecar as evidence; keep BKR/VICI zero-asset rows as explicit outlier review items. |
| Numeric null and infinity policy | PASS_WITH_MISSINGNESS_CAVEAT | numeric cells=4947696; numeric nulls=680717; null share=13.758%; infinite values=0. | Preserve nulls in the panel; impute only inside model pipelines. |
| Accounting sign/outlier sanity | REVIEW | negative total_revenue rows=18; non-positive total_assets rows=2; negative total_assets rows=0; negative total_liabilities rows=0. | Do not silently delete; disclose and keep outlier review table unless a source-specific correction is verified. |
| Accounting identity sanity | PASS_WITH_CAVEATS | Balance-sheet identity within 5% of assets for 93.9% of checked rows. | Describe identity checks as plausibility checks, not perfect accounting reconciliation. |
| Duplicate amended-filing rows | REVIEW | 30 rows across 15 ticker-period-prediction groups. | Disclose deterministic policy; a future rebuild can keep one same-date amendment row per group, but current thesis package does not silently edit the panel. |
| Structured missingness | PASS_WITH_CAVEATS | SEC accounting avg missing=30.5%; ratio avg missing=30.8%; trend avg missing=24.6%. | Treat missingness as a disclosed reporting/data-availability feature; exclude missingness indicators from economic causality claims. |
| Target label counts | REVIEW | distress_next_4q: known=31716, positives=207, missing=0; failure_pressure_conservative_v2_next_4obs: known=29819, positives=3007, missing=1897; success_resilience_next_4q: known=20160, positives=12525, missing=11556. | Use strict distress as benchmark; use failure pressure and success/resilience as main factor targets. |
| P0 timing/leakage/event audits | PASS | prediction_timestamp=PASS; distress_event_dates=PASS; leakage=PASS; macro_lag=PASS; global_event_timing=PASS; post_event_rows=PASS | Keep timing/leakage claims; strict event-date provenance now passes. |
| Strict event-date provenance | PASS | formal_distress/VERIFIED=44; near_distress/REVIEW_NON_STRICT=6 | Use the source-provenance table as evidence; keep non-strict near-distress rows as context only. |
| Model feature leakage guardrail | PASS | No blacklist overlap in model feature lists. | Do not add target/event/date metadata into model feature lists. |
| GitHub schema coverage | PASS | schema rows=185; panel columns=185. | Keep schema with the GitHub package. |

## Interpretation

- The old SEC selected-fact period-alignment defect is closed for production selected facts.
- The panel remains null-preserving; missingness is material and must be disclosed.
- Numeric outliers and duplicate amended-filing rows remain review items, not silent deletions.
- Strict legal distress event-date provenance now passes for formal distress rows; the remaining limitation is that strict distress is source-curated and rare, not a complete legal-bankruptcy database.
- The panel is scientifically usable for the thesis if these caveats are stated honestly.

## Detail Files

- `reports/data_quality/accounting_sign_outlier_detail_20260507.csv`
- `reports/data_quality/duplicate_amended_filing_rows_20260507.csv`
