# Next Steps for User

Updated: 2026-05-09

Do these only; the rest can be handled in code.

1. Do not manually edit the production panel. Use it for inspection only:

```text
data/processed/panel_v2/firm_panel_v2.parquet
data/github/firm_panel_v2.parquet
```

2. Keep SEC Financial Statement Data Set ZIP files local in:

```text
data/raw/sec_fsd_zips/
```

Do not unzip them and do not commit them to GitHub.

3. Do not add new core data sources to the main model before submission. RFSD, Hong Kong, Japan, paid datasets, NLP, and live event feeds are future research or appendix ideas now.

4. If adding any new firm candidates, do not add random small companies directly into the universe. Add candidates only with a clear reason and source trail, or ask me to do it.

5. The duplicated `PCG`/`PGNPQ` CIK mapping has been corrected by rebuild. Do not manually edit the panel; use the rebuilt exports only.

If event-review firms are revisited later, classify them carefully. Some are likely M&A/transaction or normal coverage-ending cases, not formal distress. Do not treat firms like Activision Blizzard, VMware, Pioneer Natural Resources, Hawaiian Holdings, or Six Flags as distress without source proof.

6. Use the glossary first when a project field is unclear:

```text
docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md
```

Current state:

- SEC/FRED/global-event panel is already rebuilt.
- +150 rule-selected firms are already added.
- GitHub-ready panel copies already exist.
- Current panel has 31,702 rows, 190 columns, 540 SEC CIKs, and 540 tickers / display IDs after the 2026-05-09 SEC mapping/caveat-resolution rebuild and 2026-05-10 validated-secondary target promotion.
- `prediction_date = filed_date` for every current panel row.
- Final decision plan has been accepted as the controlling direction.
- Formal strict-distress event-date provenance now has 44/44 source-verified formal rows in the current config; 6 near-distress rows remain non-strict context only.
- Market-health index outputs have been generated for dashboard/context use.
- Strict `distress_next_4q` positives increased to 207 after the source-verified event update.
- `failure_pressure_conservative_v2_next_4obs` has been promoted into the production panel as the main broader failure-pressure target.
- The dashboard now separates strict distress, broader failure pressure, and success/resilience views.
- A thesis-grade literature package now exists:
  - `docs/BIBLIOGRAPHY.md`,
  - `docs/references.bib`,
  - `docs/LITERATURE_REVIEW_DRAFT.md`,
  - `docs/INTRODUCTION_RESEARCH_GAP_DRAFT.md`,
  - `docs/THESIS_THEORETICAL_POSITIONING.md`,
  - `reports/literature/literature_matrix.csv`,
  - `reports/literature/source_to_claim_map.csv`,
  - `reports/literature/reference_quality_audit.csv`,
  - `docs/REFERENCE_CRITICAL_EVALUATION.md`,
  - `reports/literature/reference_critical_evaluation.csv`.
- The bibliography currently has 67 verified references, including 51 academic journal articles and 21 sources from 2020 onward.
- Sources with unknown or access-limited full-text status are explicitly labeled; verified metadata is not treated as automatic full-text access.
- A controlled model-tuning robustness pass now exists under `reports/model_tuning/`; it tested 35 candidate configurations per production target and found no candidate failures.
- An advanced XGBoost/LightGBM benchmark now exists under `reports/model_tuning_advanced/`; it tested 24 candidate configurations per production target and found no candidate failures.
- AutoGluon was not installed or used. Do not describe the thesis as AutoML-based unless we deliberately add and validate that workflow later.
- SEC concept mapping has been polished; debt, receivables, R&D, and low-priority revenue fallbacks are now documented in `docs/SEC_MAPPING_POLISH_20260509.md`.
- Production models, feature-group interpretation, dashboard data, screenshots, and the rendered dashboard audit have been refreshed after the 2026-05-09 SEC mapping polish.
- Dashboard polish now includes AAPL as default firm, readable global-event context, non-finite chart guards, cleaner sector/cohort display, and refreshed screenshots.

Next joint work:

- complete GitHub packaging and upload layout from the refreshed manifest;
- write thesis chapters from the chronicle, final reports, and literature-review draft;
- keep checking that every citation supports the exact sentence being written.
