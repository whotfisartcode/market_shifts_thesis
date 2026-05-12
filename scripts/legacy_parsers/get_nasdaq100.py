#!/usr/bin/env python
"""
get_nasdaq100.py
----------------
Fetch the current Nasdaq‑100 tickers from Wikipedia and write
config/ticker100.txt (one ticker per line).
"""

import pandas as pd
from pathlib import Path
import re

URL = "https://en.wikipedia.org/wiki/Nasdaq-100"
TABLES = pd.read_html(URL, header=0)

ticker_col = None
const_df   = None

# Find the table with a column that contains "Ticker"
for tbl in TABLES:
    for col in tbl.columns:
        if re.search("ticker", str(col), re.I):
            ticker_col = col
            const_df = tbl
            break
    if const_df is not None:
        break

if const_df is None:
    raise RuntimeError("Ticker column not found on Wikipedia page. Table structure changed.")

tickers = (
    const_df[ticker_col]
      .astype(str)
      .str.strip()
      .str.replace(r"\.$", "", regex=True)   # strip trailing dots
      .dropna()
      .sort_values()
      .unique()
)

out_path = Path("market_shifts/config/ticker100.txt")
out_path.parent.mkdir(exist_ok=True)
out_path.write_text("\n".join(tickers))
print(f"✅ Wrote {len(tickers)} tickers to {out_path}")
