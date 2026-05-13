# Quickstart

Use these steps after downloading or cloning the repository.

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or:

```bash
make setup
```

## 2. Check The Package

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

Expected result:

```text
GitHub package smoke check complete; failures=0
```

## 3. Run The Dashboard

```bash
streamlit run app/dashboard.py
```

Or:

```bash
make dashboard
```

## 4. Publish Online

Use Streamlit Community Cloud with:

```text
Repository: whotfisartcode/market_shifts_thesis
Branch: reproducible-deliverables-20260513
Main file path: app/dashboard.py
Python version: 3.12
```

See `DEPLOYMENT.md`.

## 5. Open The Data Directly

```python
import pandas as pd

panel = pd.read_parquet("data/github/firm_panel_v2.parquet")
print(panel.shape)
```

Expected shape:

```text
(31702, 190)
```

## 6. Fresh Data Rebuild

For a full fresh-data rebuild:

```bash
export SEC_USER_AGENT="your-name your-email@example.com"
make refresh-panel
make rebuild-models
make dashboard
```
