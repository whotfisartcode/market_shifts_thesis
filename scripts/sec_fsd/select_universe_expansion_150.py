#!/usr/bin/env python3
"""Select a controlled +150 firm universe expansion.

The expansion is deliberately rule-based:

- 75 coverage-ended / event-review firms with good SEC coverage until filings stop.
- 75 matched long-coverage current-public controls.

Coverage-ended firms are not automatically labeled as formal distress. They
enter the panel as historical/event-review firms unless a verified event date
is later added to config/distress_event_dates.csv.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"
INTERIM_DIR = PROJECT_ROOT / "data/interim"

UNIVERSE_PATH = CONFIG_DIR / "universe_v2_draft.csv"
BASELINE_UNIVERSE_PATH = CONFIG_DIR / "universe_v2_pre_expansion_20260505.csv"
EXPANSION_CANDIDATES_PATH = CONFIG_DIR / "universe_expansion_150_candidates.csv"
EXPANDED_UNIVERSE_PATH = CONFIG_DIR / "universe_v2_draft_expanded_150.csv"
SEC_TICKERS_PATH = CONFIG_DIR / "company_tickers_exchange.json"
TICKER_OVERRIDES_PATH = CONFIG_DIR / "ticker_cik_overrides.csv"
SUBMISSIONS_INDEX_PATH = INTERIM_DIR / "sec_submissions_index.csv"
SEC_COVERAGE_PATH = REPORT_DIR / "sec_submission_coverage_by_cik.csv"

TARGET_EXIT_REVIEW = 75
TARGET_CONTROLS = 75


def map_sic_to_sector(value: object) -> str | float:
    if pd.isna(value):
        return np.nan
    try:
        sic = int(float(value))
    except ValueError:
        return np.nan

    if 100 <= sic <= 999:
        return "Agriculture"
    if 1000 <= sic <= 1499:
        return "Energy"
    if 1500 <= sic <= 1799:
        return "Industrials"
    if 2000 <= sic <= 3999:
        if 2830 <= sic <= 2839 or 3840 <= sic <= 3859:
            return "Healthcare"
        if 3570 <= sic <= 3579 or 3670 <= sic <= 3679 or 3820 <= sic <= 3829:
            return "Technology"
        if 3710 <= sic <= 3799:
            return "Consumer Cyclical"
        return "Industrials"
    if 4000 <= sic <= 4999:
        if 4810 <= sic <= 4899:
            return "Communication Services"
        if 4900 <= sic <= 4999:
            return "Utilities"
        return "Industrials"
    if 5000 <= sic <= 5999:
        return "Consumer Cyclical"
    if 6000 <= sic <= 6799:
        if 6500 <= sic <= 6799:
            return "Real Estate"
        return "Financial Services"
    if 7000 <= sic <= 8999:
        if 7370 <= sic <= 7379:
            return "Technology"
        if 8000 <= sic <= 8099:
            return "Healthcare"
        if 7800 <= sic <= 7999:
            return "Communication Services"
        return "Industrials"
    return np.nan


def normalize_name(value: object) -> str:
    text = str(value).upper()
    for token in ["/DE", "/DE/", " INC", " CORP", " CORPORATION", " CO", " LTD", " PLC", " HOLDINGS", " GROUP"]:
        text = text.replace(token, "")
    return " ".join(text.replace(",", " ").replace(".", " ").split()).title()


def read_current_ticker_map() -> pd.DataFrame:
    payload = json.loads(SEC_TICKERS_PATH.read_text())
    out = pd.DataFrame(payload["data"], columns=payload["fields"])
    out = out.rename(columns={"name": "current_sec_name"})
    out["ticker"] = out["ticker"].astype(str).str.upper()
    out["cik"] = out["cik"].astype("Int64")

    if TICKER_OVERRIDES_PATH.exists():
        overrides = pd.read_csv(TICKER_OVERRIDES_PATH)
        overrides = overrides.rename(columns={"sec_name": "current_sec_name"})
        overrides["ticker"] = overrides["ticker"].astype(str).str.upper()
        overrides["cik"] = overrides["cik"].astype("Int64")
        out = pd.concat([out, overrides[["cik", "current_sec_name", "ticker", "exchange"]]], ignore_index=True)

    out["share_class_rank"] = out["ticker"].str.contains("-", regex=False).astype(int)
    out = out.sort_values(["cik", "share_class_rank", "ticker"]).drop_duplicates("cik", keep="first")
    out = out.drop(columns=["share_class_rank"])
    return out


def modal_nonempty(series: pd.Series) -> object:
    values = series.dropna().astype(str)
    values = values[values.str.len() > 0]
    if values.empty:
        return pd.NA
    return values.value_counts().index[0]


def build_coverage_table() -> pd.DataFrame:
    coverage = pd.read_csv(SEC_COVERAGE_PATH)
    submissions = pd.read_csv(
        SUBMISSIONS_INDEX_PATH,
        usecols=["cik", "countryba", "stprba", "sic"],
        low_memory=False,
    )
    submissions["cik"] = pd.to_numeric(submissions["cik"], errors="coerce").astype("Int64")
    sub_meta = (
        submissions.groupby("cik", dropna=False)
        .agg(
            countryba=("countryba", modal_nonempty),
            stprba=("stprba", modal_nonempty),
            sic_from_index=("sic", modal_nonempty),
        )
        .reset_index()
    )

    out = coverage.merge(sub_meta, on="cik", how="left")
    out["cik"] = pd.to_numeric(out["cik"], errors="coerce").astype("Int64")
    out["sic"] = out["sic"].fillna(out["sic_from_index"])
    out["Sector"] = out["sic"].map(map_sic_to_sector)
    out["first_year"] = pd.to_numeric(out["first_period"], errors="coerce") // 10000
    out["last_year"] = pd.to_numeric(out["last_period"], errors="coerce") // 10000
    return out


def round_robin_select(candidates: pd.DataFrame, target: int, sector_targets: dict[str, int] | None = None) -> pd.DataFrame:
    candidates = candidates.copy()
    candidates["Sector"] = candidates["Sector"].fillna("Unknown")
    selected_indexes: list[int] = []
    used = set()

    if sector_targets:
        for sector, count in sector_targets.items():
            sector_frame = candidates[candidates["Sector"] == sector].head(count)
            for index in sector_frame.index:
                if index not in used:
                    selected_indexes.append(index)
                    used.add(index)
        if len(selected_indexes) >= target:
            return candidates.loc[selected_indexes[:target]].copy()

    sector_order = (
        candidates.groupby("Sector")["filings"]
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )
    while len(selected_indexes) < target:
        added = False
        for sector in sector_order:
            available = candidates[(candidates["Sector"] == sector) & (~candidates.index.isin(used))]
            if available.empty:
                continue
            index = available.index[0]
            selected_indexes.append(index)
            used.add(index)
            added = True
            if len(selected_indexes) >= target:
                break
        if not added:
            break
    return candidates.loc[selected_indexes].copy()


def main() -> None:
    universe_source = BASELINE_UNIVERSE_PATH if BASELINE_UNIVERSE_PATH.exists() else UNIVERSE_PATH
    universe = pd.read_csv(universe_source)
    if not BASELINE_UNIVERSE_PATH.exists():
        universe.to_csv(BASELINE_UNIVERSE_PATH, index=False)

    current_map = read_current_ticker_map()
    coverage = build_coverage_table()
    coverage = coverage.merge(current_map, on="cik", how="left")
    coverage["has_current_ticker"] = coverage["ticker"].notna()
    coverage["coverage_span_years"] = coverage["last_year"] - coverage["first_year"] + 1
    coverage["name_clean"] = coverage["name"].map(normalize_name)

    existing_ciks = set(pd.to_numeric(universe["cik"], errors="coerce").dropna().astype(int))
    base = coverage[~coverage["cik"].astype("Int64").isin(existing_ciks)].copy()
    base = base[base["countryba"].fillna("US").eq("US")].copy()
    base = base[base["forms"].fillna("").str.contains("10-K") & base["forms"].fillna("").str.contains("10-Q")]
    non_operating_pattern = "SPDR|ISHARES|PROSHARES|VANGUARD|ETF|INDEX FUND|ACQUISITION CORP|ACQUISITION COMPANY|BLANK CHECK"
    base = base[~base["name"].fillna("").str.contains(non_operating_pattern, case=False, regex=True)].copy()

    exit_candidates = base[
        (base["filings"] >= 35)
        & (base["first_period"] <= 20181231)
        & (base["last_period"].between(20111231, 20240630))
        & ((~base["has_current_ticker"]) | (base["last_period"] <= 20231231))
        & (base["afs_values"].fillna("").str.contains("1-LAF|2-ACC", regex=True))
        & (base["Sector"].notna())
        & (base["Sector"] != "Unknown")
    ].copy()
    exit_candidates["selection_bucket"] = "coverage_ended_event_review"
    exit_candidates["selection_score"] = (
        exit_candidates["filings"].rank(method="dense", ascending=True)
        + exit_candidates["last_period"].rank(method="dense", ascending=True) / 100
        - exit_candidates["first_period"].rank(method="dense", ascending=False) / 1000
    )
    exit_candidates = exit_candidates.sort_values(
        ["filings", "last_period", "first_period"],
        ascending=[False, False, True],
    )
    selected_exit = round_robin_select(exit_candidates, TARGET_EXIT_REVIEW)

    exit_sector_counts = selected_exit["Sector"].fillna("Unknown").value_counts().to_dict()

    control_candidates = base[
        (base["has_current_ticker"])
        & (~base["ticker"].fillna("").str.contains("-", regex=False))
        & (base["filings"] >= 50)
        & (base["first_period"] <= 20111231)
        & (base["last_period"] >= 20240930)
        & (base["afs_values"].fillna("").str.contains("1-LAF|2-ACC", regex=True))
        & (base["Sector"].notna())
        & (base["Sector"] != "Unknown")
        & (~base["cik"].isin(selected_exit["cik"]))
    ].copy()
    control_candidates["selection_bucket"] = "long_coverage_matched_control"
    control_candidates["selection_score"] = (
        control_candidates["filings"].rank(method="dense", ascending=True)
        + control_candidates["last_period"].rank(method="dense", ascending=True) / 100
        - control_candidates["first_period"].rank(method="dense", ascending=False) / 1000
    )
    control_candidates = control_candidates.sort_values(
        ["Sector", "filings", "last_period", "first_period"],
        ascending=[True, False, False, True],
    )
    selected_controls = round_robin_select(control_candidates, TARGET_CONTROLS, exit_sector_counts)

    selected = pd.concat([selected_exit, selected_controls], ignore_index=True)
    selected["selected_rank_within_bucket"] = selected.groupby("selection_bucket").cumcount() + 1

    selected["selected_ticker"] = selected["ticker"].fillna(
        "CIK" + selected["cik"].astype("Int64").astype(str).str.zfill(10)
    )
    selected["selected_exchange"] = selected["exchange"].fillna("historical_or_delisted")
    selected["selected_shortname"] = selected["current_sec_name"].fillna(selected["name_clean"])
    selected["selected_industry"] = "SIC " + selected["sic"].fillna("").astype(str)

    candidate_report_cols = [
        "selection_bucket",
        "selected_rank_within_bucket",
        "selected_ticker",
        "cik",
        "name",
        "selected_shortname",
        "selected_exchange",
        "Sector",
        "selected_industry",
        "filings",
        "first_period",
        "last_period",
        "countryba",
        "stprba",
        "sic",
        "forms",
        "afs_values",
        "has_current_ticker",
        "selection_score",
    ]
    selected[candidate_report_cols].to_csv(EXPANSION_CANDIDATES_PATH, index=False)

    expansion_rows = pd.DataFrame(
        {
            "ticker": selected["selected_ticker"],
            "cik": selected["cik"].astype("Int64"),
            "firm_id": "CIK" + selected["cik"].astype("Int64").astype(str).str.zfill(10),
            "shortname": selected["selected_shortname"],
            "sec_name": selected["name"],
            "exchange": selected["selected_exchange"],
            "Sector": selected["Sector"],
            "Industry": selected["selected_industry"],
            "cohort": selected["selection_bucket"].map(
                {
                    "coverage_ended_event_review": "expansion_event_review",
                    "long_coverage_matched_control": "expansion_matched_controls",
                }
            ),
            "include_status": "include_if_num_tags_parse",
            "sec_filings": selected["filings"],
            "first_period": selected["first_period"],
            "last_period": selected["last_period"],
            "notes": np.where(
                selected["selection_bucket"].eq("coverage_ended_event_review"),
                "2026 expansion: coverage-ended event-review firm; not a formal distress label until manually verified; good SEC coverage until last_period="
                + selected["last_period"].astype(str),
                "2026 expansion: long-coverage matched control with current SEC ticker and filings from around 2009 onward.",
            ),
        }
    )

    expanded = pd.concat([universe, expansion_rows], ignore_index=True)
    expanded = expanded[universe.columns]
    expanded.to_csv(EXPANDED_UNIVERSE_PATH, index=False)
    expanded.to_csv(UNIVERSE_PATH, index=False)

    print(f"Selected {len(selected_exit)} event-review firms and {len(selected_controls)} controls")
    print(f"Wrote {EXPANSION_CANDIDATES_PATH}")
    print(f"Wrote expanded universe with {len(expanded):,} rows to {UNIVERSE_PATH}")
    print(expanded["cohort"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
