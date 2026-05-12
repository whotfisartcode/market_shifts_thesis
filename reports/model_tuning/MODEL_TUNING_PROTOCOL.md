# Model Tuning Protocol

Last updated: 2026-05-08

This is a controlled robustness/tuning experiment. It does not overwrite the production models in `models/panel_v2/` and should be written as a supplementary model-development check.

## Protocol

- Data source: `data/processed/panel_v2/firm_panel_v2.csv.gz`.
- Split policy: train <= 2018, validation 2019-2021, test 2022-2024.
- Candidate selection uses validation data only.
- Thresholds are selected on validation data using F1.
- Final test metrics are observed after validation selection and must not be used for further tuning.
- Missingness indicators created by the imputer may help prediction, but they should not be interpreted as economic factors.

## Candidate Families

- logistic regression with different regularization strengths;
- random forest with multiple depths/leaves/features and seeds;
- extra trees with multiple depths/leaves/features and seeds;
- gradient boosting with multiple learning-rate/tree-depth settings and seeds;
- histogram gradient boosting with multiple learning-rate/leaf/regularization settings.

This protocol covers the sklearn-based tuning layer. XGBoost and LightGBM are handled separately in `reports/model_tuning_advanced/`; AutoGluon and CatBoost are not part of the production evidence unless deliberately installed, rerun, and documented.

## Summary

| target | chosen_by_validation_candidate | model_family | test_rows | test_positives | test_roc_auc | test_pr_auc | test_precision | test_recall | test_f1 | threshold_from_validation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| distress_next_4q | extra_trees_cfg3_seed777 | extra_trees | 5872 | 96 | 0.8093448825600185 | 0.14272962157142668 | 0.17307692307692307 | 0.375 | 0.23684210526315785 | 0.12773606249702307 |
| failure_pressure_conservative_v2_next_4obs | hist_gradient_boosting_cfg4 | hist_gradient_boosting | 5734 | 575 | 0.9409150745425892 | 0.7475900706964291 | 0.6053333333333333 | 0.7895652173913044 | 0.6852830188679244 | 0.13060003930484151 |
| success_resilience_next_4q | random_forest_cfg1_seed202 | random_forest | 4046 | 2647 | 0.9660875475574463 | 0.9740081749427809 | 0.9343228200371058 | 0.9512655836796373 | 0.9427180831149383 | 0.4619163898310619 |

## Thesis Wording

Safe claim: the thesis did not rely on a single one-off model run. It used baseline temporal-validation models, target experiments, seed checks, feature-set ablations, and a controlled hyperparameter-tuning robustness pass.

Unsafe claim: do not say exhaustive global hyperparameter optimization was performed. The correct wording is controlled/random-grid robustness tuning under time and reproducibility constraints.
