#!/usr/bin/env python
"""
download_edgar_bulk.py
----------------------
Bulk-download 10-Q and 10-K filings for tickers in config/ticker100.txt.

• 10-Q → all available quarters
• 10-K → last 15 years

Requirements:
    pip install sec-edgar-downloader tqdm
"""

from sec_edgar_downloader import Downloader
from pathlib import Path
from tqdm import tqdm
import time

# ── Configuration ────────────────────────────────────────────────────────────────
COMPANY_NAME   = "Artem Kozin Master Thesis - Predictive analytics into company success"                 # your name or project
EMAIL_ADDRESS  = "kozinartem.1910@gmail.com"                 # your email
DOWNLOAD_ROOT  = Path("data/raw/edgar/sec-edgar-60")               # base download folder
TICKER_FILE    = Path("config/ticker60.txt")        # one ticker per line
FORMS = [
    ("10-Q", None),   # None → download all available quarterly filings
    ("10-K",  15)     # download last 15 annual filings
]
PAUSE_S = 0.2      # seconds sleep between each call (politeness)
# ────────────────────────────────────────────────────────────────────────────────

# initialise downloader
dl = Downloader(
    download_folder=str(DOWNLOAD_ROOT),
    company_name=COMPANY_NAME,
    email_address=EMAIL_ADDRESS
)

tickers = TICKER_FILE.read_text().split()

for form, limit in FORMS:
    desc = f"{form} filings"
    for tk in tqdm(tickers, desc=desc):
        try:
            # call signature: get(filing_type, company, limit=...)
            dl.get(form, tk, limit=limit)
        except Exception as e:
            print(f"⚠️ {tk} {form} error: {e}")
        time.sleep(PAUSE_S)

print("✅ All requested filings have been queued/downloaded.")
