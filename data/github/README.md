# GitHub Dataset Package

This folder contains the dataset files intended to be uploaded with the GitHub repository.

Files:

- `firm_panel_v2.csv.gz`: rebuilt SEC/FRED firm-period panel.
- `firm_panel_v2.parquet`: Parquet copy of the rebuilt panel for faster analysis.
- `firm_panel_v2_schema.csv`: column names, dtypes, feature-family labels, and missingness shares.

The full raw SEC ZIPs are not included in GitHub. They can be rebuilt from the official SEC Financial Statement Data Sets by placing quarterly ZIP files in `data/raw/sec_fsd_zips/` and running:

```bash
python3 scripts/sec_fsd/index_submissions.py
python3 scripts/sec_fsd/match_distress_candidates.py
python3 scripts/sec_fsd/build_universe_v2.py
python3 scripts/sec_fsd/build_panel_v2.py
```

Current panel summary:

- Rows: 31,702
- Columns: 190
- SEC CIKs: 540
- Tickers / display IDs: 540
- Period range: 2009-03-31 to 2026-02-28
- Prediction timestamp range: 2009-04-15 to 2026-03-31
- Strict legal distress positives, `distress_next_4q`: 207 positives across 31,702 known labels
- Main broader failure-pressure positives, `failure_pressure_conservative_v2_next_4obs`: 3,003 positives across 29,805 known labels
- Primary success/resilience positives, `success_resilience_next_4q`: 12,519 positives across 20,152 known labels
- Validated secondary industry-relative resilience positives, `industry_relative_resilience_next_4obs`: 8,093 positives across 20,039 known labels
- Validated secondary stress-resilience positives, `stress_resilience_next_4obs`: 3,707 positives across 5,901 known labels
- Validated secondary recovery positives, `recovery_next_4obs`: 5,578 positives across 11,375 known labels
- Validated secondary cash-flow quality success positives, `quality_success_cashflow_next_4obs`: 9,852 positives across 16,767 known labels

The panel includes SEC accounting fundamentals, engineered financial ratios, firm trend/deterioration features, FRED macro variables, macro-regime indicators, curated global-event context, industry metadata, explicit prediction timestamps, post-event flags, and multiple forward-looking success/failure labels.

Flow variables are standardized to single-period values where SEC cumulative filings allow derivation. Remaining unavailable values are left null in the exported dataset.

Primary modeling uses `prediction_date`, which is the SEC `filed_date` for all current rows. Raw filing metadata and target/event columns are retained for auditability but are excluded from model feature lists.

Important caveats:

- `distress_next_4q` is a strict legal/event benchmark and remains rare.
- `failure_pressure_conservative_v2_next_4obs` is the main broader failure-factor target.
- `success_resilience_next_4q` is the main success/resilience target.
- The four secondary target labels are production panel columns, but they should be framed as validated secondary outcomes for dimensional factor analysis rather than replacements for the three primary targets.
- Missing future target components remain null rather than being forced into negative labels.
- Large raw SEC ZIP files are intentionally excluded from the GitHub package.
- The panel has been rebuilt after adding `ddate == period` SEC period filtering and after the 2026-05-09 SEC mapping/caveat-resolution polish. Provenance, audit, model, tuning, feature-interpretation, dashboard screenshot, and project-QA artifacts have been regenerated after those rebuilds. See `../../REPRODUCIBILITY.md` for clone-level setup and smoke-test instructions.
