#!/usr/bin/env python3
"""Create small GitHub-safe samples from the legacy panel."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PANEL_PARQUET = PROJECT_ROOT / "data/processed/legacy_2025/firm_panel_with_zscore.parquet"
PANEL_CSV = PROJECT_ROOT / "data/processed/legacy_2025/firm_panel_with_zscore.csv"
SAMPLE_DIR = PROJECT_ROOT / "data/samples"


def read_panel() -> pd.DataFrame:
    try:
        return pd.read_parquet(PANEL_PARQUET)
    except ImportError:
        return pd.read_csv(PANEL_CSV)


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    df = read_panel()

    sample = (
        df.sort_values(["ticker", "date"])
        .groupby("ticker", group_keys=False)
        .head(2)
        .head(200)
    )
    sample.to_csv(SAMPLE_DIR / "legacy_panel_sample.csv", index=False)

    schema = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": [str(dtype) for dtype in df.dtypes],
            "missing_share": [df[col].isna().mean() for col in df.columns],
        }
    )
    schema.to_csv(SAMPLE_DIR / "legacy_panel_schema.csv", index=False)

    print(f"Wrote sample files to {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
