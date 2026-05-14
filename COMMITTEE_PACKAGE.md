# Committee Package

This GitHub repository is intentionally a committee-facing reproducibility package, not the full working archive.

The full working archive remains local on the research machine. GitHub keeps only the files needed to:

- open the dashboard,
- inspect the packaged firm panel,
- deploy the dashboard online,
- download fresh SEC and FRED inputs,
- rebuild the firm panel,
- regenerate the compact model/report tables used by the dashboard,
- read the final source-of-truth documentation.

## Included

```text
app/                         Streamlit dashboard
config/                      source catalogs and panel/model configuration
data/github/                 packaged firm panel and schema
data/samples/                compact panel sample and schema
docs/                        final source-of-truth methodology notes only
reports/modeling/            compact dashboard/modeling CSV outputs
reports/target_lab/          compact target-lab dashboard CSV outputs
reports/target_tweak_experiments/ dashboard target/feature-set summaries
reports/figures/dashboard/   dashboard screenshots
scripts/data/                SEC and FRED download helpers
scripts/sec_fsd/             firm-panel rebuild scripts
scripts/modeling/            dashboard-report/model reproduction scripts
scripts/project_audit/       package smoke check
```

## Excluded From GitHub

The following remain local and are deliberately not tracked in the public package:

- raw SEC ZIP downloads,
- raw FRED CSV downloads,
- local processed/interim rebuild tables,
- trained local model binaries,
- old parser experiments,
- deep audit logs,
- legacy plots,
- exploratory report folders not loaded by the dashboard,
- manuscript `.docx` drafts and copies,
- line-by-line thesis audit working files,
- notebooks, caches, and editor files.

## Verification

Run:

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

Expected result:

```text
GitHub package smoke check complete; failures=0
```
