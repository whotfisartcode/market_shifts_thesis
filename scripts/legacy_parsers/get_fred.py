

"""
get_fred.py
-----------
Download key macro/fiscal series from FRED and save to data/raw/fred/.
"""

from pathlib import Path
import datetime
import pandas_datareader.data as web

# 1) Configuration: series to fetch
SERIES = {
    "FEDFUNDS": "Effective Federal Funds Rate",
    "GS10":     "10-Year Treasury Constant Maturity Rate",
    "NFCI":     "Chicago Fed National Financial Conditions Index",
    "M2SL":     "M2 Money Stock",
    "GDPC1":    "Real Gross Domestic Product",
    "INDPRO":   "Industrial Production Index",
    "UNRATE":   "Civilian Unemployment Rate",
    "CAPUTLGFRBLTTM": "Capacity Utilization: Total Industry",  # optional if you want fresh pull
}

# 2) Optional extras you may test for added signal
EXTRA = {
    "USEPUINDXD":      "Economic Policy Uncertainty Index (U. Michigan)",
    "VIXCLS":          "CBOE Volatility Index (VIX)",
    "BAMLH0A0HYM2":    "ICE BofA US High Yield OAS Spread",
}

ALL_SERIES = {**SERIES, **EXTRA}

# 3) Date range
START = datetime.datetime(1980, 1, 1)
END   = datetime.datetime.today()

# 4) Output folder
OUTDIR = Path("market_shifts/data/raw/fred")
OUTDIR.mkdir(parents=True, exist_ok=True)

# 5) Fetch loop
for code, desc in ALL_SERIES.items():
    try:
        print(f"→ Fetching {code}: {desc}")
        df = web.DataReader(code, "fred", START, END)
        df.to_csv(OUTDIR / f"{code}.csv")
    except Exception as e:
        print(f"‼️  Failed to fetch {code}: {e}")

print("✅  FRED download completed.")
