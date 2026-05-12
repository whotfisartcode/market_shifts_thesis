#!/usr/bin/env python3
"""
scripts/compute_financial_ratios.py

Load firm_panel_meta, drop specified cols, compute financial ratios:
- gross_margin, operating_margin, net_margin
- debt_to_assets, equity_multiplier
- asset_turnover, inventory_turnover
- r_and_d_intensity
- cash_per_share, eps
Outputs to data/processed/firms/firm_panel_with_ratios.csv/.parquet
"""
import pandas as pd
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
META_CSV     = PROJECT_ROOT / "data/processed/firms/firm_panel_meta.csv"
META_PQT     = PROJECT_ROOT / "data/processed/firms/firm_panel_meta.parquet"
OUT_DIR      = PROJECT_ROOT / "data/processed/firms"
OUT_CSV      = OUT_DIR / "firm_panel_with_ratios.csv"
OUT_PQT      = OUT_DIR / "firm_panel_with_ratios.parquet"
# ────────────────────────────────────────────────────────────────────────

def load_panel():
    if META_PQT.exists():
        return pd.read_parquet(META_PQT)
    elif META_CSV.exists():
        return pd.read_csv(META_CSV)
    else:
        raise FileNotFoundError("Cannot find firm_panel_meta.csv or .parquet")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("🔄 Loading enriched firm panel…")
    df = load_panel()
    print(f"   → {len(df)} rows, {len(df.columns)} columns")

    # 1) Drop specified columns if present
    for col in ("gross_profit", "sales_revenue_net"):
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"   • dropped column '{col}'")

    # 2) Compute ratios (vectorized; missing data => NaN)
    # Profitability
    df["gross_margin"]     = (df["total_revenue"] - df["cost_of_revenue"]) / df["total_revenue"]
    df["operating_margin"] = df["operating_income"] / df["total_revenue"]
    df["net_margin"]       = df["net_income"] / df["total_revenue"]

    # Leverage
    df["debt_to_assets"]     = df["total_liabilities"] / df["total_assets"]
    df["equity_multiplier"]  = df["total_assets"] / (df["total_assets"] - df["total_liabilities"])

    # Efficiency
    df["asset_turnover"]     = df["total_revenue"] / df["total_assets"]
    if "inventory" in df.columns:
        df["inventory_turnover"] = df["cost_of_revenue"] / df["inventory"]

    # R&D Intensity
    if "r_and_d_expense" in df.columns:
        df["r_and_d_intensity"] = df["r_and_d_expense"] / df["total_revenue"]

    # Per-Share metrics (needs shares_outstanding)
    if "shares_outstanding" in df.columns:
        df["cash_per_share"] = df["cash_equivalents"] / df["shares_outstanding"]
    

    # 3) Report new column count
    new_cols = [c for c in df.columns if c not in pd.read_parquet(META_PQT).columns]
    print(f"   → computed {len(new_cols)} ratio columns: {new_cols}")

    # 4) Write out
    print(f"💾 Writing firm panel with ratios to:\n    {OUT_CSV}\n    {OUT_PQT}")
    df.to_csv(OUT_CSV, index=False)
    df.to_parquet(OUT_PQT, index=False)

    print("✅ compute_financial_ratios complete.")

if __name__ == "__main__":
    main()
