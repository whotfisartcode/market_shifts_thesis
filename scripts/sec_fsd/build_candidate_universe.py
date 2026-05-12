#!/usr/bin/env python3
"""Build a controlled candidate universe for the rebuilt thesis panel.

The output is not the final modeling universe. It is a review table that keeps
the old large-cap core and adds distressed/smaller candidates with explicit
source labels and inclusion priorities.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_PATH = CONFIG_DIR / "rebuild_universe_candidates.csv"


def normalize_ticker(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def read_core() -> pd.DataFrame:
    core = pd.read_csv(CONFIG_DIR / "master_tickers.csv")
    core["ticker"] = core["ticker"].map(normalize_ticker)
    core = core[core["ticker"] != ""].copy()
    core["universe_group"] = "legacy_large_cap_core"
    core["candidate_role"] = "core"
    core["event_year"] = pd.NA
    core["event_type"] = pd.NA
    core["priority"] = "keep"
    core["notes"] = "Original defended-thesis large-cap universe."
    return core.rename(columns={"shortname": "company"})


def read_distressed() -> pd.DataFrame:
    distressed = pd.read_csv(CONFIG_DIR / "distressed_candidates_seed.csv")
    distressed["ticker"] = distressed["ticker"].map(normalize_ticker)
    distressed["universe_group"] = "distressed_seed"
    distressed["candidate_role"] = "failure_candidate"
    distressed["Sector"] = pd.NA
    distressed["Industry"] = pd.NA
    distressed["Fulltimeemployees"] = pd.NA
    distressed["Weight"] = pd.NA
    return distressed


def read_extra_tickers() -> pd.DataFrame:
    path = CONFIG_DIR / "ticker100more.txt"
    if not path.exists():
        return pd.DataFrame()

    rows = []
    for raw in path.read_text().splitlines():
        ticker = normalize_ticker(raw)
        if ticker:
            rows.append(
                {
                    "ticker": ticker,
                    "company": pd.NA,
                    "Sector": pd.NA,
                    "Industry": pd.NA,
                    "Fulltimeemployees": pd.NA,
                    "Weight": pd.NA,
                    "event_year": pd.NA,
                    "event_type": pd.NA,
                    "priority": "review",
                    "notes": "Legacy extra ticker list; use only if SEC coverage and matching logic justify inclusion.",
                    "universe_group": "legacy_extra_ticker_list",
                    "candidate_role": "possible_control_or_extra",
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    frames = [frame for frame in [read_core(), read_distressed(), read_extra_tickers()] if not frame.empty]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        df = pd.concat(frames, ignore_index=True, sort=False)

    role_rank = {
        "core": 0,
        "failure_candidate": 1,
        "possible_control_or_extra": 2,
    }
    df["_role_rank"] = df["candidate_role"].map(role_rank).fillna(99)
    df = (
        df.sort_values(["ticker", "_role_rank"])
        .drop_duplicates("ticker", keep="first")
        .drop(columns="_role_rank")
        .sort_values(["candidate_role", "priority", "ticker"])
    )

    ordered = [
        "ticker",
        "company",
        "candidate_role",
        "universe_group",
        "priority",
        "event_year",
        "event_type",
        "Sector",
        "Industry",
        "Fulltimeemployees",
        "Weight",
        "notes",
    ]
    df = df[[col for col in ordered if col in df.columns]]
    df.to_csv(OUTPUT_PATH, index=False)

    counts = df["candidate_role"].value_counts().to_dict()
    print(f"Wrote {OUTPUT_PATH}")
    print(counts)


if __name__ == "__main__":
    main()
