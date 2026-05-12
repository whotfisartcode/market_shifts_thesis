# Market Shifts Thesis Dashboard

Reproducible deliverable package for the thesis project:

**Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries**

This repository is meant to be cloned, installed, and used directly. The Streamlit dashboard works from the packaged firm panel and report outputs already included in GitHub.

## Start Here

```bash
git clone https://github.com/whotfisartcode/market_shifts.git
cd market_shifts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/dashboard.py
```

Optional shortcut:

```bash
make setup
make dashboard
```

## What Is Included

- `app/dashboard.py` - Streamlit dashboard.
- `data/github/firm_panel_v2.csv.gz` - packaged firm panel used by the dashboard.
- `data/github/firm_panel_v2.parquet` - same panel in Parquet format for analysis.
- `data/github/firm_panel_v2_schema.csv` - column schema and missingness summary.
- `reports/modeling/` - model metrics, feature importance, calibration, and target summaries.
- `reports/target_lab/` - validated secondary target profiles and interpretation tables.
- `reports/target_tweak_experiments/` - compact target and feature-set experiment summaries.
- `reports/model_tuning*/` - compact tuning summaries.
- `reports/figures/dashboard/` - exported dashboard screenshots.
- `docs/` - thesis-facing methodology, data, target, and limitation notes.
- `scripts/` - data build, modeling, audit, and smoke-check scripts.
- `config/` - source catalogs, SEC concept mapping, universe definitions, and event metadata.

## Main Commands

```bash
# Verify that the GitHub package has the dashboard inputs it needs
python3 scripts/project_audit/github_package_smoke_check.py

# Run the dashboard
streamlit run app/dashboard.py
```

The smoke check should finish with:

```text
GitHub package smoke check complete; failures=0
```

## Dashboard Data

The dashboard loads the packaged panel from:

```text
data/github/firm_panel_v2.csv.gz
```

Current packaged panel:

- 31,702 firm-period rows
- 190 columns
- 540 SEC CIKs / display tickers
- period range: 2009-03-31 to 2026-02-28
- prediction timestamp range: 2009-04-15 to 2026-03-31

The repository does not need raw SEC ZIPs or local model binaries to run the dashboard.

## Repository Map

```text
app/                         Streamlit dashboard
config/                      Universe, source, target, SEC, and macro metadata
data/github/                 packaged firm panel used by the dashboard
data/samples/                small sample files and schemas
docs/                        thesis-facing methodology and interpretation notes
reports/modeling/            production model outputs and interpretation tables
reports/target_lab/          validated secondary target outputs
reports/target_tweak_experiments/ compact experiment summaries for dashboard views
reports/figures/dashboard/   dashboard screenshots
scripts/                     build, modeling, audit, and utility scripts
```

## Useful Entry Points

- [QUICKSTART.md](QUICKSTART.md) - shortest run instructions.
- [DASHBOARD_INPUTS.md](DASHBOARD_INPUTS.md) - exact files the dashboard reads.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md) - clone-level setup plus full raw rebuild notes.
- [data/README.md](data/README.md) - data package explanation.
- [reports/README.md](reports/README.md) - report folder guide.
- [docs/README.md](docs/README.md) - documentation guide.

## Excluded On Purpose

These are intentionally not part of the GitHub package:

- SEC quarterly ZIP files under `data/raw/sec_fsd_zips/`
- raw FRED downloads under `data/raw/fred/`
- large local processed/interim rebuild tables
- trained `joblib` model binaries under `models/`
- full-text literature PDFs and extracted full-text files
- local notebooks, caches, editor files, and temporary files

For a full raw-data rebuild, see [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
