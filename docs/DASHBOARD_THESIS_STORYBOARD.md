# Dashboard Thesis Storyboard

Updated: 2026-05-09

The dashboard should tell the thesis story in this order:

1. Dataset and target composition: what is in the panel and how strict distress, broader failure pressure, success/resilience, and ordinary observations differ.
2. Data coverage and missingness: why nulls are preserved and how feature families differ.
3. Models: strict distress as rare-event benchmark, broader failure pressure as main failure-factor target, success/resilience as counterpart.
4. Target lab and factor groups: feature groups are the preferred economic interpretation layer.
5. Firm explorer: firm fundamentals, ratios, deterioration, macro context, and target timeline are separated so scales and labels are not confused.
6. Artifact notes: scope, reproducibility, caveats, and safe/unsafe claims.

## Checklist

| item | status | thesis_use |
| --- | --- | --- |
| Overview outcome composition | implemented | Use for thesis result screenshot; explains where strict distress, pressure, success, and ordinary observations fit. |
| Target coverage by year | implemented | Use to explain why labels have different denominators and why null targets are unknown. |
| Firm metrics selector | implemented | Use financial fields only; targets are separated into target timeline. |
| Macro comparison standardization | implemented | Default training-period baseline; caption explains z-score baseline. |
| Target timeline separated from firm metrics | implemented | Prevents target labels from being mixed with raw financial metrics. |
| Model metrics and top features | implemented | Use with caveat that feature importance is association, not causality. |
| Factor-group view | implemented | Preferred for thesis interpretation over isolated single features. |
| Artifact caveat panel | implemented_with_caveats | Includes explicit caveat controls and source-of-truth pointers; strict event-date provenance is PASS for current formal rows. |
| Final screenshots | implemented | Screenshots already saved under reports/figures/dashboard/. |
