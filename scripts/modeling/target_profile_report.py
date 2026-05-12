#!/usr/bin/env python3
"""Profile all success/failure target definitions in the rebuilt panel."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
REPORT_DIR = PROJECT_ROOT / "reports/modeling"

TARGETS = [
    "distress_next_2q",
    "distress_next_4q",
    "distress_next_8q",
    "broad_distress_next_4q",
    "healthy_current",
    "success_profitability_next_4q",
    "success_resilience_next_4q",
    "success_quality_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "industry_relative_resilience_next_4obs",
    "stress_resilience_next_4obs",
    "recovery_next_4obs",
    "quality_success_cashflow_next_4obs",
]


def add_split(df: pd.DataFrame) -> pd.DataFrame:
    year = df["prediction_date"].dt.year
    df["temporal_split"] = "unused"
    df.loc[year <= 2018, "temporal_split"] = "train"
    df.loc[(year >= 2019) & (year <= 2021), "temporal_split"] = "validation"
    df.loc[(year >= 2022) & (year <= 2024), "temporal_split"] = "test"
    return df


def summarize(df: pd.DataFrame, group_cols: list[str], output_name: str) -> None:
    rows = []
    for target in TARGETS:
        if target not in df.columns:
            continue
        grouped = df.groupby(group_cols, dropna=False)
        for keys, group in grouped:
            if not isinstance(keys, tuple):
                keys = (keys,)
            row = dict(zip(group_cols, keys))
            row.update(
                {
                    "target": target,
                    "rows": len(group),
                    "known_rows": int(group[target].notna().sum()),
                    "missing_rows": int(group[target].isna().sum()),
                    "positives": int(group[target].fillna(0).sum()),
                    "positive_share_all_rows": group[target].fillna(0).mean(),
                    "positive_share_known": group[target].sum() / group[target].notna().sum()
                    if group[target].notna().sum()
                    else pd.NA,
                    "firms": group["cik"].nunique(),
                }
            )
            rows.append(row)
    pd.DataFrame(rows).to_csv(REPORT_DIR / output_name, index=False)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in ["period_date", "filed_date", "prediction_date", "event_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "prediction_date" not in df.columns:
        raise ValueError("Panel is missing prediction_date. Rebuild it with scripts/sec_fsd/build_panel_v2.py.")
    df = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    if "post_event_flag" in df.columns:
        df = df[df["post_event_flag"].fillna(0).astype(int) == 0].copy()
    df = add_split(df)

    overall = []
    for target in TARGETS:
        overall.append(
            {
                "target": target,
                "rows": len(df),
                "known_rows": int(df[target].notna().sum()),
                "missing_rows": int(df[target].isna().sum()),
                "positives": int(df[target].fillna(0).sum()),
                "positive_share_all_rows": df[target].fillna(0).mean(),
                "positive_share_known": df[target].sum() / df[target].notna().sum()
                if df[target].notna().sum()
                else pd.NA,
                "firms_with_positive": df.loc[df[target].fillna(0) == 1, "cik"].nunique(),
            }
        )
    pd.DataFrame(overall).to_csv(REPORT_DIR / "panel_v2_target_overall.csv", index=False)
    summarize(df, ["temporal_split"], "panel_v2_target_by_split.csv")
    summarize(df, ["Sector"], "panel_v2_target_by_sector.csv")
    summarize(df, ["cohort"], "panel_v2_target_by_cohort.csv")
    print("Wrote target profile reports")


if __name__ == "__main__":
    main()
