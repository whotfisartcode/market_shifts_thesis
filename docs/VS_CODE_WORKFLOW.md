# VS Code Workflow

Open this folder in VS Code:

```text
/Users/whotfisart/codex/Thesis work/market_shifts_clean
```

Use the VS Code integrated terminal from the project root.

If a field name is unclear, start with:

```text
docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md
```

For final thesis direction, use:

```text
docs/FINAL_SOURCE_OF_TRUTH_INDEX.md
docs/FINAL_SCOPE_LOCK_NOTE.md
docs/FINAL_TARGET_HIERARCHY.md
docs/DOCUMENT_ORGANIZATION.md
```

You can also run predefined tasks from:

```text
Terminal -> Run Task...
```

Available tasks:

- `01 Rebuild SEC/FRED panel`
- `02 Data integrity audit`
- `03 P0 audits`
- `04 Target profile report`
- `05 Train failure model`
- `06 Train success model`
- `07 Run ablation`
- `08 Analysis outputs`
- `09 Broader target experiments`
- `10 Target and feature tweak experiments`
- `11 Model tuning robustness`
- `12 Advanced boosting benchmarks`
- `Run dashboard`

## Environment

If dependencies are missing:

```bash
python3 -m pip install -r requirements.txt
```

## Rebuild Data

```bash
python3 scripts/sec_fsd/inventory_sec_zips.py
python3 scripts/sec_fsd/index_submissions.py
python3 scripts/sec_fsd/match_distress_candidates.py
python3 scripts/sec_fsd/build_universe_v2.py
python3 scripts/sec_fsd/build_panel_v2.py
python3 scripts/data_quality/audit_panel_integrity.py
```

Main panel outputs:

- `data/processed/panel_v2/firm_panel_v2.csv.gz`
- `data/processed/panel_v2/firm_panel_v2.parquet`
- `data/github/firm_panel_v2.csv.gz`
- `data/github/firm_panel_v2.parquet`

## Run Models

```bash
python3 scripts/modeling/train_panel_v2_models.py --target distress_next_4q
python3 scripts/modeling/train_panel_v2_models.py --target failure_pressure_conservative_v2_next_4obs
python3 scripts/modeling/train_panel_v2_models.py --target success_resilience_next_4q
python3 scripts/modeling/run_panel_v2_ablation.py
python3 scripts/modeling/make_panel_v2_analysis_outputs.py
python3 scripts/modeling/target_profile_report.py
python3 scripts/modeling/feature_contribution_summary.py
python3 scripts/modeling/run_model_tuning_experiments.py
python3 scripts/modeling/run_advanced_boosting_experiments.py
```

Model outputs:

- `reports/modeling/`
- `reports/figures/modeling/`
- `models/panel_v2/`
- `reports/model_tuning/`
- `reports/model_tuning_advanced/`

The tuning scripts write reports only. They do not overwrite `models/panel_v2/`.

## Run Dashboard

```bash
streamlit run app/dashboard.py
```

Then open:

```text
http://127.0.0.1:8501
```

## Suggested VS Code Layout

- Keep `app/dashboard.py` open for dashboard changes.
- Keep `scripts/modeling/` open for modeling runs.
- Use `reports/modeling/*.csv` for result inspection.
- Use `reports/data_quality/*.csv` for source, missingness, and null-treatment checks.
- Use `data/github/firm_panel_v2.parquet` for your own visual checks.
- Use `docs/LITERATURE_REVIEW_DRAFT.md`, `docs/INTRODUCTION_RESEARCH_GAP_DRAFT.md`, `docs/REFERENCE_CRITICAL_EVALUATION.md`, and `reports/literature/source_to_claim_map.csv` when writing the thesis text.

## Current Target Columns

Failure/distress:

- `distress_next_2q`
- `distress_next_4q`
- `distress_next_8q`
- `broad_distress_next_4q`
- `failure_pressure_conservative_v2_next_4obs`

Success/resilience:

- `healthy_current`
- `success_profitability_next_4q`
- `success_resilience_next_4q`
- `success_quality_next_4q`

## Literature Package

The current citation and literature-review package is:

- `docs/BIBLIOGRAPHY.md`
- `docs/references.bib`
- `docs/BIBLIOGRAPHY_AUDIT.md`
- `docs/LITERATURE_SEARCH_STRATEGY.md`
- `docs/LITERATURE_MATRIX.md`
- `reports/literature/literature_matrix.csv`
- `reports/literature/reference_quality_audit.csv`
- `docs/REFERENCE_CRITICAL_EVALUATION.md`
- `reports/literature/reference_critical_evaluation.csv`
- `reports/literature/source_to_claim_map.csv`
- `reports/literature/research_gap_synthesis.csv`
- `docs/LITERATURE_REVIEW_OUTLINE.md`
- `docs/LITERATURE_REVIEW_DRAFT.md`
- `docs/INTRODUCTION_RESEARCH_GAP_DRAFT.md`
- `docs/THESIS_THEORETICAL_POSITIONING.md`

Regenerate the package after bibliography edits with:

```bash
python3 scripts/docs/generate_literature_package.py
```

## Model Tuning Package

Use these files when writing the methods/results sections about model robustness:

- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`
- `reports/model_tuning/MODEL_TUNING_PROTOCOL.md`
- `reports/model_tuning/model_tuning_summary.csv`
- `reports/model_tuning/baseline_vs_tuned_comparison.csv`
- `reports/model_tuning/all_candidate_metrics.csv`

AutoGluon is not installed in this environment and was not used for the production thesis workflow.

## Advanced Boosting Package

XGBoost and LightGBM benchmark outputs are saved under:

- `reports/model_tuning_advanced/ADVANCED_BOOSTING_PROTOCOL.md`
- `reports/model_tuning_advanced/advanced_boosting_summary.csv`
- `reports/model_tuning_advanced/advanced_vs_existing_comparison.csv`
- `reports/model_tuning_advanced/all_candidate_metrics.csv`
