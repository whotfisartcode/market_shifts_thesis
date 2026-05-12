#!/usr/bin/env python3
"""
scripts/preprocess_sp500.py

Load the raw S&P 500 CSV, keep only date, ticker, adj_close, volume,
and write out a clean, sorted Parquet and CSV for downstream use.
"""
import pandas as pd
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────
PR      = Path(__file__).resolve().parent.parent
RAW     = PR / "data/raw/kaggle sxp500/sp500_stocks.csv"
OUT_DIR = PR / "data/processed/sp500"
OUT_CSV = OUT_DIR / "sp500_clean.csv"
OUT_PQT = OUT_DIR / "sp500_clean.parquet"
# ────────────────────────────────────────────────────────────────────────

def main():
    # ensure output folder exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) load raw CSV
    df = pd.read_csv(RAW, parse_dates=["Date"], infer_datetime_format=True)
    print("Raw columns:", df.columns.tolist())

    # 2) select & rename the columns we need
    keep = {}
    # date
    if "Date" in df.columns:
        keep["Date"] = "date"
    elif "date" in df.columns:
        keep["date"] = "date"
    else:
        raise KeyError("No Date column found in sp500_stocks.csv")

    # ticker symbol
    if "Symbol" in df.columns:
        keep["Symbol"] = "ticker"
    elif "symbol" in df.columns:
        keep["symbol"] = "ticker"
    else:
        raise KeyError("No Symbol column found in sp500_stocks.csv")

    # adjusted close
    if "Adj Close" in df.columns:
        keep["Adj Close"] = "adj_close"
    elif "Adj_Close" in df.columns:
        keep["Adj_Close"] = "adj_close"
    else:
        raise KeyError("No Adj Close column found in sp500_stocks.csv")

    # volume
    vol_col = next((c for c in df.columns if c.lower() == "Volume"), None)
    if vol_col:
        keep[vol_col] = "Volume"
    else:
        print("⚠️  Volume column not found; proceeding without volume")

    print("Keeping columns:", list(keep.keys()))
    clean = df[list(keep.keys())].rename(columns=keep)

    # 3) ensure date is datetime
    clean["date"] = pd.to_datetime(clean["date"])

    # 4) sort by ticker & date
    clean = clean.sort_values(["ticker", "date"]).reset_index(drop=True)

    # 5) write out
    clean.to_csv(OUT_CSV, index=False)
    clean.to_parquet(OUT_PQT, index=False)
    print(f"✅ Wrote cleaned S&P 500 data to:\n  {OUT_CSV}\n  {OUT_PQT}")

if __name__ == "__main__":
    main()
