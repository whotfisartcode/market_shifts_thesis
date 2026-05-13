# Reproducibility

This repository is a download-and-use package. The dashboard runs from the compact firm panel and report outputs included in GitHub.

For the shortest instructions, see `QUICKSTART.md`.

## Included

- Streamlit dashboard: `app/dashboard.py`
- Dashboard cloud dependencies: `app/requirements.txt`
- Dashboard data package: `data/github/firm_panel_v2.csv.gz`, `data/github/firm_panel_v2.parquet`, and `data/github/firm_panel_v2_schema.csv`
- Panel-construction, data-quality, modeling, and documentation scripts under `scripts/`
- Model metrics, feature-importance summaries, target-lab outputs, tuning summaries, and dashboard screenshots under `reports/`
- Current thesis documentation and bibliography under `docs/`
- Small samples and schemas under `data/samples/`

The exact dashboard inputs are listed in `DASHBOARD_INPUTS.md`.

## Excluded

- Raw SEC Financial Statement Data Set ZIPs under `data/raw/sec_fsd_zips/`
- Local FRED downloads under `data/raw/fred/`
- Large processed/interim tables under `data/processed/` and `data/interim/`
- Local trained `joblib` model binaries under `models/`
- Full-text literature PDFs and extracted full-text files under `reports/literature/legal_full_text_*`
- Local caches, temporary files, and editor metadata

The dashboard does not require the excluded raw data or model binaries. It reads the compact GitHub panel and exported modeling/report artifacts.

## Setup

Run from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Equivalent `make` command:

```bash
make setup
```

## Run The Dashboard

```bash
streamlit run app/dashboard.py
```

Equivalent `make` command:

```bash
make dashboard
```

The dashboard expects the packaged panel at `data/github/firm_panel_v2.csv.gz` and report files under `reports/modeling/`, `reports/target_lab/`, `reports/target_experiments/`, `reports/target_tweak_experiments/`, `reports/model_tuning/`, and `reports/model_tuning_advanced/`.

## Smoke Check

Use the GitHub package smoke check to verify clone-level reproducibility from included files:

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

Equivalent `make` command:

```bash
make check
```

This checks imports, dashboard input files, the packaged panel/schema, selected report dependencies, and Python compilation for the dashboard and scripts.

## Full Raw Rebuild

A full raw-data rebuild is heavier than the GitHub package because it downloads official SEC quarterly ZIP files. The full SEC ZIP collection is several GB and can take a while.

For repeated SEC downloads, set a contact user agent first:

```bash
export SEC_USER_AGENT="your-name your-email@example.com"
```

Download fresh company and macro inputs:

```bash
make download-sec
make download-fred
```

Equivalent direct commands:

```bash
python3 scripts/data/download_sec_fsd_zips.py --from 2009q1 --to latest
python3 scripts/data/download_fred_series.py
```

Then rebuild the firm panel:

```bash
python3 scripts/sec_fsd/index_submissions.py
python3 scripts/sec_fsd/match_distress_candidates.py
python3 scripts/sec_fsd/build_universe_v2.py
python3 scripts/sec_fsd/build_panel_v2.py
```

Equivalent `make` command:

```bash
make build-panel
```

`build_panel_v2.py` rewrites:

```text
data/processed/panel_v2/firm_panel_v2.csv.gz
data/processed/panel_v2/firm_panel_v2.parquet
data/github/firm_panel_v2.csv.gz
data/github/firm_panel_v2.parquet
data/github/firm_panel_v2_schema.csv
```

To run the whole fresh-data panel workflow in one command:

```bash
make refresh-panel
```

After the panel is rebuilt, rerun the production model/report outputs:

```bash
python3 scripts/modeling/train_panel_v2_models.py --target distress_next_4q
python3 scripts/modeling/train_panel_v2_models.py --target failure_pressure_conservative_v2_next_4obs
python3 scripts/modeling/train_panel_v2_models.py --target success_resilience_next_4q
python3 scripts/modeling/promote_validated_secondary_targets.py
python3 scripts/modeling/run_panel_v2_ablation.py
python3 scripts/modeling/make_panel_v2_analysis_outputs.py
python3 scripts/modeling/feature_contribution_summary.py
```

Equivalent `make` command:

```bash
make rebuild-models
```

See `README.md`, `docs/DATA_MANIFEST.md`, and `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md` for the detailed project map.
