#!/usr/bin/env python3
"""Index SEC Financial Statement Data Set submissions.

Reads only sub.txt from each quarterly ZIP. This is fast and creates a compact
coverage table used before we parse the much larger num.txt files.
"""

from pathlib import Path
from zipfile import ZipFile

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZIP_DIR = PROJECT_ROOT / "data/raw/sec_fsd_zips"
OUT_DIR = PROJECT_ROOT / "data/interim"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"

USE_COLUMNS = [
    "adsh",
    "cik",
    "name",
    "sic",
    "countryba",
    "stprba",
    "afs",
    "form",
    "period",
    "fy",
    "fp",
    "filed",
]


def quarter_from_zip(path: Path) -> str:
    return path.stem.lower()


def read_submissions(path: Path) -> pd.DataFrame:
    with ZipFile(path) as zf:
        with zf.open("sub.txt") as handle:
            df = pd.read_csv(
                handle,
                sep="\t",
                usecols=lambda col: col in USE_COLUMNS,
                dtype={
                    "adsh": "string",
                    "cik": "Int64",
                    "name": "string",
                    "sic": "string",
                    "countryba": "string",
                    "stprba": "string",
                    "afs": "string",
                    "form": "string",
                    "period": "Int64",
                    "fy": "Int64",
                    "fp": "string",
                    "filed": "Int64",
                },
            )
    df["sec_zip"] = quarter_from_zip(path)
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    zip_paths = sorted(path for path in ZIP_DIR.glob("*.zip") if path.name[:4].isdigit())
    if not zip_paths:
        raise FileNotFoundError(f"No SEC FSD ZIPs found in {ZIP_DIR}")

    submissions = pd.concat([read_submissions(path) for path in zip_paths], ignore_index=True)
    submissions = submissions[submissions["form"].isin(["10-K", "10-K/A", "10-Q", "10-Q/A"])]
    submissions.to_csv(OUT_DIR / "sec_submissions_index.csv", index=False)

    coverage = (
        submissions.groupby(["cik", "name"], dropna=False)
        .agg(
            filings=("adsh", "nunique"),
            first_period=("period", "min"),
            last_period=("period", "max"),
            first_filed=("filed", "min"),
            last_filed=("filed", "max"),
            forms=("form", lambda s: ",".join(sorted(set(s.dropna())))),
            afs_values=("afs", lambda s: ",".join(sorted(set(s.dropna())))),
            sic=("sic", lambda s: next((x for x in s.dropna()), "")),
        )
        .reset_index()
        .sort_values(["filings", "last_period"], ascending=[False, False])
    )
    coverage.to_csv(REPORT_DIR / "sec_submission_coverage_by_cik.csv", index=False)

    zip_report = (
        submissions.groupby("sec_zip")
        .agg(filings=("adsh", "nunique"), ciks=("cik", "nunique"))
        .reset_index()
        .sort_values("sec_zip")
    )
    zip_report.to_csv(REPORT_DIR / "sec_submission_coverage_by_zip.csv", index=False)

    print(f"Indexed {len(submissions):,} 10-K/10-Q submissions from {len(zip_paths)} ZIPs")
    print(f"Wrote {OUT_DIR / 'sec_submissions_index.csv'}")


if __name__ == "__main__":
    main()
