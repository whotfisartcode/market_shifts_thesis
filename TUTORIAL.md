# Tutorial: How To Use This GitHub Repository

This guide explains the repository from zero. Use it when you open GitHub and feel that there are too many files.

## 1. What This GitHub Repository Is

This repository is the public, reproducible committee package for the thesis dashboard and supporting analysis. It is not the full working archive.

In plain terms, it contains:

- the dashboard app,
- the firm panel the dashboard needs,
- model/report tables the dashboard uses,
- documentation explaining the data, targets, and limitations,
- scripts used to build, audit, and verify the package.

It is not just a code dump. It is intended to be downloaded and run.

## 2. The Most Important Files

If you only remember a few files, remember these:

```text
README.md                         Main landing page
TUTORIAL.md                       This step-by-step guide
QUICKSTART.md                     Short command-only setup guide
DASHBOARD_INPUTS.md               Exact dashboard input files
REPRODUCIBILITY.md                Reproducibility and rebuild notes
app/dashboard.py                  The Streamlit dashboard
app/requirements.txt              Minimal cloud deployment dependencies
data/github/firm_panel_v2.csv.gz  Main firm panel used by the dashboard
data/github/firm_panel_v2.parquet Same panel for direct analysis
data/github/firm_panel_v2_schema.csv Column schema
requirements.txt                  Python packages to install
```

Everything else supports one of those pieces.

## 3. What The Main Folders Mean

```text
app/
```

The dashboard lives here. The main file is `app/dashboard.py`.

```text
data/github/
```

This is the packaged dataset folder. The dashboard uses `firm_panel_v2.csv.gz` from here.

```text
reports/
```

This contains model metrics, feature importance, target summaries, and dashboard screenshots. The dashboard reads several compact CSV files from this folder.

```text
docs/
```

This contains thesis-facing documentation: data design, target definitions, limitations, bibliography, and final notes.

```text
scripts/
```

This contains build, modeling, audit, and verification scripts. You do not need to run most of them to use the dashboard.

```text
config/
```

This contains source metadata: tickers, SEC concept mappings, macro series, target/event metadata, and universe definitions.

## 4. What You Can Ignore At First

When your goal is only to run the dashboard, ignore:

- raw-data rebuild scripts,
- old methodology notes,
- detailed audit outputs,
- full raw SEC data instructions,
- model retraining scripts,
- legacy parser scripts.

The dashboard already has the packaged panel and report outputs it needs.
The omitted archive material stays in the local working archive, not in the committee GitHub package.

## 5. How To Download The Repository From GitHub

There are two normal ways.

### Option A: Clone With Git

Use this if Git is installed:

```bash
git clone https://github.com/whotfisartcode/market_shifts_thesis.git
cd market_shifts_thesis
```

### Option B: Download ZIP

Use this if you do not want to use Git:

1. Open the repository page on GitHub.
2. Click the green `Code` button.
3. Click `Download ZIP`.
4. Unzip it.
5. Open a terminal inside the unzipped folder.

The rest of the commands are the same.

## 6. How To Install The Python Environment

From the repository root, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you are using Windows PowerShell, activation is usually:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux, you can also use:

```bash
make setup
```

## 7. How To Check That The Package Is Complete

Before launching the dashboard, run the package smoke check:

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

Expected result:

```text
GitHub package smoke check complete; failures=0
```

This check confirms that:

- required Python packages can be imported,
- the packaged firm panel exists,
- the panel and schema load correctly,
- dashboard report inputs exist,
- Python scripts compile.

If this passes, the repository is in a usable state.

## 8. How To Launch The Dashboard

Run:

```bash
streamlit run app/dashboard.py
```

Or, on macOS/Linux:

```bash
make dashboard
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Open that URL in your browser.

## 9. What The Dashboard Uses Internally

The dashboard mainly uses:

```text
data/github/firm_panel_v2.csv.gz
reports/modeling/
reports/target_lab/
reports/target_tweak_experiments/
```

The exact file list is in:

```text
DASHBOARD_INPUTS.md
```

Important: the dashboard does not require raw SEC ZIP files and does not require local trained `joblib` model files.

## 10. How To Use The Firm Panel Directly

You can load the dataset in Python:

```python
import pandas as pd

panel = pd.read_parquet("data/github/firm_panel_v2.parquet")
print(panel.shape)
print(panel.head())
```

Expected shape:

```text
(31702, 190)
```

If you prefer CSV:

```python
import pandas as pd

panel = pd.read_csv("data/github/firm_panel_v2.csv.gz", low_memory=False)
print(panel.shape)
```

## 11. What The Dataset Contains

The packaged firm panel contains:

- SEC accounting fundamentals,
- financial ratios,
- trend and deterioration features,
- FRED macro variables,
- market-regime indicators,
- global event context,
- industry metadata,
- prediction timestamps,
- forward-looking success and failure targets.

Current panel size:

- 31,702 firm-period rows,
- 190 columns,
- 540 SEC CIKs / display tickers,
- period range from 2009-03-31 to 2026-02-28.

The schema is here:

```text
data/github/firm_panel_v2_schema.csv
```

## 12. How To Understand The Reports

Start with:

```text
reports/modeling/
```

This folder contains the production model summaries. Useful files include:

```text
panel_v2_model_metrics.csv
panel_v2_feature_importance.csv
calibration_metrics.csv
threshold_ranking_metrics.csv
final_model_feature_interpretation_table.csv
```

Then look at:

```text
reports/target_lab/
```

This folder explains the secondary target lab and validated secondary outcomes.

Dashboard screenshots are here:

```text
reports/figures/dashboard/
```

## 13. How To Understand The Documentation

Start with these:

```text
docs/CURRENT_STATUS.md
docs/FINAL_SOURCE_OF_TRUTH_INDEX.md
docs/DATA_MANIFEST.md
docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md
docs/MASTER_DATA_MODEL_TARGET_EXPLAINER.md
docs/FINAL_TARGET_HIERARCHY.md
docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md
```

If you only want the final thesis-facing logic, read:

```text
docs/FINAL_SOURCE_OF_TRUTH_INDEX.md
```

That file tells you which documents are the current source of truth.

## 14. Reproducibility Levels

There are two levels of reproducibility.

### Level 1: Download-And-Use Reproducibility

This is what the GitHub package is optimized for.

You can:

- clone or download the repo,
- install dependencies,
- run the smoke check,
- launch the dashboard,
- load the firm panel directly.

This level does not require raw SEC ZIPs.

### Level 2: Full Raw-Data Rebuild

This is heavier.

It requires downloading official SEC Financial Statement Data Set ZIP files and FRED inputs, then rerunning the panel construction and modeling scripts.

Use this only if you want to recreate the panel from raw sources. The instructions are in:

```text
REPRODUCIBILITY.md
```

The shortest fresh-data rebuild command is:

```bash
export SEC_USER_AGENT="your-name your-email@example.com"
make refresh-panel
make rebuild-models
make dashboard
```

`make refresh-panel` downloads official SEC Financial Statement Data Set ZIPs, downloads FRED macro data, indexes SEC submissions, rebuilds the universe, and rewrites the packaged firm panel in `data/github/`.

## 15. Publishing The Dashboard Online

Use Streamlit Community Cloud. GitHub stores the code and data, while Streamlit runs the Python dashboard and gives you a public URL.

Deployment settings:

```text
Repository: whotfisartcode/market_shifts_thesis
Branch: reproducible-deliverables-20260513
Main file path: app/dashboard.py
Python version: 3.12
```

Full instructions are in:

```text
DEPLOYMENT.md
```

## 16. Common Problems And Fixes

### Problem: `streamlit: command not found`

The environment is not activated, or dependencies were not installed.

Run:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Then try again:

```bash
streamlit run app/dashboard.py
```

### Problem: `ModuleNotFoundError`

Install dependencies again:

```bash
pip install -r requirements.txt
```

### Problem: dashboard says a file is missing

Run:

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

Then check `DASHBOARD_INPUTS.md` to see which file is expected.

### Problem: port `8501` is already in use

Run Streamlit on another port:

```bash
streamlit run app/dashboard.py --server.port 8502
```

### Problem: GitHub still looks overwhelming

Use this reading order:

1. `README.md`
2. `TUTORIAL.md`
3. `QUICKSTART.md`
4. `DASHBOARD_INPUTS.md`
5. `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`

Do not start by browsing every folder.

## 17. Recommended Workflow For A Reviewer Or Thesis Supervisor

1. Read `README.md`.
2. Run the setup commands from `QUICKSTART.md`.
3. Run the smoke check.
4. Launch the dashboard.
5. Review the data schema in `data/github/firm_panel_v2_schema.csv`.
6. Review target definitions in `docs/FINAL_TARGET_HIERARCHY.md`.
7. Review model outputs in `reports/modeling/`.
8. Review limitations in `docs/SCIENTIFIC_VALIDITY_AND_LIMITATIONS_NOTE.md`.

## 18. Short Summary

Use the repository like this:

```bash
git clone https://github.com/whotfisartcode/market_shifts_thesis.git
cd market_shifts_thesis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/project_audit/github_package_smoke_check.py
streamlit run app/dashboard.py
```

If the smoke check says `failures=0`, the GitHub package is complete enough to run the dashboard from the included firm panel.
