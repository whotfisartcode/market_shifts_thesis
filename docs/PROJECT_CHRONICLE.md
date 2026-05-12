# Project Chronicle

This is the living record for the thesis rebuild. It tracks user requests, assistant responses, decisions, failed attempts, discarded ideas, accepted ideas, artifacts, and next steps.

Current fixed thesis title:

> Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries

Submission deadline currently treated as:

> 2026-05-14 18:00 Europe/Moscow

## Current Positioning

The thesis is not being changed into a new topic. It is being substantially improved within the same approved topic.

Current recommended framing:

> A reproducible SEC/FRED firm-quarter panel for predicting forward-looking firm distress and resilience across industries, testing whether macro-market regime variables improve temporal out-of-sample prediction, with interpretable machine learning used to compare drivers across industries and regimes.

Main practical artifact:

> Streamlit analytical dashboard / decision-support tool for firm resilience and distress monitoring across industries and macro regimes.

Supporting artifacts:

- rebuilt firm-quarter dataset,
- data dictionary,
- reproducible model/scoring pipeline,
- GitHub repository with code, documentation, sample data, and dashboard instructions.

## User Requests and Decisions

### 2026-05-04 Reinstatement Submitted and Build Started

User submitted the reinstatement request.

User requested:

- dashboard artifact,
- ready-to-upload dataset/panel for GitHub,
- immediate execution of the rebuild steps.

Decision:

- Start with the SEC/FRED firm-quarter panel.
- Produce full local panel plus GitHub-safe sample/schema.
- Build Streamlit dashboard after the first stable modeling outputs exist.
- Write compressed CSV by default; write Parquet only if a Parquet engine is available.

Actions completed:

- Built first SEC/FRED panel with `scripts/sec_fsd/build_panel_v2.py`.
- Output: `data/processed/panel_v2/firm_panel_v2.csv.gz`.
- GitHub-ready copy: `data/github/firm_panel_v2.csv.gz`.
- GitHub-ready Parquet copy: `data/github/firm_panel_v2.parquet`.
- Schema: `data/github/firm_panel_v2_schema.csv`.
- Panel shape: 22,713 rows, 86 columns, 390 CIKs, 391 tickers.
- Period range: 2009-03-31 to 2026-02-28.
- Forward distress positives: 131.
- Trained first temporal-validation models with `scripts/modeling/train_panel_v2_models.py`.
- Test period: 2022-2024.
- First model run incorrectly included `cohort` as a categorical feature. This was flagged as leakage risk because the distressed cohort is sample-design information.
- Reran models after removing `cohort` from model features.
- Updated test metrics:
  - logistic regression ROC-AUC 0.806, PR-AUC 0.109,
  - random forest ROC-AUC 0.965, PR-AUC 0.150,
  - gradient boosting ROC-AUC 0.862, PR-AUC 0.095.
- Created first Streamlit dashboard artifact at `app/dashboard.py`.
- Installed Streamlit with network approval after initial sandboxed installation failed.
- Started dashboard server on port 8501 and verified HTTP 200 response at `http://127.0.0.1:8501`.

Known caveat:

- The current panel is a filing-period panel, not a fully cleaned strict fiscal-quarter panel with derived Q4 flow values. This is acceptable for first modeling but should be described carefully unless refined later.

### 2026-05-04 Dashboard First Review

User opened the dashboard and confirmed that it works technically, but judged the visualizations as not useful or impressive.

Decision:

- Keep the dashboard as a working shell for now.
- Prioritize refining empirical outputs first:
  - better distress labels,
  - ablation tests,
  - industry/regime comparisons,
  - thesis-ready plots and tables.
- Return to dashboard after stronger outputs exist, so the dashboard can display useful analytical views rather than generic charts.

Actions completed:

- Added `config/distress_event_dates.csv` for exact/near-exact distress timing.
- Updated `scripts/sec_fsd/build_panel_v2.py` to use event dates instead of year-end fallback when available.
- Rebuilt panel; forward-distress positive rows increased from 131 to 167.
- Found industry summaries were useless because distress candidates lacked sector labels.
- Added SIC-derived fallback sector mapping in `build_panel_v2.py`.
- Rebuilt panel again; panel now has `sic_sector` and filled `Sector`.
- Reran models, ablation, and analysis outputs.
- Current best no-leakage model after refinements: random forest, test ROC-AUC 0.906, PR-AUC 0.152.
- Ablation finding: firm-only random forest currently performs best by PR-AUC; macro/regime features are descriptively useful but do not improve first-pass temporal PR-AUC.
- Industry finding: highest forward-distress shares are currently Energy and Consumer Cyclical after SIC sector fallback.

### 2026-05-04 Target Definitions and VS Code Workflow

User said they are used to running models in VS Code and want access from there. User also asked for clearer exact/near-exact event date handling, multiple success/failure definitions, and feature contributions to failures/successes.

Actions completed:

- Added `docs/VS_CODE_WORKFLOW.md`.
- Added `.vscode/tasks.json` with tasks for rebuilding data, training failure/success models, running ablation, creating analysis outputs, and launching dashboard.
- Added target definitions/event-date note, now archived at `docs/_redundant/03_superseded_target_notes/TARGET_DEFINITIONS_AND_EVENT_DATES.md`.
- Updated `scripts/sec_fsd/build_panel_v2.py` to create multiple target variants:
  - `distress_next_2q`,
  - `distress_next_4q`,
  - `distress_next_8q`,
  - `broad_distress_next_4q`,
  - `healthy_current`,
  - `success_profitability_next_4q`,
  - `success_resilience_next_4q`,
  - `success_quality_next_4q`.
- Added `scripts/modeling/target_profile_report.py`.
- Updated `scripts/modeling/train_panel_v2_models.py` to accept `--target`.
- Trained both primary failure target and primary success target.
- Added `scripts/modeling/feature_contribution_summary.py`.
- Created contribution reports:
  - `reports/modeling/panel_v2_feature_contribution_long.csv`,
  - `reports/modeling/panel_v2_feature_contribution_groups.csv`.

Current target counts, 2009-2024:

- `distress_next_2q`: 82 positives.
- `distress_next_4q`: 167 positives.
- `distress_next_8q`: 340 positives.
- `broad_distress_next_4q`: 197 positives.
- `healthy_current`: 9,641 positives.
- `success_profitability_next_4q`: 18,607 positives.
- `success_resilience_next_4q`: 9,440 positives.
- `success_quality_next_4q`: 7,921 positives.

Current recommended primary targets:

- Failure: `distress_next_4q`.
- Success: `success_resilience_next_4q`.

### 2026-05-04 Panel Architecture, Macro Expansion, and Rare-Event Improvement

User asked whether the firm panel should be one dataset or separate datasets, how accounting fundamentals, ratios, macro variables, regimes, and industry metadata should be packed together, what regimes are, and whether more macro/company/qualitative data should be added to improve rare-event detection.

Decision:

- Use one modeling dataset: a firm-period panel.
- Keep raw SEC accounting values, engineered ratios, macro variables, regime indicators, industry metadata, and targets in the same row.
- Treat raw SEC/FRED files as reproducibility inputs, not separate modeling datasets.
- Add more macro data selectively, not randomly.
- Add firm-level deterioration features because rare distress prediction usually benefits more from changes in firm condition than from additional generic macro levels.
- Do not make qualitative text/NLP a main empirical workstream before the deadline. Use qualitative evidence later for case-study support and event-date verification.

Actions completed:

- Added `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md`.
- Added FRED macro catalog: `config/fred_series_catalog.csv`.
- Added FRED downloader: `scripts/data/download_fred_series.py`.
- Downloaded / refreshed FRED macro data.
- The first downloader attempt failed inside the sandbox because DNS was blocked.
- The first approved Python `urlopen` attempt hung and was stopped.
- Replaced the downloader internals with `curl` plus a timeout.
- Preserved older local BAML high-yield spread history after noticing the fresh FRED graph CSV returned only a clipped recent window for that series.
- Added new FRED variables:
  - yield curve: `T10Y2Y`, `T10Y3M`,
  - oil: `DCOILWTICO`,
  - dollar: `DTWEXBGS`,
  - inflation/input costs: `CPIAUCSL`, `PPIACO`,
  - labor/demand/housing: `PAYEMS`, `RSAFS`, `HOUST`,
  - credit: `BUSLOANS`, `DRTSCILM`.
- Added year-over-year macro changes for selected level/index series.
- Added firm deterioration features:
  - lagged ratios,
  - 4-observation growth/change variables,
  - prior four-observation loss count.
- Updated panel builder to regenerate full GitHub dataset copies automatically.
- Rebuilt panel.
- New panel shape: 22,713 rows and 147 columns.
- Reran failure model, success model, ablation, target profile, analysis outputs, and feature-contribution summaries.

Latest primary failure model:

- Target: `distress_next_4q`.
- Best main training run by PR-AUC: random forest.
- Test period: 2022-2024.
- Test positives: 58.
- ROC-AUC: 0.913.
- PR-AUC: 0.168.

Latest ablation finding:

- Best random forest ablation: firm + macro + regime.
- Test ROC-AUC: 0.903.
- Test PR-AUC: 0.173.
- Precision: 0.171.
- Recall: 0.310.
- F1: 0.221.

Interpretation:

- Macro and regime expansion helped modestly.
- Firm trend/deterioration features became highly important.
- Honest thesis framing should be that accounting condition and deterioration dominate, while macro regimes add contextual and some incremental rare-event ranking signal.

### 2026-05-04 Global Events and Dashboard Direction

User asked whether global world events could be tracked and compared against companies/sectors, whether this would be too much hassle, whether RFSD/Russian data should be added, and whether a "live" dashboard is realistic when SEC filings update quarterly.

Decision:

- Add global events, but start with a curated event calendar instead of a massive raw news/event-data pipeline.
- Treat global events as historical market-shift windows for sector analysis and dashboard storytelling.
- Keep GDELT/ACLED/EM-DAT as optional future data sources, not as urgent core dependencies.
- Do not make a fully live daily accounting dashboard claim. Use "latest available filing" scores plus higher-frequency macro/event context.
- Do not merge Russian/RFSD data into the main empirical panel before the deadline unless the user provides already-clean data. If Russian data arrives, use it as a separate dashboard tab or appendix case study.

Actions completed:

- Added global-event calendar: `config/global_event_calendar_seed.csv`.
- Added strategy note: `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md`.
- Updated `scripts/sec_fsd/build_panel_v2.py` to merge event windows into the firm-period panel.
- Added global-event context columns:
  - `global_event_count`,
  - `global_event_severity_sum`,
  - event-type count/severity fields,
  - `global_event_names`.
- Rebuilt panel.
- New panel shape: 22,713 rows and 174 columns.
- Updated schema feature families; `global_event_context` now has 27 columns.
- Updated model scripts to include event features and ablation feature set `firm_plus_macro_regime_event`.
- Added event-sector outputs to `scripts/modeling/make_panel_v2_analysis_outputs.py`.
- Generated:
  - `reports/modeling/panel_v2_global_event_sector_summary.csv`,
  - `reports/figures/modeling/panel_v2_distress_share_by_global_event_type.png`.
- Reran failure and success models, ablation, target profile, analysis outputs, and feature contributions.

Latest event-aware failure model:

- Target: `distress_next_4q`.
- Main random forest test ROC-AUC: 0.885.
- Main random forest test PR-AUC: 0.175.
- Main random forest recall: 0.138.
- Main random forest F1: 0.167.

Latest ablation:

- Best by test PR-AUC: random forest with firm + macro + regime + global event features.
- ROC-AUC: 0.863.
- PR-AUC: 0.175.
- Recall: 0.345.
- F1: 0.214.

Interpretation:

- Event context adds useful dashboard and historical-analysis value.
- It marginally improves rare-event ranking but is not a silver bullet.
- The strongest empirical explanation remains firm fundamentals and firm deterioration, with macro regimes and event windows as context.

### 2026-05-04 Factor Framing, Null Treatment, and SEC Flow Fix

User clarified that the thesis does not need to be a pure prediction exercise. It should be predictive analytics into success and failure factors across industries, including how industries react under different contexts. User also raised a serious data-integrity concern: all values must be factual, nulls must not be invented, and variables such as CapEx may be filed unevenly across quarters.

Decision:

- Frame the thesis as factor discovery, sector comparison, market-shift analysis, and early-warning artifact, not only forecasting.
- Preserve nulls in exported data.
- Use model imputation only inside the sklearn pipeline.
- Add missingness indicators inside the model pipeline so unavailable values remain visible as missingness signals.
- Treat missingness indicators separately from economic factor groups in interpretation.
- Audit SEC source tags, `qtrs`, and missingness by form/fiscal period.

Actions completed:

- Added `docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md`.
- Added `scripts/data_quality/audit_panel_integrity.py`.
- Generated:
  - `reports/data_quality/sec_fsd_variable_source_audit.csv`,
  - `reports/data_quality/panel_v2_key_missingness_by_form_fp.csv`,
  - `reports/data_quality/panel_v2_missingness_by_feature_family.csv`,
  - `reports/data_quality/panel_v2_longitudinal_missingness_summary.csv`,
  - `reports/data_quality/panel_v2_longitudinal_missingness_by_firm.csv`,
  - `reports/data_quality/panel_v2_null_treatment_audit.csv`.
- Found a real SEC-flow issue:
  - CapEx and cash-flow variables are often reported as cumulative year-to-date values in Q2/Q3.
  - The previous parser accepted only `qtrs=1` and `qtrs=4` for flow variables, so many Q2/Q3 cash-flow facts were incorrectly left missing.
- Updated `scripts/sec_fsd/build_panel_v2.py`:
  - flow variables now accept `qtrs=1`, `qtrs=2`, `qtrs=3`, and `qtrs=4`,
  - current-period values are used when directly reported,
  - otherwise single-period values are derived from cumulative SEC facts when the prior cumulative value exists,
  - unresolved cases remain null.
- Coverage improvement:
  - `capex` missingness improved from about 63.8% to about 33.3%,
  - `cash_flow_operating` missingness improved from about 55.6% to about 15.7%,
  - `cash_flow_investing` missingness improved from about 55.6% to about 15.6%,
  - `cash_flow_financing` missingness improved from about 55.5% to about 15.5%.
- Updated modeling scripts to use median imputation plus missingness indicators inside sklearn pipelines.
- Added `reports/modeling/panel_v2_feature_contribution_economic_groups.csv`, which excludes missingness indicators from economic feature-group shares.
- Rebuilt panel and reran failure model, success model, ablation, analysis outputs, target profile, and feature-contribution reports.

Latest interpretation:

- The strongest ablation by test PR-AUC is now firm-only random forest:
  - ROC-AUC: 0.901,
  - PR-AUC: 0.224,
  - precision: 0.216,
  - recall: 0.328,
  - F1: 0.260.
- Macro and global-event layers remain valuable for sector/event explanation and dashboard analysis, but firm fundamentals and deterioration are the strongest empirical signal.
- Nulls are not interpreted as zero or unchanged by default. The longitudinal audit separates variables that are never reported by many firms from variables that have intermittent gaps where prior/future values exist.

### 2026-05-04 GPT-5.5 Pro Peer Review Read

User uploaded `codex_peer_review_action_plan.json` in the project root and asked to read it. It is now organized under `../_external_inputs/02_ai_reviews_and_strategy_plans/`.

Actions completed:

- Read the JSON peer review.
- Created assessment note, now archived at `docs/_redundant/02_superseded_strategy_reviews/PEER_REVIEW_ACTION_PLAN_ASSESSMENT.md`.

Assessment:

- The review is mostly correct and useful.
- It is slightly stale because it was written before the SEC flow-standardization/null-treatment pass.
- Its P0 recommendations are valid and should be treated as required before dashboard polish and thesis writing:
  - prediction timestamp audit,
  - event-date audit,
  - model-feature leakage audit,
  - macro/event timing audit,
  - post-event row handling.

Decision:

- Freeze scope.
- Do not add new core data sources.
- Next serious work should start with P0 audits, especially using `filed_date` as the prediction timestamp instead of assuming SEC filing values were visible at `period_date`.

### Initial Thesis Audit

User asked to inspect the thesis project, rate the thesis, identify obvious improvements, and ignore the user's own assumptions.

Findings:

- Old thesis file: `../_external_inputs/01_original_thesis_and_requirements/Artem Kozin Master Thesis.docx`.
- Old thesis was below minimum master requirements: about 65 pages and 89,126 characters with spaces.
- Minimum later confirmed by requirements file: 70 pages or 95,000 characters with spaces, excluding references and appendices.
- Main critique from defense/reviews: structure messy, insufficient length, U.S.-only data questioned, weak failure cases, weak validation, weak explainability, dashboard deliverable incomplete.

Decision:

- Keep fixed title.
- Rebuild empirical work under the same topic.
- Focus on better data, better ML, explainability, temporal validation, and dashboard artifact.

### Old Project and Data Audit

User uploaded the old `market_shifts` project folder.

Findings:

- Old final panel: `last_years_thesis_data/market_shifts/data/processed/firms/MODEL/firm_panel_with_zscore.parquet`.
- Shape: 14,104 rows, 58 columns, 255 tickers.
- Date range: 2008-10-02 to 2025-05-09.
- It was not a top-100 panel; it was a 255-firm large-cap U.S. public-company universe.
- `ticker100.txt` actually contained 261 tickers.
- `ticker100more.txt` contained another 100 tickers not used in the final panel.
- Legacy ML targets were created in notebook code, not saved in the panel.
- Legacy target definitions were mostly current/past rolling labels, not forward-looking labels.
- Legacy validation used random split, not temporal validation.
- Legacy panel had serious missingness and outlier issues.

Important old data-quality problems:

- `altman_z` about 93.5% missing.
- `r_and_d_intensity`, `inventory_turnover`, `gross_margin`, and `Z_MVE_TL` more than 82% missing.
- `price` about 68.5% missing.
- Several accounting variables contained suspicious negative values and extreme ratios.
- One duplicate ticker-date row.

Decision:

- Treat old panel as reference/baseline only.
- Rebuild panel from SEC Financial Statement Data Sets instead of raw EDGAR filing parsing.

### Clean Folder Creation

User asked to organize the work folder and approved creating a separate clean copy.

Created:

- `market_shifts_clean/`

Important copied materials:

- config files,
- old FRED macro CSVs,
- old processed XBRL extracts,
- old S&P price data,
- old final panel parquet and CSV,
- old AutoGluon notebook archive,
- old parsing scripts,
- old figures,
- project overview JSON files.

Created documentation and scripts:

- `README.md`
- `docs/DATA_MANIFEST.md`
- `docs/_redundant/01_legacy_project_docs/LEGACY_DATA_AUDIT_SUMMARY.md`
- `.gitignore`
- `requirements.txt`
- `scripts/data_quality/audit_legacy_panel.py`
- `scripts/data_quality/create_legacy_sample.py`
- `data/samples/legacy_panel_sample.csv`
- `data/samples/legacy_panel_schema.csv`

Failed/handled attempt:

- Running the audit script first failed because the system Python lacked a Parquet engine.
- Fixed by adding CSV fallback to `audit_legacy_panel.py`.

Decision:

- Old uploaded folder remains untouched.
- Clean folder is the active workspace.
- Full data and model artifacts stay local/ignored; GitHub should contain code, docs, sample outputs, and reproducibility instructions.

### Smaller and Distressed Companies

User asked whether to add smaller companies to capture bankruptcies/failures.

Decision:

- Yes, but not random smaller companies.
- Use three cohorts:
  - core large-cap firms,
  - additional controls from the old extra ticker list,
  - distressed/bankrupt/near-distressed firms with SEC coverage.

Created:

- `config/distress_candidate_seed.csv`
- `config/distressed_candidates_seed.csv` existed and was later incorporated.
- `scripts/sec_fsd/index_submissions.py`
- `scripts/sec_fsd/match_distress_candidates.py`
- `scripts/sec_fsd/build_universe_v2.py`
- `config/ticker_cik_overrides.csv`
- `docs/_redundant/04_universe_expansion_history/UNIVERSE_EXPANSION_PLAN.md`

SEC ticker mapping:

- Tried to download `company_tickers_exchange.json`.
- First download returned SEC rate-limit HTML page.
- Bad response archived at `_archive/failed_downloads/company_tickers_exchange_rate_limited.html`.
- Retried with SEC-compliant User-Agent; download succeeded.

Manual overrides added:

- `HES` -> `HESS CORP`
- `K` -> `KELLANOVA`

Current universe after adding SEC ZIPs from 2009:

- 396 total rows.
- 254 core large-cap CIK rows.
- 99 additional controls included.
- 1 additional control pending (`SW`, only 7 filings).
- 42 distressed or near-distressed candidates included.

Important note:

- Old 255 ticker core collapses to 254 SEC CIK rows because `GOOG` and `GOOGL` map to the same SEC company.

### SEC ZIPs

User downloaded SEC Financial Statement Data Set ZIPs.

Current ZIP state:

- 69 ZIPs.
- Range: `2009q1.zip` through `2026q1.zip`.
- Size: about 5.6 GB.
- Inventory: 69 valid, 69 complete.
- `2009q1.zip` is tiny and mostly header-only; accepted as normal.
- SEC submission index after full range: 394,700 10-K/10-Q submissions.

Decision:

- Use SEC Financial Statement Data Sets as the main source.
- Do not parse raw EDGAR filings unless absolutely necessary.

### Research Gap Report

User uploaded `../perplexity research gap report.md` and asked for brutal assessment. It is now organized under `../_external_inputs/03_research_gap_inputs/`.

Assessment:

- Useful and directionally correct.
- Best identified gap: cross-industry, macro-regime-aware, interpretable prediction of firm success/failure.
- Too broad if followed literally.
- Mentions too many possible directions: survival analysis, SMEs, governance, digital footprints, project success factors, international comparisons.

Decision:

- Use the report for positioning, not as a full implementation plan.
- Freeze scope around SEC/FRED/U.S. public companies, temporal validation, explainable ML, dashboard.

Created:

- `docs/_redundant/02_superseded_strategy_reviews/RESEARCH_GAP_ASSESSMENT.md`

### Thesis Requirements File

User uploaded `../Final_thesis_requirements.pdf`. It is now organized under `../_external_inputs/01_original_thesis_and_requirements/`.

Actions:

- Extracted requirement text, now archived at `docs/_redundant/05_raw_extracted_inputs/final_thesis_requirements_extracted.txt`.
- Created `docs/THESIS_REQUIREMENTS_CHECKLIST.md`.

Key requirements:

- Master thesis minimum: 70 pages or 95,000 characters with spaces.
- Minimum excludes references and appendices.
- Research-format main body should include:
  - extended introduction,
  - literature review,
  - methodology,
  - results,
  - discussion and future research.
- Reference list: at least 50 sources.
- 50-60% should be academic journal articles.
- At least 33% should be foreign English-language academic journal articles.
- Must show processed empirical material.
- Must justify methods and data collection/processing.
- Must show scientific novelty and/or practical significance.

Decision:

- Treat this as a research-format thesis with a practical artifact.
- The artifact is the dashboard plus reproducible pipeline/data dictionary.

### Other SEC and International Data Ideas

User asked whether other SEC datasets or another continent, e.g. Hong Kong, should be used.

SEC dataset assessment:

- Main: SEC Financial Statement Data Sets.
- Useful optional support: SEC submissions/company facts.
- Potential but too risky now: Financial Statement and Notes, insider transactions, 13F, fails-to-deliver.
- Not useful for topic: Form D, Regulation A, crowdfunding, mutual fund datasets.

International data assessment:

- Hong Kong: not recommended as a main dataset before deadline; no equally clean SEC-like standardized bulk panel.
- Japan EDINET: best non-U.S. official option, but too risky for deadline because of API/taxonomy/language/mapping complexity.
- EU ESEF: useful conceptually but too short and mostly annual from 2020 onward.
- SEC foreign private issuers: only realistic international extension if needed, because it stays inside SEC infrastructure.

Decision:

- Do not add another continent as main empirical sample.
- Mention international/Russian data as limitation or future research unless a clean ready dataset appears immediately.

### Reinstatement Submission

User said they were creating a reinstatement submission and had told them this is improving the thesis work.

Recommendation:

- Keep same thesis topic.
- Do not present as a new thesis.
- Frame as substantial improvement of same approved topic:
  - rebuilt empirical base,
  - expanded distressed firm sample,
  - macro market-shift indicators,
  - temporal validation,
  - interpretable ML,
  - completed dashboard/repository deliverables.

### Artifact Discussion

User asked whether dashboard can be the artifact, because supervisor wanted an artifact with novelty.

Recommendation:

- Yes. Dashboard is a valid artifact if framed as an analytical decision-support tool.
- Best artifact:
  - Streamlit dashboard for monitoring firm-level resilience/distress across industries and macro regimes.
- Supporting artifacts:
  - clean dataset/data dictionary,
  - reproducible ML scoring pipeline.

Discarded:

- Complex API as primary artifact. Too much engineering for too little thesis value before deadline.

## Current Active Files

Core docs:

- `README.md`
- `docs/DATA_MANIFEST.md`
- `docs/_redundant/01_legacy_project_docs/LEGACY_DATA_AUDIT_SUMMARY.md`
- `docs/_redundant/02_superseded_strategy_reviews/RESEARCH_GAP_ASSESSMENT.md`
- `docs/_redundant/02_superseded_strategy_reviews/SUBMISSION_SPRINT_PLAN.md`
- `docs/THESIS_REQUIREMENTS_CHECKLIST.md`
- `docs/_redundant/04_universe_expansion_history/UNIVERSE_EXPANSION_PLAN.md`
- `docs/NEXT_STEPS_FOR_USER.md`
- `docs/PROJECT_CHRONICLE.md`

Core configuration and data inputs:

- `config/universe_v2_draft.csv`
- `config/company_tickers_exchange.json`
- `config/distress_candidate_seed.csv`
- `config/distressed_candidates_seed.csv`
- `config/ticker_cik_overrides.csv`
- `data/interim/sec_submissions_index.csv`
- `reports/data_quality/sec_fsd_zip_inventory.csv`
- `reports/data_quality/sec_submission_coverage_by_cik.csv`
- `reports/data_quality/distress_candidate_coverage.csv`

Core scripts:

- `scripts/sec_fsd/inventory_sec_zips.py`
- `scripts/sec_fsd/index_submissions.py`
- `scripts/sec_fsd/match_distress_candidates.py`
- `scripts/sec_fsd/build_universe_v2.py`
- `scripts/data_quality/audit_legacy_panel.py`
- `scripts/data_quality/create_legacy_sample.py`

## Discarded or Deferred Ideas

Discarded for main scope:

- Changing thesis topic.
- Making Russian companies the main empirical sample.
- Hong Kong as main empirical comparison.
- Japan EDINET as main empirical comparison.
- Raw EDGAR 10-K/10-Q filing parsing.
- Complex API before dashboard.
- Random small-company expansion.
- Random train/test split as main validation.

Deferred:

- SEC foreign private issuers.
- SEC Company Facts fallback validation.
- Insider transactions/13F/fails-to-deliver features.
- Full international comparison.
- Paid Russian data.
- API endpoint after dashboard.

Accepted:

- Same title, improved thesis.
- SEC FSD as main data.
- FRED macro/regime data.
- Expanded distress cohort.
- Temporal validation.
- Interpretable ML.
- Streamlit dashboard as artifact.
- GitHub reproducibility package with samples, not full data.

## Next Steps for Assistant

Immediate implementation sequence:

1. Build SEC FSD numeric parser for selected universe and tag map.
2. Create clean firm-quarter panel in `data/processed/panel_v2/`.
3. Add FRED macro variables and lagged regime features.
4. Define forward-looking labels:
   - `distress_next_4q`,
   - resilience/success label.
5. Run data-quality audit on the rebuilt panel.
6. Train baseline and ML models:
   - regularized logistic regression,
   - tree-based model,
   - gradient boosting if dependency setup is smooth.
7. Use temporal validation.
8. Produce thesis-ready figures:
   - dataset coverage,
   - class balance,
   - model comparison,
   - ROC/PR,
   - confusion matrix,
   - feature importance,
   - industry/regime comparison.
9. Build Streamlit dashboard.
10. Prepare GitHub-ready README and sample outputs.
11. Help write/restructure thesis text around actual outputs.

## Next Steps for User

1. Finish reinstatement submission using same-topic/improved-thesis framing.
2. Do not promise a new country/continent dataset.
3. Do not promise a complex API.
4. Keep the artifact wording stable: analytical dashboard / decision-support tool.
5. Tell the assistant if the supervisor/program requires the work to be explicitly "project format" instead of "research format"; otherwise proceed as research-format with practical artifact.
6. Provide any supervisor comments immediately when received.
7. Avoid manually moving/changing files inside `market_shifts_clean` unless coordinated.

## Current Risk Register

High risk:

- Time until 2026-05-14 is short.
- Panel parser/modeling/dashboard/writing all still need execution.
- Scope creep would kill the submission.

Medium risk:

- SEC tag mapping may need careful handling across industries and accounting concepts.
- Failure labels must be defensible and not leaky.
- Class imbalance remains important.
- References must reach 50+ and meet academic/English share requirements.

Low/manageable risk:

- Dashboard artifact is feasible.
- GitHub package is feasible.
- Data volume is sufficient.
- Topic/title fit is defensible.

## 2026-05-04 P0 Peer-Review Audit Implementation

User direction:

- User accepted the recommendation to follow the peer-review action plan.
- Priority was to make the dataset/model defensible before further dashboard polishing.

Implemented:

- Added explicit prediction timestamps to the panel:
  - `prediction_date = filed_date`;
  - `prediction_date_source`;
  - `prediction_year`;
  - `prediction_quarter`.
- Rebuilt macro and global-event context on `prediction_date`, not `period_date`.
- Rebuilt forward distress targets so an event must occur strictly after `prediction_date`.
- Added `days_from_period_to_event`, `days_to_event`, and `post_event_flag`.
- Excluded post-event rows from primary model training.
- Removed filing metadata from model features:
  - `form`;
  - `afs`.
- Added leakage/audit-only feature blacklist:
  - `config/model_feature_blacklist.csv`.
- Added P0 audit runner:
  - `scripts/data_quality/run_p0_audits.py`.
- Added saved model feature lists:
  - `reports/data_quality/model_feature_lists/distress_next_4q_features.csv`;
  - `reports/data_quality/model_feature_lists/success_resilience_next_4q_features.csv`;
  - `reports/data_quality/model_feature_lists/distress_next_4q_ablation_features.csv`.
- Updated VS Code tasks to include P0 audits.
- Updated `app/dashboard.py` to filter and sort by `prediction_date` instead of accounting `period_date`.

Rebuilt outputs:

- Panel rows: 22,713.
- Panel columns: 180.
- CIKs: 390.
- Tickers: 391.
- Period range: 2009-03-31 to 2026-02-28.
- Prediction timestamp range: 2009-04-15 to 2026-03-31.
- `prediction_date_source = filed_date` for all rows.
- `post_event_flag = 1` rows: 390.
- `distress_next_4q` positive rows in full panel: 170.
- `success_resilience_next_4q` positive rows in full panel: 9,421.

P0 audit result:

- Prediction timestamp audit: `PASS`.
- Leakage audit: `PASS`.
- Macro lag audit: `PASS`.
- Global-event timing audit: `PASS`.
- Post-event row audit: `PASS`.
- Distress event-date audit: `REVIEW`.

Reason for remaining `REVIEW`:

- `config/distress_event_dates.csv` is still an initial seed file.
- Some event dates fall before first panel observations or after last available SEC filing observations for the affected ticker.
- This is not a code blocker, but it is a thesis evidence/citation blocker.

Latest model results after stricter P0 policy:

- Main distress target: `distress_next_4q`.
- Main distress model: random forest.
- Test rows: 4,318.
- Test positives: 64.
- Test ROC-AUC: 0.869.
- Test PR-AUC: 0.112.
- Test precision: 0.165.
- Test recall: 0.250.
- Test F1: 0.199.

Distress ablation:

- Best PR-AUC remains firm-only random forest.
- Firm-only random forest ROC-AUC: 0.894.
- Firm-only random forest PR-AUC: 0.195.
- Firm-only random forest precision: 0.238.
- Firm-only random forest recall: 0.234.
- Firm-only random forest F1: 0.236.

Success/resilience result:

- Main success target: `success_resilience_next_4q`.
- Best model by PR-AUC: random forest.
- Test rows: 4,318.
- Test positives: 2,044.
- Test ROC-AUC: 0.982.
- Test PR-AUC: 0.975.
- Test precision: 0.935.
- Test recall: 0.940.
- Test F1: 0.938.

Interpretation:

- Distress metrics are lower than before because the timestamp policy is stricter and post-event rows are excluded.
- This is the correct tradeoff: lower but defensible metrics are preferable to high metrics that can be attacked as timing leakage.
- The thesis should present distress as rare-event early warning and factor discovery, not as a perfect bankruptcy predictor.
- Streamlit server was started on `http://localhost:8501`; direct shell HTTP verification was blocked by local sandbox networking, but the server reported the local URL successfully.

## 2026-05-05 Broader Target Experiments

User request:

- Revisit failure and success targets.
- Test broader targets, including a combined "three-in-one" target.
- Create a separate folder for each test, with plots, metrics, and logs.
- Run multiple tests and record results.
- Scan for inconsistencies and avoid data fabrication or artificial target inflation.
- Update project record and next steps.

Implemented:

- Added broader-target experiment runner:
  - `scripts/modeling/run_broader_target_experiments.py`.
- Created experiment results root:
  - `reports/target_experiments/`.
- Created four isolated experiment folders:
  - `reports/target_experiments/test_broader_targets1/`,
  - `reports/target_experiments/test_broader_targets2/`,
  - `reports/target_experiments/test_broader_targets3/`,
  - `reports/target_experiments/test_broader_targets4/`.
- Each folder contains:
  - `experiment_config.json`,
  - `target_profile.csv`,
  - `target_overlap.csv`,
  - `inconsistency_audit.csv`,
  - `model_metrics.csv`,
  - `test_metric_summary.csv`,
  - `feature_importance.csv`,
  - best PR/ROC plots,
  - best test predictions,
  - `run_log.md`.
- Created cross-experiment comparison:
  - `reports/target_experiments/experiment_comparison.csv`,
  - `reports/target_experiments/all_broader_target_model_metrics.csv`,
  - `reports/target_experiments/README.md`.
- Created written assessment:
  - `docs/_redundant/03_superseded_target_notes/BROADER_TARGET_EXPERIMENTS.md`.

Integrity actions:

- Post-event rows were excluded before target construction.
- Rows with fewer than three future observations were not forced to 0.
- Unknown future-financial labels were left null and removed only from the model fit for that target.
- Every experimental failure target includes strict `distress_next_4q`.
- Success targets are explicitly blocked if the same row qualifies for same-experiment failure pressure.
- No missing SEC/FRED values were forward-filled or invented.

Inconsistency scan result:

- failure/success overlap rows: 0 in all four experiments.
- post-event rows in experiment frame: 0.
- strict distress rows missed by experimental failure target: 0.
- rows with fewer than three future observations: 1,165.
- unknown failure target rows: 1,063.
- unknown success target rows: 1,165.

Key result:

- `test_broader_targets1` has the highest raw metrics but is too loose to use as the primary failure target.
- `test_broader_targets4` is the best defensible target upgrade.

Recommended broader failure target:

- `failure_pressure_conservative_next_4obs`.
- Definition: formal distress OR repeated future losses plus either balance stress, deterioration, or repeated unhealthy state.
- Best model: random forest.
- Test positives: 255.
- Test positive share: 7.8%.
- Test ROC-AUC: 0.947.
- Test PR-AUC: 0.693.
- Test precision: 0.610.
- Test recall: 0.762.
- Test F1: 0.677.

Recommended composite success target:

- `success_composite_strict_next_4obs`.
- Definition: profitability, resilience, and quality all satisfied.
- Best model by PR-AUC: gradient boosting.
- Test positives: 687.
- Test positive share: 21.4%.
- Test ROC-AUC: 0.964.
- Test PR-AUC: 0.847.
- Test precision: 0.773.
- Test recall: 0.856.
- Test F1: 0.813.

Interpretation:

- Strict `distress_next_4q` should stay as the legally clean benchmark.
- `failure_pressure_conservative_next_4obs` should be considered the main broader economic failure-pressure target.
- `success_composite_strict_next_4obs` should be considered the main three-in-one high-quality success target.
- Loose target variants are useful as sensitivity checks but should not be presented as the primary thesis target because they can be criticized as too broad.

## 2026-05-05 Second-Pass Target And Feature Tweaks

User request:

- Explore more target options thoroughly.
- Test small tweaks and document what changed.
- Evaluate whether the dataset is good enough to formulate factor conclusions.
- Revise targets and data-point usage.
- Make sure the results can feed into a much more useful final dashboard.

Implemented:

- Added second-pass experiment runner:
  - `scripts/modeling/run_target_feature_tweak_experiments.py`.
- Created results root:
  - `reports/target_tweak_experiments/`.
- Created five target-tweak folders:
  - `test_target_tweaks1`,
  - `test_target_tweaks2`,
  - `test_target_tweaks3`,
  - `test_target_tweaks4`,
  - `test_target_tweaks5`.
- Created feature-set ablation folder:
  - `reports/target_tweak_experiments/feature_set_ablation/`.
- Created written assessment:
  - `docs/_redundant/03_superseded_target_notes/TARGET_AND_FACTOR_TWEAK_ASSESSMENT.md`.
- Added compact dashboard input tables:
  - `reports/target_tweak_experiments/dashboard_best_target_rows.csv`,
  - `reports/target_tweak_experiments/dashboard_feature_set_performance.csv`,
  - `reports/target_tweak_experiments/dashboard_factor_group_best_models.csv`.
- Updated dashboard:
  - added `Target Lab` tab with target experiment summary, feature-set ablation, and factor-group importance.
- Added VS Code task:
  - `10 Target and feature tweak experiments`.

Target tweaks tested:

- `failure_pressure_conservative_v2_next_4obs`
  - small stability check on conservative failure target;
  - result effectively matched prior conservative target.
- `failure_pressure_profit_roa_next_4obs`
  - future losses plus weak ROA/operating margin and pressure signal.
- `failure_pressure_balance_liquidity_next_4obs`
  - balance-sheet and liquidity stress detector.
- `failure_pressure_sector_strict_next_4obs`
  - sector-relative strict future ROA pressure.
- `failure_pressure_score3_next_4obs`
  - component-score failure target.
- `success_resilience_quality_v2_next_4obs`
  - profitability and resilience plus quality or low-stress balance sheet.
- `success_quality_growth_next_4obs`
  - strict quality/growth success target.
- `success_stable_balance_next_4obs`
  - balance-sheet stability success target.
- `success_sector_quality_next_4obs`
  - sector-relative quality success target.
- `success_score3_next_4obs`
  - component-score success target.

Feature sets tested:

- `firm_core`: accounting + ratios + trend + sector.
- `ratios_trends_only`: financial ratios + trend + sector.
- `raw_accounting_only`: raw accounting fundamentals + sector.
- `macro_event_only`: macro, regime, event, and sector context.
- `all_features`: full feature list.

Integrity handling:

- Post-event rows stayed excluded.
- Unknown future labels stayed null.
- Failure/success overlap was blocked.
- Strict distress was captured in all broader failure targets.
- Missing fundamentals were not forward-filled or invented.

Dataset-quality conclusion:

- The dataset is good enough for factor-analysis conclusions.
- It is not equally good for all claims.
- It is strong for firm-level financial deterioration, resilience, leverage/liquidity pressure, and profitability/quality analysis.
- It is weak if the thesis tries to claim macro/event variables alone predict failure.

Best raw second-pass failure target:

- `failure_pressure_balance_liquidity_next_4obs`.
- Best model: random forest.
- Test positives: 674.
- Test positive share: 20.7%.
- Test ROC-AUC: 0.958.
- Test PR-AUC: 0.905.
- Test precision: 0.821.
- Test recall: 0.823.
- Test F1: 0.821.

Interpretation:

- This target is very learnable but narrow.
- It should be a dashboard diagnostic target, not the main thesis failure target.

Stable general broader failure target:

- `failure_pressure_conservative_next_4obs` and `failure_pressure_conservative_v2_next_4obs`.
- Test positives: 255.
- Test positive share: 7.8%.
- Best model: random forest.
- Test PR-AUC: about 0.69.
- Test F1: about 0.68.

Interpretation:

- This remains the best general economic failure-pressure candidate.
- The v2 tweak did not materially alter results, which supports target stability.

Best second-pass success target:

- `success_resilience_quality_v2_next_4obs`.
- Best model: random forest.
- Test positives: 1,224.
- Test positive share: 38.1%.
- Test ROC-AUC: 0.974.
- Test PR-AUC: 0.950.
- Test F1: 0.898.

Feature-set ablation result:

- For recommended failure targets, `firm_core` matched or slightly beat `all_features`.
- For recommended success targets, `firm_core` and `ratios_trends_only` matched or beat `all_features`.
- `raw_accounting_only` was useful but weaker.
- `macro_event_only` was weak predictively.

Implication:

- Firm-level variables are the empirical core of the thesis.
- Macro/regime/global-event variables should be used for context, comparative analysis, and dashboard filtering.
- The dashboard should show market-shift context around firm conditions, not pretend macro events alone explain firm success/failure.

Dominant factor groups:

- financial ratios;
- firm trend/deterioration;
- accounting fundamentals.

Recurring factor drivers:

- ROA;
- net income;
- prior negative-income count;
- net margin and lagged net margin;
- leverage/assets;
- equity/assets;
- total liabilities;
- lagged leverage;
- operating margin.

Revised thesis target hierarchy:

1. Strict legal distress:
   - `distress_next_4q`.
2. General economic failure pressure:
   - conservative failure-pressure target.
3. Diagnostic balance/liquidity pressure:
   - `failure_pressure_balance_liquidity_next_4obs`.
4. Main composite success:
   - `success_resilience_quality_v2_next_4obs`.
5. Strict quality/growth success:
   - `success_quality_growth_next_4obs`.

Dashboard implications:

- Add target selector for the hierarchy above.
- Add feature-set/factor group panels.
- Add sector, macro-regime, and event context filters.
- Add firm-level component views for profitability, leverage/liquidity, deterioration, and quality.
- Use macro/global events as contextual lenses, not as the core predictor.

## 2026-05-05 Missingness Indicator Audit And Target Repair

Trigger:

- The GPT-5.5 Pro audit flagged `missingindicator_total_liabilities` as suspicious because it dominated some success-target feature-importance outputs.
- The requested action was to diagnose it before removing anything.

Diagnosis:

- `missingindicator_total_liabilities` is not a raw SEC field.
- It is generated by `SimpleImputer(add_indicator=True)` inside the sklearn model pipeline.
- Raw `total_liabilities` is missing in 7,357 of 22,713 panel rows.
- A derivation attempt using `total_assets - total_equity` was not safe enough for silent filling: median absolute difference where both reported and derived values existed was about 574.8 million, with only about 25.2% close by the audit rule.
- The old `success_resilience_next_4q` target was contaminated because missing future leverage/liability values could make future `healthy_current` false, turning unknown future components into non-success labels.

Action:

- Added `scripts/data_quality/investigate_total_liabilities_missing_indicator.py`.
- Patched `scripts/sec_fsd/build_panel_v2.py` so `success_profitability_next_4q`, `success_resilience_next_4q`, and `success_quality_next_4q` are missing-aware.
- Rebuilt the panel.
- Reran P0 audits, panel integrity audit, target profiles, missingness diagnostics, model training, analysis outputs, and feature contribution summaries.

Post-fix target status:

- `success_resilience_next_4q` known rows: 14,526.
- `success_resilience_next_4q` unknown rows: 8,187.
- `success_resilience_next_4q` positive rows: 9,567.
- Rows currently `0` but missing-aware audit says unknown: 0.
- Known current/revised disagreements: 0.

Current model status:

- `distress_next_4q`: random forest, test ROC-AUC 0.869, PR-AUC 0.112, F1 0.199.
- `success_resilience_next_4q`: random forest, test ROC-AUC 0.961, PR-AUC 0.976, F1 0.937.

Interpretation decision:

- Missingness indicators may remain in predictive models after diagnosis.
- They must not be interpreted as direct economic factors.
- Final interpretation tables now separate missingness indicators from substantive feature groups:
  - `reports/modeling/final_model_feature_interpretation_table.csv`;
  - `reports/modeling/final_feature_group_contribution_table.csv`.

Topic relevance note:

- Created `docs/TOPIC_RELEVANCE_AND_SCOPE_NOTE.md`.
- The topic remains defensible if framed as SEC/FRED/global-event financial distress and resilience prediction under market shifts.
- Another country or RFSD should remain future research or optional appendix scope, not the main model.

## 2026-05-05 Rule-Based +150 Firm Expansion

User decision:

- Add 150 firms.
- Use a 50/50 structure:
  - event-review / coverage-ended firms;
  - matched controls.
- Require good SEC coverage until the relevant event or filing-history end.
- Run validation and keep the data professionally defensible.

Implementation:

- Added `scripts/sec_fsd/select_universe_expansion_150.py`.
- Created baseline backup:
  - `config/universe_v2_pre_expansion_20260505.csv`;
  - `data/processed/panel_v2_pre_expansion_20260505/`.
- Wrote candidate report:
  - `config/universe_expansion_150_candidates.csv`.
- Rebuilt the production panel from `config/universe_v2_draft.csv`.

Selection:

- 75 `expansion_event_review` firms.
- 75 `expansion_matched_controls` firms.
- All 150 additions parsed successfully.

Expanded panel:

- rows: 31,786;
- CIKs: 540;
- tickers / firm display IDs: 541.

Validation:

- P0 prediction timestamp: PASS.
- P0 leakage: PASS.
- P0 macro lag: PASS.
- P0 global event timing: PASS.
- P0 post-event rows: PASS.
- distress event dates: REVIEW.
- One invalid timestamp row was removed and saved to `reports/data_quality/invalid_prediction_timestamp_rows.csv`.

Important result:

- Strict `distress_next_4q` positives did not increase because the new event-review firms are not yet verified formal distress cases.
- Strict distress model performance dropped after expansion:
  - expanded PR-AUC 0.060;
  - expanded F1 0.098.
- Success/resilience remains strong:
  - expanded PR-AUC 0.967;
  - expanded F1 0.928.
- Broader financial-pressure targets remain useful:
  - conservative failure pressure PR-AUC 0.736, F1 0.702;
  - balance/liquidity pressure PR-AUC 0.907, F1 0.816.

Interpretation:

- The expansion is useful for the thesis if used as broader financial-pressure and resilience evidence.
- It is not yet useful as a strict formal-bankruptcy improvement claim.
- Next defensibility step is event-date verification for the event-review bucket.

## 2026-05-05 Project Vocabulary Clarification

User asked what `regime` and `prediction_date` mean in this project, and asked that the chronicle and status files be updated so the project is easier to understand.

Clarification:

- `prediction_date` is the date from which the model is allowed to make a prediction.
- In the current panel, `prediction_date = filed_date` for every row.
- `period_date` is the accounting period end date, not the date the information became public.
- Using `filed_date` as `prediction_date` prevents look-ahead leakage because a model should not know a filing before the SEC filing date.
- `prediction_date_source = filed_date` for all 31,786 rows in the current production panel.

Regime clarification:

- A regime is a macro-market environment flag derived from FRED data.
- It is not a raw SEC company field and not a target.
- Examples include high-rate regime, market-stress regime, yield-curve inversion regime, inflation-pressure regime, oil-shock regime, strong-dollar regime, demand-slowdown regime, credit-tightening regime, and crisis regime.
- Regime indicators make "market shifts" operational and interpretable.
- They are most useful for sector comparison, dashboard filters, and thesis discussion.
- Current model evidence still says firm fundamentals, ratios, and deterioration features carry the strongest predictive signal.

Panel/split clarification:

- The core panel should stay one factual dataset with identifiers, SEC fundamentals, ratios, trends, macro variables, regime indicators, global-event context, industry metadata, targets, and audit fields.
- Train/validation/test split should be derived by modeling scripts from `prediction_date`, not stored as a permanent factual column in the panel.
- Current modeling split policy is train through 2018, validation 2019-2021, and test 2022-2024.

Documentation updated:

- Created `docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md`.
- Updated `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md` with current panel counts and time-field definitions.
- Updated `docs/CURRENT_STATUS.md` with current +150 expansion counts, current model results, and the glossary section.
- Updated `docs/DATA_MANIFEST.md` with the current reference-doc roles.
- Updated `docs/TARGET_DEFINITIONS_FINAL_REVIEW.md`, `docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md`, `docs/TOPIC_RELEVANCE_AND_SCOPE_NOTE.md`, `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md`, `docs/MISSINGNESS_INDICATOR_POLICY.md`, `docs/NEXT_STEPS_FOR_USER.md`, and `docs/VS_CODE_WORKFLOW.md` where current counts or field guidance were stale.

Current production panel snapshot after this clarification:

- rows: 31,786;
- columns: 180;
- SEC CIKs: 540;
- tickers / firm display IDs: 541;
- period range: 2009-03-31 to 2026-02-28;
- prediction timestamp range: 2009-04-15 to 2026-03-31;
- strict `distress_next_4q` positives: 207 after the later source-verified event-date update.

## 2026-05-05 Strategic Next Steps Review Assessed

User uploaded a GPT-5.5 Pro extended-thinking review in JSON format:

```text
/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/strategic_next_steps_20260505.json
```

Task:

- read the review thoroughly;
- assess whether it is completely right;
- identify mistakes or misleading claims;
- decide next steps;
- update documentation, logs, status, and next-step files.

Assessment result:

- The review is mostly right and should be accepted as the strategic direction.
- The main recommendation is correct: freeze scope, verify event dates, finalize a target hierarchy, refine dashboard, and write from saved reports.
- The numeric claims matched the local reports and panel at that checkpoint, before later target promotion:
  - panel: 31,786 rows, 180 columns, 540 CIKs, 541 ticker/display IDs;
  - `prediction_date_source = filed_date` for all rows;
  - strict `distress_next_4q`: best expanded-panel model gradient boosting, test PR-AUC about 0.060, F1 about 0.098;
  - `success_resilience_next_4q`: best expanded-panel model random forest, test PR-AUC about 0.967, F1 about 0.928;
  - `failure_pressure_conservative_v2_next_4obs`: experiment PR-AUC about 0.736, F1 about 0.702;
  - `failure_pressure_balance_liquidity_next_4obs`: experiment PR-AUC about 0.907, F1 about 0.816.

Corrections and guardrails:

- Broader pressure targets are currently experiment outputs, not production panel columns.
- Event-review firms are not automatically distress firms.
- Some event-review names in the external review, such as Activision Blizzard, VMware, Pioneer Natural Resources, Hawaiian Holdings, and Six Flags Entertainment, should be treated as classification checks, not presumed formal distress.
- The current workspace is not a Git repository, so a "git commit" is conditional; local backup/snapshot or later GitHub repo setup is needed instead.
- The review's grade estimate is subjective and should not be treated as evidence.

Documents created:

- `docs/_redundant/02_superseded_strategy_reviews/STRATEGIC_NEXT_STEPS_20260505_REVIEW.md`
- `docs/FINAL_SCOPE_LOCK_NOTE.md`
- `docs/FINAL_TARGET_HIERARCHY.md`

Documents updated:

- `docs/CURRENT_STATUS.md`
- `docs/NEXT_STEPS_FOR_USER.md`
- `docs/DATA_MANIFEST.md`
- `reports/RUN_STATUS_FINAL.md`
- `docs/PROJECT_CHRONICLE.md`

Strategic decision:

- The main scope is locked.
- No RFSD, Hong Kong, Japan, paid data, NLP, or live event feed will be added to the main model before submission.
- Strict legal distress remains the clean benchmark.
- Broader financial pressure is the main failure-factor direction if productionized or clearly labeled as experiment output.
- `success_resilience_next_4q` remains the production success/resilience target for now.
- Event-date verification is the next P0 task.

Next priority order:

1. Verify formal distress event dates.
2. Classify event-review expansion firms into formal distress, near distress, M&A/transaction, normal exit, missing evidence, or exclude.
3. Decide whether to productionize final broader targets.
4. If anything is productionized or event dates change, rerun the full audit/model/report chain.
5. Refine dashboard and capture screenshots.
6. Write the thesis from the chronicle, final reports, figures, and dashboard artifact.

## 2026-05-05 Final Decision Plan Accepted And Implemented Conservatively

User uploaded the final decision plan produced after discussion with the strategist, GPT-5.5 Pro, and DeepSeek:

```text
/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/final_codex_decision_plan_20260505_1.json
```

Task:

- move in that direction;
- keep the work controlled and production-safe;
- update project documentation.

Accepted direction:

- make a controlled final production pass, not a broad expansion;
- keep strict `distress_next_4q` as the clean legal-distress benchmark;
- verify event-review firms before adding strict distress positives;
- promote at most one broader failure-pressure target only if clean and audited;
- build a market-health index from existing macro/regime/global-event data;
- keep market-price data as an optional separate audit branch;
- defer CHS/Merton and other heavier market-risk modeling unless a simple market-data branch first passes mapping, coverage, and leakage checks.

Implementation completed without mutating the production panel:

- created final decision-plan note, now archived at `docs/_redundant/02_superseded_strategy_reviews/FINAL_DECISION_PLAN_20260505.md`;
- created `docs/DISTRESS_EVENT_DATE_PROVENANCE.md`;
- created `docs/MARKET_HEALTH_INDEX_NOTE.md`;
- created `scripts/data_quality/create_event_review_scaffold.py`;
- created `scripts/features/build_market_health_index.py`;
- generated `reports/data_quality/final_distress_event_date_audit.csv`;
- generated `reports/data_quality/event_review_firm_classification_scaffold.csv`;
- generated `reports/data_quality/event_review_scaffold_summary.csv`;
- generated `reports/data_quality/market_health_index_audit.csv`;
- generated `reports/modeling/market_health_index_by_prediction_date.csv`;
- generated `reports/modeling/market_health_by_year_regime_sector.csv`;
- generated `reports/figures/modeling/market_health_index_timeseries.png`.

Initial event-review result before production merge:

- 75 event-review expansion firms remain separated from production labels.
- 8 source-verified formal distress candidates were identified for a production decision.
- 11 likely merger/transaction candidates were flagged as do-not-label unless contrary source evidence is found.
- 0 unverified formal distress candidates are being treated as usable strict labels.

Source-verified formal distress candidates currently scaffolded:

- Rite Aid, 2023-10-15;
- SunPower, 2024-08-05;
- Acorda Therapeutics, 2024-04-01;
- Pennsylvania Real Estate Investment Trust, 2023-12-10;
- Conn's, 2024-07-23;
- Ebix, 2023-12-17;
- Vertex Energy, 2024-09-24;
- Unit Corp, 2020-05-22.

Market-health result:

- 3,319 date-level market-health rows were created.
- 18 audit rows record the component inputs and alignment policy.
- The index uses prediction-date-aligned macro/event fields only.
- The index is a dashboard/context layer, not a bankruptcy target and not a causal proof.

Initial production guardrail before the source-verified merge:

- no event dates were added to `config/distress_event_dates.csv`;
- no production panel file was edited;
- no broader target was promoted;
- no market-price features were merged.

Next decision:

- decide whether to add the eight source-verified formal distress candidates to `config/distress_event_dates.csv`.

If yes:

1. update the config;
2. rebuild the panel;
3. rerun P0 audits;
4. rerun target profiles;
5. rerun strict distress and success/resilience models;
6. regenerate final interpretation tables and dashboard inputs;
7. update documentation again.

## 2026-05-05 Source-Verified Event-Date Merge And Full Rerun

After reading the final decision plan more carefully, the next controlled production change was made:

- the plan requires explicit approval for broader target promotion;
- it allows formal distress events to enter the strict target once source-supported;
- the user had asked to move in this direction.

Action:

- added eight source-verified event-review formal distress events to `config/distress_event_dates.csv`;
- rebuilt the production panel and GitHub dataset copies with `scripts/sec_fsd/build_panel_v2.py`;
- reran P0 audits;
- reran panel integrity audit;
- reran target profiles;
- retrained `distress_next_4q` and `success_resilience_next_4q`;
- reran strict-distress ablation;
- regenerated analysis outputs, feature contribution tables, market-health outputs, event-review scaffolds, broader target experiments, and target-tweak experiments.

Eight events added:

- Rite Aid, 2023-10-15;
- SunPower, 2024-08-05;
- Acorda Therapeutics, 2024-04-01;
- Pennsylvania Real Estate Investment Trust, 2023-12-10;
- Conn's, 2024-07-23;
- Ebix, 2023-12-17;
- Vertex Energy, 2024-09-24;
- Unit Corp, 2020-05-22.

Updated production panel:

- rows: 31,786;
- columns: 180;
- SEC CIKs: 540;
- tickers / firm display IDs: 541;
- strict `distress_next_4q` positives: 207.

P0 status:

- prediction timestamp: PASS;
- leakage: PASS;
- macro lag: PASS;
- global event timing: PASS;
- post-event rows: PASS;
- distress event dates: REVIEW.

Reason event-date status remains REVIEW:

- 42 older `initial_seed` event rows still need source provenance;
- several source-verified events occur after the last available pre-event SEC filing, which is normal for delisted or bankrupt firms but still flagged for review by the audit.

Updated strict legal distress model:

- target: `distress_next_4q`;
- best model by PR-AUC: gradient boosting;
- test rows: 5,885;
- test positives: 96;
- ROC-AUC: 0.752;
- PR-AUC: 0.068;
- precision: 0.064;
- recall: 0.375;
- F1: 0.109.

Updated success model:

- target: `success_resilience_next_4q`;
- best model: random forest;
- test rows: 4,047;
- test positives: 2,475;
- ROC-AUC: 0.958;
- PR-AUC: 0.966;
- precision: 0.907;
- recall: 0.944;
- F1: 0.925.

Updated broader target evidence:

- `failure_pressure_conservative_v2_next_4obs`: PR-AUC 0.739, F1 0.705.
- `failure_pressure_balance_liquidity_next_4obs`: PR-AUC 0.906, F1 0.813.
- `success_resilience_quality_v2_next_4obs`: PR-AUC 0.929, F1 0.875.

Interpretation:

- source verification improved strict event coverage and raised strict test positives from 64 to 96;
- strict legal distress remains rare and should stay the benchmark, not the headline performance claim;
- `failure_pressure_conservative_v2_next_4obs` remains the best defensible main broader failure-pressure candidate;
- `failure_pressure_balance_liquidity_next_4obs` remains a strong diagnostic target but is too narrow for the main failure definition;
- productionizing the broader target was the next decision point at that moment and was completed later on 2026-05-05.

## 2026-05-05 Broader Failure-Pressure Target Promotion, Dashboard Refresh, And Bibliography

User direction:

- move in the accepted final-decision-plan direction;
- perform next steps, validate, and report what changed;
- review the whole project and create a professionally curated bibliography for thesis references.

Decision made:

- promote one broader target only;
- choose `failure_pressure_conservative_v2_next_4obs` as the main production broader failure-pressure target;
- keep strict `distress_next_4q` as the clean legal benchmark;
- keep `success_resilience_next_4q` as the production success/resilience target;
- keep balance/liquidity pressure and composite success targets as robustness/diagnostic outputs for now.

Code changes:

- added production target construction in `scripts/sec_fsd/build_panel_v2.py`;
- inserted the broader target before forward success targets are created;
- added `failure_pressure_conservative_v2_next_4obs` to target-profile and feature-contribution scripts;
- added the target to `config/model_feature_blacklist.csv`;
- updated `app/dashboard.py` so the dashboard exposes strict distress, broader failure pressure, and success/resilience as separate target views.

Validation and rerun:

- rebuilt production panel and GitHub-ready copies;
- reran P0 audits: prediction timestamp PASS, leakage PASS, macro lag PASS, global event timing PASS, post-event rows PASS, distress event dates REVIEW;
- reran panel integrity audit;
- reran target profile reports;
- retrained three production target models;
- reran strict ablation;
- regenerated analysis outputs, feature contribution summaries, market-health outputs, and event-review scaffolds;
- compiled the dashboard successfully.

Production panel after promotion:

- rows: 31,786;
- columns: 181;
- SEC CIKs: 540;
- tickers / display IDs: 541.

Target status after promotion:

- `distress_next_4q`: 31,786 known rows, 207 positives overall, 96 test positives.
- `failure_pressure_conservative_v2_next_4obs`: 29,886 known rows, 1,900 unknown rows, 2,957 positives overall, 599 test positives.
- `success_resilience_next_4q`: 20,169 known rows, 11,617 unknown rows, 12,073 positives overall, 2,475 test positives.

Model results after promotion:

- `distress_next_4q`: best current model gradient boosting, test ROC-AUC 0.752, PR-AUC 0.068, F1 0.109.
- `failure_pressure_conservative_v2_next_4obs`: best current model by PR-AUC/F1 random forest, test ROC-AUC 0.942, PR-AUC 0.740, F1 0.689.
- `success_resilience_next_4q`: best current model random forest, test ROC-AUC 0.958, PR-AUC 0.966, F1 0.925.

Bibliography work:

- created `docs/BIBLIOGRAPHY.md`;
- created `docs/references.bib`;
- verified key citations through web sources and official pages where relevant;
- organized references by thesis use: core distress literature, business analytics/design-science artifact framing, ML/evaluation, explainability, missingness/data integrity, official SEC/FRED data sources, event-data context, and optional market-based default extensions.

Interpretation:

- the thesis now has a cleaner target hierarchy: legal distress as benchmark, broader financial pressure as main failure-factor target, and success/resilience as the positive outcome;
- strict bankruptcy-style prediction remains weak because the event is rare and only source-verified formal distress should enter it;
- the broader target materially improves learnability while staying economically defensible;
- the dashboard is now better aligned with the thesis claim because it does not over-center legal bankruptcy.

## 2026-05-05 Dashboard Firm Explorer Refinement

User feedback:

- the per-ticker dashboard view was still messy;
- Apple and similar long-history firms showed too many metrics together;
- raw metrics with different scales should not be forced onto one shared chart;
- macro context was too limited because only a few fixed variables were visible;
- M2 money supply, oil prices, and other macro variables should be selectable in a clean way.

Action:

- kept the existing Streamlit dashboard and refined `app/dashboard.py`;
- replaced hard-coded firm-ratio and macro charts with grouped selectors and chart modes;
- added firm metric groups for profitability, balance/liquidity, revenue/scale, trend signals, targets, and all numeric fields;
- added macro groups for rates/credit, money/inflation, labor/demand, markets/commodities, regime flags, global events, and all macro/regime/event fields;
- added three chart modes:
  - separate raw scales for honest metric-specific interpretation;
  - one raw metric for focused inspection;
  - standardized comparison for overlaying differently scaled metrics;
- added firm-vs-macro comparison where a selected firm metric is compared against selected macro/regime/event variables;
- included M2 money supply and oil-price variables in the macro selector workflow;
- moved the raw recent observations into a separate Firm Explorer tab with a narrower default column set.

Validation:

- `python3 -m py_compile app/dashboard.py` passed;
- Streamlit restarted on port 8501;
- local HTTP smoke test returned 200.

## 2026-05-05 Dashboard Metric Semantics And Standardization Correction

User feedback:

- standardized comparison of ROA/ROI-like firm variables against M2 money supply needs a professional method;
- target labels should not appear inside firm financial metric groups;
- `All Numeric` was too broad because it included broad distress labels and calendar fields;
- accounts receivable needed clearer classification;
- the panel contains many more usable financial columns than the small initial dashboard selector exposed.

Action:

- removed targets from firm metric groups and moved them to a separate `Target Timeline` tab;
- replaced `All Numeric` with `All Financial Metrics`;
- expanded selectable firm financial metrics to 62 current financial fields:
  - 30 SEC accounting fundamentals;
  - 11 financial ratios;
  - 21 trend/deterioration features;
- classified accounts receivable as working capital/liquidity;
- added explicit standardization baselines:
  - selected firm window;
  - filtered panel/date baseline;
  - 2009-2018 training-period baseline;
- implemented date-level macro/regime/event standardization for panel-wide baselines so duplicate firm rows do not overweight macro dates.

Interpretation:

- standardized dashboard overlays are now visual z-scores, not raw financial magnitudes;
- the training-period baseline is the most methodologically conservative option for thesis screenshots because it does not use validation/test-period information to set the reference scale;
- raw-scale views remain available for metric-specific interpretation.

Validation:

- `python3 -m py_compile app/dashboard.py` passed;
- local HTTP smoke test returned 200.

## 2026-05-07 Final Caveat-Resolution And SEC Provenance Polish

User direction:

- implement the remaining perfection priorities:
  - distress-event caveat handling;
  - SEC mapping provenance;
  - duplicate/amendment policy;
  - GitHub reproducibility freeze;
  - dashboard thesis-story polish;
  - model interpretation stability;
  - writing discipline.

Action:

- created `scripts/sec_fsd/build_sec_selected_fact_provenance.py`;
- scanned raw SEC FSD ZIPs from `data/raw/sec_fsd_zips/`;
- generated row-level selected-fact provenance:
  - `reports/data_quality/sec_selected_fact_provenance.parquet`;
  - `reports/data_quality/sec_selected_fact_provenance.csv.gz`;
  - `reports/data_quality/sec_selected_fact_provenance_summary.csv`;
  - `reports/data_quality/sec_selected_fact_method_summary.csv`;
  - `reports/data_quality/sec_selected_fact_panel_validation.csv`;
  - `reports/data_quality/sec_selected_fact_panel_validation_review_rows.csv`;
- created `scripts/project_audit/final_polish_caveat_package.py`;
- generated:
  - `reports/data_quality/distress_event_final_policy.csv`;
  - `reports/data_quality/duplicate_amendment_deterministic_policy.csv`;
  - `reports/data_quality/duplicate_ticker_period_prediction_detail.csv`;
  - `reports/reproducibility/freeze_manifest_20260507.csv`;
  - `reports/reproducibility/github_release_file_list_20260507.csv`;
  - `reports/modeling/model_interpretation_stability_summary.csv`;
  - `reports/modeling/model_interpretation_top_groups_by_target_model.csv`;
  - `reports/dashboard/dashboard_polish_checklist.csv`;
  - `docs/FINAL_CAVEAT_RESOLUTION_REGISTER.md`;
  - `docs/REPRODUCIBILITY_FREEZE_20260507.md`;
  - `docs/DASHBOARD_THESIS_STORYBOARD.md`;
  - `docs/MODEL_INTERPRETATION_STABILITY_NOTE.md`;
- updated `app/dashboard.py` Artifact Notes tab with thesis story and caveat controls;
- refreshed dashboard screenshots under `reports/figures/dashboard/`;
- updated `docs/SEC_CONCEPT_MAPPING_AUDIT.md`, `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md`, `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`, and `docs/CURRENT_STATUS.md`.

Validation:

- selected SEC fact provenance rows: 661,533;
- panel-matched selected facts: 661,509;
- selected-value mismatches above tolerance: 0;
- missing panel values for selected facts: 24, all documented as belonging to one invalid timestamp row excluded from the production panel;
- `python3 -m py_compile scripts/sec_fsd/build_sec_selected_fact_provenance.py scripts/project_audit/final_polish_caveat_package.py app/dashboard.py` passed.

Interpretation:

- SEC mapping is now more defensible because every selected accounting fact can be traced back to a selected SEC tag, qtrs value, unit, source ZIP, and direct/derived method;
- the production panel was not manually edited;
- strict distress dates remain caveated where source verification is not complete;
- duplicate/amendment handling now has a deterministic future rebuild policy;
- the project is closer to upload-ready, but the actual GitHub commit/upload and final thesis text still remain.

## 2026-05-06 Full Project Audit Restart And Review

User direction:

- restart the interrupted full project overview/audit;
- audit every file as far as practical;
- expose downsides, weaknesses, hidden risks, missing pieces, recommendations, and next steps.

Action:

- verified the existing machine-readable audit outputs under `reports/project_audit/`;
- confirmed the full review report at `reports/project_audit/FULL_PROJECT_REVIEW_20260506.md`;
- checked core panel metadata, model-output consistency, feature-blacklist results, dependency imports, P0 audit status, and README/package-facing documentation;
- corrected the root README expansion section so it no longer reports the older 254 + 99 + 42 universe state;
- added the full audit report to current source-of-truth/status files.

Validation:

- files inventoried: 2,718;
- workspace size: 5.715 GB;
- Python compile checks: 40 PASS;
- JSON/notebook parse checks: 27 PASS;
- CSV quick checks: 1,215 PASS;
- Parquet checks: 961 PASS;
- SEC ZIP checks: 69 PASS;
- model-output consistency checks: 3 PASS;
- feature-blacklist checks: 4 PASS;
- required-config checks: 6 PASS;
- dependency imports: required packages available;
- core panel: 31,786 rows, 181 columns, 540 CIKs, 541 ticker/display IDs, no infinite numeric values;
- P0 audits: all PASS except distress event dates remain REVIEW.

Interpretation:

- the project is technically viable for the thesis, but the main risks are still claim discipline rather than file corruption;
- strict legal distress must stay a rare-event benchmark with provenance caveats;
- broader failure pressure and success/resilience remain the main factor-analysis outcomes;
- remaining practical work is dashboard screenshots, event-date provenance, amendment-duplicate handling decision, doc-reference cleanup, GitHub packaging, and thesis writing.

## 2026-05-06 Review Of The Project Review

User direction:

- perform a review of the review itself.

Finding:

- the full project review was mostly accurate and useful;
- its main weakness was not a major factual contradiction, but possible overconfidence in what automated PASS checks prove;
- CSV checks are sample parse checks, SEC ZIP checks are member-presence checks, dependency checks are local-environment checks, and model-output consistency checks compare saved outputs rather than proving clean-machine retraining reproducibility;
- the GitHub panel equality claim needed clarification because the audit CSV recorded shape equality, not content equality.

Action:

- added `reports/project_audit/REVIEW_OF_FULL_PROJECT_REVIEW_20260506.md`;
- patched `reports/project_audit/FULL_PROJECT_REVIEW_20260506.md` with an `Audit Method Limitations` section;
- clarified that a separate post-audit check confirmed the core and GitHub panel copies have identical shapes, columns, and content in the current workspace.

Interpretation:

- the review is fit for strategist/supervisor handoff after the limitations patch;
- the final thesis should still avoid overclaiming strict legal distress prediction, complete event coverage, or fresh-machine reproducibility before packaging is tested.

## 2026-05-07 Final Scientific-Validity QA Sprint

User direction:

- read `final_scientific_validity_qa_codex_plan_20260506.json`;
- act on the plan;
- prepare the project for the next task after completion.

Action:

- added final QA runner `scripts/project_audit/final_scientific_validity_qa.py`;
- added clean virtualenv smoke checker `scripts/project_audit/clean_venv_smoke_check.py`;
- added dashboard screenshot runner `scripts/project_audit/capture_dashboard_screenshots.py`;
- created pre-QA snapshot outputs:
  - `reports/project_audit/pre_qa_snapshot_manifest.csv`;
  - `reports/project_audit/pre_qa_model_snapshot.csv`;
- updated distress-event provenance:
  - `docs/DISTRESS_EVENT_DATE_PROVENANCE.md`;
  - `reports/data_quality/final_distress_event_date_audit.csv`;
  - `reports/data_quality/event_date_scientific_validity_summary.csv`;
- audited amendment/duplicate handling without editing the production panel:
  - `docs/AMENDMENT_DUPLICATE_HANDLING_NOTE.md`;
  - `reports/data_quality/amendment_duplicate_audit.csv`;
  - `reports/data_quality/amendment_duplicate_summary.csv`;
  - `reports/data_quality/dropped_duplicate_filing_rows.csv`;
- audited SEC concept mapping and accounting sanity:
  - `docs/SEC_CONCEPT_MAPPING_AUDIT.md`;
  - `reports/data_quality/sec_concept_mapping_summary.csv`;
  - `reports/data_quality/sec_concept_coverage_by_year_form_sector.csv`;
  - `reports/data_quality/accounting_identity_sanity_summary.csv`;
  - `reports/data_quality/extreme_accounting_outlier_review.csv`;
- created scientific-validity and claim-control docs:
  - `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`;
  - `reports/project_audit/scientific_validity_summary.csv`;
  - `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`;
- ran package reproducibility checks:
  - local processed-panel smoke test passed;
  - temporary clean virtualenv install and smoke check passed with zero failures;
  - outputs at `reports/project_audit/package_smoke_test_report.md`, `reports/project_audit/package_smoke_test_results.csv`, and `reports/project_audit/clean_venv_smoke_test_results.csv`;
- cleaned documentation-reference audit:
  - `reports/project_audit/doc_reference_audit_clean.csv` has zero actionable rows;
  - `reports/project_audit/doc_reference_todo.md` says no actionable missing local references remain after filtering;
- captured nine dashboard screenshots under `reports/figures/dashboard/`;
- created appendix evidence index:
  - `reports/final_thesis_appendix_pack/README.md`;
- updated README, current status, final source-of-truth index, run status, and full project review.

Validation:

- final scientific-validity QA runner compiled and completed;
- dashboard screenshot runner compiled and completed through Playwright/Chromium;
- package smoke test: 14 PASS rows;
- clean virtualenv smoke test: 0 FAIL rows;
- core and GitHub panels remain content-equal;
- full audit after QA: 2,759 files, 43 Python files compiled PASS, 1,232 CSV quick checks PASS, 961 Parquet checks PASS, 69 ZIP checks PASS.

Interpretation:

- structural readiness is now supported by a scientific-validity layer;
- strict distress event dates remain `REVIEW`, with 36 initial-seed formal rows still caveated and eight source-verified formal rows;
- no production panel data were manually edited;
- duplicate/amendment rows are audited and should be disclosed unless a deterministic rebuild is approved;
- dashboard evidence exists, but the screenshot report records non-blocking chart-library warnings;
- GitHub/version-freeze packaging remains the main non-writing deliverable.

## 2026-05-06 Model Tuning And AutoGluon Decision

User concern:

- one or two model runs might not be enough for a professional thesis;
- AutoGluon and other model families might have many useful parameters;
- the machine-learning work should look thorough and defensible.

Action:

- added controlled tuning script:
  - `scripts/modeling/run_model_tuning_experiments.py`;
- ran tuning for the three production targets:
  - `distress_next_4q`;
  - `failure_pressure_conservative_v2_next_4obs`;
  - `success_resilience_next_4q`;
- wrote outputs under:
  - `reports/model_tuning/`;
- created interpretation note:
  - `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`.

Protocol:

- same production panel as the main models;
- train through 2018;
- validation 2019-2021;
- test 2022-2024;
- candidate selection uses validation data only;
- thresholds selected on validation F1;
- test metrics observed only after validation selection;
- production model files were not overwritten.

Experiment scale:

- 35 candidate configurations per target;
- 105 candidate configurations across all three production targets;
- 315 split-metric rows in `reports/model_tuning/all_candidate_metrics.csv`;
- no candidate failures.

Candidate families tested:

- logistic regression;
- random forest;
- extra trees;
- gradient boosting;
- histogram gradient boosting.

Results:

- `distress_next_4q`: validation-selected `extra_trees_cfg3_seed777`, test PR-AUC 0.073 and F1 0.159. This improves F1 versus the production benchmark but does not solve the rare strict-distress problem.
- `failure_pressure_conservative_v2_next_4obs`: validation-selected `hist_gradient_boosting_cfg1`, test PR-AUC 0.747 and F1 0.694. This slightly improves the production random forest and supports the broader failure-pressure target.
- `success_resilience_next_4q`: validation-selected `gradient_boosting_cfg3_seed202`, test PR-AUC 0.960 and F1 0.919. The production random forest remains stronger, so tuning confirms robustness rather than replacing the success model.

AutoGluon decision:

- AutoGluon was not installed in the current environment;
- XGBoost and LightGBM were not installed at the time of the first controlled scikit-learn tuning pass;
- AutoGluon should not be claimed as part of the thesis unless deliberately installed, rerun, validated, and documented;
- safest thesis wording is controlled scikit-learn tuning and robustness checks under temporal validation.

## 2026-05-06 XGBoost And LightGBM Advanced Benchmark

User direction:

- install and try multiple runs on XGBoost and LightGBM;
- treat package dependencies as manageable because users can install them.

Action:

- installed Python packages:
  - `xgboost==3.2.0`;
  - `lightgbm==4.6.0`;
- installed macOS OpenMP runtime:
  - `brew install libomp`;
- added packages to `requirements.txt`;
- added advanced benchmark runner:
  - `scripts/modeling/run_advanced_boosting_experiments.py`;
- added VS Code task:
  - `12 Advanced boosting benchmarks`;
- wrote outputs under:
  - `reports/model_tuning_advanced/`.

Protocol:

- same production panel as the main models;
- train through 2018;
- validation 2019-2021;
- test 2022-2024;
- candidate selection uses validation data only;
- thresholds selected on validation F1;
- imbalance handled with train-split `scale_pos_weight`;
- production model files were not overwritten.

Experiment scale:

- 24 candidate configurations per target;
- 72 candidate configurations across all three production targets;
- 216 split-metric rows in `reports/model_tuning_advanced/all_candidate_metrics.csv`;
- no candidate failures.

Results:

- `distress_next_4q`: validation-selected `xgboost_cfg1_seed42`, test PR-AUC 0.088 and F1 0.140. This improves PR-AUC versus production and scikit-learn tuning, but not F1 versus the extra-trees tuned model.
- `failure_pressure_conservative_v2_next_4obs`: validation-selected `lightgbm_cfg3_seed42`, test PR-AUC 0.760 and F1 0.686. This is the best PR-AUC so far for the main failure-pressure target, but not the best F1.
- `success_resilience_next_4q`: validation-selected `xgboost_cfg4_seed777`, test PR-AUC 0.962 and F1 0.919. The production random forest remains stronger.

Interpretation:

- advanced boosting is useful as a robustness benchmark;
- XGBoost/LightGBM improve ranking for strict distress and broader failure pressure;
- advanced boosting does not replace the current success/resilience headline model;
- thesis wording should say advanced boosted-tree benchmarks, not AutoML or exhaustive search.

## 2026-05-06 Document Organization Pass

User request:

- organize the documents;
- move redundant documents into a redundant folder;
- use category folders so the project is easier to understand.

Action:

- created current document map:
  - `docs/DOCUMENT_ORGANIZATION.md`;
- created redundant archive manifest:
  - `docs/_redundant/README.md`;
- moved superseded clean-workspace documents into:
  - `docs/_redundant/01_legacy_project_docs/`;
  - `docs/_redundant/02_superseded_strategy_reviews/`;
  - `docs/_redundant/03_superseded_target_notes/`;
  - `docs/_redundant/04_universe_expansion_history/`;
  - `docs/_redundant/05_raw_extracted_inputs/`;
- moved Finder metadata files into:
  - `docs/_redundant/00_system_junk/`;
- organized user-uploaded root-level external inputs into:
  - `../_external_inputs/01_original_thesis_and_requirements/`;
  - `../_external_inputs/02_ai_reviews_and_strategy_plans/`;
  - `../_external_inputs/03_research_gap_inputs/`;
  - `../_external_inputs/00_system_junk/`.

Validation:

- current top-level `docs/` now has 31 active document files;
- `docs/_redundant/` contains 21 archived files;
- `../_external_inputs/` contains 18 external input files;
- `.vscode/tasks.json` still validates as JSON;
- source-of-truth, workflow, manifest, current-status, and run-status files were updated to point to the new organization.

Interpretation:

- nothing thesis-relevant was deleted;
- current writing should start from `docs/DOCUMENT_ORGANIZATION.md` or `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`;
- archived files remain available for reasoning history but should not be treated as current project status.

## 2026-05-06 Reference Critical Evaluation Layer

User direction:

- make sure all literature sources can be described, critiqued, and evaluated;
- explicitly label anything unknown or inaccessible.

Action:

- extended `scripts/docs/generate_literature_package.py`;
- created `docs/REFERENCE_CRITICAL_EVALUATION.md`;
- created `reports/literature/reference_critical_evaluation.csv`;
- added per-source fields:
  - short description of what the source says;
  - critique or limitation;
  - evaluation for this thesis;
  - evidence role;
  - safe thesis use;
  - do-not-use-for warning;
  - accessibility status;
  - peer-review status;
  - metadata verification status;
  - unknown or inaccessible flag.

Validation:

- critical-evaluation rows: 67;
- critical-evaluation columns: 14;
- sources with clear public/official/open-page access flag: 11;
- sources with unknown or access-limited notes: 56;
- sources evaluated on verified metadata/source-summary level with full text not assumed: 55;
- sources evaluated on public/official page level: 12;
- generator compiles with `python3 -m py_compile`.

Interpretation:

- all 67 sources are now described, critiqued, and evaluated;
- verified metadata is not treated as full-text access;
- paywalled or not-locally-checked full text is labeled as unknown/access-limited rather than silently assumed;
- official reports and data docs are labeled as useful for data and context but not as peer-reviewed theory.

## 2026-05-06 Mandatory Literature Review Sprint

User direction:

- proceed with the strategist's final polish and literature plan;
- make the literature truthful about what the papers/books actually say;
- include newer literature, not only classic 1960s-1980s economic and bankruptcy-prediction papers;
- perform deep research and continue along the plan.

Action:

- created a reproducible literature-package generator at `scripts/docs/generate_literature_package.py`;
- expanded the bibliography from a starter set into a verified 67-reference thesis package;
- kept the classical sources because they are foundational, but added recent 2020-2025 material in bankruptcy prediction, ML surveys, post-pandemic bankruptcy risk, explainable AI, official data context, and resilience theory;
- created `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md` so the final writing phase has one source-of-truth map;
- created `docs/LITERATURE_SEARCH_STRATEGY.md`;
- created `docs/LITERATURE_MATRIX.md` and `reports/literature/literature_matrix.csv`;
- created `docs/BIBLIOGRAPHY_AUDIT.md` and `reports/literature/reference_quality_audit.csv`;
- created `reports/literature/source_to_claim_map.csv`;
- created `reports/literature/research_gap_synthesis.csv`;
- regenerated `docs/BIBLIOGRAPHY.md` and `docs/references.bib`;
- corrected first-pass metadata after web verification for several recent sources, including Dasilas and Rigani (2024), Zhao et al. (2024), Billios et al. (2024), Bragoli et al. (2022), Charalambous et al. (2022), Zhang et al. (2022), and Valaskova et al. (2023);
- created writing scaffolds:
  - `docs/LITERATURE_REVIEW_OUTLINE.md`,
  - `docs/LITERATURE_REVIEW_DRAFT.md`,
  - `docs/INTRODUCTION_RESEARCH_GAP_DRAFT.md`,
  - `docs/THESIS_THEORETICAL_POSITIONING.md`.

Validation:

- literature matrix rows: 67;
- required literature matrix columns: 17/17 present;
- BibTeX entries: 67;
- BibTeX brace balance: passed;
- academic journal articles: 51;
- peer-reviewed sources: 56;
- sources from 2020 onward: 21;
- verified DOI/official/publisher/report links: 67/67;
- required bucket coverage passed:
  - classical distress/failure prediction: 11;
  - firm fundamentals/ratios/deterioration: 7;
  - macro/credit/market-shift context: 6;
  - ML/rare-event/evaluation/temporal validation: 15;
  - interpretability/XAI: 7;
  - missing data and data integrity: 4;
  - design science/dashboard/decision support: 5;
  - strategic management/resilience framing: 6;
  - official data and context: 6.

Interpretation:

- the literature package now supports the thesis without pretending the field is new;
- the safest novelty claim is the integrated artifact: audited SEC/FRED/global-event panel, filing-date prediction timestamps, target hierarchy, temporal validation, interpretable factors, and dashboard decision support;
- the writing must keep market-based default models, broad resilience theory, macro/credit context, and official reports in their proper roles;
- the literature review draft is evidence-heavy but still needs to be adapted into the final thesis voice and university formatting.

## 2026-05-05 Overview Outcome Composition Correction

User feedback:

- the Overview chart showed success share around 0.6, failure pressure around 0.1, and strict distress around 0.01;
- those values did not add up, making it unclear where the remaining rows went;
- the labels `known success labels` and related cards were confusing;
- the user asked whether the remaining rows are mediocre/surviving and whether that category should be added.

Finding:

- the old Overview chart mixed different denominators;
- success share was positive success among rows with a known success target;
- failure-pressure share was positive pressure among rows with a known pressure target;
- strict distress share used all rows because strict distress is always labeled 0/1;
- the three plotted lines were independent target rates, not a mutually exclusive classification.

Default 2009-2024 count check:

- total selected rows: 29,511;
- success/resilience: 11,687 rows;
- broader pressure without legal distress: 2,708 rows;
- strict legal distress: 207 rows;
- neutral/surviving, meaning known non-success and known non-pressure: 5,521 rows;
- unknown future horizon: 9,388 rows.

Action:

- added a dashboard-only mutually exclusive outcome category;
- added an `Outcome Composition by Year` chart;
- added `Target Coverage by Year`;
- renamed target-label metric cards to target-observed cards;
- added visible cards for neutral/surviving and unknown future horizon.

Interpretation:

- the neutral/surviving category is real and useful, but it is not the same as success;
- unknown horizon rows should not be forced into success/failure/neutral because that would invent labels where future observations are insufficient;
- the dashboard can now show both the thesis targets and the mutually exclusive state taxonomy separately.

Validation:

- `python3 -m py_compile app/dashboard.py` passed;
- local HTTP smoke test returned 200.

## 2026-05-07 Manual High-Risk Audit

User request:

- manually audit the higher-risk items rather than relying only on generated PASS tables.

Action:

- created `docs/MANUAL_HIGH_RISK_AUDIT_20260507.md`;
- manually inspected distress event policy, duplicate/amended filing detail, SEC selected-fact provenance, outlier rows, model leakage reports, and source-of-truth docs;
- checked external sources for a sample of distress events, including BBBY, SIVB, SI, AAMRQ, HTZ, CHK, and CIT.

Critical finding:

- the selected SEC fact provenance table proves panel reproducibility but revealed a deeper economic alignment issue;
- selected facts can come from prior-year comparative `ddate` values inside the filing because the current selector does not require `ddate == period`;
- examples found manually:
  - AAPL FY2022 10-K `total_revenue = -7.942B` because a `2020-09-30` revenue fact was used inside the 2022 filing and differenced against a 2022 cumulative value;
  - BKR 2017 Q2 `total_assets = 0` from a `2016-12-31` assets fact rather than the 2017 Q2 period;
- targeted counts showed 367,743 of 661,533 selected facts have `ddate != period`, and 31,697 of 31,720 accession IDs have at least one selected fact with this issue.

Decision:

- do not treat the current accounting-feature models, success/failure-pressure targets, dashboard values, or GitHub dataset as final thesis evidence until the SEC selector is rebuilt with current-period filtering and all downstream artifacts are regenerated;
- retain the distress event caveat policy;
- duplicate/amendment risk remains secondary and should be handled deterministically during rebuild.

## 2026-05-07 SEC Period-Alignment Selector Fix

User direction:

- begin the required next step: fix SEC period alignment before rebuilding the empirical chain.

Action:

- patched `scripts/sec_fsd/build_panel_v2.py`;
- added a shared current-period filter requiring selected SEC facts to satisfy `ddate == period`;
- patched `scripts/sec_fsd/build_sec_selected_fact_provenance.py` so the provenance sidecar mirrors the panel selector;
- added `ddate_period_aligned` to selected-fact provenance output;
- ran syntax checks on both patched scripts.

Targeted validation:

- AAPL FY2022 now selects the current-period 2022 annual revenue fact and derives Q4 revenue from 2022 cumulative values instead of mixing in a 2020 comparative fact;
- BKR 2017 Q2 still has a current-period zero-assets raw SEC fact in the targeted check, so it remains an outlier-review item after the full rebuild.

Decision:

- the code-level selector fix is implemented;
- at that moment, the production panel had not yet been rebuilt;
- at that moment, current panel/model/dashboard/GitHub artifacts remained draft until the full rebuild, provenance regeneration, numeric audit, target rebuild, model rerun, dashboard refresh, and GitHub package refresh were completed.

## 2026-05-07 Period-Aligned Firm Panel Rebuild

User direction:

- continue to step 2 and rebuild `firm_panel_v2` from the patched selector.

Action:

- ran `python3 scripts/sec_fsd/build_panel_v2.py`;
- regenerated `data/processed/panel_v2/firm_panel_v2.csv.gz`;
- regenerated `data/processed/panel_v2/firm_panel_v2.parquet`;
- regenerated `data/github/firm_panel_v2.csv.gz`;
- regenerated `data/github/firm_panel_v2.parquet`;
- regenerated `data/github/firm_panel_v2_schema.csv`;
- regenerated sample panel/schema outputs under `data/samples/`.

Rebuilt panel status:

- rows: 31,783;
- columns: 181;
- SEC CIKs: 540;
- ticker/display IDs: 541;
- period range: 2009-03-31 to 2026-02-28;
- prediction range: 2009-04-15 to 2026-03-31;
- `prediction_date_source = filed_date` for all 31,783 rows;
- processed and GitHub Parquet copies have identical columns and content.

Target counts after rebuild:

- `distress_next_4q`: 31,783 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,883 known rows, 3,011 positives, 1,900 missing;
- `success_resilience_next_4q`: 20,160 known rows, 12,525 positives, 11,623 missing.

Targeted checks:

- AAPL FY2022 `total_revenue` is now about 90.146B for the annual filing row, replacing the old impossible negative value caused by prior-year comparative mixing;
- negative `total_revenue` rows fell from 249 to 18;
- non-positive `total_assets` rows fell from 3 to 2;
- BKR 2017 Q2 and VICI 2017 Q3 remain non-positive-asset outliers for post-rebuild review;
- infinite numeric values: 0.

Decision:

- step 2 is complete;
- the rebuilt panel is structurally usable for the next audit step;
- saved provenance sidecar, audit reports, model outputs, feature interpretation, dashboard screenshots, and freeze manifests still need regeneration from the rebuilt panel before final thesis claims.

## 2026-05-07 Post-Rebuild Provenance, Audit, Modeling, And Dashboard Rerun

User direction:

- execute the remaining post-rebuild chain:
  - rebuild selected-fact provenance and verify `ddate != period` collapses to zero or documented exceptions;
  - recheck AAPL FY2022, BKR 2017 Q2, negative revenue rows, non-positive assets, missingness, and accounting sanity;
  - rebuild/refresh target profiles;
  - rerun temporal models for the three final targets;
  - rerun feature-group interpretation;
  - refresh dashboard data and screenshots.

Actions:

- ran `python3 scripts/sec_fsd/build_sec_selected_fact_provenance.py`;
- reran P0 audits with `scripts/data_quality/run_p0_audits.py`;
- reran panel integrity reports with `scripts/data_quality/audit_panel_integrity.py`;
- reran target profiles with `scripts/modeling/target_profile_report.py`;
- retrained baseline temporal models for:
  - `distress_next_4q`;
  - `failure_pressure_conservative_v2_next_4obs`;
  - `success_resilience_next_4q`;
- reran feature contribution summaries with `scripts/modeling/feature_contribution_summary.py`;
- reran controlled tuning with `scripts/modeling/run_model_tuning_experiments.py`;
- reran XGBoost/LightGBM robustness with `scripts/modeling/run_advanced_boosting_experiments.py`;
- refreshed dashboard screenshots with `scripts/project_audit/capture_dashboard_screenshots.py`;
- reran `scripts/project_audit/final_scientific_validity_qa.py`;
- reran `scripts/project_audit/full_project_audit.py`;
- updated the source-of-truth documentation files so they no longer describe post-rebuild model/provenance/dashboard outputs as stale.

Selected-fact provenance result:

- selected fact rows: 660,989;
- selected rows with `ddate != period`: 0;
- `ddate_period_aligned = True` for all selected rows;
- panel value mismatches above tolerance: 0;
- selected facts missing from production-panel comparison: 24 documented exclusions.

Spot checks:

- AAPL FY2022 `total_revenue` provenance now uses period `20220930`, `ddate = 20220930`, source ZIP `2022q4`, and derives Q4 revenue as about 90.146B using `derived_from_cumulative_qtrs_4_minus_3`;
- BKR 2017 Q2 remains a current-period zero-assets/zero-revenue SEC fact, so it is a real outlier-review case rather than the old period-alignment defect.

P0 and integrity status:

- prediction timestamp: PASS;
- leakage: PASS;
- macro lag: PASS;
- global event timing: PASS;
- post-event rows: PASS;
- distress event dates: REVIEW;
- infinite numeric values: 0;
- average missingness remains material in SEC accounting fundamentals, financial ratios, firm trends, and event metadata.

Baseline temporal model results:

- `distress_next_4q`: best baseline random forest, test rows 5,885, test positives 96, ROC-AUC 0.830, PR-AUC 0.105, F1 0.150;
- `failure_pressure_conservative_v2_next_4obs`: best baseline random forest, test rows 5,747, test positives 575, ROC-AUC 0.950, PR-AUC 0.759, F1 0.730;
- `success_resilience_next_4q`: best baseline random forest, test rows 4,047, test positives 2,648, ROC-AUC 0.966, PR-AUC 0.973, F1 0.941.

Controlled tuning result:

- 35 candidate configurations per final target, 105 total, no candidate failures;
- `distress_next_4q`: validation-selected `random_forest_cfg2_seed42`, test PR-AUC 0.170, F1 0.178;
- `failure_pressure_conservative_v2_next_4obs`: validation-selected `hist_gradient_boosting_cfg1`, test PR-AUC 0.745, F1 0.724;
- `success_resilience_next_4q`: validation-selected `random_forest_cfg1_seed42`, test PR-AUC 0.973, F1 0.940.

XGBoost/LightGBM robustness result:

- 24 candidate configurations per final target, 72 total, no candidate failures;
- `distress_next_4q`: validation-selected `xgboost_cfg1_seed777`, test PR-AUC 0.131, F1 0.197;
- `failure_pressure_conservative_v2_next_4obs`: validation-selected `lightgbm_cfg3_seed777`, test PR-AUC 0.745, F1 0.712;
- `success_resilience_next_4q`: validation-selected `lightgbm_cfg3_seed202`, test PR-AUC 0.974, F1 0.933.

Dashboard status:

- screenshots refreshed under `reports/figures/dashboard/`;
- all requested screenshot views passed capture;
- capture report records non-blocking Vega/Altair warnings about empty/infinite chart extents, so dashboard evidence is thesis-usable but still caveated as `PASS_WITH_CAVEATS`.

Decision:

- the SEC period-alignment caveat is resolved for selected production facts;
- strict distress remains a rare-event benchmark; formal event-date provenance is now resolved for the current package, but the target is still not a complete legal-bankruptcy database;
- `failure_pressure_conservative_v2_next_4obs` remains the main failure-factor target;
- `success_resilience_next_4q` remains the main success/resilience counterpart;
- model results are now post-rebuild results and can be used in thesis writing with the stated caveats;
- no new data sources should be added before submission.

## 2026-05-08 Interruption Recovery And Status Reconciliation

User returned after a suspected interruption and asked whether something had been interrupted overnight.

Audit check:

- recent artifacts from 2026-05-07 were present, including rebuilt panel exports, model artifacts, dashboard screenshots, source-verification outputs, P0 audit outputs, package audit outputs, and updated documentation;
- process-list inspection was blocked by macOS sandbox permissions, so live background processes could not be verified through `ps`;
- `reports/data_quality/p0_audit_status.csv` showed all P0 audits as PASS, including `distress_event_dates`;
- `reports/data_quality/event_date_scientific_validity_summary.csv` showed 44 formal distress rows as VERIFIED and 6 near-distress rows as REVIEW_NON_STRICT context only;
- `reports/data_quality/distress_event_source_verification_summary_20260507.md` showed 44 formal source records written and 0 formal `initial_seed` rows remaining.

Found contradiction:

- `docs/CURRENT_STATUS.md` and the consolidated caveat audit reflected resolved formal event-date provenance;
- `reports/RUN_STATUS_FINAL.md` and `reports/project_audit/scientific_validity_summary.csv` still carried stale `strict distress event dates = REVIEW` language.

Action:

- updated `reports/RUN_STATUS_FINAL.md` so the current audit status says `distress event dates: PASS`;
- updated the event-review scaffold summary in `reports/RUN_STATUS_FINAL.md` from 8 to 44 source-verified formal distress cases in config;
- updated the current scientific-validity summary from `strict distress event dates: REVIEW` to `PASS`;
- updated `reports/project_audit/scientific_validity_summary.csv` to match the final event-date source-provenance state;
- updated one stale validation bullet in `docs/CURRENT_STATUS.md`.

Current interpretation:

- formal strict-distress event-date provenance is resolved for the current package;
- near-distress rows remain non-strict context only;
- strict distress is still a rare-event benchmark, but the remaining caveat is now target rarity and legal-scope completeness, not missing source provenance for the current formal event rows;
- remaining data-integrity review items are accounting sign/outlier rows, duplicate/amended-filing policy disclosure, material missingness, and dashboard chart warnings.

## 2026-05-08 Full Manual Logic/UI/Backend Audit

User direction:

- run a full audit;
- manually inspect important firm-panel rows by hand-picking a few hundred rows;
- hand-check model logic and code;
- audit dashboard logic, UI, and backend behavior thoroughly.

Actions:

- created `scripts/project_audit/manual_logic_dashboard_audit_20260508.py`;
- generated a fixed manual-review sample of 415 rows at `reports/project_audit/manual_panel_row_audit_sample_20260508.csv`;
- sampled distress positives, broader failure-pressure positives, success/resilience positives, neutral/surviving rows, unknown future horizons, outliers, duplicate rows, global-event rows, stress-regime rows, temporal-test-window rows, and anchor tickers;
- recomputed accounting ratios, lag/trend features, SEC selected-fact alignment, production target logic, model feature-list guardrails, temporal split boundaries, saved model metrics, and dashboard field coverage;
- reran `scripts/project_audit/full_project_audit.py`;
- started the Streamlit dashboard on `http://localhost:8501`;
- used browser checks for Overview, Firm Explorer, Macro Compare, desktop viewport, and mobile viewport.

Important findings:

- P0 timing/leakage/event audits remain PASS;
- selected SEC facts remain current-period aligned in the provenance sidecar;
- model feature lists have no blacklist/target-metadata overlap;
- temporal splits remain train <= 2018, validation 2019-2021, test 2022-2024 with no key overlap;
- the dashboard exposes 62/62 usable financial fields and 68/68 chartable macro/regime/event fields;
- the dashboard renders without a fatal Streamlit error or framework overlay.

Historical high-risk finding before the later alias-collapse rebuild:

- `CIK 1004980` appears twice as `PCG` and `PGNPQ`;
- both ticker/display IDs duplicate the same SEC filings;
- `PGNPQ` carries formal 2019 distress labels while the corresponding `PCG` rows do not;
- this created contradictory target labels for identical firm-period financial features around PG&E's 2019 distress event;
- this became the highest-priority scientific-integrity fix before the later alias-collapse rebuild resolved it.

Other caveats:

- formula recomputation mismatches are small but reveal that `clean_extremes` runs after ratio/trend construction, so some lag features preserve pre-cleaning extreme values;
- one failure-pressure target recomputation mismatch is explained by the duplicated `PCG`/`PGNPQ` CIK sequence;
- rendered dashboard emits repeated non-fatal Vega/Altair "Infinite extent" warnings;
- Firm Explorer metric cards truncate long sector/cohort labels;
- at that point, `global_event_names` was present in the data but not yet surfaced as readable text context in the dashboard.

Decision:

- do not treat the current panel as final-frozen until the `PCG`/`PGNPQ` duplicate-CIK issue is either fixed by rebuild or explicitly disclosed;
- recommended next technical step is to collapse same-CIK ticker/display aliases deterministically, keep the formal distress metadata, rebuild the downstream chain, and refresh models, dashboard, and screenshots;
- no new external data source is needed for this fix.

## 2026-05-08 Step 1 Scientific Data-Construction Fix

User direction:

- proceed with step 1 of the next steps;
- treat the work as a high-grade ML/economics/scientific data-construction fix.

Actions:

- updated `scripts/sec_fsd/build_panel_v2.py` so the universe is deduplicated by SEC CIK before parsing;
- preserved duplicate ticker/display aliases through `ticker_aliases` and `event_lookup_tickers`;
- kept `PCG` as the primary display identity for `CIK 1004980` and preserved `PGNPQ` as event provenance;
- updated target construction so distress events can be matched through ticker aliases rather than only the primary display ticker;
- added a rebuild-time audit output at `reports/data_quality/duplicate_cik_alias_resolution.csv`;
- added `ticker_aliases`, `event_lookup_tickers`, `duplicate_cik_alias_count`, and `event_source_ticker` to the model blacklist;
- moved derived-feature cleaning to run after ratios, after trend construction, and again after target construction;
- added rebuild-time cleanup audit outputs named `reports/data_quality/derived_feature_extreme_cleanup_post_ratio_pre_trend.csv`, `reports/data_quality/derived_feature_extreme_cleanup_post_trend_pre_target.csv`, and `reports/data_quality/derived_feature_extreme_cleanup_final.csv`;
- updated schema classification so alias and event-source columns are metadata rather than model features.

Validation:

- `scripts/sec_fsd/build_panel_v2.py` passed `python3 -m py_compile`;
- `scripts/modeling/train_panel_v2_models.py` passed `python3 -m py_compile`;
- post-collapse universe validation returned 540 rows, 540 unique CIKs, and 0 duplicated CIK rows;
- `CIK 1004980` now resolves to `ticker = PCG`, `ticker_aliases = PCG;PGNPQ`, and `event_lookup_tickers = PCG;PGNPQ`;
- targeted target-logic validation on the single `PCG` history attaches the `PGNPQ` source-verified 2019 bankruptcy event to the collapsed CIK history, yielding 67 rows, 5 strict `distress_next_4q` positives, and 29 post-event rows;
- synthetic validation confirmed that an extreme ratio cleaned before trend construction does not leak into lagged ratio features.

Current limitation:

- this section recorded the code-level fix before production rebuild;
- the next section records the completed step-2 rebuild and audit rerun.

## 2026-05-08 Step 2 Rebuild And Audit Rerun

User direction:

- proceed to step 2 after the scientific data-construction fix.

Actions:

- rebuilt `firm_panel_v2` from `scripts/sec_fsd/build_panel_v2.py`;
- regenerated processed and GitHub panel exports;
- regenerated selected SEC fact provenance with `scripts/sec_fsd/build_sec_selected_fact_provenance.py`;
- reran target profile reports;
- reran P0 audits;
- reran panel integrity audit;
- reran data-integrity caveat audit;
- patched `scripts/data_quality/run_p0_audits.py` so distress-event audit coverage matches event rows through `event_lookup_tickers`, not only primary display tickers.

Rebuilt panel:

- 31,716 rows;
- 185 columns;
- 540 CIKs;
- 540 ticker/display IDs;
- 0 duplicated CIK/submission rows;
- processed and GitHub panel copies match exactly.

Target counts:

- `distress_next_4q`: 31,716 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,819 known rows, 3,007 positives, 1,897 missing;
- `success_resilience_next_4q`: 20,160 known rows, 12,525 positives, 11,556 missing.

Audit results:

- P0 audits are all PASS;
- selected SEC fact provenance has 660,989 selected facts;
- selected facts with `ddate != period`: 0;
- selected-value mismatches above tolerance: 0;
- documented panel-comparison exclusions: 24;
- numeric infinities: 0;
- accounting sign/outlier sanity remains REVIEW, with 18 negative revenue rows and 2 non-positive asset rows preserved for review;
- duplicate amended/same-date filing issue remains REVIEW, with 30 rows across 15 groups under the existing deterministic disclosure policy.

PCG/PGNPQ result:

- the rebuilt production panel keeps a single `PCG` history for `CIK 1004980`;
- `PGNPQ` is retained as alias/event-source metadata;
- the source-verified 2019 bankruptcy event is attached to the single CIK history;
- the previous duplicate-CIK row inflation is removed.

Next technical step:

- rerun temporal models, feature-group interpretation, dashboard outputs, screenshots, and full project audit on the rebuilt panel.

## 2026-05-08 Rebuilt Production Panel Audit And Target Missingness Check

User direction:

- audit the rebuilt production panel before proceeding to step 3 model reruns;
- explain what missing target counts mean.

Actions:

- reran P0 timing/leakage/event audits;
- reran the panel integrity audit;
- corrected the consolidated caveat audit script so it uses post-alias-collapse expected dimensions and target counts rather than pre-rebuild constants;
- wrote the refreshed caveat audit to `reports/data_quality/data_integrity_caveat_audit_20260508.csv`;
- wrote focused target-missingness reports:
  - `reports/data_quality/target_missingness_summary_20260508.csv`;
  - `reports/data_quality/failure_pressure_missingness_reasons_20260508.csv`;
  - `reports/data_quality/success_resilience_missingness_reasons_20260508.csv`;
  - `reports/data_quality/success_resilience_missingness_component_detail_20260508.csv`;
  - `reports/data_quality/rebuilt_panel_quick_integrity_20260508.csv`.

Audit result:

- production panel shape remains 31,716 rows and 185 columns;
- processed and GitHub panel copies match exactly;
- 540 CIKs and 540 ticker/display IDs;
- prediction date equals filed date for all rows;
- no infinite numeric values;
- P0 audits all PASS;
- selected SEC fact provenance remains PASS with 660,989 selected facts, zero `ddate != period` selected rows, zero selected-value mismatches, and 24 documented exclusions;
- remaining REVIEW items are 18 negative revenue rows, 2 non-positive total-asset rows, and 30 same-ticker/period/prediction amended-filing rows across 15 groups.

Target-missingness result:

- `distress_next_4q`: 31,716 known rows, 207 positives, 0 missing;
- `failure_pressure_conservative_v2_next_4obs`: 29,819 known rows, 3,007 positives, 1,897 missing;
- failure-pressure missing rows consist of 1,488 rows with fewer than three future filing observations plus 409 post-event rows excluded from primary prediction;
- `success_resilience_next_4q`: 20,160 known rows, 12,525 positives, 11,556 missing;
- success/resilience missing rows consist of 1,620 rows with fewer than three future filing observations plus 9,936 rows with future filings but fewer than three future rows where net income, ROA, and leverage/assets are all available;
- the dominant component behind success/resilience target missingness is missing future `total_liabilities` / `leverage_assets` coverage.

Interpretation:

- missing target labels mean "unknown / not safely labelable for this target", not failure and not success;
- rows with missing labels should be excluded for that specific target's supervised model;
- raw feature nulls remain preserved in the panel and are imputed only inside modeling pipelines;
- keeping unknown target labels as null is scientifically safer than converting missing future information into negative labels.

## 2026-05-08 Step 3 Post-Rebuild Modeling And Interpretation Rerun

User direction:

- proceed to step 3 after the rebuilt panel audit;
- rerun modeling and interpretation on the corrected production panel.

Actions:

- reran baseline temporal models for:
  - `distress_next_4q`;
  - `failure_pressure_conservative_v2_next_4obs`;
  - `success_resilience_next_4q`;
- reran target profile reports;
- reran feature-contribution and feature-group interpretation summaries;
- reran descriptive sector, regime, year, cohort, and global-event analysis outputs;
- reran strict-distress feature-set ablation;
- reran controlled sklearn tuning for 35 candidate configurations per production target;
- reran XGBoost and LightGBM robustness benchmarks for 24 candidate configurations per production target;
- regenerated post-rebuild summary tables:
  - `reports/modeling/post_rebuild_model_summary_20260508.csv`;
  - `reports/modeling/post_rebuild_best_model_by_metric_20260508.csv`;
  - `reports/modeling/model_interpretation_stability_summary.csv`;
  - `reports/modeling/model_interpretation_top_groups_by_target_model.csv`;
- reran P0 audits and the consolidated caveat audit after model feature-list regeneration.

Validation:

- P0 audits all PASS after model reruns;
- model feature leakage guardrail PASS;
- sklearn tuning candidate-failure files are header-only;
- XGBoost/LightGBM candidate-failure files are header-only;
- script syntax checks passed for the touched modeling scripts.

Current model results:

- strict legal distress remains a rare-event benchmark:
  - baseline random forest test PR-AUC 0.157, F1 0.147;
  - validation-selected XGBoost gives the best threshold F1 at 0.241, but with lower PR-AUC 0.121;
- broader failure pressure remains the main failure-factor target:
  - baseline random forest test ROC-AUC 0.955, PR-AUC 0.764, F1 0.731;
  - sklearn and advanced boosted-tree robustness runs remain strong but do not beat the baseline random forest on the main held-out metrics;
- success/resilience remains strong and stable:
  - baseline random forest test ROC-AUC 0.966, PR-AUC 0.973, F1 0.942;
  - LightGBM has slightly higher PR-AUC at 0.974 but lower F1 at 0.938.

Current interpretation:

- economic feature-group interpretation is refreshed from the rebuilt panel;
- strict distress is driven mainly by accounting fundamentals, deterioration trends, financial ratios, and macro conditions;
- failure pressure is driven mainly by accounting fundamentals, macro conditions, deterioration trends, financial ratios, and sector context;
- success/resilience is driven mainly by financial ratios, accounting fundamentals, deterioration trends, and sector context;
- missingness indicators remain excluded from economic-factor interpretation.

Remaining after step 3:

- dashboard screenshots and rendered UI/project audit were the next required artifact step;
- continue thesis writing from current source-of-truth docs and refreshed post-rebuild model outputs;
- do not add new data sources before submission unless the thesis scope is deliberately reopened.

## 2026-05-08 Step 4 Dashboard Artifact Refresh

User direction:

- if the Step-3 modeling/interpretation rerun is verified, proceed to Step 4.

Actions:

- treated Step 4 as the dashboard/artifact refresh after the corrected production panel and post-rebuild model outputs;
- patched `app/dashboard.py` so chart helpers drop non-finite values and show an explanatory message when the current selection has no chartable numeric observations;
- added readable global-event context in Firm Explorer so `global_event_names` is not only hidden in raw rows and is not treated as a numeric macro chart field;
- changed Firm Explorer default ticker to `AAPL` when available;
- changed sector/cohort and overview prediction-window display away from cramped metric widgets;
- patched `scripts/project_audit/capture_dashboard_screenshots.py` to use a taller screenshot viewport and capture the Macro Compare chart with the standardized comparison visible;
- reran the static/manual dashboard audit and refreshed `reports/project_audit/FULL_MANUAL_LOGIC_UI_BACKEND_AUDIT_20260508.md`;
- refreshed `reports/project_audit/manual_dashboard_rendered_audit_20260508.csv`;
- regenerated the nine dashboard screenshots under `reports/figures/dashboard/`;
- performed an in-browser rendered interaction check against `http://127.0.0.1:8501/`.

Validation:

- dashboard static/backend coverage: PASS;
- financial dashboard coverage: 62/62 usable financial fields;
- macro/regime/event dashboard coverage: 68/68 chartable fields;
- readable `global_event_names` context: PASS;
- rendered app page identity: PASS;
- app blank-page/framework-overlay check: PASS;
- Firm Explorer interaction: PASS, AAPL visible by default;
- Macro Compare interaction: PASS, training-period baseline visible;
- browser error-level logs: 0 app errors;
- screenshot capture: all nine requested screenshots PASS.

Remaining artifact caveat:

- the screenshot capture report still records non-fatal Streamlit/Vega chart-library warnings, including infinite-extent warnings from chart rendering in hidden/secondary tab states. These are not browser app errors and should be disclosed as dashboard warning caveats rather than scientific validity failures.

## 2026-05-09 SEC Concept-Mapping Polish

User direction:

- try to perfect the SEC mapping, using internet/official sources if needed.

Reasoning:

- "Perfect" SEC mapping is not scientifically possible because SEC FSD values are as-filed XBRL facts and tag use varies by firm, year, sector, and filer practice.
- The realistic professional goal is a conservative, auditable concept map with row-level provenance, current-period filtering, and explicit caveats.
- Official SEC FSD documentation supports this framing: the data are as filed, flattened from XBRL submissions, updated by quarter, and not guaranteed by the SEC to be error-free.

Actions:

- reviewed official SEC Financial Statement Data Sets documentation;
- scanned local SEC FSD ZIPs for high-coverage unmapped candidate tags;
- patched `config/sec_fsd_concept_map.csv`;
- expanded debt mappings:
  - `LongTermDebtNoncurrent`;
  - `LongTermDebtAndCapitalLeaseObligations`;
  - `DebtCurrent`;
  - `LongTermDebtCurrent`;
  - `LongTermDebtAndCapitalLeaseObligationsCurrent`;
- added `LiabilitiesNoncurrent` as a separate `noncurrent_liabilities` field;
- expanded receivables with `ReceivablesNetCurrent` and `AccountsReceivableNet`;
- expanded R&D with `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost`;
- added `RevenueFromContractWithCustomerIncludingAssessedTax` as a low-priority revenue fallback;
- deliberately did not map `LiabilitiesAndStockholdersEquity` to total liabilities;
- deliberately did not silently derive `total_liabilities = total_assets - total_equity`;
- added `long_term_debt` and `short_term_debt` to the production model feature list after coverage became usable;
- patched SEC/data-quality audit scripts to include the new field and maintain current-period fact filtering;
- regenerated the panel, GitHub panel copies, schema, SEC selected-fact provenance, P0 audits, caveat audits, target profiles, baseline models, controlled tuning, advanced boosting, ablation, descriptive outputs, feature-group interpretation, master explainer, and source-of-truth docs.

Validation:

- production panel now has 31,717 rows, 186 columns, 540 CIKs, and 540 ticker/display IDs;
- processed and GitHub panel copies match exactly;
- selected SEC facts: 700,844;
- selected facts with `ddate != period`: 0;
- selected-value mismatches above tolerance: 0;
- documented panel-comparison exclusions: 25;
- P0 audits: all PASS;
- numeric infinities: 0.

Coverage effect:

- `long_term_debt` missingness improved to 27.1%;
- `short_term_debt` missingness improved to 39.0%;
- `accounts_receivable` missingness improved to 24.8%;
- `r_and_d_expense` missingness improved to 73.0%;
- `total_revenue` missingness improved to 10.6%.

Post-polish model results:

- strict legal distress remains a rare-event benchmark:
  - baseline random forest test PR-AUC 0.125, F1 0.148;
  - validation-selected ExtraTrees test PR-AUC 0.154, F1 0.230;
  - advanced XGBoost test PR-AUC 0.143, F1 0.229;
- broader failure pressure remains the main failure-factor target:
  - baseline random forest test PR-AUC 0.758, F1 0.725;
  - validation-selected HistGradientBoosting test PR-AUC 0.744, F1 0.705;
  - advanced LightGBM test PR-AUC 0.744, F1 0.723;
- success/resilience remains strong and stable:
  - baseline random forest test PR-AUC 0.975, F1 0.938;
  - validation-selected random forest test PR-AUC 0.974, F1 0.937;
  - advanced XGBoost test PR-AUC 0.974, F1 0.938.

New documentation:

- `docs/SEC_MAPPING_POLISH_20260509.md`.

Thesis implication:

- The thesis can now say SEC mapping was refined through a documented, source-aware, post-audit improvement pass.
- It must still not claim perfect cross-firm taxonomy harmonization or causal certainty.

## 2026-05-10 Validated Secondary Target Promotion

User direction:

- make the four additional validated targets part of the production panel, with validation/calibration/audits if needed.
- clarify that `PROJECT_CHRONICLE.md` should not be deleted, but may be appended/updated as the historical project log.

Actions:

- promoted four validated secondary target labels into the production panel:
  - `industry_relative_resilience_next_4obs`;
  - `stress_resilience_next_4obs`;
  - `recovery_next_4obs`;
  - `quality_success_cashflow_next_4obs`;
- added `scripts/modeling/promote_validated_secondary_targets.py` as the controlled post-build promotion step;
- refreshed processed and GitHub-ready panel copies plus schema/sample outputs;
- updated schema classification so the four promoted labels are `target_label` columns;
- added the promoted target labels, diagnostic target, and robustness-extension labels to `config/model_feature_blacklist.csv`;
- reran calibration/ranking via `scripts/modeling/run_validation_extension_gate.py`;
- reran baseline temporal model reports for the four promoted secondary targets;
- reran target profiles, P0 audits, project audit, final scientific-validity QA, Target Lab outputs, and robustness-extension target audit;
- refreshed source-of-truth and package-facing docs to use the new 31,702 x 190 production panel state.

Current production panel after promotion:

- rows: 31,702;
- columns: 190;
- SEC CIKs: 540;
- ticker/display IDs: 540;
- processed and GitHub panel copies match exactly;
- `prediction_date = filed_date` for every row.

Promoted secondary target counts:

- `industry_relative_resilience_next_4obs`: 20,039 known rows, 8,093 positives, 11,663 missing;
- `stress_resilience_next_4obs`: 5,901 known rows, 3,707 positives, 25,801 missing;
- `recovery_next_4obs`: 11,375 known rows, 5,578 positives, 20,327 missing;
- `quality_success_cashflow_next_4obs`: 16,767 known rows, 9,852 positives, 14,935 missing.

Validation/calibration status:

- selected calibrators use validation-period isotonic calibration;
- `industry_relative_resilience_next_4obs`: calibrated test PR-AUC 0.844, Brier 0.127, ECE 0.030;
- `stress_resilience_next_4obs`: calibrated test PR-AUC 0.969, Brier 0.061, ECE 0.019;
- `recovery_next_4obs`: calibrated test PR-AUC 0.968, Brier 0.065, ECE 0.019;
- `quality_success_cashflow_next_4obs`: calibrated test PR-AUC 0.949, Brier 0.078, ECE 0.036.

Baseline temporal model status:

- `industry_relative_resilience_next_4obs`: best baseline gradient boosting, test PR-AUC 0.855, F1 0.787;
- `stress_resilience_next_4obs`: best baseline random forest, test PR-AUC 0.974, F1 0.937;
- `recovery_next_4obs`: best baseline random forest, test PR-AUC 0.977, F1 0.915;
- `quality_success_cashflow_next_4obs`: best baseline gradient boosting, test PR-AUC 0.953, F1 0.920.

Audit status:

- P0 audits: PASS;
- validated secondary target promotion audit: PASS;
- model-output consistency audit: PASS for all seven production model targets;
- feature blacklist audit: PASS, with no target-label overlap in model feature lists;
- project core-panel audit: PASS, 31,702 rows and 190 columns;
- scientific-validity QA: PASS/PASS_WITH_CAVEATS only, no blocking failure;
- robustness-extension target audit: PASS, with robustness labels still outside production.

Final target hierarchy after promotion:

- primary production targets:
  - `distress_next_4q`;
  - `failure_pressure_conservative_v2_next_4obs`;
  - `success_resilience_next_4q`;
- validated secondary production outcomes:
  - `industry_relative_resilience_next_4obs`;
  - `stress_resilience_next_4obs`;
  - `recovery_next_4obs`;
  - `quality_success_cashflow_next_4obs`;
- diagnostic only:
  - `deterioration_next_4obs`;
- robustness-extension only:
  - `sector_relative_improvement_next_4obs`;
  - `persistent_resilience_next_6obs`.

Thesis implication:

- The thesis can now use the four promoted targets as production-panel secondary outcomes for dimensional factor analysis.
- They should not replace the three primary targets.
- Feature importance, direction-of-effect, permutation importance, and reason-code reports support factor discussion, but remain association-based and not causal proof.
