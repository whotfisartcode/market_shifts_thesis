# Reports Folder

This folder contains compact outputs used by the dashboard and thesis interpretation.

## Dashboard-Critical Reports

```text
reports/modeling/
reports/target_lab/
reports/target_tweak_experiments/dashboard_*.csv
reports/model_tuning/model_tuning_summary.csv
reports/model_tuning_advanced/advanced_boosting_summary.csv
reports/figures/dashboard/
```

The exact dashboard input list is in `../DASHBOARD_INPUTS.md`.

## Useful Subfolders

- `reports/modeling/` - production model metrics, feature importance, calibration, target distributions, and interpretation tables.
- `reports/target_lab/` - validated secondary target profiles, reason-code summaries, feature-level importance, and target-lab summaries.
- `reports/target_tweak_experiments/` - compact target-tweak and feature-set summary tables.
- `reports/model_tuning/` and `reports/model_tuning_advanced/` - compact tuning summaries.
- `reports/data_quality/` - selected audit summaries and feature-list outputs.
- `reports/figures/dashboard/` - dashboard screenshots.
- `reports/reproducibility/` - tracked-file manifest and package-freeze artifacts.

Deep experiment run folders and legacy plots are intentionally excluded from GitHub to keep the package readable.
