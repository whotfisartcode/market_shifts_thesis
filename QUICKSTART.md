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

## 4. Open The Data Directly

```python
import pandas as pd

panel = pd.read_parquet("data/github/firm_panel_v2.parquet")
print(panel.shape)
```

Expected shape:

```text
(31702, 190)
```
