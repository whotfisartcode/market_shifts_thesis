#!/usr/bin/env python3
"""
scripts/build_firm_panel.py

Merge all 10-Q and 10-K parsed panels into one raw firm panel.
Skips missing/empty files, concatenates, sorts, drops 'source'.
Writes CSV + Parquet to data/processed/firms/firm_panel_raw.*
"""
import argparse
from pathlib import Path

import pandas as pd

# ─── Config ─────────────────────────────────────────────────────────────
TICKER_FILE = Path("config/ticker100.txt")
OUT_DIR     = Path("data/processed/firms")
OUT_CSV     = OUT_DIR / "firm_panel_raw.csv"
OUT_PQT     = OUT_DIR / "firm_panel_raw.parquet"

Q2_ROOT     = Path("data/processed/xbrl/regex_all")
K4_ROOT     = Path("data/processed/xbrl/q4quarter_all")
# ────────────────────────────────────────────────────────────────────────

def load_panel(path_csv: Path, path_pqt: Path) -> pd.DataFrame:
    """
    Load CSV if present, else Parquet if present.
    Returns empty DataFrame if neither exists or if file is empty.
    """
    df = pd.DataFrame()
    if path_csv.exists():
        df = pd.read_csv(path_csv)
    elif path_pqt.exists():
        df = pd.read_parquet(path_pqt)
    # skip empty
    if df.empty:
        return pd.DataFrame()
    return df

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tickers = [t.strip() for t in TICKER_FILE.read_text().splitlines() if t.strip()]

    panels = []
    for ticker in tickers:
        # 10-Q
        q_csv = Q2_ROOT / ticker / f"{ticker}_pre2019_regex.csv"
        q_pqt = Q2_ROOT / ticker / f"{ticker}_pre2019_regex.parquet"
        df_q = load_panel(q_csv, q_pqt)
        if not df_q.empty:
            panels.append(df_q)
        # 10-K
        k_csv = K4_ROOT / ticker / f"{ticker}_q4quarter.csv"
        k_pqt = K4_ROOT / ticker / f"{ticker}_q4quarter.parquet"
        df_k = load_panel(k_csv, k_pqt)
        if not df_k.empty:
            panels.append(df_k)

    if not panels:
        print("❌ No data found for any ticker — check paths and ticker list.")
        return

    # concatenate, sort, drop source
    firm_panel = pd.concat(panels, ignore_index=True)
    if "source" in firm_panel.columns:
        firm_panel = firm_panel.drop(columns=["source"])
    firm_panel = firm_panel.sort_values(["ticker", "date"])
    
    # write out
    firm_panel.to_csv(OUT_CSV, index=False)
    firm_panel.to_parquet(OUT_PQT, index=False)
    print(f"✅ Wrote raw firm panel with {len(firm_panel)} rows to:")
    print(f"   • {OUT_CSV}")
    print(f"   • {OUT_PQT}")

if __name__ == "__main__":
    main()
