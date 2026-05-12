# scripts/get_sp500_tickers.py

import pandas as pd

# 1) Read the S&P 500 table from Wikipedia
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
df  = pd.read_html(url, header=0)[0]

# 2) Extract the Symbol column
tickers = df["Symbol"].sort_values().tolist()

# 3) Print them (or save to a file)
print(", ".join(tickers))

# 4) Optionally save to config/tickers_sp500.txt
with open("market_shifts/config/tickers.txt", "w") as f:
    f.write("\n".join(tickers))
print(f"Saved {len(tickers)} tickers to config/tickers_sp500.txt")
