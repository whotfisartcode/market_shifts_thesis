# Dashboard Artifact

The dashboard is ready to run from the GitHub package. It uses the included firm panel and compact report outputs; it does not need raw SEC ZIPs or trained model binaries.

Run from the project root:

```bash
streamlit run app/dashboard.py
```

Or:

```bash
make dashboard
```

The dashboard reads:

- `data/github/firm_panel_v2.csv.gz`
- target-specific model metrics and feature-importance files in `reports/modeling/`
- target experiment summaries in `reports/target_experiments/`
- target-tweak and feature-set summaries in `reports/target_tweak_experiments/`
- model-tuning summaries in `reports/model_tuning/` and `reports/model_tuning_advanced/`

Dashboard views:

- Overview with mutually exclusive outcome composition and target coverage,
- Data Coverage with panel and missingness diagnostics,
- Models with target-specific temporal metrics and feature importance,
- Target Lab with target experiments, feature-set ablations, and tuning summaries,
- Firm Explorer with financial metrics, macro comparison, target timeline, and recent rows,
- Artifact Notes for thesis/GitHub documentation.

See `../DASHBOARD_INPUTS.md` for the exact input-file list.

Use the dashboard for interpretation and screenshots. Do not treat dashboard filters or visual standardization as changes to the underlying panel.
