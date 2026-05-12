#!/usr/bin/env python3
"""Build a market-health index from existing panel macro/regime context.

This script does not modify the production panel. It reads the current
SEC/FRED/global-event panel and writes separate audit, summary, and figure
outputs for thesis/dashboard use.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / ".cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.parquet"
DATA_QUALITY_DIR = PROJECT_ROOT / "reports/data_quality"
MODELING_DIR = PROJECT_ROOT / "reports/modeling"
FIG_DIR = PROJECT_ROOT / "reports/figures/modeling"


@dataclass(frozen=True)
class StressInput:
    column: str
    component: str
    direction: int
    description: str


STRESS_INPUTS = [
    StressInput("BAMLH0A0HYM2", "credit_stress_score", 1, "High-yield spread; higher means tighter risky credit."),
    StressInput("NFCI", "credit_stress_score", 1, "Chicago Fed financial conditions; higher means tighter conditions."),
    StressInput("DRTSCILM", "credit_stress_score", 1, "Bank lending standards tightening; higher means tighter credit."),
    StressInput("FEDFUNDS", "rate_pressure_score", 1, "Federal funds rate; higher means higher rate pressure."),
    StressInput("T10Y2Y", "rate_pressure_score", -1, "10Y-2Y curve slope; lower/inverted means more stress."),
    StressInput("T10Y3M", "rate_pressure_score", -1, "10Y-3M curve slope; lower/inverted means more stress."),
    StressInput("CPIAUCSL_yoy_pct", "inflation_pressure_score", 1, "CPI YoY; higher means inflation pressure."),
    StressInput("PPIACO_yoy_pct", "inflation_pressure_score", 1, "PPI YoY; higher means input-cost pressure."),
    StressInput("DCOILWTICO_yoy_pct", "inflation_pressure_score", 1, "WTI oil YoY; higher means oil/input shock pressure."),
    StressInput("UNRATE", "demand_weakness_score", 1, "Unemployment rate; higher means demand/labor stress."),
    StressInput("RSAFS_yoy_pct", "demand_weakness_score", -1, "Retail sales YoY; lower means weaker demand."),
    StressInput("INDPRO_yoy_pct", "demand_weakness_score", -1, "Industrial production YoY; lower means weaker activity."),
    StressInput("PAYEMS_yoy_pct", "demand_weakness_score", -1, "Payrolls YoY; lower means weaker labor growth."),
    StressInput("HOUST_yoy_pct", "demand_weakness_score", -1, "Housing starts YoY; lower means rate-sensitive demand weakness."),
    StressInput("VIXCLS", "market_volatility_score", 1, "VIX; higher means market volatility stress."),
    StressInput("USEPUINDXD", "market_volatility_score", 1, "Economic policy uncertainty; higher means uncertainty stress."),
    StressInput("global_event_severity_sum", "event_stress_score", 1, "Curated global-event severity active at prediction date."),
    StressInput("global_event_count", "event_stress_score", 1, "Curated global-event count active at prediction date."),
]


def zscore_from_train(series: pd.Series, train_mask: pd.Series) -> tuple[pd.Series, float, float]:
    values = pd.to_numeric(series, errors="coerce")
    train_values = values[train_mask & values.notna()]
    mean = float(train_values.mean()) if not train_values.empty else np.nan
    std = float(train_values.std(ddof=0)) if not train_values.empty else np.nan
    if not np.isfinite(std) or std == 0:
        z = pd.Series(np.nan, index=series.index, dtype="float64")
    else:
        z = (values - mean) / std
    return z.clip(-4, 4), mean, std


def build_index(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    needed = ["prediction_date", "prediction_year"] + [item.column for item in STRESS_INPUTS if item.column in panel.columns]
    macro = (
        panel[needed]
        .drop_duplicates(subset=["prediction_date"])
        .sort_values("prediction_date")
        .reset_index(drop=True)
    )
    train_mask = macro["prediction_year"].between(2009, 2018)

    audit_rows = []
    component_columns: dict[str, list[str]] = {}

    for item in STRESS_INPUTS:
        if item.column not in macro.columns:
            audit_rows.append(
                {
                    "input_column": item.column,
                    "component": item.component,
                    "direction": item.direction,
                    "status": "missing_from_panel",
                    "train_mean": np.nan,
                    "train_std": np.nan,
                    "missing_share": np.nan,
                    "description": item.description,
                }
            )
            continue

        z, mean, std = zscore_from_train(macro[item.column], train_mask)
        score_col = f"{item.column}_stress_z"
        macro[score_col] = z * item.direction
        component_columns.setdefault(item.component, []).append(score_col)
        audit_rows.append(
            {
                "input_column": item.column,
                "component": item.component,
                "direction": item.direction,
                "status": "used",
                "train_mean": mean,
                "train_std": std,
                "missing_share": float(pd.to_numeric(macro[item.column], errors="coerce").isna().mean()),
                "description": item.description,
            }
        )

    for component, cols in component_columns.items():
        macro[component] = macro[cols].mean(axis=1, skipna=True)

    component_names = sorted(component_columns)
    macro["market_stress_score"] = macro[component_names].mean(axis=1, skipna=True)
    macro["market_health_score"] = -macro["market_stress_score"]

    train_scores = macro.loc[train_mask, "market_stress_score"].dropna()
    q25 = float(train_scores.quantile(0.25))
    q75 = float(train_scores.quantile(0.75))
    q90 = float(train_scores.quantile(0.90))

    conditions = [
        macro["market_stress_score"] <= q25,
        macro["market_stress_score"] <= q75,
        macro["market_stress_score"] <= q90,
    ]
    macro["market_health_regime"] = np.select(
        conditions,
        ["healthy", "neutral", "stressed"],
        default="severe_stress",
    )

    audit = pd.DataFrame(audit_rows)
    audit["training_period"] = "prediction_year 2009-2018"
    audit["stress_score_quantile_25_train"] = q25
    audit["stress_score_quantile_75_train"] = q75
    audit["stress_score_quantile_90_train"] = q90
    audit["panel_modified"] = False
    audit["alignment_policy"] = "prediction_date only; no future macro values"

    output_cols = [
        "prediction_date",
        "prediction_year",
        *component_names,
        "market_stress_score",
        "market_health_score",
        "market_health_regime",
    ]
    return macro[output_cols], audit


def write_outputs(index: pd.DataFrame, audit: pd.DataFrame, panel: pd.DataFrame) -> None:
    DATA_QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    MODELING_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    index.to_csv(MODELING_DIR / "market_health_index_by_prediction_date.csv", index=False)
    audit.to_csv(DATA_QUALITY_DIR / "market_health_index_audit.csv", index=False)

    enriched = panel.merge(index, on=["prediction_date", "prediction_year"], how="left")
    summary = (
        enriched.groupby(["prediction_year", "Sector", "market_health_regime"], dropna=False)
        .agg(
            rows=("adsh", "count"),
            firms=("cik", "nunique"),
            distress_next_4q_positive=("distress_next_4q", "sum"),
            success_resilience_next_4q_positive=("success_resilience_next_4q", "sum"),
            market_stress_score_mean=("market_stress_score", "mean"),
            market_health_score_mean=("market_health_score", "mean"),
        )
        .reset_index()
    )
    summary["distress_next_4q_share"] = summary["distress_next_4q_positive"] / summary["rows"]
    summary["success_resilience_next_4q_share"] = summary["success_resilience_next_4q_positive"] / summary["rows"]
    summary.to_csv(MODELING_DIR / "market_health_by_year_regime_sector.csv", index=False)

    monthly = (
        index.set_index("prediction_date")
        .resample("M")[["market_stress_score", "market_health_score"]]
        .mean()
        .dropna(how="all")
        .reset_index()
    )
    plt.figure(figsize=(11, 5))
    plt.plot(monthly["prediction_date"], monthly["market_stress_score"], label="Market stress score", linewidth=1.7)
    plt.axhline(0, color="black", linewidth=0.7, alpha=0.5)
    plt.title("Market-health index from existing macro/regime/event context")
    plt.xlabel("Prediction date")
    plt.ylabel("Training-period standardized stress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "market_health_index_timeseries.png", dpi=200)
    plt.close()


def main() -> None:
    panel = pd.read_parquet(PANEL_PATH)
    panel["prediction_date"] = pd.to_datetime(panel["prediction_date"], errors="coerce")
    index, audit = build_index(panel)
    write_outputs(index, audit, panel)
    print(f"Wrote {len(index):,} market-health date rows")
    print(f"Wrote {len(audit):,} market-health audit rows")


if __name__ == "__main__":
    main()
