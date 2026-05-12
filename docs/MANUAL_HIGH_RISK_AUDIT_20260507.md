# Manual High-Risk Audit

Date: 2026-05-07

Update note, 2026-05-08: the SEC `ddate == period` finding in this file remains the historical reason for the rebuild. The event-date counts and event-date status below are no longer current: formal strict-distress provenance is now PASS with 44/44 formal rows source-verified. Use `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md`, `docs/CURRENT_STATUS.md`, and `reports/data_quality/event_date_scientific_validity_summary.csv` for current status.

This note records a manual audit of the highest-risk thesis items. It uses the current project artifacts plus targeted manual extractions from the panel/provenance tables. It is not another automated pass/fail report.

## Bottom Line

The biggest risk is not distress-event provenance or duplicate amendments. The biggest risk is SEC fact period alignment.

The row-level provenance table proves that the production panel matches the selected SEC facts, but manual inspection shows that the selected facts can come from the wrong SEC `ddate` inside the filing. This means the selector can choose prior-year comparative facts and use them as current-period accounting values.

Until this is fixed and the panel/models/dashboard are rebuilt, the current accounting-feature models should be treated as reproducible draft results, not final thesis evidence.

## 1. SEC Fact Period Alignment

Status: `CRITICAL_REBUILD_REQUIRED`

What was checked:

- `reports/data_quality/sec_selected_fact_provenance.parquet`
- `reports/data_quality/sec_selected_fact_provenance_summary.csv`
- `reports/data_quality/sec_selected_fact_panel_validation.csv`
- `reports/data_quality/extreme_accounting_outlier_review.csv`
- `scripts/sec_fsd/build_panel_v2.py`
- `scripts/sec_fsd/build_sec_selected_fact_provenance.py`

Automated validation result:

- selected fact rows: 661,533;
- matched panel values: 661,509;
- selected-value panel mismatches above tolerance: 0;
- missing panel values for selected facts: 24, all tied to one invalid LGND timestamp row excluded from the production panel.

Manual finding:

- 367,743 of 661,533 selected facts have SEC `ddate` different from the filing `period`.
- This affects almost every filing row: 31,697 of 31,720 accession IDs in the selected-fact provenance table have at least one selected fact where `ddate != period`.
- High-share examples:
  - `total_revenue`: 15,954 of 27,679 selected facts have `ddate != period`;
  - `net_income`: 18,561 of 31,554;
  - `total_assets`: 16,951 of 31,646;
  - `cash_equivalents`: 20,582 of 30,380.

Why this matters:

- SEC filings often include current-period facts and prior-year comparative facts in the same filing.
- The current selector sorts by `adsh`, `variable`, `qtrs`, `priority`, and `tag`, but does not first require the selected fact's `ddate` to match the filing period.
- Therefore, a prior-year comparative value can become the current panel value.

Code locations:

- `scripts/sec_fsd/build_panel_v2.py` lines 214-228 select one non-flow fact per submission-variable without `ddate == period` filtering.
- `scripts/sec_fsd/build_panel_v2.py` lines 249-277 standardize flows by fiscal year/qtrs, but the selected qtrs facts may still be prior-year comparative facts.
- `scripts/sec_fsd/build_sec_selected_fact_provenance.py` mirrors the same behavior, so the sidecar confirms reproducibility of the current selection, not economic correctness of the selected period.

Manual examples:

- AAPL FY2022 10-K:
  - panel row: `AAPL`, `0000320193-22-000108`, period `2022-09-30`, filed `2022-10-28`;
  - panel `total_revenue = -7.942B`;
  - provenance shows selected SEC fact `RevenueFromContractWithCustomerExcludingAssessedTax`, qtrs `4`, `ddate = 20200930`, reported value `274.515B`;
  - it was differenced against a 2022 prior cumulative value of `282.457B`, producing the impossible-looking negative revenue.
- BKR 2017 Q2:
  - panel row: `BKR`, `0001701605-17-000066`, period `2017-06-30`, filed `2017-07-28`;
  - panel `total_assets = 0`;
  - provenance shows selected `Assets`, `ddate = 20161231`, not `20170630`.

Additional red flags:

- 249 panel rows have negative `total_revenue`.
- 3 panel rows have non-positive `total_assets`: BKR 2017 Q2, EQT 2011 FY, VICI 2017 Q3.
- Some negative revenue rows may be possible for special financial-sector concepts, but negative 10-K revenue for AAPL and other ordinary operating firms is not thesis-safe.

Required fix:

1. Update the SEC selection logic so selected facts must be current-period facts:
   - balance facts: require `ddate == period` before choosing qtrs `0`;
   - current-quarter flow facts: require `ddate == period` for qtrs `1`;
   - cumulative flow facts: require `ddate == period` before deriving single-period values;
   - shares/EPS: require current-period `ddate` where the value is used as current-period information.
2. Rebuild:
   - SEC panel;
   - selected-fact provenance;
   - ratios and trend features;
   - target labels that depend on future fundamentals;
   - model metrics and feature interpretation;
   - dashboard data package and GitHub-ready dataset.
3. Re-run the same manual spot checks after rebuild:
   - AAPL FY2022 revenue should not be negative because of prior-year ddate mixing;
   - BKR 2017 Q2 assets should either be current-period assets or null;
   - non-positive assets and negative revenue lists should be reviewed again.

Thesis implication:

- Current strict legal distress labels are less affected because they come from event dates.
- Failure-pressure and success/resilience targets are affected because they use accounting ratios and future fundamentals.
- Current model results are useful as a pipeline proof, but not final empirical evidence until rebuilt.

## 2. Distress Event Dates

Status: `REVIEW_REMAINS_VALID`

Current policy counts from `reports/data_quality/distress_event_final_policy.csv`:

- 8 source-verified strict distress events;
- 36 retained only with explicit review caveat;
- 6 excluded from strict distress and kept as near-distress/context only.

Manual source spot-check:

- BBBY date `2023-04-23` is supported by the company's SEC filing, which states that Bed Bath & Beyond filed Chapter 11 cases on April 23, 2023: https://www.sec.gov/Archives/edgar/data/886158/000088615823000059/bbby-20230225.htm
- SIVB date `2023-03-10` is supported by the FDIC failed-bank page for Silicon Valley Bank: https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/silicon-valley.html
- SI date `2023-03-08` is supported by the Federal Reserve release referring to Silvergate's voluntary self-liquidation announced on March 8, 2023: https://www.federalreserve.gov/newsevents/pressreleases/enforcement20230601a.htm
- AAMRQ date `2011-11-29` is supported by American Airlines investor-relations release on AMR/American Chapter 11: https://americanairlines.gcs-web.com/news-releases/news-release-details/amr-and-american-airlines-file-chapter-11-reorganization-achieve
- HTZ date `2020-05-22` is supported by Hertz's company release stating it filed Chapter 11 on May 22, 2020: https://newsroom.hertz.com/press-releases/press-release-details/hertz-global-holdings-takes-action-to-strengthen-capital-structure-following-impact-of-glo/
- CHK date `2020-06-28` is supported by Chesapeake's Chapter 11 release: https://www.prnewswire.com/news-releases/chesapeake-energy-corporation-commences-voluntary-chapter-11-process-301084764.html
- CIT date `2009-11-01` is supported by a later CIT SEC filing describing the bankruptcy filing and emergence: https://www.sec.gov/Archives/edgar/data/1171825/000089109210001264/e38098def14a.htm

Manual conclusion:

- The caveat policy is appropriate. Do not claim all 36 initial-seed rows are fully source-verified until each is individually backed by a source.
- The strict distress target can remain a benchmark, but should not be the headline empirical target.

## 3. Duplicate And Amended Filings

Status: `DISCLOSED_MINOR_RISK`

What was checked:

- `reports/data_quality/duplicate_ticker_period_prediction_detail.csv`
- `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md`

Manual finding:

- The detail file lists 30 rows forming 15 duplicate groups.
- These are same CIK/ticker/period/prediction-date pairs, usually primary forms and same-day amendments:
  - 12 `10-Q` rows;
  - 12 `10-Q/A` rows;
  - 3 `10-K` rows;
  - 3 `10-K/A` rows.
- Examples include BKNG, BSX, CHTR, CVX, FLR, ICE, IVZ, MTB, NLY, PPL, ROST, and UAMY.

Manual conclusion:

- This is not evidence of random cross-firm duplication.
- It is a deterministic amendment policy issue.
- In the rebuild, choose one row per exact `cik + period_date + prediction_date` group. For prediction realism, the safest default is to keep the original non-amended filing when original and amendment share the same filing date, unless the thesis explicitly uses amended restatement data.

## 4. Missingness And Missingness Indicators

Status: `ACCEPTABLE_WITH_DISCLOSURE_AFTER_REBUILD`

What was checked:

- `docs/MISSINGNESS_INDICATOR_POLICY.md`
- `reports/data_quality/missingindicator_total_liabilities_diagnosis.md`
- `reports/data_quality/panel_v2_missingness_by_feature_family.csv`

Manual conclusion:

- The policy is conceptually correct: raw nulls stay null; imputation happens only inside modeling pipelines; missingness indicators can help prediction but are not economic causes.
- The previous `missingindicator_total_liabilities` target-contamination issue is documented as fixed.
- However, SEC period-alignment errors can create false values where nulls would be more honest. This means missingness should be re-audited after the SEC selector is fixed.

## 5. Model And Interpretation Readiness

Status: `PIPELINE_READY_BUT_RESULTS_NOT_FINAL`

What was checked:

- `reports/data_quality/leakage_audit.csv`
- `reports/modeling/panel_v2_model_metrics.csv`
- `reports/modeling/model_interpretation_stability_summary.csv`
- `docs/MODEL_INTERPRETATION_STABILITY_NOTE.md`

Manual conclusion:

- Feature-list leakage checks show no blacklisted target/metadata columns in current model feature lists.
- Temporal validation is the right validation structure.
- Feature-group interpretation is the right thesis framing.
- But accounting features, ratios, deterioration features, success targets, and failure-pressure targets inherit the SEC period-alignment risk.

Therefore:

- Do not present current model metrics as final.
- After rebuilding the panel, rerun the same models and compare whether the main feature-group story survives.
- If the story changes, the rebuilt results replace the current results.

## 6. Reproducibility And GitHub Package

Status: `STRUCTURALLY_READY_BUT_FREEZE_MUST_BE_REPLACED_AFTER_REBUILD`

What was checked:

- `docs/REPRODUCIBILITY_FREEZE_20260507.md`
- `reports/reproducibility/freeze_manifest_20260507.csv`
- `data/github/firm_panel_v2.parquet`
- `data/github/firm_panel_v2.csv.gz`
- `data/github/firm_panel_v2_schema.csv`

Manual conclusion:

- The package is structurally presentable.
- The freeze manifest is useful.
- But it currently freezes a panel with an unresolved SEC selected-fact period-alignment issue.
- After rebuild, regenerate the GitHub package and freeze manifest.

## Priority Actions

1. Fix SEC fact selection with `ddate == period` filtering.
2. Rebuild the panel and provenance sidecar.
3. Re-audit outliers, negative revenue, non-positive assets, missingness, and accounting identity plausibility.
4. Rebuild targets and rerun temporal models.
5. Rebuild dashboard data and screenshots.
6. Only then treat GitHub package, model metrics, and dashboard as final.

## Safe Wording Until Fixed

Use:

"The current manual audit found that the SEC extraction pipeline is reproducible but requires period-alignment correction before final empirical claims are made."

Do not use:

"The accounting panel is final and scientifically validated."
