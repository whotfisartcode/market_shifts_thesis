#!/usr/bin/env python3
"""Audit the legacy defended-thesis panel.

The script intentionally performs read-only checks and writes compact CSV
summaries under reports/data_quality/.
"""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = PROJECT_ROOT / "data/processed/legacy_2025/firm_panel_with_zscore.parquet"
PANEL_CSV_PATH = PROJECT_ROOT / "data/processed/legacy_2025/firm_panel_with_zscore.csv"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        df = pd.read_parquet(PANEL_PATH)
    except ImportError:
        df = pd.read_csv(PANEL_CSV_PATH)

    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "tickers": df["ticker"].nunique() if "ticker" in df else None,
        "date_min": pd.to_datetime(df["date"]).min() if "date" in df else None,
        "date_max": pd.to_datetime(df["date"]).max() if "date" in df else None,
        "duplicate_ticker_date": int(df.duplicated(["ticker", "date"]).sum())
        if {"ticker", "date"}.issubset(df.columns)
        else None,
    }
    pd.DataFrame([summary]).to_csv(REPORT_DIR / "legacy_panel_summary.csv", index=False)

    missing = (
        df.isna()
        .mean()
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index": "column"})
        .sort_values("missing_share", ascending=False)
    )
    missing.to_csv(REPORT_DIR / "legacy_panel_missingness.csv", index=False)

    numeric = df.select_dtypes(include=[np.number])
    quality_rows = []
    for col in numeric.columns:
        series = numeric[col]
        finite = series.replace([np.inf, -np.inf], np.nan)
        quality_rows.append(
            {
                "column": col,
                "missing": int(series.isna().sum()),
                "inf": int(np.isinf(series.to_numpy(dtype=float, copy=True)).sum()),
                "negative": int((series < 0).sum()),
                "zero": int((series == 0).sum()),
                "min": finite.min(),
                "p01": finite.quantile(0.01),
                "median": finite.median(),
                "p99": finite.quantile(0.99),
                "max": finite.max(),
            }
        )
    pd.DataFrame(quality_rows).to_csv(REPORT_DIR / "legacy_panel_numeric_quality.csv", index=False)

    if {"ticker", "date"}.issubset(df.columns):
        ticker_counts = (
            df.groupby("ticker")
            .size()
            .rename("rows")
            .reset_index()
            .sort_values(["rows", "ticker"], ascending=[False, True])
        )
        ticker_counts.to_csv(REPORT_DIR / "legacy_panel_ticker_counts.csv", index=False)

    print(f"Wrote audit outputs to {REPORT_DIR}")


if __name__ == "__main__":
    main()
