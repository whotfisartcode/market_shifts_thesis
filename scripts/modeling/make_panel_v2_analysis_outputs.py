#!/usr/bin/env python3
"""Create thesis-ready descriptive industry and regime outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
REPORT_DIR = PROJECT_ROOT / "reports/modeling"
FIG_DIR = PROJECT_ROOT / "reports/figures/modeling"


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in ["period_date", "filed_date", "prediction_date", "event_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "prediction_date" not in df.columns:
        raise ValueError("Panel is missing prediction_date. Rebuild it with scripts/sec_fsd/build_panel_v2.py.")
    df = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    if "post_event_flag" in df.columns:
        df = df[df["post_event_flag"].fillna(0).astype(int) == 0].copy()
    df["distress_next_4q"] = df["distress_next_4q"].astype(int)
    return df


def industry_outputs(df: pd.DataFrame) -> None:
    industry = (
        df.groupby("Sector", dropna=False)
        .agg(
            rows=("adsh", "count"),
            firms=("cik", "nunique"),
            distress_rows=("distress_next_4q", "sum"),
            avg_leverage=("leverage_assets", "mean"),
            avg_roa=("roa", "mean"),
            avg_cash_assets=("cash_assets", "mean"),
        )
        .reset_index()
    )
    industry["distress_share"] = industry["distress_rows"] / industry["rows"]
    industry = industry.sort_values("distress_share", ascending=False)
    industry.to_csv(REPORT_DIR / "panel_v2_industry_summary.csv", index=False)

    plot_data = industry[industry["rows"] >= 100].sort_values("distress_share", ascending=True)
    plt.figure(figsize=(9, 6))
    plt.barh(plot_data["Sector"].fillna("Unknown"), plot_data["distress_share"])
    plt.xlabel("Forward distress share")
    plt.title("Forward distress label share by sector")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "panel_v2_distress_share_by_sector.png", dpi=200)
    plt.close()


def regime_outputs(df: pd.DataFrame) -> None:
    regime_cols = [
        "high_rate_regime",
        "market_stress_regime",
        "tight_financial_conditions",
        "crisis_regime",
    ]
    rows = []
    for regime in regime_cols:
        for value, group in df.groupby(regime, dropna=False):
            rows.append(
                {
                    "regime": regime,
                    "value": value,
                    "rows": len(group),
                    "firms": group["cik"].nunique(),
                    "distress_rows": int(group["distress_next_4q"].sum()),
                    "distress_share": group["distress_next_4q"].mean(),
                    "avg_leverage": group["leverage_assets"].mean(),
                    "avg_roa": group["roa"].mean(),
                    "avg_unrate": group["UNRATE"].mean(),
                    "avg_vix": group["VIXCLS"].mean(),
                    "avg_fedfunds": group["FEDFUNDS"].mean(),
                }
            )
    regime_summary = pd.DataFrame(rows)
    regime_summary.to_csv(REPORT_DIR / "panel_v2_regime_summary.csv", index=False)

    plot_data = regime_summary.copy()
    plot_data["label"] = plot_data["regime"] + "=" + plot_data["value"].astype(str)
    plot_data = plot_data.sort_values("distress_share", ascending=True)
    plt.figure(figsize=(9, 6))
    plt.barh(plot_data["label"], plot_data["distress_share"])
    plt.xlabel("Forward distress share")
    plt.title("Forward distress label share by macro regime")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "panel_v2_distress_share_by_regime.png", dpi=200)
    plt.close()


def time_outputs(df: pd.DataFrame) -> None:
    yearly = (
        df.groupby(df["prediction_date"].dt.year)
        .agg(
            rows=("adsh", "count"),
            firms=("cik", "nunique"),
            distress_rows=("distress_next_4q", "sum"),
            avg_unrate=("UNRATE", "mean"),
            avg_vix=("VIXCLS", "mean"),
            avg_fedfunds=("FEDFUNDS", "mean"),
        )
        .reset_index()
        .rename(columns={"prediction_date": "year"})
    )
    yearly["distress_share"] = yearly["distress_rows"] / yearly["rows"]
    yearly.to_csv(REPORT_DIR / "panel_v2_yearly_summary.csv", index=False)

    plt.figure(figsize=(9, 5))
    plt.plot(yearly["year"], yearly["distress_share"], marker="o", label="Distress share")
    plt.xlabel("Year")
    plt.ylabel("Forward distress share")
    plt.title("Forward distress label share over time")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "panel_v2_distress_share_over_time.png", dpi=200)
    plt.close()


def cohort_outputs(df: pd.DataFrame) -> None:
    cohort = (
        df.groupby("cohort", dropna=False)
        .agg(
            rows=("adsh", "count"),
            firms=("cik", "nunique"),
            distress_rows=("distress_next_4q", "sum"),
            avg_leverage=("leverage_assets", "mean"),
            avg_roa=("roa", "mean"),
        )
        .reset_index()
    )
    cohort["distress_share"] = cohort["distress_rows"] / cohort["rows"]
    cohort.to_csv(REPORT_DIR / "panel_v2_cohort_summary.csv", index=False)


def global_event_outputs(df: pd.DataFrame) -> None:
    if "global_event_count" not in df.columns:
        return

    event_count_cols = [
        col
        for col in df.columns
        if col.startswith("global_event_") and col.endswith("_count") and col != "global_event_count"
    ]
    rows = []
    for col in event_count_cols:
        event_type = col.removeprefix("global_event_").removesuffix("_count")
        event_df = df[df[col] > 0].copy()
        if event_df.empty:
            continue

        rows.append(
            {
                "event_type": event_type,
                "Sector": "ALL",
                "rows": len(event_df),
                "firms": event_df["cik"].nunique(),
                "distress_rows": int(event_df["distress_next_4q"].sum()),
                "distress_share": event_df["distress_next_4q"].mean(),
                "success_resilience_share": event_df["success_resilience_next_4q"].mean(),
                "avg_roa": event_df["roa"].mean(),
                "avg_leverage": event_df["leverage_assets"].mean(),
                "avg_cash_assets": event_df["cash_assets"].mean(),
            }
        )

        by_sector = (
            event_df.groupby("Sector", dropna=False)
            .agg(
                rows=("adsh", "count"),
                firms=("cik", "nunique"),
                distress_rows=("distress_next_4q", "sum"),
                success_resilience_share=("success_resilience_next_4q", "mean"),
                avg_roa=("roa", "mean"),
                avg_leverage=("leverage_assets", "mean"),
                avg_cash_assets=("cash_assets", "mean"),
            )
            .reset_index()
        )
        by_sector["event_type"] = event_type
        by_sector["distress_share"] = by_sector["distress_rows"] / by_sector["rows"]
        rows.extend(by_sector.to_dict("records"))

    if not rows:
        return

    summary = pd.DataFrame(rows)
    summary = summary[
        [
            "event_type",
            "Sector",
            "rows",
            "firms",
            "distress_rows",
            "distress_share",
            "success_resilience_share",
            "avg_roa",
            "avg_leverage",
            "avg_cash_assets",
        ]
    ].sort_values(["event_type", "distress_share"], ascending=[True, False])
    summary.to_csv(REPORT_DIR / "panel_v2_global_event_sector_summary.csv", index=False)

    plot_data = summary[(summary["Sector"] == "ALL") & (summary["rows"] >= 100)].sort_values(
        "distress_share",
        ascending=True,
    )
    plt.figure(figsize=(9, 6))
    plt.barh(plot_data["event_type"], plot_data["distress_share"])
    plt.xlabel("Forward distress share")
    plt.title("Forward distress label share by global event type")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "panel_v2_distress_share_by_global_event_type.png", dpi=200)
    plt.close()


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    industry_outputs(df)
    regime_outputs(df)
    time_outputs(df)
    cohort_outputs(df)
    global_event_outputs(df)
    print("Wrote industry/regime/time analysis outputs")


if __name__ == "__main__":
    main()
