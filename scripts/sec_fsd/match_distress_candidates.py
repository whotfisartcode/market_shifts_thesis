#!/usr/bin/env python3
"""Match manually seeded distress candidates to SEC FSD submission coverage."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = PROJECT_ROOT / "config/distress_candidate_seed.csv"
LEGACY_SEED_PATH = PROJECT_ROOT / "config/distressed_candidates_seed.csv"
COVERAGE_PATH = PROJECT_ROOT / "reports/data_quality/sec_submission_coverage_by_cik.csv"
OUT_DIR = PROJECT_ROOT / "data/interim"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"


def normalize(value: object) -> str:
    return "".join(ch for ch in str(value).upper() if ch.isalnum())


def read_seeds() -> pd.DataFrame:
    seed_frames = []
    if SEED_PATH.exists():
        seed_frames.append(pd.read_csv(SEED_PATH))

    if LEGACY_SEED_PATH.exists():
        legacy = pd.read_csv(LEGACY_SEED_PATH)
        legacy = legacy.rename(
            columns={
                "ticker": "last_ticker",
                "company": "company_name_pattern",
                "event_type": "distress_type",
            }
        )
        legacy["distress_type"] = legacy["distress_type"].replace({"chapter_11": "bankruptcy"})
        seed_frames.append(
            legacy[["last_ticker", "company_name_pattern", "distress_type", "event_year", "priority", "notes"]]
        )

    if not seed_frames:
        raise FileNotFoundError("No distress seed files found")

    seeds = pd.concat(seed_frames, ignore_index=True)
    seeds["last_ticker"] = seeds["last_ticker"].astype(str).str.upper()
    seeds["company_name_pattern"] = seeds["company_name_pattern"].astype(str)
    seeds["company_norm"] = seeds["company_name_pattern"].map(normalize)
    seeds = seeds.drop_duplicates(["last_ticker", "company_norm"], keep="first")
    return seeds.drop(columns=["company_norm"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    seeds = read_seeds()
    coverage = pd.read_csv(COVERAGE_PATH)
    coverage["name_norm"] = coverage["name"].map(normalize)

    matches = []
    for _, seed in seeds.iterrows():
        pattern_norm = normalize(seed["company_name_pattern"])
        hit = coverage[coverage["name_norm"].str.contains(pattern_norm, na=False)].copy()
        if hit.empty:
            matches.append({**seed.to_dict(), "match_status": "not_found_in_downloaded_zips"})
            continue

        hit = hit.sort_values(["filings", "last_period"], ascending=[False, False])
        for rank, (_, row) in enumerate(hit.iterrows(), start=1):
            matches.append(
                {
                    **seed.to_dict(),
                    "match_status": "matched",
                    "match_rank": rank,
                    "cik": row["cik"],
                    "sec_name": row["name"],
                    "filings": row["filings"],
                    "first_period": row["first_period"],
                    "last_period": row["last_period"],
                    "forms": row["forms"],
                    "afs_values": row["afs_values"],
                    "sic": row["sic"],
                    "coverage_ok_8_filings": bool(row["filings"] >= 8),
                }
            )

    matched = pd.DataFrame(matches)
    matched.to_csv(OUT_DIR / "distress_candidate_matches.csv", index=False)
    matched.to_csv(REPORT_DIR / "distress_candidate_coverage.csv", index=False)

    found = (matched["match_status"] == "matched").sum()
    unique_found = matched.loc[matched["match_status"] == "matched", "last_ticker"].nunique()
    print(f"Matched {unique_found} seeded tickers across {found} SEC candidate rows")
    print(f"Wrote {OUT_DIR / 'distress_candidate_matches.csv'}")


if __name__ == "__main__":
    main()
