#!/usr/bin/env python3
"""Build the rebuilt SEC/FRED firm-period panel for the thesis.

The script reads SEC Financial Statement Data Set ZIPs directly, extracts only
the selected thesis universe and mapped concepts, adds ratio/macroeconomic
features, and writes a full local panel plus GitHub-safe samples.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZIP_DIR = PROJECT_ROOT / "data/raw/sec_fsd_zips"
CONFIG_DIR = PROJECT_ROOT / "config"
FRED_DIR = PROJECT_ROOT / "data/raw/fred"
OUT_DIR = PROJECT_ROOT / "data/processed/panel_v2"
SAMPLE_DIR = PROJECT_ROOT / "data/samples"
GITHUB_DIR = PROJECT_ROOT / "data/github"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"

UNIVERSE_PATH = CONFIG_DIR / "universe_v2_draft.csv"
CONCEPT_MAP_PATH = CONFIG_DIR / "sec_fsd_concept_map.csv"
EVENT_DATES_PATH = CONFIG_DIR / "distress_event_dates.csv"
FRED_CATALOG_PATH = CONFIG_DIR / "fred_series_catalog.csv"
GLOBAL_EVENT_CALENDAR_PATH = CONFIG_DIR / "global_event_calendar_seed.csv"
DERIVED_FEATURE_ABS_MAX = 100.0
SALES_REVENUE_SIGN_NORMALIZED_TAGS = {
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet",
}
CORE_ACCOUNTING_COLS = [
    "accounts_receivable",
    "capex",
    "cash_equivalents",
    "cash_flow_financing",
    "cash_flow_investing",
    "cash_flow_operating",
    "cost_of_revenue",
    "current_assets",
    "current_liabilities",
    "depreciation_amortization",
    "gross_profit",
    "inventory",
    "long_term_debt",
    "net_income",
    "noncurrent_liabilities",
    "operating_income",
    "ppe_net",
    "pretax_income",
    "r_and_d_expense",
    "retained_earnings",
    "sg_and_a",
    "shares_outstanding",
    "short_term_debt",
    "total_assets",
    "total_equity",
    "total_liabilities",
    "total_revenue",
    "wavg_shares_basic",
    "wavg_shares_diluted",
]

FULL_PANEL_CSV_GZ = OUT_DIR / "firm_panel_v2.csv.gz"
FULL_PANEL_PARQUET = OUT_DIR / "firm_panel_v2.parquet"
SAMPLE_PANEL_CSV = SAMPLE_DIR / "firm_panel_v2_sample.csv"
SCHEMA_CSV = SAMPLE_DIR / "firm_panel_v2_schema.csv"
GITHUB_PANEL_CSV_GZ = GITHUB_DIR / "firm_panel_v2.csv.gz"
GITHUB_PANEL_PARQUET = GITHUB_DIR / "firm_panel_v2.parquet"
GITHUB_SCHEMA_CSV = GITHUB_DIR / "firm_panel_v2_schema.csv"


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace({0: np.nan})
    return numerator / denominator


def derived_feature_columns(panel: pd.DataFrame) -> list[str]:
    base_ratio_cols = {
        "leverage_assets",
        "equity_assets",
        "current_ratio",
        "cash_assets",
        "net_margin",
        "operating_margin",
        "gross_margin",
        "roa",
        "r_and_d_intensity",
        "inventory_assets",
        "receivables_assets",
    }
    suffixes = ("_ratio", "_lag1", "_growth_4obs", "_change_4obs")
    return [
        col
        for col in panel.columns
        if col in base_ratio_cols or any(col.endswith(suffix) for suffix in suffixes)
    ]


def read_universe() -> pd.DataFrame:
    universe = pd.read_csv(UNIVERSE_PATH)
    keep = universe["include_status"].isin(["include_legacy_core", "include_if_num_tags_parse"])
    universe = universe[keep].copy()
    universe["cik"] = universe["cik"].astype("Int64")
    universe = universe[universe["cik"].notna()].copy()
    universe = collapse_duplicate_cik_aliases(universe)
    return universe


def collapse_duplicate_cik_aliases(universe: pd.DataFrame) -> pd.DataFrame:
    """Keep one firm history per SEC CIK while preserving ticker aliases.

    Some distressed ticker symbols are aliases for an already-included SEC CIK.
    If left as separate universe rows, the same SEC filings are duplicated with
    different target labels. The panel is CIK-based, so the correct production
    behavior is one row history per CIK with alias tickers retained for event
    lookup and audit provenance.
    """
    if universe.empty:
        return universe

    priority = {
        "include_legacy_core": 0,
        "include_if_num_tags_parse": 1,
    }
    working = universe.copy()
    working["_include_priority"] = working["include_status"].map(priority).fillna(99)
    working["_metadata_score"] = working[["Sector", "Industry", "exchange"]].notna().sum(axis=1)
    resolved_rows = []
    audit_rows = []

    for cik, group in working.groupby("cik", dropna=False):
        group = group.sort_values(
            ["_include_priority", "_metadata_score", "sec_filings", "ticker"],
            ascending=[True, False, False, True],
        )
        primary = group.iloc[0].copy()
        aliases = sorted(group["ticker"].dropna().astype(str).unique())
        alias_text = ";".join(aliases)
        primary["ticker_aliases"] = alias_text
        primary["event_lookup_tickers"] = alias_text
        primary["duplicate_cik_alias_count"] = len(aliases)

        if len(group) > 1:
            alias_notes = []
            for _, row in group.iterrows():
                note = str(row.get("notes", "") or "")
                if note:
                    alias_notes.append(f"{row['ticker']}: {note}")
            existing_note = str(primary.get("notes", "") or "")
            primary["notes"] = (
                existing_note
                + f"; duplicate_cik_aliases={alias_text}; duplicate_cik_primary={primary['ticker']}; "
                + " | ".join(alias_notes)
            ).strip("; ")
            audit_rows.append(
                {
                    "cik": int(cik) if pd.notna(cik) else pd.NA,
                    "primary_ticker": primary["ticker"],
                    "alias_tickers": alias_text,
                    "rows_collapsed": len(group),
                    "primary_include_status": primary["include_status"],
                    "all_include_statuses": ";".join(group["include_status"].dropna().astype(str).unique()),
                    "policy": "keep_one_cik_history_preserve_aliases_for_event_lookup",
                }
            )
        resolved_rows.append(primary)

    out = pd.DataFrame(resolved_rows).drop(columns=["_include_priority", "_metadata_score"], errors="ignore")
    if audit_rows:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(audit_rows).to_csv(REPORT_DIR / "duplicate_cik_alias_resolution.csv", index=False)
    else:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            columns=[
                "cik",
                "primary_ticker",
                "alias_tickers",
                "rows_collapsed",
                "primary_include_status",
                "all_include_statuses",
                "policy",
            ]
        ).to_csv(REPORT_DIR / "duplicate_cik_alias_resolution.csv", index=False)
    return out.reset_index(drop=True)


def read_concept_map() -> pd.DataFrame:
    concept_map = pd.read_csv(CONCEPT_MAP_PATH)
    concept_map["tag"] = concept_map["tag"].astype(str)
    return concept_map


def quarter_from_zip(path: Path) -> str:
    return path.stem.lower()


def read_sub(path: Path, selected_ciks: set[int]) -> pd.DataFrame:
    with ZipFile(path) as zf:
        with zf.open("sub.txt") as handle:
            sub = pd.read_csv(
                handle,
                sep="\t",
                dtype={
                    "adsh": "string",
                    "cik": "Int64",
                    "name": "string",
                    "sic": "string",
                    "afs": "string",
                    "form": "string",
                    "period": "Int64",
                    "fy": "Int64",
                    "fp": "string",
                    "filed": "Int64",
                },
                usecols=lambda col: col
                in {"adsh", "cik", "name", "sic", "afs", "form", "period", "fy", "fp", "filed"},
            )
    sub = sub[sub["cik"].isin(selected_ciks)]
    sub = sub[sub["form"].isin(["10-K", "10-K/A", "10-Q", "10-Q/A"])]
    sub = sub.dropna(subset=["adsh", "period"])
    sub["sec_zip"] = quarter_from_zip(path)
    return sub


def read_num(path: Path, adsh_values: set[str], concept_map: pd.DataFrame) -> pd.DataFrame:
    if not adsh_values:
        return pd.DataFrame()

    tags = set(concept_map["tag"])
    with ZipFile(path) as zf:
        with zf.open("num.txt") as handle:
            num = pd.read_csv(
                handle,
                sep="\t",
                dtype={
                    "adsh": "string",
                    "tag": "string",
                    "version": "string",
                    "ddate": "Int64",
                    "qtrs": "Int64",
                    "uom": "string",
                    "segments": "string",
                    "coreg": "string",
                    "value": "float64",
                },
                usecols=lambda col: col
                in {"adsh", "tag", "ddate", "qtrs", "uom", "segments", "coreg", "value"},
            )

    num = num[num["adsh"].isin(adsh_values)]
    num = num[num["tag"].isin(tags)]
    num = num[num["value"].notna()]

    if num.empty:
        return num

    num["segments"] = num["segments"].fillna("")
    num["coreg"] = num["coreg"].fillna("")
    num = num[(num["segments"] == "") & (num["coreg"] == "")]
    num = num[num["uom"].isin(["USD", "shares", "USD/shares", "pure"])]
    return num


def add_period_alignment_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Mark SEC facts whose reported data date matches the filing period.

    SEC FSD filings include current-period facts and comparative prior-period
    facts in the same submission. The panel must only select facts where the
    SEC fact `ddate` matches the submission `period`; otherwise prior-year
    comparatives can be mistaken for current accounting values.
    """
    out = df.copy()
    out["ddate_period_aligned"] = out["ddate"].eq(out["period"]).fillna(False)
    return out


def filter_current_period_facts(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only SEC facts aligned to the filing period end date."""
    if df.empty:
        return df.copy()
    flagged = add_period_alignment_flag(df)
    return flagged.loc[flagged["ddate_period_aligned"]].copy()


def parse_sec_fsd(universe: pd.DataFrame, concept_map: pd.DataFrame) -> pd.DataFrame:
    selected_ciks = set(universe["cik"].dropna().astype(int))
    zip_paths = sorted(path for path in ZIP_DIR.glob("*.zip") if path.name[:4].isdigit())
    rows = []

    for index, path in enumerate(zip_paths, start=1):
        sub = read_sub(path, selected_ciks)
        if sub.empty:
            continue

        num = read_num(path, set(sub["adsh"].astype(str)), concept_map)
        if num.empty:
            continue

        num = num.merge(concept_map, on="tag", how="inner")
        num = num.merge(sub, on="adsh", how="inner")
        statement_conditions = [
            ((num["statement"] == "balance") & (num["qtrs"] == 0)).fillna(False).to_numpy(dtype=bool),
            ((num["statement"] == "flow") & (num["qtrs"].isin([1, 2, 3, 4]))).fillna(False).to_numpy(dtype=bool),
            ((num["statement"] == "shares") & (num["qtrs"].isin([0, 1, 4]))).fillna(False).to_numpy(dtype=bool),
            ((num["statement"] == "eps") & (num["qtrs"].isin([1, 4]))).fillna(False).to_numpy(dtype=bool),
        ]
        num["statement_rank"] = np.select(
            statement_conditions,
            [0, 0, 0, 0],
            default=9,
        )
        num = num[num["statement_rank"] == 0]
        if num.empty:
            continue

        rows.append(num)
        if index % 10 == 0:
            print(f"Processed {index}/{len(zip_paths)} ZIPs")

    if not rows:
        raise RuntimeError("No SEC numeric rows matched the selected universe/concept map")

    long_raw = pd.concat(rows, ignore_index=True)
    long = standardize_sec_values(long_raw)

    id_cols = [
        "adsh",
        "cik",
        "name",
        "sic",
        "afs",
        "form",
        "period",
        "fy",
        "fp",
        "filed",
        "sec_zip",
    ]
    meta = long[id_cols].drop_duplicates("adsh")
    wide = long.pivot(index="adsh", columns="variable", values="value").reset_index()
    panel = meta.merge(wide, on="adsh", how="left")
    return panel


def standardize_sec_values(long_raw: pd.DataFrame) -> pd.DataFrame:
    """Choose one value per submission-variable and standardize flow periods.

    SEC flow facts may be filed as current-quarter values (`qtrs=1`) or as
    cumulative YTD values (`qtrs=2`, `qtrs=3`, `qtrs=4`). For comparability,
    this panel uses single-period flow values. If a current-quarter value is
    not reported, the script derives it from cumulative values when the prior
    cumulative period is available.
    """

    long_raw = long_raw.copy()
    long_raw = normalize_sec_sign_conventions(long_raw)
    long_raw = filter_current_period_facts(long_raw)
    if long_raw.empty:
        return long_raw.assign(value_method=pd.Series(dtype="object"))

    long_raw["period_date"] = pd.to_datetime(
        long_raw["period"].astype("Int64").astype(str),
        format="%Y%m%d",
        errors="coerce",
    )
    long_raw["filed_date"] = pd.to_datetime(
        long_raw["filed"].astype("Int64").astype(str),
        format="%Y%m%d",
        errors="coerce",
    )
    long_raw = long_raw.sort_values(["adsh", "variable", "qtrs", "priority", "tag"])
    long_raw = long_raw.drop_duplicates(["adsh", "variable", "qtrs"], keep="first")

    non_flow = long_raw[long_raw["statement"] != "flow"].copy()
    qtrs_preference = {
        "balance": {0: 0},
        "shares": {0: 0, 1: 1, 4: 2},
        "eps": {1: 0, 4: 1},
    }
    non_flow["qtrs_rank"] = non_flow.apply(
        lambda row: qtrs_preference.get(str(row["statement"]), {}).get(int(row["qtrs"]), 9),
        axis=1,
    )
    non_flow = non_flow.sort_values(["adsh", "variable", "qtrs_rank", "priority", "tag"])
    non_flow = non_flow.drop_duplicates(["adsh", "variable"], keep="first")
    non_flow["value_method"] = "reported"

    flow = long_raw[long_raw["statement"] == "flow"].copy()
    if flow.empty:
        return non_flow.drop(columns=["period_date", "filed_date", "qtrs_rank"], errors="ignore")

    standardized_groups = []
    group_cols = ["cik", "variable", "fy"]
    for _, group in flow.groupby(group_cols, dropna=False):
        standardized = standardize_flow_group(group)
        if not standardized.empty:
            standardized_groups.append(standardized)
    standardized_flow = pd.concat(standardized_groups, ignore_index=True) if standardized_groups else pd.DataFrame()

    out = pd.concat([non_flow, standardized_flow], ignore_index=True)
    out = out.sort_values(["adsh", "variable", "priority", "tag"])
    out = out.drop_duplicates(["adsh", "variable"], keep="first")
    return out.drop(columns=["period_date", "filed_date", "qtrs_rank"], errors="ignore")


def normalize_sec_sign_conventions(long_raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize narrow XBRL sign conventions where the economic direction is clear.

    Some older filings report `SalesRevenue*` values with a credit-balance
    negative sign. For consolidated sales-revenue tags, a negative sign is a
    presentation convention rather than economically negative sales. Broader
    `Revenues` tags are not flipped because investment, insurance, commodity,
    and refund-heavy presentations can legitimately be negative.
    """
    out = long_raw.copy()
    out["source_reported_value"] = out["value"]
    out["value_sign_policy"] = "as_reported"

    sign_mask = (
        out["variable"].eq("total_revenue")
        & out["tag"].isin(SALES_REVENUE_SIGN_NORMALIZED_TAGS)
        & out["value"].lt(0)
    )
    if sign_mask.any():
        out.loc[sign_mask, "value"] = out.loc[sign_mask, "value"].abs()
        out.loc[sign_mask, "value_sign_policy"] = "absolute_value_for_sales_revenue_credit_sign"
    return out


def standardize_flow_group(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values(["period_date", "filed_date", "qtrs", "priority", "tag"])
    selected: dict[str, pd.Series] = {}
    latest_cumulative: dict[int, float] = {}

    for _, row in group.iterrows():
        adsh = str(row["adsh"])
        qtrs = int(row["qtrs"])
        fp = str(row["fp"]) if pd.notna(row["fp"]) else ""
        value = row["value"]

        candidate = None
        method = None
        if qtrs == 1:
            candidate = row.copy()
            method = "reported_single_period"
        elif qtrs in {2, 3, 4} and (qtrs - 1) in latest_cumulative:
            candidate = row.copy()
            candidate["value"] = value - latest_cumulative[qtrs - 1]
            method = f"derived_from_cumulative_qtrs_{qtrs}_minus_{qtrs - 1}"
            if str(row.get("variable")) == "total_revenue" and candidate["value"] < 0:
                candidate["value"] = np.nan
                method = f"{method}_set_null_negative_revenue"

        # Prefer an explicitly reported single-period value when both current
        # quarter and cumulative values exist in the same submission.
        if candidate is not None and (adsh not in selected or qtrs == 1):
            candidate["value_method"] = method
            selected[adsh] = candidate

        if qtrs > 1 or (qtrs == 1 and fp == "Q1"):
            latest_cumulative[qtrs] = value

    if not selected:
        return pd.DataFrame(columns=group.columns.tolist() + ["value_method"])

    return pd.DataFrame(selected.values())


def add_universe_metadata(panel: pd.DataFrame, universe: pd.DataFrame) -> pd.DataFrame:
    meta_cols = [
        "ticker",
        "cik",
        "firm_id",
        "shortname",
        "sec_name",
        "exchange",
        "Sector",
        "Industry",
        "cohort",
        "include_status",
        "notes",
        "ticker_aliases",
        "event_lookup_tickers",
        "duplicate_cik_alias_count",
    ]
    meta_cols = [col for col in meta_cols if col in universe.columns]
    panel = panel.merge(universe[meta_cols], on="cik", how="left", suffixes=("", "_universe"))
    panel["period_date"] = pd.to_datetime(panel["period"].astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
    panel["filed_date"] = pd.to_datetime(panel["filed"].astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
    panel["prediction_date"] = panel["filed_date"].fillna(panel["period_date"])
    panel["prediction_date_source"] = np.where(
        panel["filed_date"].notna(),
        "filed_date",
        "period_date_fallback",
    )
    panel["calendar_year"] = panel["period_date"].dt.year
    panel["calendar_quarter"] = panel["period_date"].dt.quarter
    panel["prediction_year"] = panel["prediction_date"].dt.year
    panel["prediction_quarter"] = panel["prediction_date"].dt.quarter
    panel["sic_sector"] = panel["sic"].map(map_sic_to_sector)
    panel["Sector"] = panel["Sector"].fillna(panel["sic_sector"])
    return panel


def drop_invalid_prediction_rows(panel: pd.DataFrame) -> pd.DataFrame:
    invalid = panel["filed_date"].notna() & panel["period_date"].notna() & (panel["filed_date"] < panel["period_date"])
    if invalid.any():
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        panel.loc[invalid].to_csv(REPORT_DIR / "invalid_prediction_timestamp_rows.csv", index=False)
    return panel.loc[~invalid].copy()


def resolve_same_information_date_duplicates(panel: pd.DataFrame) -> pd.DataFrame:
    """Keep one filing per CIK/period/prediction timestamp.

    Same-day original/amended filings do not add a new information date for a
    predictive panel. The deterministic policy keeps the original non-amended
    filing first, then falls back to stable accession-number ordering. Amended
    filings with different prediction dates are retained because they represent
    later information availability.
    """
    keys = ["cik", "period_date", "prediction_date"]
    if panel.empty or not all(col in panel.columns for col in keys):
        return panel

    working = panel.copy()
    working["_amended_rank"] = working["form"].fillna("").astype(str).str.endswith("/A").astype(int)
    working["_form_rank"] = working["form"].map({"10-K": 0, "10-Q": 0, "10-K/A": 1, "10-Q/A": 1}).fillna(9)
    working = working.sort_values(keys + ["_amended_rank", "_form_rank", "adsh"])

    duplicate_mask = working.duplicated(keys, keep=False)
    dropped_mask = working.duplicated(keys, keep="first")
    dropped = working.loc[dropped_mask].drop(columns=["_amended_rank", "_form_rank"], errors="ignore").copy()
    dropped["drop_reason"] = "deterministic_same_cik_period_prediction_duplicate"
    dropped["drop_policy"] = "prefer_non_amended_same_information_date_then_lexicographic_adsh"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if duplicate_mask.any():
        reviewed = working.loc[duplicate_mask].drop(columns=["_amended_rank", "_form_rank"], errors="ignore").copy()
        reviewed["duplicate_policy"] = np.where(
            reviewed.index.isin(dropped.index),
            "drop_same_information_date_duplicate",
            "keep_preferred_same_information_date_row",
        )
        reviewed.to_csv(REPORT_DIR / "same_information_date_duplicate_resolution.csv", index=False)
    else:
        pd.DataFrame(columns=panel.columns.tolist() + ["duplicate_policy"]).to_csv(
            REPORT_DIR / "same_information_date_duplicate_resolution.csv",
            index=False,
        )

    dropped.to_csv(REPORT_DIR / "dropped_duplicate_filing_rows.csv", index=False)
    return working.loc[~dropped_mask].drop(columns=["_amended_rank", "_form_rank"], errors="ignore").copy()


def apply_accounting_quality_controls(panel: pd.DataFrame) -> pd.DataFrame:
    """Null source-selected values that are not economically meaningful facts."""
    panel = panel.copy()
    rows = []

    if "total_assets" in panel:
        asset_mask = panel["total_assets"].notna() & (panel["total_assets"] <= 0)
        for idx, row in panel.loc[asset_mask].iterrows():
            zero_cols = [
                col
                for col in CORE_ACCOUNTING_COLS
                if col in panel.columns and pd.notna(row.get(col)) and float(row.get(col)) == 0.0
            ]
            cols_to_null = sorted(set(["total_assets", *zero_cols]))
            rows.append(
                {
                    "ticker": row.get("ticker"),
                    "cik": row.get("cik"),
                    "adsh": row.get("adsh"),
                    "form": row.get("form"),
                    "period_date": row.get("period_date"),
                    "prediction_date": row.get("prediction_date"),
                    "policy": "non_positive_assets_set_core_zero_accounting_values_null",
                    "columns_set_null": ";".join(cols_to_null),
                    "reason": "Non-positive total assets are not a meaningful operating-firm accounting state in this panel.",
                }
            )
            panel.loc[idx, cols_to_null] = np.nan

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(REPORT_DIR / "accounting_quality_controls_applied.csv", index=False)
    return panel


def map_sic_to_sector(value: object) -> str | float:
    if pd.isna(value):
        return np.nan
    try:
        sic = int(float(value))
    except ValueError:
        return np.nan

    if 100 <= sic <= 999:
        return "Agriculture"
    if 1000 <= sic <= 1499:
        return "Energy"
    if 1500 <= sic <= 1799:
        return "Industrials"
    if 2000 <= sic <= 3999:
        if 2830 <= sic <= 2839 or 3840 <= sic <= 3859:
            return "Healthcare"
        if 3570 <= sic <= 3579 or 3670 <= sic <= 3679 or 3820 <= sic <= 3829:
            return "Technology"
        if 3710 <= sic <= 3799:
            return "Consumer Cyclical"
        return "Industrials"
    if 4000 <= sic <= 4999:
        if 4810 <= sic <= 4899:
            return "Communication Services"
        if 4900 <= sic <= 4999:
            return "Utilities"
        return "Industrials"
    if 5000 <= sic <= 5999:
        return "Consumer Cyclical"
    if 6000 <= sic <= 6799:
        if 6500 <= sic <= 6799:
            return "Real Estate"
        return "Financial Services"
    if 7000 <= sic <= 8999:
        if 7370 <= sic <= 7379:
            return "Technology"
        if 8000 <= sic <= 8099:
            return "Healthcare"
        if 7800 <= sic <= 7999:
            return "Communication Services"
        return "Industrials"
    return np.nan


def add_ratios(panel: pd.DataFrame) -> pd.DataFrame:
    for col in [
        "total_assets",
        "total_liabilities",
        "current_assets",
        "current_liabilities",
        "total_equity",
        "total_revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "cash_equivalents",
        "inventory",
        "accounts_receivable",
        "r_and_d_expense",
    ]:
        if col not in panel:
            panel[col] = np.nan

    panel["leverage_assets"] = safe_divide(panel["total_liabilities"], panel["total_assets"])
    panel["equity_assets"] = safe_divide(panel["total_equity"], panel["total_assets"])
    panel["current_ratio"] = safe_divide(panel["current_assets"], panel["current_liabilities"])
    panel["cash_assets"] = safe_divide(panel["cash_equivalents"], panel["total_assets"])
    panel["net_margin"] = safe_divide(panel["net_income"], panel["total_revenue"])
    panel["operating_margin"] = safe_divide(panel["operating_income"], panel["total_revenue"])
    panel["gross_margin"] = safe_divide(panel["gross_profit"], panel["total_revenue"])
    panel["roa"] = safe_divide(panel["net_income"], panel["total_assets"])
    panel["r_and_d_intensity"] = safe_divide(panel["r_and_d_expense"], panel["total_revenue"])
    panel["inventory_assets"] = safe_divide(panel["inventory"], panel["total_assets"])
    panel["receivables_assets"] = safe_divide(panel["accounts_receivable"], panel["total_assets"])
    return panel


def add_firm_trend_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).copy()
    grouped = panel.groupby("cik", group_keys=False)

    lag_cols = [
        "roa",
        "leverage_assets",
        "current_ratio",
        "cash_assets",
        "net_margin",
        "operating_margin",
        "gross_margin",
    ]
    for col in lag_cols:
        if col in panel:
            panel[f"{col}_lag1"] = grouped[col].shift(1)

    growth_cols = [
        "total_revenue",
        "total_assets",
        "cash_equivalents",
        "total_liabilities",
        "current_assets",
        "current_liabilities",
    ]
    for col in growth_cols:
        if col in panel:
            previous = grouped[col].shift(4)
            panel[f"{col}_growth_4obs"] = safe_divide(panel[col], previous) - 1

    change_cols = [
        "roa",
        "leverage_assets",
        "current_ratio",
        "cash_assets",
        "net_margin",
        "operating_margin",
        "gross_margin",
    ]
    for col in change_cols:
        if col in panel:
            panel[f"{col}_change_4obs"] = panel[col] - grouped[col].shift(4)

    if "net_income" in panel:
        negative_history = [(grouped["net_income"].shift(step) < 0).astype(float) for step in range(1, 5)]
        panel["net_income_negative_count_prior_4obs"] = sum(negative_history)
    return panel


def infer_yoy_periods(fred: pd.DataFrame) -> int:
    median_days = fred["fred_date"].sort_values().diff().dt.days.median()
    if pd.isna(median_days):
        return 4
    if median_days <= 3:
        return 252
    if median_days <= 10:
        return 52
    if median_days <= 45:
        return 12
    if median_days <= 120:
        return 4
    return 1


def read_fred_series(path: Path, transforms: str = "raw") -> pd.DataFrame:
    df = pd.read_csv(path)
    date_col = next((col for col in df.columns if col.lower() in {"date", "observation_date"}), df.columns[0])
    value_col = next((col for col in df.columns if col != date_col), df.columns[-1])
    out = df[[date_col, value_col]].copy()
    out.columns = ["fred_date", path.stem]
    out["fred_date"] = pd.to_datetime(out["fred_date"], errors="coerce")
    out[path.stem] = pd.to_numeric(out[path.stem], errors="coerce")
    out = out.dropna(subset=["fred_date"]).sort_values("fred_date")
    if "raw_yoy" in str(transforms):
        periods = infer_yoy_periods(out)
        out[f"{path.stem}_yoy_pct"] = out[path.stem].pct_change(periods=periods, fill_method=None) * 100
    return out


def fred_series_to_merge() -> list[tuple[Path, str]]:
    if FRED_CATALOG_PATH.exists():
        catalog = pd.read_csv(FRED_CATALOG_PATH)
        catalog = catalog[catalog["include_in_panel"].astype(int) == 1]
        rows = []
        for _, row in catalog.iterrows():
            path = FRED_DIR / f"{row['series_id']}.csv"
            if path.exists():
                rows.append((path, str(row.get("transforms", "raw"))))
        return rows

    return [(path, "raw") for path in sorted(FRED_DIR.glob("*.csv")) if path.name != "fred_download_log.csv"]


def add_fred(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values("prediction_date")
    for path, transforms in fred_series_to_merge():
        fred = read_fred_series(path, transforms)
        panel = pd.merge_asof(
            panel.sort_values("prediction_date"),
            fred,
            left_on="prediction_date",
            right_on="fred_date",
            direction="backward",
        ).drop(columns=["fred_date"], errors="ignore")

    if "FEDFUNDS" in panel:
        panel["high_rate_regime"] = (panel["FEDFUNDS"] >= 4.0).astype("Int64")
    if "VIXCLS" in panel:
        panel["market_stress_regime"] = (panel["VIXCLS"] >= 25.0).astype("Int64")
    if "NFCI" in panel:
        panel["tight_financial_conditions"] = (panel["NFCI"] > 0.0).astype("Int64")
    if "BAMLH0A0HYM2" in panel:
        panel["credit_spread_stress_regime"] = (panel["BAMLH0A0HYM2"] >= 5.0).astype("Int64")
    if "T10Y2Y" in panel or "T10Y3M" in panel:
        panel["yield_curve_inversion_regime"] = (
            panel[[col for col in ["T10Y2Y", "T10Y3M"] if col in panel]].lt(0).any(axis=1)
        ).astype("Int64")
    if "CPIAUCSL_yoy_pct" in panel:
        panel["inflation_pressure_regime"] = (panel["CPIAUCSL_yoy_pct"] >= 4.0).astype("Int64")
    if "DCOILWTICO_yoy_pct" in panel:
        panel["oil_shock_regime"] = (panel["DCOILWTICO_yoy_pct"] >= 30.0).astype("Int64")
    if "DTWEXBGS_yoy_pct" in panel:
        panel["strong_dollar_regime"] = (panel["DTWEXBGS_yoy_pct"] >= 5.0).astype("Int64")
    if "RSAFS_yoy_pct" in panel:
        panel["demand_slowdown_regime"] = (panel["RSAFS_yoy_pct"] < 0.0).astype("Int64")
    if "DRTSCILM" in panel:
        panel["credit_tightening_regime"] = (panel["DRTSCILM"] > 0.0).astype("Int64")

    panel["crisis_regime"] = panel["prediction_year"].isin([2009, 2020, 2022, 2023]).astype("Int64")
    return panel


def add_global_event_context(panel: pd.DataFrame) -> pd.DataFrame:
    if not GLOBAL_EVENT_CALENDAR_PATH.exists():
        return panel

    events = pd.read_csv(GLOBAL_EVENT_CALENDAR_PATH, parse_dates=["event_start", "event_end"])
    if events.empty:
        return panel

    panel = panel.copy().reset_index(drop=True)
    event_types = sorted(events["event_type"].dropna().astype(str).unique())
    panel["global_event_count"] = 0
    panel["global_event_severity_sum"] = 0.0
    for event_type in event_types:
        panel[f"global_event_{event_type}_count"] = 0
        panel[f"global_event_{event_type}_severity"] = 0.0

    active_names: list[list[str]] = [[] for _ in range(len(panel))]
    context_dates = panel["prediction_date"]
    for _, event in events.iterrows():
        mask = context_dates.between(event["event_start"], event["event_end"], inclusive="both")
        event_type = str(event["event_type"])
        severity = float(event["severity_1_5"]) if pd.notna(event["severity_1_5"]) else 1.0

        panel.loc[mask, "global_event_count"] += 1
        panel.loc[mask, "global_event_severity_sum"] += severity
        panel.loc[mask, f"global_event_{event_type}_count"] += 1
        panel.loc[mask, f"global_event_{event_type}_severity"] += severity

        for index in panel.index[mask]:
            active_names[index].append(str(event["event_name"]))

    panel["global_event_names"] = ["; ".join(names) if names else pd.NA for names in active_names]
    return panel


def parse_event_year(notes: object) -> float:
    if pd.isna(notes):
        return np.nan
    text = str(notes)
    marker = "event_year="
    if marker not in text:
        return np.nan
    try:
        return float(text.split(marker, 1)[1].split(";", 1)[0])
    except ValueError:
        return np.nan


def add_targets(panel: pd.DataFrame) -> pd.DataFrame:
    panel["event_year"] = panel["notes"].map(parse_event_year)
    if EVENT_DATES_PATH.exists():
        events = pd.read_csv(EVENT_DATES_PATH, parse_dates=["event_date"])
        event_cols = ["ticker", "event_date", "event_type", "event_label", "verification_status"]
        events = events[event_cols].rename(columns={"ticker": "event_source_ticker"})
        if "event_lookup_tickers" not in panel.columns:
            panel["event_lookup_tickers"] = panel["ticker"].astype(str)
        row_lookup = panel[["adsh", "ticker", "event_lookup_tickers"]].copy()
        row_lookup["_row_id"] = row_lookup.index
        row_lookup["event_source_ticker"] = row_lookup["event_lookup_tickers"].fillna(row_lookup["ticker"]).astype(str).str.split(";")
        row_lookup = row_lookup.explode("event_source_ticker")
        row_lookup["event_source_ticker"] = row_lookup["event_source_ticker"].astype(str).str.strip()
        matched_events = row_lookup.merge(events, on="event_source_ticker", how="left")
        matched_events = matched_events[matched_events["event_date"].notna()].copy()
        if not matched_events.empty:
            matched_events["event_rank"] = matched_events["event_label"].map({"formal_distress": 0, "near_distress": 1}).fillna(9)
            matched_events = matched_events.sort_values(["_row_id", "event_rank", "event_date"])
            matched_events = matched_events.drop_duplicates("_row_id", keep="first")
            event_payload = matched_events[
                ["_row_id", "event_source_ticker", "event_date", "event_type", "event_label", "verification_status"]
            ].set_index("_row_id")
            for column in ["event_source_ticker", "event_date", "event_type", "event_label", "verification_status"]:
                panel[column] = pd.NA
            for column in event_payload.columns:
                panel.loc[event_payload.index, column] = event_payload[column]
            panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
        else:
            panel["event_source_ticker"] = pd.NA
            panel["event_date"] = pd.NaT
            panel["event_type"] = pd.NA
            panel["event_label"] = pd.NA
            panel["verification_status"] = pd.NA
    else:
        panel["event_source_ticker"] = pd.NA
        panel["event_date"] = pd.NaT
        panel["event_type"] = pd.NA
        panel["event_label"] = pd.NA
        panel["verification_status"] = pd.NA

    notes = panel["notes"].fillna("").astype(str)
    panel["formal_distress_firm"] = (
        (panel["event_label"] == "formal_distress")
        | (
            (panel["cohort"] == "distress_candidates")
            & notes.str.contains("bankruptcy|bank_failure|liquidation|receivership", case=False, regex=True)
            & ~notes.str.contains("near_distress", case=False, regex=False)
        )
    ).astype("Int64")
    panel["near_distress_firm"] = (
        (panel["event_label"] == "near_distress")
        | notes.str.contains("near_distress", case=False, regex=False)
    ).astype("Int64")

    fallback_event_date = pd.to_datetime(
        panel["event_year"].astype("Int64").astype(str) + "-12-31",
        format="%Y-%m-%d",
        errors="coerce",
    )
    panel["event_date"] = panel["event_date"].fillna(fallback_event_date)

    days_from_period_to_event = (panel["event_date"] - panel["period_date"]).dt.days
    days_to_event = (panel["event_date"] - panel["prediction_date"]).dt.days
    panel["days_from_period_to_event"] = days_from_period_to_event
    panel["days_to_event"] = days_to_event
    panel["post_event_flag"] = (
        (panel["formal_distress_firm"] == 1) & panel["event_date"].notna() & (panel["prediction_date"] >= panel["event_date"])
    ).astype("Int64")
    panel["distress_next_2q"] = (
        (panel["formal_distress_firm"] == 1) & (days_to_event > 0) & (days_to_event <= 228)
    ).astype("Int64")
    panel["distress_next_4q"] = (
        (panel["formal_distress_firm"] == 1) & (days_to_event > 0) & (days_to_event <= 456)
    ).astype("Int64")
    panel["distress_next_8q"] = (
        (panel["formal_distress_firm"] == 1) & (days_to_event > 0) & (days_to_event <= 912)
    ).astype("Int64")
    panel["broad_distress_next_4q"] = (
        ((panel["formal_distress_firm"] == 1) | (panel["near_distress_firm"] == 1))
        & (days_to_event > 0)
        & (days_to_event <= 456)
    ).astype("Int64")

    panel["healthy_current"] = (
        (panel["net_income"] > 0)
        & (panel["roa"] > 0)
        & (panel["leverage_assets"].between(0, 0.85, inclusive="both"))
        & (panel["formal_distress_firm"] == 0)
    ).astype("Int64")
    panel["resilient_profitability"] = panel["healthy_current"]
    panel = add_failure_pressure_targets(panel)
    return add_forward_success_targets(panel)


def add_failure_pressure_targets(panel: pd.DataFrame) -> pd.DataFrame:
    """Add the promoted broader financial-pressure target.

    The target remains null when there are not enough future filing observations,
    unless strict legal distress is already observed within the four-quarter window.
    Post-event rows are left null because they are excluded from primary modeling.
    """
    target_col = "failure_pressure_conservative_v2_next_4obs"
    panel = panel.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).copy()
    panel[target_col] = pd.Series(pd.NA, index=panel.index, dtype="Int64")
    work = panel[panel["post_event_flag"].fillna(0).astype(int) == 0].copy()

    def future_shifts(group: pd.DataFrame, column: str) -> list[pd.Series]:
        return [group[column].shift(-step) for step in range(1, 5)]

    def valid_count(shifts: list[pd.Series]) -> pd.Series:
        return pd.concat([series.notna().astype(int) for series in shifts], axis=1).sum(axis=1)

    def condition_count(shifts: list[pd.Series], condition) -> pd.Series:
        return pd.concat([condition(series).fillna(False).astype(int) for series in shifts], axis=1).sum(axis=1)

    def add_group_target(group: pd.DataFrame) -> pd.DataFrame:
        group = group.copy()
        future_observation_count = sum(group["adsh"].shift(-step).notna().astype(int) for step in range(1, 5))

        net_income = future_shifts(group, "net_income")
        roa = future_shifts(group, "roa")
        leverage = future_shifts(group, "leverage_assets")
        current_ratio = future_shifts(group, "current_ratio")
        cash_assets = future_shifts(group, "cash_assets")
        revenue = future_shifts(group, "total_revenue")
        assets = future_shifts(group, "total_assets")

        future_net_income_valid_count = valid_count(net_income)
        future_income_nonpositive_count = condition_count(net_income, lambda series: series <= 0)
        future_leverage_stress_count = condition_count(leverage, lambda series: series > 0.85)
        future_liquidity_stress_count = condition_count(current_ratio, lambda series: series < 1.0)
        future_cash_stress_count = condition_count(cash_assets, lambda series: series < 0.03)

        future_roa_mean = pd.concat(roa, axis=1).mean(axis=1, skipna=True)
        future_roa_change = future_roa_mean - group["roa"]
        future_revenue_growth = revenue[-1] / group["total_revenue"].replace(0, np.nan) - 1
        future_assets_growth = assets[-1] / group["total_assets"].replace(0, np.nan) - 1

        unhealthy_parts = []
        for index in range(4):
            unhealthy_parts.append(
                (
                    (net_income[index].notna() & (net_income[index] <= 0))
                    | (roa[index].notna() & (roa[index] <= 0))
                    | (leverage[index].notna() & (leverage[index] > 0.85))
                ).astype(int)
            )
        future_unhealthy_count = pd.concat(unhealthy_parts, axis=1).sum(axis=1)

        formal = group["distress_next_4q"].fillna(0).astype(int) == 1
        valid_horizon = future_observation_count >= 3
        valid_or_formal = valid_horizon | formal
        severe_profit_failure = (future_income_nonpositive_count >= 3) & (future_net_income_valid_count >= 3)
        balance_stress_any = (
            (future_leverage_stress_count >= 1)
            | (future_liquidity_stress_count >= 1)
            | (future_cash_stress_count >= 1)
        ) & valid_horizon
        strong_deterioration = (
            (future_roa_change <= -0.04)
            | (future_revenue_growth <= -0.15)
            | (future_assets_growth <= -0.15)
        ) & valid_horizon
        unhealthy_future = (future_unhealthy_count >= 3) & valid_horizon
        positive = formal | (severe_profit_failure & (balance_stress_any | strong_deterioration | unhealthy_future))

        out = pd.Series(pd.NA, index=group.index, dtype="Int64")
        out.loc[valid_or_formal] = positive.loc[valid_or_formal].fillna(False).astype(int).astype("Int64")
        group[target_col] = out
        return group[[target_col]]

    if not work.empty:
        targets = work.groupby("cik", group_keys=False).apply(add_group_target)
        panel.loc[targets.index, target_col] = targets[target_col]
    return panel


def add_forward_success_targets(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).copy()

    def add_group_targets(group: pd.DataFrame) -> pd.DataFrame:
        net_income_valid = group["net_income"].notna().astype(float)
        roa_valid = group["roa"].notna().astype(float)
        leverage_valid = group["leverage_assets"].notna().astype(float)

        net_income_positive = ((group["net_income"] > 0) & group["net_income"].notna()).astype(float)
        leverage_ok = (
            group["leverage_assets"].between(0, 0.85, inclusive="both") & group["leverage_assets"].notna()
        ).astype(float)
        healthy_components_valid = (
            group["net_income"].notna() & group["roa"].notna() & group["leverage_assets"].notna()
        ).astype(float)
        healthy_missing_aware = (
            (healthy_components_valid == 1)
            & (group["net_income"] > 0)
            & (group["roa"] > 0)
            & group["leverage_assets"].between(0, 0.85, inclusive="both")
        ).astype(float)
        roa_value = group["roa"].astype(float).fillna(0)

        def future_sum(series: pd.Series) -> pd.Series:
            return sum(series.shift(-step).fillna(0) for step in range(1, 5))

        future_net_income_valid_count = future_sum(net_income_valid)
        future_roa_valid_count = future_sum(roa_valid)
        future_leverage_valid_count = future_sum(leverage_valid)
        future_health_valid_count = future_sum(healthy_components_valid)
        future_healthy_count = future_sum(healthy_missing_aware)
        future_positive_income_count = future_sum(net_income_positive)
        future_leverage_ok_count = future_sum(leverage_ok)
        future_roa_sum = future_sum(roa_value)
        future_roa_mean = future_roa_sum / future_roa_valid_count.replace(0, np.nan)

        no_formal_distress = group["formal_distress_firm"].fillna(0).astype(int) == 0

        def nullable_target(known: pd.Series, positive: pd.Series) -> pd.Series:
            out = pd.Series(pd.NA, index=group.index, dtype="Int64")
            out.loc[known] = positive.loc[known].astype(int).astype("Int64")
            return out

        profitability_known = future_net_income_valid_count >= 3
        group["success_profitability_next_4q"] = nullable_target(
            profitability_known,
            future_positive_income_count >= 3,
        )

        resilience_known = future_health_valid_count >= 3
        group["success_resilience_next_4q"] = nullable_target(
            resilience_known,
            (future_healthy_count >= 3) & no_formal_distress,
        )

        quality_known = (
            (future_net_income_valid_count >= 3)
            & (future_roa_valid_count >= 3)
            & (future_leverage_valid_count >= 3)
        )
        group["success_quality_next_4q"] = nullable_target(
            quality_known,
            (future_positive_income_count >= 3)
            & (future_roa_mean > 0.01)
            & (future_leverage_ok_count >= 3)
            & no_formal_distress,
        )
        return group

    return panel.groupby("cik", group_keys=False).apply(add_group_targets)


def clean_extremes(panel: pd.DataFrame, stage: str = "final") -> pd.DataFrame:
    numeric_cols = panel.select_dtypes(include=[np.number]).columns
    panel[numeric_cols] = panel[numeric_cols].replace([np.inf, -np.inf], np.nan)
    cleanup_rows = []
    for col in derived_feature_columns(panel):
        if col not in panel:
            continue
        extreme_mask = panel[col].abs() > DERIVED_FEATURE_ABS_MAX
        extreme_count = int(extreme_mask.fillna(False).sum())
        if extreme_count:
            panel.loc[extreme_mask, col] = np.nan
        cleanup_rows.append(
            {
                "stage": stage,
                "column": col,
                "threshold_abs_gt": DERIVED_FEATURE_ABS_MAX,
                "values_set_null": extreme_count,
                "missing_share_after": float(panel[col].isna().mean()),
            }
        )
    if cleanup_rows:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(cleanup_rows).to_csv(REPORT_DIR / f"derived_feature_extreme_cleanup_{stage}.csv", index=False)
    return panel


def write_reports(panel: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "rows": len(panel),
        "columns": len(panel.columns),
        "firms_cik": panel["cik"].nunique(),
        "tickers": panel["ticker"].nunique(),
        "date_min": panel["period_date"].min(),
        "date_max": panel["period_date"].max(),
        "prediction_date_min": panel["prediction_date"].min(),
        "prediction_date_max": panel["prediction_date"].max(),
        "prediction_date_fallback_rows": int((panel["prediction_date_source"] == "period_date_fallback").sum()),
        "post_event_rows": int(panel["post_event_flag"].sum()),
        "distress_next_2q_positive": int(panel["distress_next_2q"].sum()),
        "distress_next_4q_positive": int(panel["distress_next_4q"].sum()),
        "distress_next_8q_positive": int(panel["distress_next_8q"].sum()),
        "broad_distress_next_4q_positive": int(panel["broad_distress_next_4q"].sum()),
        "resilient_profitability_positive": int(panel["resilient_profitability"].sum()),
        "success_profitability_next_4q_positive": int(panel["success_profitability_next_4q"].sum()),
        "success_resilience_next_4q_positive": int(panel["success_resilience_next_4q"].sum()),
        "success_quality_next_4q_positive": int(panel["success_quality_next_4q"].sum()),
    }
    pd.DataFrame([summary]).to_csv(REPORT_DIR / "panel_v2_summary.csv", index=False)

    missing = (
        panel.isna()
        .mean()
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index": "column"})
        .sort_values("missing_share", ascending=False)
    )
    missing.to_csv(REPORT_DIR / "panel_v2_missingness.csv", index=False)

    coverage = (
        panel.groupby(["cohort", "ticker"], dropna=False)
        .agg(
            rows=("adsh", "nunique"),
            first_period=("period_date", "min"),
            last_period=("period_date", "max"),
            first_prediction_date=("prediction_date", "min"),
            last_prediction_date=("prediction_date", "max"),
        )
        .reset_index()
        .sort_values(["cohort", "rows"], ascending=[True, False])
    )
    coverage.to_csv(REPORT_DIR / "panel_v2_firm_coverage.csv", index=False)


def classify_schema_column(column: str) -> str:
    identifiers = {
        "adsh",
        "cik",
        "name",
        "ticker",
        "ticker_aliases",
        "event_lookup_tickers",
        "firm_id",
        "shortname",
        "sec_name",
        "period",
        "period_date",
        "filed",
        "filed_date",
        "prediction_date",
        "prediction_date_source",
        "prediction_year",
        "prediction_quarter",
        "fy",
        "fp",
        "form",
        "afs",
        "sec_zip",
        "calendar_year",
        "calendar_quarter",
    }
    industry = {
        "sic",
        "sic_sector",
        "Sector",
        "Industry",
        "exchange",
        "cohort",
        "include_status",
        "notes",
        "duplicate_cik_alias_count",
    }
    accounting = {
        "accounts_receivable",
        "capex",
        "cash_equivalents",
        "cash_flow_financing",
        "cash_flow_investing",
        "cash_flow_operating",
        "cost_of_revenue",
        "current_assets",
        "current_liabilities",
        "depreciation_amortization",
        "eps_basic",
        "eps_diluted",
        "gross_profit",
        "inventory",
        "long_term_debt",
        "net_income",
        "noncurrent_liabilities",
        "operating_income",
        "ppe_net",
        "pretax_income",
        "r_and_d_expense",
        "retained_earnings",
        "sg_and_a",
        "shares_outstanding",
        "short_term_debt",
        "total_assets",
        "total_equity",
        "total_liabilities",
        "total_revenue",
        "wavg_shares_basic",
        "wavg_shares_diluted",
    }
    ratios = {
        "leverage_assets",
        "equity_assets",
        "current_ratio",
        "cash_assets",
        "net_margin",
        "operating_margin",
        "gross_margin",
        "roa",
        "r_and_d_intensity",
        "inventory_assets",
        "receivables_assets",
    }
    event_metadata = {
        "event_year",
        "event_date",
        "event_type",
        "event_label",
        "event_source_ticker",
        "verification_status",
        "formal_distress_firm",
        "near_distress_firm",
        "days_from_period_to_event",
        "days_to_event",
        "post_event_flag",
    }
    targets = {
        "distress_next_2q",
        "distress_next_4q",
        "distress_next_8q",
        "broad_distress_next_4q",
        "healthy_current",
        "resilient_profitability",
        "success_profitability_next_4q",
        "success_resilience_next_4q",
        "success_quality_next_4q",
        "failure_pressure_conservative_v2_next_4obs",
        "industry_relative_resilience_next_4obs",
        "stress_resilience_next_4obs",
        "recovery_next_4obs",
        "quality_success_cashflow_next_4obs",
    }
    regimes = {col for col in [
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
    ]}

    if column in identifiers:
        return "identifier_or_time"
    if column in industry:
        return "industry_or_universe_metadata"
    if column in accounting:
        return "sec_accounting_fundamental"
    if column in ratios:
        return "financial_ratio"
    if column.endswith("_lag1") or column.endswith("_growth_4obs") or column.endswith("_change_4obs") or column == "net_income_negative_count_prior_4obs":
        return "firm_trend_or_deterioration"
    if column in regimes:
        return "macro_regime_indicator"
    if column.startswith("global_event_"):
        return "global_event_context"
    if column in event_metadata:
        return "event_metadata"
    if column in targets:
        return "target_label"
    return "macro_variable" if column.isupper() or column.endswith("_yoy_pct") else "other"


def write_outputs(panel: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    GITHUB_DIR.mkdir(parents=True, exist_ok=True)

    panel.to_csv(FULL_PANEL_CSV_GZ, index=False, compression="gzip")
    panel.to_csv(GITHUB_PANEL_CSV_GZ, index=False, compression="gzip")
    try:
        panel.to_parquet(FULL_PANEL_PARQUET, index=False)
        panel.to_parquet(GITHUB_PANEL_PARQUET, index=False)
    except ImportError:
        print("Parquet engine unavailable; wrote CSV.GZ only")

    sample = panel.sort_values(["ticker", "prediction_date", "period_date"]).groupby("ticker", group_keys=False).head(2).head(500)
    sample.to_csv(SAMPLE_PANEL_CSV, index=False)

    schema = pd.DataFrame(
        {
            "column": panel.columns,
            "dtype": [str(dtype) for dtype in panel.dtypes],
            "feature_family": [classify_schema_column(col) for col in panel.columns],
            "missing_share": [panel[col].isna().mean() for col in panel.columns],
        }
    )
    schema.to_csv(SCHEMA_CSV, index=False)
    schema.to_csv(GITHUB_SCHEMA_CSV, index=False)


def main() -> None:
    universe = read_universe()
    concept_map = read_concept_map()
    print(f"Building panel for {universe['cik'].nunique()} CIKs")
    panel = parse_sec_fsd(universe, concept_map)
    panel = add_universe_metadata(panel, universe)
    panel = drop_invalid_prediction_rows(panel)
    panel = resolve_same_information_date_duplicates(panel)
    panel = apply_accounting_quality_controls(panel)
    panel = add_ratios(panel)
    panel = clean_extremes(panel, stage="post_ratio_pre_trend")
    panel = add_firm_trend_features(panel)
    panel = clean_extremes(panel, stage="post_trend_pre_target")
    panel = add_fred(panel)
    panel = add_global_event_context(panel)
    panel = add_targets(panel)
    panel = clean_extremes(panel, stage="final")
    panel = panel.sort_values(["ticker", "prediction_date", "period_date", "filed_date"])
    write_reports(panel)
    write_outputs(panel)
    print(f"Wrote {len(panel):,} rows to {FULL_PANEL_CSV_GZ}")


if __name__ == "__main__":
    main()
