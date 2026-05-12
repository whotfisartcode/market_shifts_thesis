#!/usr/bin/env python3
"""Inventory SEC Financial Statement Data Set ZIP files.

Run this after downloading quarterly SEC ZIPs into data/raw/sec_fsd_zips/.
The script does not extract files permanently; it only checks ZIP contents and
writes a compact CSV report.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZIP_DIR = PROJECT_ROOT / "data/raw/sec_fsd_zips"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"
REQUIRED_MEMBERS = {"sub.txt", "num.txt", "pre.txt", "tag.txt"}


def infer_period(filename: str) -> tuple[int | None, int | None]:
    compact = filename.lower().replace("_", "").replace("-", "")
    match = re.search(r"(20\d{2})q([1-4])", compact)
    if match:
        return int(match.group(1)), int(match.group(2))

    match = re.search(r"([1-4])q(20\d{2})", compact)
    if match:
        return int(match.group(2)), int(match.group(1))

    return None, None


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    for path in sorted(ZIP_DIR.glob("*.zip")):
        row = {
            "file": path.name,
            "size_mb": round(path.stat().st_size / 1024 / 1024, 2),
            "year": None,
            "quarter": None,
            "valid_zip": False,
            "member_count": None,
            "has_sub": False,
            "has_num": False,
            "has_pre": False,
            "has_tag": False,
            "missing_required": "",
        }
        row["year"], row["quarter"] = infer_period(path.name)

        try:
            with zipfile.ZipFile(path) as zf:
                names = {Path(name).name.lower() for name in zf.namelist()}
                row["valid_zip"] = True
                row["member_count"] = len(names)
                for member in REQUIRED_MEMBERS:
                    row[f"has_{member.split('.')[0]}"] = member in names
                missing = sorted(REQUIRED_MEMBERS - names)
                row["missing_required"] = ",".join(missing)
        except zipfile.BadZipFile:
            row["missing_required"] = "bad_zip"

        rows.append(row)

    out = pd.DataFrame(rows)
    output_path = REPORT_DIR / "sec_fsd_zip_inventory.csv"
    out.to_csv(output_path, index=False)

    if out.empty:
        print(f"No SEC ZIPs found in {ZIP_DIR}")
    else:
        valid = int(out["valid_zip"].sum())
        complete = int((out["missing_required"] == "").sum())
        print(f"Inventoried {len(out)} ZIPs: {valid} valid, {complete} complete")
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
