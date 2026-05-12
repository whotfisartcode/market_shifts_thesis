#!/usr/bin/env python3
"""
scripts/batch_parse_pre2019.py

Master wrapper: runs your coarse‐regex 10Q parser over all tickers.
"""
import subprocess
from pathlib import Path

TICKER_FILE = Path("config/ticker100.txt")
SCRIPT      = Path("scripts/New14thmayparsing/(WORKS)10Qoarse_regex_pre2019.py")
ROOT        = "data/raw/edgar/sec-edgar-filings"
FORM        = "10-Q"
OUT_BASE    = Path("data/processed/xbrl/regex_pre2019_all")

def main():
    tickers = [t.strip() for t in TICKER_FILE.read_text().splitlines() if t.strip()]
    for ticker in tickers:
        out = OUT_BASE / ticker
        out.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python", str(SCRIPT),
            "--root",  ROOT,
            "--ticker",ticker,
            "--form",  FORM,
            "--out",   str(out)
        ]
        print("▶", " ".join(cmd))
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
