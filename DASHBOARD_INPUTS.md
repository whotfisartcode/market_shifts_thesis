# Dashboard Inputs

The dashboard is designed to run from files included in this repository. It does not load raw SEC ZIPs and it does not load local `joblib` model binaries.

## Required Core Dataset

```text
data/github/firm_panel_v2.csv.gz
```

This is the file used by `app/dashboard.py`.

Analysis-friendly copy:

```text
data/github/firm_panel_v2.parquet
```

Schema:

```text
data/github/firm_panel_v2_schema.csv
```

## Required Dashboard Report Files

```text
reports/modeling/panel_v2_model_metrics.csv
reports/modeling/panel_v2_feature_importance.csv
reports/modeling/panel_v2_temporal_split_summary.csv
reports/modeling/calibration_metrics.csv
reports/modeling/threshold_ranking_metrics.csv
reports/target_lab/validated_secondary_target_profiles.csv
reports/target_lab/exploratory_reason_code_summary.csv
reports/target_lab/exploratory_feature_level_importance.csv
reports/target_lab/exploratory_feature_direction_effects.csv
reports/target_lab/exploratory_feature_group_importance.csv
reports/target_tweak_experiments/dashboard_best_target_rows.csv
reports/target_tweak_experiments/dashboard_feature_set_performance.csv
reports/target_tweak_experiments/dashboard_factor_group_best_models.csv
```

The dashboard also loads per-target modeling files when available:

```text
reports/modeling/panel_v2_<target>_model_metrics.csv
reports/modeling/panel_v2_<target>_feature_importance.csv
reports/modeling/panel_v2_<target>_temporal_split_summary.csv
```

Production targets:

```text
distress_next_4q
failure_pressure_conservative_v2_next_4obs
success_resilience_next_4q
industry_relative_resilience_next_4obs
stress_resilience_next_4obs
recovery_next_4obs
quality_success_cashflow_next_4obs
```

## Verify Inputs

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

This checks that the packaged panel, schema, dashboard inputs, and Python files are present and loadable.
