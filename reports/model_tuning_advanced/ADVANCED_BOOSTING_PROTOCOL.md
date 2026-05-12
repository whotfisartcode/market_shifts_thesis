# Advanced Boosting Experiment Protocol

Last updated: 2026-05-08

This is an advanced benchmark layer for XGBoost and LightGBM. It does not overwrite production models.

## Protocol

- Data source: `data/processed/panel_v2/firm_panel_v2.csv.gz`.
- Split policy: train <= 2018, validation 2019-2021, test 2022-2024.
- Candidate selection uses validation data only.
- Thresholds are selected on validation data using F1.
- Final test metrics are observed after validation selection and must not be used for further tuning.
- Class imbalance is handled with train-split `scale_pos_weight`.

## Candidate Counts

| model_family | candidate_configs |
| --- | --- |
| lightgbm | 12 |
| xgboost | 12 |

## Validation-Selected Summary

| target | chosen_by_validation_candidate | model_family | test_rows | test_positives | test_roc_auc | test_pr_auc | test_precision | test_recall | test_f1 | threshold_from_validation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| distress_next_4q | xgboost_cfg1_seed777 | xgboost | 5872 | 96 | 0.8493199229570637 | 0.14176366670174206 | 0.16783216783216784 | 0.25 | 0.20083682008368203 | 0.48588329553604126 |
| failure_pressure_conservative_v2_next_4obs | lightgbm_cfg4_seed42 | lightgbm | 5734 | 575 | 0.9399610642439974 | 0.7390715018231307 | 0.7170138888888888 | 0.7182608695652174 | 0.7176368375325802 | 0.35455306705270573 |
| success_resilience_next_4q | xgboost_cfg4_seed202 | xgboost | 4046 | 2647 | 0.9652593344104334 | 0.9742192086148127 | 0.9393361312476154 | 0.9301095579901776 | 0.9347000759301444 | 0.44754940271377563 |

## Thesis Wording

Safe claim: XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks using the same temporal validation protocol.

Unsafe claim: do not call the result AutoML or exhaustive search. This is a controlled advanced boosting benchmark.
