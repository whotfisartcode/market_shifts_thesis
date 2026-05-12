# Model Tuning And AutoGluon Note

Last updated: 2026-05-09

## Bottom Line

The thesis should not present the machine-learning work as one or two isolated model runs. After the 2026-05-09 SEC mapping polish, the baseline temporal-validation models, controlled sklearn tuning, feature-set ablation, feature-group interpretation, and advanced XGBoost/LightGBM benchmarks were rerun.

AutoGluon should not be made the main thesis model at this stage. XGBoost and LightGBM have now been installed and tested separately as advanced boosted-tree benchmarks. AutoGluon remains a heavier AutoML layer and should be named only as an optional future extension unless it is deliberately installed, rerun, documented, and validated.

## What Was Run

Script:

```text
scripts/modeling/run_model_tuning_experiments.py
```

Output root:

```text
reports/model_tuning/
```

Protocol:

- data source: `data/processed/panel_v2/firm_panel_v2.csv.gz`;
- production targets only:
  - `distress_next_4q`;
  - `failure_pressure_conservative_v2_next_4obs`;
  - `success_resilience_next_4q`;
- train split: `prediction_date` through 2018;
- validation split: 2019-2021;
- test split: 2022-2024;
- candidate choice uses validation metrics only;
- classification thresholds are selected on validation F1;
- test metrics are observed after validation selection and must not be used for further tuning.

Experiment scale:

- 35 candidate configurations per target;
- 105 candidate configurations across three targets;
- 315 split-metric rows in `reports/model_tuning/all_candidate_metrics.csv`;
- no candidate failures; each `candidate_failures.csv` is header-only.

Candidate families:

- logistic regression with multiple L2 regularization strengths;
- random forest with multiple depth, leaf, feature, and seed settings;
- extra trees with multiple depth, leaf, feature, and seed settings;
- gradient boosting with multiple tree-depth and learning-rate settings;
- histogram gradient boosting with multiple leaf and regularization settings.

## Baseline Versus Validation-Selected Tuned Models

| Target | Production baseline | Baseline PR-AUC | Baseline F1 | Validation-selected tuned candidate | Tuned PR-AUC | Tuned F1 | Interpretation |
| --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| `distress_next_4q` | random forest | 0.125 | 0.148 | `extra_trees_cfg3_seed42` | 0.154 | 0.230 | Tuning improves strict-distress PR-AUC and threshold F1, but strict legal distress remains rare and weak as a headline target. |
| `failure_pressure_conservative_v2_next_4obs` | random forest | 0.758 | 0.725 | `hist_gradient_boosting_cfg3` | 0.744 | 0.705 | Tuning supports robustness, while the baseline random forest remains stronger on the held-out test window. |
| `success_resilience_next_4q` | random forest | 0.975 | 0.938 | `random_forest_cfg1_seed42` | 0.974 | 0.937 | Tuning confirms robustness; success/resilience is stable across model configurations. |

Source file:

```text
reports/model_tuning/baseline_vs_tuned_comparison.csv
```

## Advanced XGBoost And LightGBM Benchmarks

Script:

```text
scripts/modeling/run_advanced_boosting_experiments.py
```

Output root:

```text
reports/model_tuning_advanced/
```

Experiment scale:

- 24 candidate configurations per target;
- 72 candidate configurations across three production targets;
- 216 split-metric rows in `reports/model_tuning_advanced/all_candidate_metrics.csv`;
- no candidate failures.

Validation-selected advanced candidates:

| Target | Advanced candidate | Family | Advanced PR-AUC | Advanced F1 | Interpretation |
| --- | --- | --- | ---: | ---: | --- |
| `distress_next_4q` | `xgboost_cfg1_seed42` | XGBoost | 0.143 | 0.229 | Better F1 than the baseline strict-distress model, but strict legal distress remains a rare-event benchmark. |
| `failure_pressure_conservative_v2_next_4obs` | `lightgbm_cfg4_seed777` | LightGBM | 0.744 | 0.723 | Strong robustness result, but still slightly below the production random forest on the held-out test window. |
| `success_resilience_next_4q` | `xgboost_cfg4_seed202` | XGBoost | 0.974 | 0.938 | Nearly tied with the baseline random forest; success/resilience remains stable across boosted-tree robustness checks. |

Source file:

```text
reports/model_tuning_advanced/advanced_vs_existing_comparison.csv
```

## How To Position This In The Thesis

Safe wording:

> The modeling stage combined baseline temporal-validation models, feature-set ablations, broader target experiments, and a controlled hyperparameter/seed robustness pass. Tuning candidates were selected on a validation window and then evaluated once on the held-out 2022-2024 test window.

Also safe:

> XGBoost and LightGBM were tested as advanced boosted-tree benchmarks using the same temporal validation protocol. They provide robustness evidence; random forest remains the strongest headline model for broader failure pressure and success/resilience, while boosted trees remain close robustness checks.

Unsafe wording:

> Exhaustive AutoML search was performed.

Do not write that unless AutoGluon or a comparable AutoML workflow is actually installed, run, and documented. The correct claim is controlled, reproducible tuning under time and dependency constraints.

## Interpretation Rules

- `distress_next_4q` remains the strict legal benchmark, not the main performance headline.
- `failure_pressure_conservative_v2_next_4obs` remains the main failure-factor target because it is broader, more learnable, and economically interpretable.
- `success_resilience_next_4q` remains the main success/resilience counterpart; the production random forest is still the strongest headline model.
- Missingness indicators may help prediction but must not be interpreted as economic drivers.
- Feature-group interpretation should be emphasized over isolated single-feature claims.

## AutoGluon Decision

Environment check on 2026-05-06:

```text
autogluon: False
autogluon.tabular: False
xgboost: True, version 3.2.0
lightgbm: True, version 4.6.0
catboost: False
```

macOS note:

```text
brew install libomp
```

was required for the native XGBoost/LightGBM libraries to load.

Recommendation:

- keep the current scikit-learn workflow as the thesis production workflow;
- use XGBoost and LightGBM as advanced robustness benchmarks, not as an AutoML claim;
- do not add AutoGluon before submission unless there is a specific reason and enough time to rerun, validate, document, and debug it;
- mention AutoGluon and CatBoost as future robustness extensions if useful;
- if installed later, keep AutoGluon outputs under a separate folder and do not overwrite current production results.
