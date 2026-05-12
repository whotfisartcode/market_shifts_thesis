# Reproducibility Freeze 2026-05-07

> Superseded status note, 2026-05-10: this was an interim freeze note, not the final current package freeze. For current production facts and package status, use `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`, `docs/FACTUAL_FREEZE_20260509.md`, `reports/RUN_STATUS_FINAL.md`, and current project-audit outputs.

This freeze records the core files that should be uploaded or referenced for the final thesis artifact.

## Main Package Files

- `data/github/firm_panel_v2.parquet`
- `data/github/firm_panel_v2.csv.gz`
- `data/github/firm_panel_v2_schema.csv`
- `app/dashboard.py`
- `requirements.txt`
- `README.md`
- current source-of-truth docs and final reports listed in `reports/reproducibility/freeze_manifest_20260507.csv`

## Raw Data Policy

Raw SEC ZIP files are not included in GitHub because they are large. They stay local under `data/raw/sec_fsd_zips/` or are redownloaded from SEC. FRED raw series stay local or can be regenerated from the FRED catalog.

## Smoke Commands

```bash
python3 scripts/project_audit/clean_venv_smoke_check.py
python3 scripts/project_audit/final_scientific_validity_qa.py
python3 -m streamlit run app/dashboard.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
```

## Manifest

The checksum manifest is:

```text
reports/reproducibility/freeze_manifest_20260507.csv
```

All listed files should have `exists = True` before final GitHub upload.
