#!/usr/bin/env python3
"""Summarize model feature importances into thesis-readable groups."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports/modeling"


TARGETS = ["distress_next_4q", "success_resilience_next_4q", "failure_pressure_conservative_v2_next_4obs"]


def clean_feature_name(feature: str) -> str:
    return (
        feature.replace("num__", "")
        .replace("missingindicator_", "Missing: ")
        .replace("cat__", "")
        .replace("Sector_", "Sector: ")
    )


def group_feature(feature: str) -> str:
    raw = feature.replace("num__", "").replace("cat__", "")
    if raw.startswith("missingindicator_"):
        return "Missingness indicators"
    if raw.startswith("Sector_"):
        return "Industry / sector"
    if raw.startswith("global_event_"):
        return "Global event context"
    if raw in {
        "BAMLH0A0HYM2",
        "FEDFUNDS",
        "GDPC1",
        "GS10",
        "INDPRO",
        "INDPRO_yoy_pct",
        "M2SL",
        "M2SL_yoy_pct",
        "NFCI",
        "UNRATE",
        "USEPUINDXD",
        "VIXCLS",
        "T10Y2Y",
        "T10Y3M",
        "DCOILWTICO",
        "DCOILWTICO_yoy_pct",
        "DTWEXBGS",
        "DTWEXBGS_yoy_pct",
        "CPIAUCSL",
        "CPIAUCSL_yoy_pct",
        "PPIACO",
        "PPIACO_yoy_pct",
        "PAYEMS",
        "PAYEMS_yoy_pct",
        "RSAFS",
        "RSAFS_yoy_pct",
        "HOUST",
        "HOUST_yoy_pct",
        "BUSLOANS",
        "BUSLOANS_yoy_pct",
        "DRTSCILM",
    }:
        return "Macro conditions"
    if raw in {
        "high_rate_regime",
        "market_stress_regime",
        "tight_financial_conditions",
        "credit_spread_stress_regime",
        "yield_curve_inversion_regime",
        "inflation_pressure_regime",
        "oil_shock_regime",
        "strong_dollar_regime",
        "demand_slowdown_regime",
        "credit_tightening_regime",
        "crisis_regime",
        "prediction_quarter",
    }:
        return "Macro regime / time"
    if raw.endswith("_lag1") or raw.endswith("_growth_4obs") or raw.endswith("_change_4obs") or raw == "net_income_negative_count_prior_4obs":
        return "Firm trend / deterioration"
    if raw in {"leverage_assets", "equity_assets", "current_ratio", "cash_assets", "net_margin", "operating_margin", "gross_margin", "roa", "r_and_d_intensity", "inventory_assets", "receivables_assets"}:
        return "Financial ratios"
    if raw in {"total_assets", "total_liabilities", "long_term_debt", "short_term_debt", "current_assets", "current_liabilities", "cash_equivalents", "total_equity", "total_revenue", "gross_profit", "operating_income", "net_income", "cash_flow_operating", "capex"}:
        return "Accounting fundamentals"
    return "Other"


def main() -> None:
    frames = []
    grouped_frames = []

    for target in TARGETS:
        path = REPORT_DIR / f"panel_v2_{target}_feature_importance.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["target"] = target
        df["feature_clean"] = df["feature"].map(clean_feature_name)
        df["feature_group"] = df["feature"].map(group_feature)
        df["economic_interpretation_allowed"] = df["feature_group"] != "Missingness indicators"
        df["interpretation_note"] = df["feature_group"].map(
            lambda group: (
                "Reporting/data-availability indicator; keep separate from economic factor interpretation."
                if group == "Missingness indicators"
                else "Substantive model feature group usable for economic interpretation with normal caveats."
            )
        )
        frames.append(df)

        grouped = (
            df.groupby(["target", "model", "feature_group"], as_index=False)["importance"]
            .sum()
            .sort_values(["target", "model", "importance"], ascending=[True, True, False])
        )
        grouped_frames.append(grouped)

    if frames:
        long = pd.concat(frames, ignore_index=True)
        long.to_csv(REPORT_DIR / "panel_v2_feature_contribution_long.csv", index=False)
        long.to_csv(REPORT_DIR / "final_model_feature_interpretation_table.csv", index=False)
    if grouped_frames:
        grouped_out = pd.concat(grouped_frames, ignore_index=True)
        grouped_out.to_csv(REPORT_DIR / "panel_v2_feature_contribution_groups.csv", index=False)
        grouped_out.to_csv(REPORT_DIR / "final_feature_group_contribution_table.csv", index=False)

        economic = grouped_out[grouped_out["feature_group"] != "Missingness indicators"].copy()
        totals = economic.groupby(["target", "model"])["importance"].transform("sum")
        economic["importance_share_ex_missingness"] = economic["importance"] / totals
        economic.to_csv(REPORT_DIR / "panel_v2_feature_contribution_economic_groups.csv", index=False)
    print("Wrote feature contribution summaries")


if __name__ == "__main__":
    main()
