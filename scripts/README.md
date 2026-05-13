# Scripts Folder

The repository includes scripts for rebuilding, modeling, auditing, and package checks.

## Most Useful Commands

```bash
python3 scripts/project_audit/github_package_smoke_check.py
streamlit run app/dashboard.py
```

## Main Subfolders

- `scripts/project_audit/` - package checks, dashboard screenshot capture, and project audits.
- `scripts/sec_fsd/` - SEC Financial Statement Data Set indexing and panel construction.
- `scripts/data/` - external data download helpers for SEC Financial Statement ZIPs and FRED macro series.
- `scripts/data_quality/` - panel integrity, leakage, provenance, and data-quality checks.
- `scripts/modeling/` - model training, target lab, tuning, ablation, and interpretation scripts.
- `scripts/features/` - feature and index construction helpers.
- `scripts/docs/` - thesis/documentation generation helpers.
- `scripts/legacy_parsers/` - older parser scripts kept for traceability.

The dashboard package does not require a raw-data rebuild. Use the rebuild scripts only if you are recreating the panel from SEC/FRED inputs.

Fresh raw-data entry points:

```bash
make download-sec
make download-fred
make build-panel
```
