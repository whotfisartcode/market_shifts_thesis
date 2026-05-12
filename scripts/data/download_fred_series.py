#!/usr/bin/env python3
"""Download selected FRED series listed in config/fred_series_catalog.csv."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "config/fred_series_catalog.csv"
OUT_DIR = PROJECT_ROOT / "data/raw/fred"


def download_series(series_id: str, out_path: Path) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    existing = pd.read_csv(out_path) if out_path.exists() else None
    subprocess.run(
        ["curl", "-L", "--fail", "--max-time", "60", "-o", str(out_path), url],
        check=True,
    )
    downloaded = pd.read_csv(out_path)

    # Some FRED graph CSV requests can return a clipped chart window for a
    # series. Preserve older local history when a fresh download is shorter.
    if existing is not None and len(existing) > len(downloaded):
        existing.columns = ["observation_date", series_id]
        downloaded.columns = ["observation_date", series_id]
        downloaded = (
            pd.concat([existing, downloaded], ignore_index=True)
            .drop_duplicates("observation_date", keep="last")
            .sort_values("observation_date")
        )
        downloaded.to_csv(out_path, index=False)
    return downloaded


def main() -> None:
    catalog = pd.read_csv(CATALOG_PATH)
    selected = catalog[catalog["include_in_panel"].astype(int) == 1]["series_id"].tolist()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for series_id in selected:
        out_path = OUT_DIR / f"{series_id}.csv"
        try:
            df = download_series(series_id, out_path)
            rows.append({"series_id": series_id, "status": "downloaded", "rows": len(df), "path": str(out_path)})
            print(f"Downloaded {series_id}: {len(df):,} rows", flush=True)
        except (subprocess.CalledProcessError, TimeoutError) as exc:
            status = f"failed: {type(exc).__name__}: {exc}"
            rows.append({"series_id": series_id, "status": status, "rows": 0, "path": str(out_path)})
            print(f"FAILED {series_id}: {exc}", flush=True)

    pd.DataFrame(rows).to_csv(OUT_DIR / "fred_download_log.csv", index=False)


if __name__ == "__main__":
    main()
