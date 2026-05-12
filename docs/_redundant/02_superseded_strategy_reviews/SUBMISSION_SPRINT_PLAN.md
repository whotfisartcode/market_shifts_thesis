# Submission Sprint Plan

Deadline: 2026-05-14 18:00 Europe/Moscow.

This plan is intentionally scoped for submission, not perfection. The goal is a defensible thesis package with a rebuilt dataset, explainable ML results, dashboard, plots, screenshots, and a complete paper.

## Brutal Scope Decision

Keep the title and topic. Do not pivot to Russian company data as the main empirical sample. Russian data can be discussed as a limitation/future extension only unless a clean, ready dataset appears immediately.

The feasible thesis contribution is:

> A cross-industry, macro-regime-aware firm success/distress prediction study using SEC financial statement data, FRED macro indicators, temporal validation, and interpretable machine learning.

This is enough novelty for a master thesis if executed cleanly.

## Time Budget

### May 4-5: Dataset Rebuild

- Parse SEC FSD `sub.txt` and `num.txt` for `config/universe_v2_draft.csv`.
- Build firm-quarter panel in `data/processed/panel_v2/`.
- Add FRED macro features with lags.
- Add simple industry/regime variables.
- Generate data-quality tables.

Exit criteria:

- Panel exists.
- Missingness is measured.
- Target labels exist.
- Data dictionary exists.

### May 6-7: Modeling

- Build baseline logistic regression.
- Build random forest or extra trees.
- Build gradient boosting model.
- Use temporal splits, not random splits.
- Handle imbalance with class weights and threshold tuning.
- Generate ROC-AUC, PR-AUC, confusion matrices, calibration, and top-feature tables.

Exit criteria:

- At least 3 model families run.
- At least one explainability output exists.
- Results are exportable as CSV/PNG.

### May 8: Interpretability and Robustness

- SHAP or permutation importance.
- Feature importance by industry group.
- Feature importance by macro regime.
- Sensitivity checks: no macro features vs macro features, pooled vs industry features, large-cap core vs expanded universe.

Exit criteria:

- 4-6 thesis-ready plots.
- A clear answer to whether market-shift variables improve prediction.

### May 9: Dashboard/API

- Build Streamlit dashboard first.
- Pages/views: overview, data coverage, model results, firm explorer, industry/regime comparison.
- Include screenshots for the thesis.

Exit criteria:

- Dashboard runs locally.
- README explains how to run it.
- Screenshots saved to `reports/figures/dashboard/`.

### May 10-12: Writing

- Rewrite structure around the actual empirical pipeline.
- Focus literature on the gap: cross-industry, macro-regime-aware, interpretable prediction.
- Keep theory concise.
- Add methodology, data, results, dashboard, limitations.

Exit criteria:

- Complete draft exceeds minimum character/page requirement.
- Figures and tables inserted.
- Claims match the actual code outputs.

### May 13: Edit and Package

- Fix formatting, references, captions, table numbering.
- Create GitHub-ready repo state.
- Prepare dataset/sample-data documentation.
- Final dashboard screenshots.

Exit criteria:

- Paper is complete.
- Code package is reproducible.
- No obvious contradiction between paper, code, and dashboard.

### May 14: Final QA

- Export final document.
- Check page/character count.
- Check all screenshots render.
- Check dashboard instructions.
- Submit before 18:00.

## Must Not Do

- Do not build a complex API before the panel/modeling are stable.
- Do not chase Russian data unless it is immediately clean and usable.
- Do not add random small firms.
- Do not use random train/test split as the main result.
- Do not overclaim novelty as state-of-the-art research.

## Minimum Defensible Model Set

- Regularized logistic regression: interpretable baseline.
- Balanced random forest or extra trees: robust nonlinear baseline.
- XGBoost/LightGBM/CatBoost if dependency setup is smooth; otherwise scikit-learn histogram gradient boosting.

## Minimum Defensible Outputs

- Dataset coverage table.
- Missingness table.
- Target class balance table.
- Model comparison table.
- Confusion matrix.
- ROC and precision-recall curves.
- Feature importance / SHAP plot.
- Industry/regime comparison plot.
- Dashboard screenshots.
