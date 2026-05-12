# Market Shifts Thesis Project

Working title: **Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries**

This clean workspace separates the useful thesis assets from the older VS Code working folder. The old upload remains untouched at:

`../last_years_thesis_data/market_shifts`

## Current State

The defended-thesis legacy dataset was a large-cap U.S. public-company panel, not a top-100-only sample:

- 255 firms in the final panel
- 14,104 firm-date observations
- 58 columns
- Date range: 2008-10-02 to 2025-05-09
- Main file: `data/processed/legacy_2025/firm_panel_with_zscore.parquet`

Important caveat: the legacy panel has known data-quality and methodology issues. It should be treated as a starting point, not the final empirical dataset.

The active rebuilt panel is:

- `data/processed/panel_v2/firm_panel_v2.parquet`
- `data/processed/panel_v2/firm_panel_v2.csv.gz`
- 31,702 rows
- 190 columns
- 540 SEC CIKs
- 540 tickers / display IDs
- Date range: 2009-03-31 to 2026-02-28
- Primary failure target: `distress_next_4q`
- Main broader failure-pressure target: `failure_pressure_conservative_v2_next_4obs`
- Primary success target: `success_resilience_next_4q`
- Validated secondary production targets: `industry_relative_resilience_next_4obs`, `stress_resilience_next_4obs`, `recovery_next_4obs`, `quality_success_cashflow_next_4obs`

## Directory Layout

```text
config/                         Ticker lists, metadata, SEC concept map, FRED/event catalogs
config/universe_v2_draft.csv    Coverage-checked draft universe for rebuilt panel
data/raw/fred/                  FRED macro CSVs used by the rebuilt panel
data/raw/sec_fsd_zips/          SEC Financial Statement Data Set ZIPs
data/samples/                   Small GitHub-safe sample outputs
data/interim/                   Temporary rebuilt tables
data/processed/legacy_2025/     Legacy final panel from the defended thesis
data/processed/legacy_xbrl/     Legacy processed XBRL extracts
data/processed/panel_v2/        Rebuilt clean firm-period panel
data/processed/sp500_legacy/    Legacy market-price file
scripts/legacy_parsers/         Old parser/download scripts kept for reference
scripts/sec_fsd/                New SEC Financial Statement Data Set parser
scripts/data/                   Data download helpers
scripts/data_quality/           Audit and validation scripts
scripts/modeling/               New modeling scripts
notebooks/archive/              Old notebooks
reports/data_quality/           Audit outputs
reports/figures/                Legacy and rebuilt modeling figures
models/                         Local model artifacts, ignored by Git
app/                            Streamlit dashboard artifact
docs/                           Current project notes, source-of-truth docs, and document organization map
docs/_redundant/                Historical/superseded documents kept for traceability
_archive/                       Local archive for obsolete material
```

The running project record is kept in `docs/PROJECT_CHRONICLE.md`.

## GitHub Policy

GitHub should contain:

- source code
- configuration
- README and documentation
- small samples or schemas
- compact audit summaries
- reproducibility instructions
- the compact processed panel if repository size remains acceptable

GitHub should not contain:

- full SEC ZIPs
- full raw filings
- large raw/intermediate processed panels
- AutoGluon model artifacts
- local notebooks with huge embedded outputs

The current GitHub-ready panel is about 11 MB as Parquet and 14 MB as compressed CSV, so it can be uploaded with the repository if needed. Full SEC ZIPs stay out of GitHub.

See `REPRODUCIBILITY.md` for the clone-level setup, dashboard run command, package smoke check, and full raw-data rebuild sequence.

## Rebuild Workflow

```bash
python3 scripts/data/download_fred_series.py
python3 scripts/sec_fsd/build_panel_v2.py
python3 scripts/modeling/train_panel_v2_models.py --target distress_next_4q
python3 scripts/modeling/train_panel_v2_models.py --target failure_pressure_conservative_v2_next_4obs
python3 scripts/modeling/train_panel_v2_models.py --target success_resilience_next_4q
python3 scripts/modeling/promote_validated_secondary_targets.py
python3 scripts/modeling/train_panel_v2_models.py --target industry_relative_resilience_next_4obs
python3 scripts/modeling/train_panel_v2_models.py --target stress_resilience_next_4obs
python3 scripts/modeling/train_panel_v2_models.py --target recovery_next_4obs
python3 scripts/modeling/train_panel_v2_models.py --target quality_success_cashflow_next_4obs
python3 scripts/modeling/run_validation_extension_gate.py
python3 scripts/modeling/run_panel_v2_ablation.py
python3 scripts/modeling/make_panel_v2_analysis_outputs.py
python3 scripts/modeling/feature_contribution_summary.py
```

See `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md` for the controlled smaller/distressed-company expansion and one-panel design.
See `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md` for the one-dataset panel design and macro/regime explanation.
See `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md` for the event-context layer and dashboard direction.
See `docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md` for the factor-analysis framing, source lineage, and null-treatment policy.
See `docs/DOCUMENT_ORGANIZATION.md` for the current document map.
See `docs/BIBLIOGRAPHY.md` and `docs/references.bib` for the curated reference list.
See `docs/FACTUAL_FREEZE_20260509.md` for current package-facing counts, and `reports/project_audit/` for project audit outputs.
See `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md` for the final scientific-validity layer.
See `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md` for final thesis claim guardrails.

## Expanded Universe

The current expanded universe keeps the defended-thesis core and adds controlled, coverage-checked candidates:

- 254 core large-cap CIK rows. The old 255 ticker panel collapses `GOOG` and `GOOGL` to one SEC CIK.
- 100 additional-control universe rows.
- 42 distress or near-distress candidate rows.
- 75 event-review expansion firms.
- 75 matched-control expansion firms.
- 546 universe rows total.
- The production panel currently contains 540 SEC CIKs and 540 ticker/display IDs after SEC coverage, identifier, alias-collapse, and panel-construction constraints.

Historical expansion planning is archived at `docs/_redundant/04_universe_expansion_history/UNIVERSE_EXPANSION_PLAN.md`. Current counts and interpretation are in `docs/CURRENT_STATUS.md` and `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md`.

## Dashboard

Run the thesis dashboard artifact with:

```bash
streamlit run app/dashboard.py
```

The dashboard reads the GitHub-ready panel in `data/github/firm_panel_v2.csv.gz` and model outputs from `reports/modeling/`.

Final dashboard screenshots are stored in `reports/figures/dashboard/`.

Current package state: the panel has been rebuilt after adding `ddate == period` SEC period filtering on 2026-05-07 and after the 2026-05-09 SEC mapping/caveat-resolution polish. The provenance/model/dashboard/QA chain has been regenerated, P0 audits pass, strict distress event-date provenance is `PASS`, and the GitHub deliverable package contains the dashboard, compact firm panel, schema, modeling/report outputs, scripts, and documentation needed for clone-level reproduction from included artifacts.
