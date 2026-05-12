# Research Gap Assessment

Source reviewed: `../_external_inputs/03_research_gap_inputs/perplexity research gap report.md`.

## Assessment

The report is directionally good and useful for thesis positioning. Its strongest proposed gap is:

> Cross-industry, macro-regime-aware, interpretable prediction of firm success and failure.

This fits the fixed thesis title and the dataset we are rebuilding. It also directly repairs the old thesis weaknesses:

- the old sample had too few true failure cases,
- the old model used random splits,
- the old macro variables were not converted into a clear market-shift/regime argument,
- the old results were not explainable enough.

## What Is Strong

- The gap is not just "use ML for bankruptcy"; that topic is saturated.
- It connects firm financial statements, industry differences, and macro conditions.
- It gives a defensible reason to use FRED macro variables.
- It supports temporal validation and out-of-regime testing.
- It supports SHAP/permutation importance as a thesis contribution, not only as a technical afterthought.

## What Is Weak

- The report is too broad. It mentions survival analysis, project success factors, digital footprints, governance, SMEs, cross-country studies, and macro shocks. We cannot implement all of that by May 14.
- Some cited papers may be weak, inaccessible, or not central enough. The final thesis should use fewer, higher-quality references.
- The "success" side needs to be operationalized carefully. Bankruptcy/failure is clearer than "success." Success should be defined as sustained profitability/resilience, not vague business success.
- Russian company data should not become the main empirical promise unless a clean dataset appears immediately.

## Recommended Thesis Positioning

Use this narrower contribution:

> This thesis develops a reproducible firm-quarter panel from SEC Financial Statement Data Sets and FRED macro data to predict forward-looking firm distress and resilience across industries. It evaluates whether macro-market regime variables improve temporal out-of-sample prediction and uses interpretable machine-learning methods to compare financial success/failure drivers across industries and market regimes.

## Research Questions

1. Do firm-level financial ratios combined with macro-market indicators predict future distress/resilience better than firm-level variables alone?
2. Does model performance remain stable across market regimes such as crisis, low-rate expansion, pandemic shock, inflation/tightening, and post-tightening periods?
3. Which predictors matter most across industries and regimes, and do those drivers differ between large-cap survivors and distressed/smaller firms?

## Final Judgment

We are on the right track. The topic is viable and better than the old version. The risk is not the idea; the risk is execution time. Scope must be frozen around SEC/FRED/U.S. public companies, interpretable ML, dashboard, and thesis writing.
