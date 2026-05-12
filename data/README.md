# Data Folder

Use `data/github/` for the packaged dashboard dataset.

## Included In GitHub

```text
data/github/firm_panel_v2.csv.gz
data/github/firm_panel_v2.parquet
data/github/firm_panel_v2_schema.csv
data/github/README.md
data/samples/
```

`firm_panel_v2.csv.gz` is the dashboard input. `firm_panel_v2.parquet` is the same panel in an analysis-friendly format.

Current packaged panel:

- 31,702 rows
- 190 columns
- 540 SEC CIKs / display tickers
- period range: 2009-03-31 to 2026-02-28

## Not Included In GitHub

```text
data/raw/
data/interim/
data/processed/
```

Those folders are for local raw-data rebuilds. They are intentionally ignored except for placeholder `.gitkeep` files.
