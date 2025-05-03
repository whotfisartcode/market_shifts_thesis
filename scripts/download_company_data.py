#!/usr/bin/env python
"""
download_company_data.py
------------------------
For every ticker in config/tickers.txt:
  • downloads monthly price history
  • downloads quarterly income statement and balance sheet
Saves everything under data/raw/
"""

import yfinance as yf
from pathlib import Path

# ---------- folders ----------
RAW_PRICE_DIR = Path("market_shifts/data/raw/company_price")
RAW_FIN_DIR   = Path("market_shifts/data/raw/company_financials")
RAW_PRICE_DIR.mkdir(parents=True, exist_ok=True)
RAW_FIN_DIR.mkdir(parents=True, exist_ok=True)

# ---------- load ticker list ----------
tickers = Path("market_shifts/config/tickers.txt").read_text().split()
print(f"Found {len(tickers)} tickers")

# ---------- loop and download ----------
for t in tickers:
    print(f"↳ downloading {t}")
    tk = yf.Ticker(t)

    # 1) monthly price
    hist = tk.history(period="max", interval="1mo")
    hist.to_csv(RAW_PRICE_DIR / f"{t}_price.csv")

    # 2) quarterly income + balance sheet
    fin = tk.quarterly_financials.T
    bs  = tk.quarterly_balance_sheet.T
    fin.to_csv(RAW_FIN_DIR / f"{t}_income.csv")
    bs.to_csv (RAW_FIN_DIR / f"{t}_bs.csv")

print("✅  All downloads complete")
