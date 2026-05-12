# Sample Data

Small files in this folder are intended for GitHub. They let another person inspect the legacy panel structure without downloading full local datasets.

Generated files:

- `legacy_panel_sample.csv`: up to 200 example rows from the legacy panel.
- `legacy_panel_schema.csv`: column names, inferred dtypes, and missingness shares.

Regenerate with:

```bash
python3 scripts/data_quality/create_legacy_sample.py
```
