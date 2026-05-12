# Data Manifest

This manifest records what was copied into the clean workspace and how it should be used.

## Current Reference Docs

| Path | Purpose |
| --- | --- |
| `docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md` | Plain-language definitions of panel fields, regimes, prediction dates, targets, missing values, and model metadata. |
| `docs/CURRENT_STATUS.md` | Current project state, panel counts, model results, audit status, and immediate next steps. |
| `docs/PROJECT_CHRONICLE.md` | Running project record: decisions, reasoning, failed ideas, implemented ideas, and current interpretation. |
| `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md` | Explanation of the one-panel architecture, feature families, and expansion strategy. |
| `docs/DOCUMENT_ORGANIZATION.md` | Current map of source-of-truth, thesis-writing, methodology, and archived documents. |
| `docs/FINAL_SCOPE_LOCK_NOTE.md` | Scope-freeze record: what is in the thesis, what is future research, and what claims are safe or unsafe. |
| `docs/FINAL_TARGET_HIERARCHY.md` | Final target hierarchy for strict distress, broader failure pressure, diagnostic pressure, and success/resilience. |
| `docs/STRATEGIST_HANDOFF_20260505.md` | Consolidated current-state handoff package for external strategic review. |
| `docs/DISTRESS_EVENT_DATE_PROVENANCE.md` | Event-date source-verification policy, event-review classifications, and strict distress labeling rules. |
| `docs/MARKET_HEALTH_INDEX_NOTE.md` | Explanation of the market-health index context layer and its integrity policy. |
| `docs/BIBLIOGRAPHY.md` | Curated thesis bibliography grouped by how each source supports the paper. |
| `docs/references.bib` | BibTeX file for citation-manager import. |

Superseded planning/review documents are retained under `docs/_redundant/` with a dedicated archive manifest.

## Current Generated Scripts And Outputs

| Path | Purpose | Git policy |
| --- | --- | --- |
| `scripts/data_quality/create_event_review_scaffold.py` | Builds the event-date provenance audit and event-review classification scaffold without changing production labels. | Track |
| `scripts/features/build_market_health_index.py` | Builds the market-health index from existing prediction-date-aligned macro/regime/global-event fields. | Track |
| `reports/data_quality/final_distress_event_date_audit.csv` | Current strict event-date provenance scaffold for existing event rows. | Track or include as report artifact |
| `reports/data_quality/event_review_firm_classification_scaffold.csv` | Event-review firm classification scaffold; includes source-verified candidates and do-not-label decisions. | Track or include as report artifact |
| `reports/data_quality/event_review_scaffold_summary.csv` | Compact event-review scaffold counts. | Track |
| `reports/data_quality/market_health_index_audit.csv` | Market-health input audit and leakage/alignment policy record. | Track |
| `reports/data_quality/readiness_table_20260505.csv` | Compact PASS / REVIEW / TODO readiness table for strategist handoff and final QA. | Track |
| `reports/modeling/market_health_index_by_prediction_date.csv` | Market-health scores by prediction date for dashboard/context. | Track if size is acceptable |
| `reports/modeling/market_health_by_year_regime_sector.csv` | Market-health, regime, sector, and distress/success summary table. | Track |
| `reports/figures/modeling/market_health_index_timeseries.png` | Figure for dashboard/thesis market-shift context. | Track |
| `app/dashboard.py` | Streamlit artifact exposing strict distress, broader failure pressure, success/resilience, target experiments, firm histories, and model outputs. | Track |

## Legacy Assets Copied

| Path | Purpose | Git policy |
| --- | --- | --- |
| `config/master_tickers.csv` | Ticker metadata and sector/industry labels for 261 large-cap firms. | Track |
| `config/ticker100.txt` | Legacy ticker universe; despite the name, contains 261 tickers. | Track |
| `config/ticker100more.txt` | Additional 100 tickers that were not used in the final legacy panel. | Track |
| `config/company_tickers_exchange.json` | SEC ticker-CIK-exchange mapping used for current public tickers. | Track |
| `config/ticker_cik_overrides.csv` | Manual ticker-CIK overrides for historical/corporate-action cases. | Track |
| `config/distress_candidate_seed.csv` | New distress and near-distress candidate seed list. | Track |
| `config/distressed_candidates_seed.csv` | Initial review list of bankruptcy/distress candidates for the rebuilt sample. | Track |
| `config/rebuild_universe_candidates.csv` | Generated candidate universe combining legacy core, distressed seed, and old extra tickers. | Track |
| `config/universe_v2_draft.csv` | Generated draft expanded universe after SEC coverage checks. | Track |
| `config/tag_map.txt` | Legacy XBRL concept mapping. | Track |
| `data/raw/fred/*.csv` | Legacy raw FRED macro series. | Ignore in Git unless small samples are needed |
| `data/processed/legacy_2025/firm_panel_with_zscore.parquet` | Main defended-thesis panel. | Ignore in Git, publish externally if needed |
| `data/processed/legacy_2025/firm_panel_with_zscore.csv` | CSV copy of the same legacy panel. | Ignore in Git |
| `data/processed/legacy_xbrl/` | Legacy processed XBRL extracts, much smaller than raw filings. | Ignore in Git |
| `data/processed/sp500_legacy/` | Legacy market-price extract. Known to have high missingness. | Ignore in Git |
| `data/samples/` | Small generated sample files and schema for GitHub/reproducibility checks. | Track |
| `notebooks/archive/legacy_gluon.ipynb` | Old AutoGluon notebook. Useful as historical reference only. | Track only if outputs are stripped |
| `scripts/legacy_parsers/` | Old parsing and download scripts. | Track as reference if cleaned |
| `reports/figures/` | Legacy figures used in old thesis/defense. | Optional track |

## Known Legacy Data Issues

- Current final panel has 255 tickers, not 100.
- `master_tickers.csv` has 261 tickers; missing from final panel: `ARM`, `ASML`, `AZN`, `CCEP`, `GFS`, `PDD`.
- The legacy ML targets were created in the notebook, not saved in the panel.
- Legacy targets are current/past rolling labels, not true forward-looking labels.
- Legacy model validation used a random 80/20 split.
- Several numeric columns contain impossible signs, extreme outliers, or infinite ratios.
- `price` and market data coverage are weak in the legacy panel.
- Small sample/schema outputs can be regenerated with `python3 scripts/data_quality/create_legacy_sample.py`.

## Planned New Data

| Source | Intended use |
| --- | --- |
| SEC Financial Statement Data Sets | Rebuild standardized U.S. firm-quarter financial panel without raw filing parsing. |
| FRED | Macro-financial context and lagged stress indicators. |
| Market data | Returns, volatility, drawdowns, and liquidity features. |
| Russian company data | Later external comparison or robustness sample. |
