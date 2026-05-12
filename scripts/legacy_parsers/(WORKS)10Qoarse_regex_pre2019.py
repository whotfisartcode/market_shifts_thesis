#!/usr/bin/env python3
"""
scripts/(WORKS)10Qparse_regex_pre2019.py

Extract the FIRST <us-gaap:…> fact for each tag via regex,
pulling the period-end date from any of:
  • <dei:DocumentPeriodEndDate>YYYY-MM-DD</dei:…>
  • FILED AS OF DATE:    YYYYMMDD
  • DATE AS OF CHANGE:   … YYYYMMDD

No HTML parser, no Arelle—pure regex.
"""
import argparse, logging, re
from pathlib import Path

import pandas as pd

# ─── Tag map (localName → output column) ────────────────────────────────
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

NS = "us-gaap:"  # prefix to scan for

# ─── Regexes ─────────────────────────────────────────────────────────────
# 1) three ways to get the date
RE_DEI       = re.compile(r"<dei:DocumentPeriodEndDate>\s*(\d{4}-\d{2}-\d{2})\s*</dei:DocumentPeriodEndDate>", re.IGNORECASE)
RE_FILED     = re.compile(r"FILED AS OF DATE:\s*(\d{8})", re.IGNORECASE)
RE_CHANGED   = re.compile(r"DATE\s+AS\s+OF\s+CHANGE:.*?(\d{8})", re.IGNORECASE)
# 2) match first us-gaap tag instance
#    note: group(1) is the localName, group(2) is the number text
RE_TAG_FIRST = {
    local: re.compile(
        rf"<{NS}{local}\b[^>]*>\s*([0-9,\.\-]+)\s*</{NS}{local}>",
        re.IGNORECASE
    )
    for local in TAG_MAP
}


def parse_submission(txt_path: Path, ticker: str) -> pd.DataFrame:
    """
    Read full-submission.txt, extract one date and the FIRST occurrence
    of each TAG_MAP item. Returns an empty DataFrame if no date or no tags.
    """
    text = txt_path.read_text(errors="ignore")

    # 1) find the date
    m = RE_DEI.search(text)
    if m:
        date = m.group(1)
    else:
        m = RE_FILED.search(text) or RE_CHANGED.search(text)
        if not m:
            return pd.DataFrame()
        d8 = m.group(1)
        date = f"{d8[:4]}-{d8[4:6]}-{d8[6:]}"

    records = []
    for local, col in TAG_MAP.items():
        pat = RE_TAG_FIRST[local]
        m2 = pat.search(text)
        if not m2:
            continue
        valtxt = m2.group(1).replace(",", "")
        try:
            val = float(valtxt)
        except ValueError:
            continue
        records.append({
            "ticker": ticker,
            "filing": txt_path.parent.name,
            "date":   date,
            "tag":    col,
            "value":  val,
            "source": txt_path.name,
        })

    return pd.DataFrame(records)


def main(root: Path, ticker: str, form: str, out: Path):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger()

    base = root / ticker / form
    if not base.exists():
        log.error(f"No folder: {base}")
        return

    acc_dirs = sorted(d for d in base.iterdir() if d.is_dir())
    log.info(f"Found {len(acc_dirs)} filings under {ticker}/{form}")

    all_rows, summary = [], []
    for acc in acc_dirs:
        txt = acc / "full-submission.txt"
        if not txt.exists():
            log.warning(f"Skipping {acc.name}: no full-submission.txt")
            continue

        df = parse_submission(txt, ticker)
        summary.append({
            "ticker": ticker,
            "filing": acc.name,
            "file":   txt.name,
            "n_tags": len(df),
        })
        if not df.empty:
            all_rows.append(df)

    if not all_rows:
        log.error("No XBRL facts extracted.")
        return

    # concat & dedupe
    full = pd.concat(all_rows, ignore_index=True).drop_duplicates(
        subset=["ticker", "date", "tag", "value"]
    )
    log.info(f"Extracted {len(full)} facts total")

    # pivot to wide form
    panel = (
        full
        .pivot_table(
            index=["ticker", "date", "source"],
            columns="tag",
            values="value",
            aggfunc="first"
        )
        .reset_index()
        .sort_values(["ticker", "date"])
    )
    log.info(f"Panel shape: {panel.shape}")

    # write outputs
    out.mkdir(parents=True, exist_ok=True)
    panel.to_csv(  out / f"{ticker}_pre2019_regex.csv",    index=False)
    panel.to_parquet(out / f"{ticker}_pre2019_regex.parquet",index=False)
    pd.DataFrame(summary).to_csv(
        out / f"{ticker}_pre2019_summary.csv",    index=False
    )
    pd.DataFrame(summary).to_parquet(
        out / f"{ticker}_pre2019_summary.parquet",index=False
    )
    log.info(f"Wrote files into {out!s}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root",   type=Path, required=True, help="EDGAR root folder")
    p.add_argument("--ticker", type=str,  required=True, help="Ticker, e.g. AAPL")
    p.add_argument("--form",   type=str,  default="10-Q", help="Form folder")
    p.add_argument("--out",    type=Path, default=Path("data/processed/xbrl/regex_pre2019"),
                   help="Output folder")
    args = p.parse_args()
    main(**vars(args))



# python scripts/New14thmayparsing/parse_regex_pre2019.py --root data/raw/edgar/sec-edgar-filings --ticker AAPL --form 10-Q --out data/processed/xbrl/testpre2019_aapl


