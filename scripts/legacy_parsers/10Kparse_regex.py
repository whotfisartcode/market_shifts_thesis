#!/usr/bin/env python3
"""
scripts/parse_regex_10k_quarter.py

Robust Q4‐quarter extractor for 10-K filings.
1) Tries explicit contextRef patterns (Q4QTD, STD, ThreeMonths… etc.)
2) Falls back to “last minus second-last” trick if needed.
"""

import argparse, logging, re, datetime
from pathlib import Path

import pandas as pd

# ─── Your GAAP tag map ────────────────────────────────────────────────────
TAG_MAP = {
    # Income Statement
    "SalesRevenueNet":       "sales_revenue_net",
    "Revenues":              "total_revenue",
    "CostOfRevenue":         "cost_of_revenue",
    "GrossProfit":           "gross_profit",
    "ResearchAndDevelopmentExpense":                             "r_and_d_expense",
    "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost": "r_and_d_expense",
    "OperatingIncomeLoss":    "operating_income",
    "EarningsBeforeInterestTaxesDepreciationAndAmortization":"ebitda",
    "DepreciationDepletionAndAmortization":"depreciation_amortization",
    "NetIncomeLoss":          "net_income",

    # Balance Sheet
    "Assets":                 "total_assets",
    "AssetsCurrent":          "current_assets",
    "CashAndCashEquivalentsFairValue":      "cash_equivalents",
    "CashAndCashEquivalentsAtCarryingValue":"cash_equivalents",
    "LiabilitiesCurrent":     "current_liabilities",
    "Liabilities":            "total_liabilities",
    "LiabilitiesAndStockholdersEquity":     "liabilities_plus_equity",
    "InventoryNet":           "inventory",
    "AccountsReceivableNetCurrent":"accounts_receivable",
    "PropertyPlantAndEquipmentNet":"ppe_net",
    "StockholdersEquity":     "total_equity",
    "RetainedEarningsAccumulatedDeficit":"retained_earnings",

    # Cash Flow
    "NetCashProvidedByUsedInOperatingActivities": "cash_flow_operating",
    "NetCashProvidedByUsedInInvestingActivities": "cash_flow_investing",
    "NetCashProvidedByUsedInFinancingActivities": "cash_flow_financing",
    "PaymentsToAcquirePropertyPlantAndEquipment":"capex",
    "DividendsPaidOrganizational":"dividends_paid",

    # Shares & EPS
    "CommonStockSharesOutstanding":"shares_outstanding",
    "WeightedAverageNumberOfSharesOutstandingBasic":"wavg_shares_basic",
    "WeightedAverageNumberOfSharesOutstandingDiluted":"wavg_shares_diluted",
    "EarningsPerShareBasic":"eps_basic",
    "EarningsPerShareDiluted":"eps_diluted",


    # ──────────────────────────────────────────────────────────────
    # Additional Research & Development synonyms
    "ResearchAndDevelopmentCost":                  "r_and_d_expense",
    "ResearchAndDevelopmentExpenseNet":            "r_and_d_expense",
    "ResearchAndDevelopmentCostsAndExpenses":      "r_and_d_expense",
    "EngineeringResearchAndDevelopment":           "r_and_d_expense",
    "DevelopmentAndResearchExpense":               "r_and_d_expense",

    # Extra Income‐Statement synonyms
    "SalesRevenueGoodsNet":                        "sales_revenue_net",
    "NetSales":                                    "sales_revenue_net",
    "TotalNetRevenue":                             "total_revenue",
    "CostsAndExpenses":                            "cost_of_revenue",
    "OperatingProfitLoss":                         "operating_income",
    "ProfitLossFromContinuingOperations":          "net_income",
    "ProfitLoss":                                  "net_income",

    # Extra Balance‐Sheet synonyms
    "PropertyPlantAndEquipmentGross":              "ppe_net",
    "PropertyPlantEquipmentNet":                   "ppe_net",
    "TradeAndOtherReceivablesNet":                 "accounts_receivable",
    "InventoryGross":                              "inventory",
    "CurrentPortionOfLongTermDebt":                "current_liabilities",
    "LongTermDebt":                                "total_liabilities",
    "AdditionalPaidInCapital":                     "total_equity",
    "EquityAttributableToOwnersOfParent":          "total_equity",

    # Extra Cash‐Flow synonyms
    "CashFlowFromOperatingActivities":             "cash_flow_operating",
    "CashFlowFromInvestingActivities":             "cash_flow_investing",
    "CashFlowFromFinancingActivities":             "cash_flow_financing",
    "CapitalExpenditures":                         "capex",
    "PurchasesOfPropertyPlantAndEquipment":        "capex",

    # Extra Shares & EPS synonyms
    "BasicWeightedAverageSharesOutstanding":       "wavg_shares_basic",
    "DilutedWeightedAverageSharesOutstanding":     "wavg_shares_diluted",
    "EarningsPerShareDilutedNumberOfShares":       "eps_diluted",
}

NS = "us-gaap:"  # inline prefix

# ─── Date extraction ─────────────────────────────────────────────────────
RE_DEI     = re.compile(r"<dei:DocumentPeriodEndDate>\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
RE_FILED   = re.compile(r"FILED AS OF DATE:\s*(\d{8})",                 re.IGNORECASE)
RE_CHANGED = re.compile(r"DATE\s+AS\s+OF\s+CHANGE:.*?(\d{8})",         re.IGNORECASE)

def parse_period_end(text: str) -> datetime.date | None:
    m = RE_DEI.search(text)
    if m:
        return datetime.date.fromisoformat(m.group(1))
    m = RE_FILED.search(text) or RE_CHANGED.search(text)
    if m:
        d8 = m.group(1)
        return datetime.date(int(d8[:4]), int(d8[4:6]), int(d8[6:8]))
    return None

def try_patterns(text: str, filing_year: int, end_date: datetime.date, tag: str) -> float | None:
    """
    Attempt explicit patterns first; if none match, fall back to
    subtracting the penultimate from the last numeric fact.
    """
    end_d8 = end_date.strftime("%Y%m%d")

    # 1) exact Q4QTD for this filing year
    pat_q4 = re.compile(
        rf"<{NS}{tag}\b[^>]*contextRef=\"[^\"]*{filing_year}Q4QTD[^\"]*\"[^>]*>\s*([0-9,.\-]+)",
        re.IGNORECASE
    )
    m = pat_q4.search(text)
    if m:
        return float(m.group(1).replace(",", ""))

    # 2) STD_91 or STD_92 style
    pat_std = re.compile(
        rf"<{NS}{tag}\b[^>]*contextRef=\"[^\"]*STD_9[12]_{end_d8}[^\"]*\"[^>]*>\s*([0-9,.\-]+)",
        re.IGNORECASE
    )
    m = pat_std.search(text)
    if m:
        return float(m.group(1).replace(",", ""))

    # 3) ThreeMonthsEndedDDMonYYYY
    for m in re.finditer(
        rf"<{NS}{tag}\b[^>]*contextRef=\"ThreeMonthsEnded(\d{{2}}[A-Za-z]{{3}}\d{{4}})\"[^>]*>\s*([0-9,.\-]+)",
        text, re.IGNORECASE
    ):
        dstr, val = m.groups()
        try:
            d = datetime.datetime.strptime(dstr, "%d%b%Y").date()
            if d == end_date:
                return float(val.replace(",", ""))
        except:
            pass

    # 4) Duration_MM_DD_YYYY_To_MM_DD_YYYY
    m = re.search(
        rf"<{NS}{tag}\b[^>]*contextRef=\"Duration_[^\"]*_To_(\d{{1,2}}_\d{{1,2}}_\d{{4}})\"[^>]*>\s*([0-9,.\-]+)",
        text, re.IGNORECASE
    )
    if m:
        end = datetime.datetime.strptime(m.group(1), "%m_%d_%Y").date()
        if end == end_date:
            return float(m.group(2).replace(",", ""))

    # 5) FROM_MonDD_YYYY_TO_MonDD_YYYY
    m = re.search(
        rf"<{NS}{tag}\b[^>]*contextRef=\"FROM_[^_]+_\d{{4}}_TO_[A-Za-z]{{3}}\d{{1,2}}_(\d{{4}})\"[^>]*>\s*([0-9,.\-]+)",
        text, re.IGNORECASE
    )
    if m:
        return float(m.group(2).replace(",", ""))

    # 6) GENERIC FALLBACK: last two values difference
    vals = [
        float(v.replace(",", ""))
        for v in re.findall(rf"<{NS}{tag}\b[^>]*>\s*([0-9,.\-]+)\s*</{NS}{tag}>", text, re.IGNORECASE)
    ]
    if len(vals) >= 2:
        return vals[-1] - vals[-2]
    if vals:
        # at least give the last (YTD) if no second-to-last
        return vals[-1]

    return None

def parse_10k_quarter(txt_path: Path, ticker: str) -> pd.DataFrame:
    text = txt_path.read_text(errors="ignore")
    end_date = parse_period_end(text)
    if not end_date:
        return pd.DataFrame()
    filing_year = end_date.year

    records = []
    for local, col in TAG_MAP.items():
        val = try_patterns(text, filing_year, end_date, local)
        if val is not None:
            records.append({
                "ticker": ticker,
                "filing": txt_path.parent.name,
                "date":   end_date.isoformat(),
                "tag":    col,
                "value":  val,
                "source": txt_path.name
            })
    return pd.DataFrame(records)

def main(root: Path, ticker: str, form: str, out: Path):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger()
# ─── Skip if we already have an output for this ticker ───────────
    csv_out = out / f"{ticker}_q4quarter.csv"
    if csv_out.exists():
        log.info(f"Output exists ({csv_out}), skipping ticker {ticker}.")
        return
# ──────────────────────────────────────────────────────────────────
    base = root / ticker / form
    if not base.exists():
        log.error(f"No folder: {base}")
        return

    acc_dirs = sorted(d for d in base.iterdir() if d.is_dir())
    log.info(f"Found {len(acc_dirs)} filings for {ticker}/{form}")

    all_dfs, summary = [], []
    for acc in acc_dirs:
        # build path to the canonical filing file
        txt = acc / "full-submission.txt"

        # robustly skip if anything goes wrong checking/reading it
        try:
            # this covers both “doesn’t exist” and OSError/EINVAL on stat
            if not txt.exists() or not txt.is_file():
                raise FileNotFoundError("no full-submission.txt")
        except Exception as e:
            log.warning(f"Skipping {acc.name}: {e}")
            continue

        # now safe to call your parser
        df = parse_10k_quarter(txt, ticker)
        
        df = parse_10k_quarter(txt, ticker)
        summary.append({
            "ticker": ticker,
            "filing": acc.name,
            "file":   txt.name,
            "n_tags": len(df)
        })
        if not df.empty:
            all_dfs.append(df)

    if not all_dfs:
        log.error("No Q4 quarter facts extracted.")
        return

    full = pd.concat(all_dfs, ignore_index=True).drop_duplicates(
        subset=["ticker","date","tag","value"]
    )
    log.info(f"Extracted {len(full)} Q4 records")

    panel = (
        full.pivot_table(
            index=["ticker","date","source"],
            columns="tag",
            values="value",
            aggfunc="first"
        )
        .reset_index()
        .sort_values(["ticker","date"])
    )
    log.info(f"Panel shape: {panel.shape}")

    out.mkdir(parents=True, exist_ok=True)
    panel.to_csv(  out / f"{ticker}_q4quarter.csv",    index=False)
    panel.to_parquet(out / f"{ticker}_q4quarter.parquet", index=False)
    pd.DataFrame(summary).to_csv(out / f"{ticker}_q4quarter_summary.csv",    index=False)
    pd.DataFrame(summary).to_parquet(out / f"{ticker}_q4quarter_summary.parquet", index=False)
    log.info(f"Wrote results to {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root",   type=Path, required=True)
    parser.add_argument("--ticker", type=str,  required=True)
    parser.add_argument("--form",   type=str,  default="10-K")
    parser.add_argument("--out",    type=Path, default=Path("data/processed/xbrl/q4quarter"))
    args = parser.parse_args()
    main(**vars(args))


# python scripts/New14thmayparsing/10Kparse_regex.py --root data/raw/edgar/sec-edgar-filings --ticker AAPL --form 10-K --out data/processed/xbrl/test10K_aapl