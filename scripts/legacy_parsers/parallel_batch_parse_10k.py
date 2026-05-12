#!/usr/bin/env python3
"""
scripts/New14thmayparsing/parallel_batch_parse_10k.py

Batch‐run 10Kparse_regex.py in parallel across all tickers, using all available CPU cores.
"""

import subprocess
from pathlib import Path
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

# ——— CONFIGURATION —————————————————————————————————————————————————————
# Path to your tickers file (one ticker per line)
TICKER_FILE = Path("config/ticker100.txt")

# The 10-K parser you wrote
SCRIPT      = Path("scripts/New14thmayparsing/10Kparse_regex.py")

# EDGAR root
ROOT        = "data/raw/edgar/sec-edgar-filings"

# Always 10-K here
FORM        = "10-K"

# Base output folder for all tickers
OUT_BASE    = Path("data/processed/xbrl/q4quarter_all")
# ——————————————————————————————————————————————————————————————————————————————

def run_ticker(ticker: str):
    tenk_folder = Path(ROOT) / ticker / FORM
    if not tenk_folder.exists() or not tenk_folder.is_dir():
        print(f"⚠️  Skipping {ticker}: no folder at {tenk_folder}")
        return

    out_dir = OUT_BASE / ticker
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", str(SCRIPT),
        "--root", ROOT,
        "--ticker", ticker,
        "--form", FORM,
        "--out", str(out_dir)
    ]
    print(f"▶ Running for {ticker}: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Parser failed for {ticker}: {e}")

def main():
    # read tickers
    tickers = [line.strip() for line in TICKER_FILE.read_text().splitlines() if line.strip()]

    # how many workers? use all cores
    max_workers = os.cpu_count() - 1 
    print(f"ℹ️  Starting parsing on {len(tickers)} tickers with {max_workers} workers...")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_ticker, t): t for t in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            # any unhandled exception in run_ticker will be re-raised here
            try:
                future.result()
            except Exception as exc:
                print(f"❌ Unexpected error on {ticker}: {exc}")

if __name__ == "__main__":
    main()
