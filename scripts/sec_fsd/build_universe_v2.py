#!/usr/bin/env python3
"""Build a draft expanded universe for the rebuilt thesis panel."""

from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MASTER_PATH = PROJECT_ROOT / "config/master_tickers.csv"
MORE_TICKERS_PATH = PROJECT_ROOT / "config/ticker100more.txt"
DISTRESS_MATCHES_PATH = PROJECT_ROOT / "data/interim/distress_candidate_matches.csv"
SEC_TICKERS_PATH = PROJECT_ROOT / "config/company_tickers_exchange.json"
TICKER_OVERRIDES_PATH = PROJECT_ROOT / "config/ticker_cik_overrides.csv"
SEC_COVERAGE_PATH = PROJECT_ROOT / "reports/data_quality/sec_submission_coverage_by_cik.csv"
LEGACY_PANEL_CSV = PROJECT_ROOT / "data/processed/legacy_2025/firm_panel_with_zscore.csv"
OUT_PATH = PROJECT_ROOT / "config/universe_v2_draft.csv"


def read_ticker_file(path: Path) -> list[str]:
    return [line.strip().upper() for line in path.read_text().splitlines() if line.strip()]


def read_sec_ticker_map() -> pd.DataFrame:
    if not SEC_TICKERS_PATH.exists():
        return pd.DataFrame(columns=["cik", "sec_name", "ticker", "exchange"])

    payload = json.loads(SEC_TICKERS_PATH.read_text())
    ticker_map = pd.DataFrame(payload["data"], columns=payload["fields"])
    ticker_map = ticker_map.rename(columns={"name": "sec_name"})
    ticker_map["ticker"] = ticker_map["ticker"].astype(str).str.upper()
    ticker_map["cik"] = ticker_map["cik"].astype("Int64")
    if TICKER_OVERRIDES_PATH.exists():
        overrides = pd.read_csv(TICKER_OVERRIDES_PATH)
        overrides["ticker"] = overrides["ticker"].astype(str).str.upper()
        overrides["cik"] = overrides["cik"].astype("Int64")
        ticker_map = pd.concat(
            [ticker_map, overrides[["cik", "sec_name", "ticker", "exchange"]]],
            ignore_index=True,
        )
        ticker_map = ticker_map.drop_duplicates("ticker", keep="last")
    return ticker_map


def read_sec_coverage() -> pd.DataFrame:
    if not SEC_COVERAGE_PATH.exists():
        return pd.DataFrame(columns=["cik", "sec_filings", "first_period", "last_period"])

    coverage = pd.read_csv(SEC_COVERAGE_PATH)
    coverage = coverage.sort_values(["cik", "filings"], ascending=[True, False])
    coverage = coverage.drop_duplicates("cik", keep="first")
    coverage = coverage.rename(columns={"filings": "sec_filings"})
    return coverage[["cik", "sec_filings", "first_period", "last_period"]]


def enrich_with_sec(base: pd.DataFrame, ticker_map: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    out = base.merge(ticker_map, on="ticker", how="left")
    out = out.merge(coverage, on="cik", how="left")
    out["firm_id"] = out["cik"].apply(lambda value: f"CIK{int(value):010d}" if pd.notna(value) else "")
    out.loc[out["firm_id"] == "", "firm_id"] = out.loc[out["firm_id"] == "", "ticker"]
    return out


def main() -> None:
    ticker_map = read_sec_ticker_map()
    coverage = read_sec_coverage()

    master = pd.read_csv(MASTER_PATH)
    if LEGACY_PANEL_CSV.exists():
        legacy_tickers = pd.read_csv(LEGACY_PANEL_CSV, usecols=["ticker"])["ticker"].dropna().unique()
        core = pd.DataFrame({"ticker": sorted(legacy_tickers)})
        core = core.merge(master[["ticker", "shortname", "Sector", "Industry"]], on="ticker", how="left")
    else:
        core = master[["ticker", "shortname", "Sector", "Industry"]].copy()
    core = enrich_with_sec(core, ticker_map, coverage)
    core["cohort"] = "core_large_cap"
    core["include_status"] = "include_legacy_core"
    core["notes"] = "Existing defended-thesis universe."

    more_tickers = read_ticker_file(MORE_TICKERS_PATH)
    more = pd.DataFrame(
        {
            "ticker": more_tickers,
            "shortname": "",
            "Sector": "",
            "Industry": "",
            "cohort": "additional_controls",
            "notes": "Existing extra ticker list; use as matched non-distressed controls if SEC coverage is sufficient.",
        }
    )
    more = enrich_with_sec(more, ticker_map, coverage)
    more["include_status"] = "pending_sec_coverage_check"
    more.loc[more["sec_filings"].fillna(0) >= 8, "include_status"] = "include_if_num_tags_parse"

    if DISTRESS_MATCHES_PATH.exists():
        matches = pd.read_csv(DISTRESS_MATCHES_PATH)
        distress = matches[matches["match_status"] == "matched"].copy()
        distress = distress[distress.get("coverage_ok_8_filings", False) == True]
        distress = distress.sort_values(["last_ticker", "filings"], ascending=[True, False])
        distress = distress.drop_duplicates("last_ticker", keep="first")
        distress_out = pd.DataFrame(
            {
                "ticker": distress["last_ticker"],
                "shortname": distress["sec_name"],
                "sec_name": distress["sec_name"],
                "exchange": "",
                "cik": distress["cik"].astype("Int64"),
                "Sector": "",
                "Industry": "",
                "firm_id": "CIK" + distress["cik"].astype("Int64").astype(str).str.zfill(10),
                "cohort": "distress_candidates",
                "include_status": "include_if_num_tags_parse",
                "notes": distress["distress_type"].astype(str)
                + "; event_year="
                + distress["event_year"].astype(str)
                + "; filings="
                + distress["filings"].astype(str),
                "sec_filings": distress["filings"],
                "first_period": distress["first_period"],
                "last_period": distress["last_period"],
            }
        )
    else:
        distress_out = pd.DataFrame(columns=core.columns)

    universe = pd.concat([core, more, distress_out], ignore_index=True)
    universe = universe.drop_duplicates(["cohort", "firm_id"], keep="first")
    column_order = [
        "ticker",
        "cik",
        "firm_id",
        "shortname",
        "sec_name",
        "exchange",
        "Sector",
        "Industry",
        "cohort",
        "include_status",
        "sec_filings",
        "first_period",
        "last_period",
        "notes",
    ]
    universe = universe[[col for col in column_order if col in universe.columns]]
    universe.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(universe):,} draft universe rows to {OUT_PATH}")
    print(universe["cohort"].value_counts().to_string())


if __name__ == "__main__":
    main()
