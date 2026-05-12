# Package Smoke Test Report

This Level 1 smoke test checks reproducibility from the processed/GitHub panel. It does not rebuild the full raw SEC ZIP pipeline.

## Status Counts

- `PASS`: 15.

## Interpretation

A `PASS` result means the current local package can load the processed panel, compile scripts, import dependencies, and run a lightweight model check. It is not a guarantee of clean-machine success unless the same commands are rerun in a fresh environment.

Large raw SEC ZIPs remain outside the GitHub package. Full raw-data rebuild reproducibility is a heavier Level 2 check.

## Clean Virtualenv Check

`reports/project_audit/clean_venv_smoke_test_results.csv` exists with `0` FAIL rows.
This verifies dependency installation and processed-panel loading in a temporary clean virtual environment.
