#!/usr/bin/env python3
"""Generate the thesis-ready master data/model/target explainer.

The output is intentionally generated from the current schema and saved report
artifacts so that the column dictionary stays synchronized with the production
panel.
"""

from __future__ import annotations

import csv
import glob
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "data/github/firm_panel_v2_schema.csv"
DOC_PATH = ROOT / "docs/MASTER_DATA_MODEL_TARGET_EXPLAINER.md"
DICT_PATH = ROOT / "reports/documentation/master_column_dictionary.csv"


def pct(x: float | int | None, digits: int = 1) -> str:
    if x is None or pd.isna(x):
        return "not documented"
    return f"{100 * float(x):.{digits}f}%"


def metric(x: float | int | None, digits: int = 3) -> str:
    if x is None or pd.isna(x):
        return "not documented"
    return f"{float(x):.{digits}f}"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def read_feature_columns() -> set[str]:
    cols: set[str] = set()
    for path in glob.glob(str(ROOT / "reports/data_quality/model_feature_lists/*features.csv")):
        df = pd.read_csv(path)
        if "column" in df.columns:
            cols.update(df["column"].dropna().astype(str))
    return cols


IDENTIFIER_MEANINGS = {
    "adsh": "SEC accession/submission identifier for the filing observation.",
    "cik": "SEC Central Index Key, used as the stable firm identifier.",
    "name": "SEC company name from the filing/submission metadata.",
    "afs": "SEC accelerated-filer status metadata.",
    "form": "SEC filing form, mainly 10-K, 10-K/A, 10-Q, and 10-Q/A.",
    "period": "SEC filing period end date in numeric YYYYMMDD form.",
    "fy": "Fiscal year reported in the SEC filing metadata.",
    "fp": "Fiscal period code from SEC metadata, such as FY, Q1, Q2, or Q3.",
    "filed": "SEC filing date in numeric YYYYMMDD form.",
    "sec_zip": "SEC FSD ZIP/source package from which the filing was parsed.",
    "ticker": "Ticker or display identifier used for readability.",
    "firm_id": "Internal firm identifier used to join firm-level observations.",
    "shortname": "Short readable firm name.",
    "sec_name": "Company name from SEC metadata.",
    "period_date": "Accounting period end date described by the filing.",
    "filed_date": "Date when the SEC filing became available.",
    "prediction_date": "Information date for modeling; equals filed_date in the production panel.",
    "prediction_date_source": "Audit field showing which date source produced prediction_date.",
    "calendar_year": "Calendar year of the accounting period.",
    "calendar_quarter": "Calendar quarter of the accounting period.",
    "prediction_year": "Calendar year of prediction_date, used for temporal validation splits.",
    "prediction_quarter": "Calendar quarter of prediction_date; current model feature for filing-season context.",
}

INDUSTRY_MEANINGS = {
    "sic": "SEC SIC industry code.",
    "exchange": "Listing exchange or exchange metadata where available.",
    "Sector": "Broad sector label used for industry comparisons and current model categorical encoding.",
    "Industry": "More detailed industry label used for dashboard and descriptive analysis.",
    "cohort": "Universe-selection bucket explaining why the firm is included.",
    "include_status": "Universe inclusion status metadata.",
    "notes": "Free-form universe note; contents are not standardized for modeling.",
    "sic_sector": "Sector grouping derived from SIC metadata.",
}

ACCOUNTING_MEANINGS = {
    "accounts_receivable": "Accounts receivable, usually current receivables net of allowances.",
    "capex": "Capital expenditure, primarily payments to acquire property, plant, and equipment.",
    "cash_equivalents": "Cash and cash equivalents, including restricted cash when mapped by the SEC concept map.",
    "cash_flow_financing": "Net cash provided by or used in financing activities.",
    "cash_flow_investing": "Net cash provided by or used in investing activities.",
    "cash_flow_operating": "Net cash provided by or used in operating activities.",
    "cost_of_revenue": "Cost of revenue, cost of goods sold, or cost of sales according to mapped SEC tags.",
    "current_assets": "Current assets.",
    "current_liabilities": "Current liabilities.",
    "depreciation_amortization": "Depreciation, depletion, and amortization expense.",
    "eps_basic": "Basic earnings per share.",
    "eps_diluted": "Diluted earnings per share.",
    "gross_profit": "Gross profit where separately reported.",
    "inventory": "Inventory, net.",
    "long_term_debt": "Long-term debt where separately reported.",
    "net_income": "Net income or loss.",
    "noncurrent_liabilities": "Noncurrent liabilities where separately reported.",
    "operating_income": "Operating income or loss.",
    "ppe_net": "Property, plant, and equipment, net.",
    "pretax_income": "Income or loss before income taxes, extraordinary items, and noncontrolling interest where mapped.",
    "r_and_d_expense": "Research and development expense.",
    "retained_earnings": "Retained earnings or accumulated deficit.",
    "sg_and_a": "Selling, general, and administrative expense.",
    "shares_outstanding": "Common shares outstanding.",
    "short_term_debt": "Short-term borrowings or current debt.",
    "total_assets": "Total assets.",
    "total_equity": "Stockholders' equity, including noncontrolling interest where mapped.",
    "total_liabilities": "Total liabilities.",
    "total_revenue": "Revenue, sales, or revenue from contracts with customers according to mapped SEC tags.",
    "wavg_shares_basic": "Weighted average basic shares outstanding.",
    "wavg_shares_diluted": "Weighted average diluted shares outstanding.",
}

RATIO_FORMULAS = {
    "leverage_assets": ("total liabilities divided by total assets", "Calculated leverage ratio showing how much of assets are financed by liabilities."),
    "equity_assets": ("total equity divided by total assets", "Calculated capitalization ratio showing book equity relative to assets."),
    "current_ratio": ("current assets divided by current liabilities", "Calculated liquidity ratio for short-term balance-sheet coverage."),
    "cash_assets": ("cash and equivalents divided by total assets", "Calculated liquidity buffer relative to firm size."),
    "net_margin": ("net income divided by total revenue", "Calculated profitability margin after all expenses."),
    "operating_margin": ("operating income divided by total revenue", "Calculated operating profitability margin."),
    "gross_margin": ("gross profit divided by total revenue", "Calculated gross profitability margin where gross profit is available."),
    "roa": ("net income divided by total assets", "Calculated return on assets; it is an engineered ratio, not a raw SEC line item."),
    "r_and_d_intensity": ("R&D expense divided by total revenue", "Calculated innovation/intangible-investment intensity where R&D is reported."),
    "inventory_assets": ("inventory divided by total assets", "Calculated inventory exposure relative to assets."),
    "receivables_assets": ("accounts receivable divided by total assets", "Calculated receivables exposure relative to assets."),
}

MACRO_META = {
    "BAMLH0A0HYM2": ("High-yield corporate bond spread", "Credit stress and risky financing conditions", "Higher spreads are expected to be associated with more distress pressure and lower resilience."),
    "FEDFUNDS": ("Federal funds rate", "Monetary policy and rate pressure", "Higher rates may increase financing pressure, especially for leveraged firms."),
    "GDPC1": ("Real GDP", "Aggregate economic activity", "Weaker growth is expected to be associated with lower firm resilience."),
    "GS10": ("10-year Treasury yield", "Long-term rate environment", "Higher yields may raise discount rates and financing costs."),
    "INDPRO": ("Industrial production index", "Production-side economic activity", "Weaker industrial activity may pressure cyclical sectors."),
    "INDPRO_yoy_pct": ("Industrial production year-over-year percent change", "Growth-rate version of industrial activity", "Lower growth is expected to signal demand weakness."),
    "M2SL": ("M2 money supply", "Liquidity and monetary conditions", "Liquidity contraction or slower money growth may coincide with tighter conditions."),
    "M2SL_yoy_pct": ("M2 money supply year-over-year percent change", "Liquidity growth rate", "Lower growth may indicate less supportive liquidity conditions."),
    "NFCI": ("Chicago Fed National Financial Conditions Index", "Broad financial conditions", "Higher values mean tighter conditions and may be associated with pressure."),
    "UNRATE": ("Unemployment rate", "Labor-market weakness", "Higher unemployment can proxy demand stress and macro weakness."),
    "USEPUINDXD": ("U.S. economic policy uncertainty index", "Policy uncertainty", "Higher uncertainty may reduce investment and increase risk."),
    "VIXCLS": ("VIX volatility index", "Market volatility and risk appetite", "Higher volatility is expected to coincide with risk stress."),
    "T10Y2Y": ("10-year minus 2-year Treasury spread", "Yield-curve slope", "Lower or inverted spread can signal future macro stress."),
    "T10Y3M": ("10-year minus 3-month Treasury spread", "Yield-curve slope", "Lower or inverted spread can signal future macro stress."),
    "DCOILWTICO": ("WTI crude oil price", "Commodity and energy cost shock", "Higher or volatile oil prices may affect sectors differently."),
    "DCOILWTICO_yoy_pct": ("WTI crude oil year-over-year percent change", "Oil shock pressure", "Large increases may pressure input costs and consumers while helping some energy firms."),
    "DTWEXBGS": ("Broad nominal U.S. dollar index", "Dollar strength and external competitiveness", "A stronger dollar may pressure exporters and firms with foreign revenue exposure."),
    "DTWEXBGS_yoy_pct": ("Broad dollar index year-over-year percent change", "Dollar-strength shock", "Higher growth may indicate exchange-rate pressure."),
    "CPIAUCSL": ("Consumer price index", "Consumer inflation level", "Higher inflation can increase cost and rate pressure."),
    "CPIAUCSL_yoy_pct": ("CPI year-over-year percent change", "Inflation pressure", "Higher inflation may raise costs and monetary-policy pressure."),
    "PPIACO": ("Producer price index for all commodities", "Input-cost inflation level", "Higher producer prices may pressure margins."),
    "PPIACO_yoy_pct": ("PPI year-over-year percent change", "Input-cost inflation pressure", "Higher growth may pressure cost structures."),
    "PAYEMS": ("Total nonfarm payroll employment", "Labor-market activity", "Weaker employment conditions can signal demand weakness."),
    "PAYEMS_yoy_pct": ("Payroll employment year-over-year percent change", "Labor-market growth", "Lower growth may signal weakening demand conditions."),
    "RSAFS": ("Retail sales", "Consumer demand", "Lower retail sales may pressure consumer-facing firms."),
    "RSAFS_yoy_pct": ("Retail sales year-over-year percent change", "Consumer-demand growth", "Lower growth is expected to weaken resilience in demand-sensitive sectors."),
    "HOUST": ("Housing starts", "Rate-sensitive real-economy activity", "Lower housing starts may indicate rate-sensitive demand weakness."),
    "HOUST_yoy_pct": ("Housing starts year-over-year percent change", "Housing activity growth", "Lower growth can indicate pressure on housing-linked sectors."),
    "BUSLOANS": ("Commercial and industrial loans", "Business credit availability", "Weak loan growth can indicate tighter credit or weaker demand."),
    "BUSLOANS_yoy_pct": ("Commercial and industrial loans year-over-year percent change", "Business-credit growth", "Lower growth may signal tighter credit availability."),
    "DRTSCILM": ("Bank lending standards for C&I loans to large and middle-market firms", "Credit tightening", "Higher tightening standards are expected to increase financing pressure."),
}

REGIME_MEANINGS = {
    "high_rate_regime": "Federal funds rate is at least 4 percent.",
    "market_stress_regime": "VIX is at least 25.",
    "tight_financial_conditions": "NFCI is above 0, meaning tighter-than-average financial conditions.",
    "credit_spread_stress_regime": "High-yield spread is at least 5 percentage points.",
    "yield_curve_inversion_regime": "T10Y2Y or T10Y3M is below 0.",
    "inflation_pressure_regime": "CPI year-over-year inflation is at least 4 percent.",
    "oil_shock_regime": "WTI oil year-over-year change is at least 30 percent.",
    "strong_dollar_regime": "Broad U.S. dollar index year-over-year change is at least 5 percent.",
    "demand_slowdown_regime": "Retail sales year-over-year change is below 0.",
    "credit_tightening_regime": "Bank lending-standards tightening measure is positive.",
    "crisis_regime": "Prediction year is 2009, 2020, 2022, or 2023.",
}

EVENT_METADATA_MEANINGS = {
    "event_year": "Year of a curated distress event for firms with event metadata.",
    "event_date": "Curated formal distress event date where available.",
    "event_type": "Curated distress/near-distress event type.",
    "event_label": "Readable event label for the curated event.",
    "verification_status": "Manual/source verification status for the event-date row.",
    "formal_distress_firm": "Firm-level flag for a formal distress event in the event metadata.",
    "near_distress_firm": "Firm-level flag for near-distress or context cases not used as strict legal distress.",
    "days_from_period_to_event": "Days from accounting period end to the curated event date.",
    "days_to_event": "Days from prediction_date to the curated event date.",
    "post_event_flag": "Flag for rows on or after a formal event date; excluded from primary forward-looking model training.",
}

TARGET_MEANINGS = {
    "distress_next_2q": "Strict formal distress within the shorter forward horizon; exact day horizon is not documented / requires review.",
    "distress_next_4q": "Strict formal distress event after prediction_date and within 456 days.",
    "distress_next_8q": "Strict formal distress within the longer forward horizon; exact day horizon is not documented / requires review.",
    "broad_distress_next_4q": "Earlier broad distress target retained as a secondary label; exact current rule is not documented / requires review.",
    "healthy_current": "Current-period healthy-firm indicator; exact rule is not documented / requires review.",
    "resilient_profitability": "Current or historical profitability/resilience indicator; exact rule is not documented / requires review.",
    "failure_pressure_conservative_v2_next_4obs": "Main production broader failure-pressure target: formal distress or repeated future profitability weakness with serious balance-stress, deterioration, or unhealthy-future signals.",
    "success_profitability_next_4q": "Missing-aware forward profitability target with 29,977 known rows and 24,963 positives.",
    "success_resilience_next_4q": "Main production success/resilience target requiring enough observed future net income, ROA, and leverage/assets components.",
    "success_quality_next_4q": "Missing-aware future success-quality target with 20,161 known rows and 8,691 positives.",
}


def source_for_family(family: str, column: str) -> str:
    if family == "sec_accounting_fundamental":
        return "SEC"
    if family == "financial_ratio":
        return "calculated ratio"
    if family == "firm_trend_or_deterioration":
        return "trend feature"
    if family == "macro_variable":
        return "FRED"
    if family == "macro_regime_indicator":
        return "regime"
    if family == "global_event_context":
        return "global event"
    if family == "target_label":
        return "target"
    if family == "event_metadata":
        return "target/audit metadata"
    if family == "industry_or_universe_metadata":
        return "metadata"
    if family == "identifier_or_time":
        return "SEC metadata"
    return "not documented / requires review"


def meaning_for(column: str, family: str) -> str:
    if column in IDENTIFIER_MEANINGS:
        return IDENTIFIER_MEANINGS[column]
    if column in INDUSTRY_MEANINGS:
        return INDUSTRY_MEANINGS[column]
    if column in ACCOUNTING_MEANINGS:
        return ACCOUNTING_MEANINGS[column]
    if column in RATIO_FORMULAS:
        return RATIO_FORMULAS[column][1] + f" Formula: {RATIO_FORMULAS[column][0]}."
    if column.endswith("_lag1"):
        base = column.removesuffix("_lag1")
        return f"One-observation lag of {base}, using prior firm observation only."
    if column.endswith("_growth_4obs"):
        base = column.removesuffix("_growth_4obs")
        return f"Four-observation growth feature for {base}: current value versus value four prior observations earlier."
    if column.endswith("_change_4obs"):
        base = column.removesuffix("_change_4obs")
        return f"Four-observation change feature for {base}: current value minus value four prior observations earlier."
    if column == "net_income_negative_count_prior_4obs":
        return "Count of prior four firm observations with negative net income."
    if column in MACRO_META:
        return MACRO_META[column][0] + "."
    if column in REGIME_MEANINGS:
        return REGIME_MEANINGS[column]
    if column == "global_event_count":
        return "Count of curated global event windows active on the prediction_date."
    if column == "global_event_severity_sum":
        return "Sum of severity scores for curated global event windows active on the prediction_date."
    if column == "global_event_names":
        return "Readable names of active curated global events attached to the prediction_date."
    if column.startswith("global_event_"):
        rest = column.removeprefix("global_event_")
        if rest.endswith("_count"):
            event_type = rest.removesuffix("_count").replace("_", " ")
            return f"Count of active curated {event_type} event windows at prediction_date."
        if rest.endswith("_severity"):
            event_type = rest.removesuffix("_severity").replace("_", " ")
            return f"Severity sum for active curated {event_type} event windows at prediction_date."
    if column in EVENT_METADATA_MEANINGS:
        return EVENT_METADATA_MEANINGS[column]
    if column in TARGET_MEANINGS:
        return TARGET_MEANINGS[column]
    return "not documented / requires review"


def missingness_caveat(row: pd.Series) -> str:
    family = row["feature_family"]
    col = row["column"]
    share = float(row["missing_share"])
    base = f"Schema missing share: {pct(share)}."
    if share == 0:
        return base + " No missing values observed in the schema snapshot."
    if family == "target_label":
        return base + " Null target labels mean unknown future outcome or insufficient future information, not automatic zero."
    if family == "event_metadata":
        return base + " Event metadata is populated mainly for event-linked firms; missing means no documented event metadata on that row."
    if family == "global_event_context" and col == "global_event_names":
        return base + " Names can be null when no curated event name is active; numeric count/severity fields should be used for analysis."
    if family == "global_event_context":
        return base + " Event context is curated and aligned to prediction_date; nulls are preserved where context is unavailable."
    if family in {"sec_accounting_fundamental", "financial_ratio", "firm_trend_or_deterioration"}:
        if share >= 0.5:
            return base + " High missingness; may reflect non-reporting, non-applicability, unmapped tags, dimensional exclusions, or unresolved flow derivation."
        if share >= 0.2:
            return base + " Moderate missingness; nulls are preserved and imputed only inside modeling pipelines."
        return base + " Low to moderate missingness; nulls are preserved."
    if family == "macro_variable":
        return base + " Macro values are aligned to prediction_date; any missing values remain null before model-pipeline imputation."
    if family == "industry_or_universe_metadata":
        return base + " Metadata missingness affects description/filtering and should not be invented."
    if family == "identifier_or_time":
        return base + " Identifier/time metadata missingness should be reviewed before using the field operationally."
    return base + " Missingness policy not documented / requires review."


def build_column_dictionary(schema: pd.DataFrame, model_cols: set[str]) -> pd.DataFrame:
    rows = []
    for _, row in schema.iterrows():
        col = row["column"]
        fam = row["feature_family"]
        metadata_only = fam in {"identifier_or_time", "industry_or_universe_metadata", "event_metadata"} and col not in model_cols
        if col in {"cohort", "include_status", "notes", "adsh", "cik", "name", "firm_id", "sec_name", "sec_zip", "prediction_date_source"}:
            metadata_only = True
        rows.append(
            {
                "column": col,
                "dtype": row["dtype"],
                "feature_family": fam,
                "plain_english_meaning": meaning_for(col, fam),
                "source": source_for_family(fam, col),
                "can_use_in_current_models": "yes" if col in model_cols else "no",
                "metadata_or_audit_only": "yes" if metadata_only else "no",
                "missing_share": row["missing_share"],
                "missingness_caveat": missingness_caveat(row),
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    def esc(v: object) -> str:
        s = "" if pd.isna(v) else str(v)
        s = s.replace("|", "\\|").replace("\n", " ")
        return s

    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        out.append("| " + " | ".join(esc(row[c]) for c in columns) + " |")
    return "\n".join(out)


def load_best_models() -> dict[str, dict]:
    files = {
        "distress_next_4q": ROOT / "reports/modeling/panel_v2_distress_next_4q_best_model.json",
        "failure_pressure_conservative_v2_next_4obs": ROOT / "reports/modeling/panel_v2_failure_pressure_conservative_v2_next_4obs_best_model.json",
        "success_resilience_next_4q": ROOT / "reports/modeling/panel_v2_success_resilience_next_4q_best_model.json",
        "industry_relative_resilience_next_4obs": ROOT / "reports/modeling/panel_v2_industry_relative_resilience_next_4obs_best_model.json",
        "stress_resilience_next_4obs": ROOT / "reports/modeling/panel_v2_stress_resilience_next_4obs_best_model.json",
        "recovery_next_4obs": ROOT / "reports/modeling/panel_v2_recovery_next_4obs_best_model.json",
        "quality_success_cashflow_next_4obs": ROOT / "reports/modeling/panel_v2_quality_success_cashflow_next_4obs_best_model.json",
    }
    return {target: read_json(path) for target, path in files.items()}


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def best_model_table(best_models: dict[str, dict]) -> str:
    rows = []
    for target, bm in best_models.items():
        rows.append(
            {
                "target": target,
                "best_model": bm["model"],
                "test_rows": bm["rows"],
                "test_positives": bm["positives"],
                "roc_auc": metric(bm["roc_auc"]),
                "pr_auc": metric(bm["pr_auc"]),
                "precision": metric(bm["precision"]),
                "recall": metric(bm["recall"]),
                "f1": metric(bm["f1"]),
            }
        )
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_macro_table() -> str:
    rows = []
    for col, (measure, role, expected) in MACRO_META.items():
        rows.append(
            {
                "variable": col,
                "what it measures": measure,
                "why it belongs": role,
                "expected relationship": expected,
                "alignment": "Aligned to prediction_date; YoY fields use prior-year comparison and no future macro values.",
                "dashboard/modeling": "Available as dashboard context and current model feature.",
            }
        )
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_regime_table() -> str:
    rows = []
    for col, meaning in REGIME_MEANINGS.items():
        rows.append(
            {
                "regime": col,
                "meaning": meaning,
                "expected relationship": "Stress regimes are expected to be associated with higher pressure or lower resilience, but this is interpreted as association, not causal proof.",
                "alignment": "Derived from prediction-date-aligned macro values.",
                "dashboard/modeling": "Available as dashboard filter/context and current model feature.",
            }
        )
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_accounting_table(schema: pd.DataFrame) -> str:
    cols = list(ACCOUNTING_MEANINGS)
    rows = []
    for col in cols:
        srow = schema.loc[schema["column"] == col].iloc[0]
        rows.append(
            {
                "field": col,
                "plain meaning": ACCOUNTING_MEANINGS[col],
                "statement type": "flow" if col in {
                    "capex", "cash_flow_financing", "cash_flow_investing", "cash_flow_operating",
                    "cost_of_revenue", "depreciation_amortization", "eps_basic", "eps_diluted",
                    "gross_profit", "net_income", "operating_income", "pretax_income",
                    "r_and_d_expense", "sg_and_a", "total_revenue", "wavg_shares_basic",
                    "wavg_shares_diluted",
                } else "balance/share",
                "missing share": pct(srow["missing_share"]),
            }
        )
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_ratio_table(schema: pd.DataFrame) -> str:
    rows = []
    for col, (formula, meaning) in RATIO_FORMULAS.items():
        srow = schema.loc[schema["column"] == col].iloc[0]
        rows.append({"ratio": col, "formula": formula, "meaning": meaning, "missing share": pct(srow["missing_share"])})
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_targets_table() -> str:
    rows = [
        {
            "target": "distress_next_4q",
            "role": "Strict legal distress benchmark",
            "definition": "Positive when a formal distress event occurs after prediction_date and within 456 days.",
            "known/positive": "31,702 known; 207 positives.",
            "model result": "Gradient boosting test PR-AUC 0.104; F1 0.182.",
            "limitation": "Strict legal distress is source-verified for current formal rows but remains rare.",
        },
        {
            "target": "failure_pressure_conservative_v2_next_4obs",
            "role": "Main broader failure-factor target",
            "definition": "Formal distress, or repeated future profitability weakness with serious balance-stress, deterioration, or unhealthy-future signal; at least three future observations required unless formal distress overrides.",
            "known/positive": "29,805 known; 3,003 positives; 1,897 unknown.",
            "model result": "Random forest test PR-AUC 0.758; F1 0.725.",
            "limitation": "Not a legal bankruptcy label; exact component thresholds are not fully exposed in the current prose docs / require review if quoted.",
        },
        {
            "target": "success_resilience_next_4q",
            "role": "Main success/resilience target",
            "definition": "Positive when at least three of the next four future observations have positive net income, positive ROA, acceptable leverage/assets, and no formal distress.",
            "known/positive": "20,152 known; 12,519 positives; 11,550 unknown.",
            "model result": "Random forest test PR-AUC 0.975; F1 0.938.",
            "limitation": "Unknown future components remain null; metrics are not comparable mechanically to rare strict distress.",
        },
        {
            "target": "industry_relative_resilience_next_4obs",
            "role": "Validated secondary production outcome",
            "definition": "Positive when future profitability is above sector-year peer medians in at least three future observations, leverage is not in the sector-year worst quartile, and no formal distress occurs.",
            "known/positive": "20,039 known; 8,093 positives; 11,663 unknown.",
            "model result": "Gradient boosting baseline test PR-AUC 0.855; F1 0.787; calibrated gate test PR-AUC 0.844.",
            "limitation": "Sector-year thresholds support relative benchmarking, not causal peer effects.",
        },
        {
            "target": "stress_resilience_next_4obs",
            "role": "Validated secondary production outcome",
            "definition": "Evaluated only under elevated current market stress; positive when at least three of the next four observations remain financially healthy and no formal distress occurs.",
            "known/positive": "5,901 known; 3,707 positives; 25,801 unknown.",
            "model result": "Random forest baseline test PR-AUC 0.974; F1 0.937; calibrated gate test PR-AUC 0.969.",
            "limitation": "Stress-gated target has narrower coverage and a high positive base rate, so ranking lift is modest.",
        },
        {
            "target": "recovery_next_4obs",
            "role": "Validated secondary production outcome",
            "definition": "Evaluated only for currently weak firms; positive when future observations improve to healthy status repeatedly and no formal distress occurs.",
            "known/positive": "11,375 known; 5,578 positives; 20,327 unknown.",
            "model result": "Random forest baseline test PR-AUC 0.977; F1 0.915; calibrated gate test PR-AUC 0.968.",
            "limitation": "Interpretation is leverage-sensitive because current weakness and future health definitions include leverage/assets.",
        },
        {
            "target": "quality_success_cashflow_next_4obs",
            "role": "Validated secondary production outcome",
            "definition": "Positive when at least three future observations show positive net income, positive ROA, positive operating cash flow, acceptable leverage/assets, and no formal distress.",
            "known/positive": "16,767 known; 9,852 positives; 14,935 unknown.",
            "model result": "Gradient boosting baseline test PR-AUC 0.953; F1 0.920; calibrated gate test PR-AUC 0.949.",
            "limitation": "Cash-flow support adds quality information, but leverage and profitability remain stronger model drivers.",
        },
    ]
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_tuning_table() -> str:
    base = load_csv(ROOT / "reports/model_tuning/baseline_vs_tuned_comparison.csv")
    rows = []
    for _, r in base.iterrows():
        rows.append(
            {
                "target": r["target"],
                "baseline": r["production_baseline_model"],
                "baseline PR-AUC/F1": f"{metric(r['baseline_test_pr_auc'])} / {metric(r['baseline_test_f1'])}",
                "validation-selected tuned": r["validation_selected_tuned_candidate"],
                "tuned PR-AUC/F1": f"{metric(r['tuned_test_pr_auc'])} / {metric(r['tuned_test_f1'])}",
                "interpretation": "Validation selected; test observed once and not used for further tuning.",
            }
        )
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_advanced_table() -> str:
    rows = [
        {
            "target": "distress_next_4q",
            "advanced candidate": "xgboost_cfg1_seed42",
            "family": "XGBoost",
            "advanced PR-AUC/F1": "0.088 / 0.140",
            "positioning": "Robustness benchmark from docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md, not production overwrite.",
        },
        {
            "target": "failure_pressure_conservative_v2_next_4obs",
            "advanced candidate": "lightgbm_cfg3_seed42",
            "family": "LightGBM",
            "advanced PR-AUC/F1": "0.760 / 0.686",
            "positioning": "Robustness benchmark from docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md, not production overwrite.",
        },
        {
            "target": "success_resilience_next_4q",
            "advanced candidate": "xgboost_cfg4_seed777",
            "family": "XGBoost",
            "advanced PR-AUC/F1": "0.962 / 0.919",
            "positioning": "Robustness benchmark from docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md, not production overwrite.",
        },
    ]
    return markdown_table(pd.DataFrame(rows), list(rows[0].keys()))


def build_markdown(schema: pd.DataFrame, dictionary: pd.DataFrame) -> str:
    best_models = load_best_models()
    family_counts = schema["feature_family"].value_counts().rename_axis("feature_family").reset_index(name="columns")
    miss_family = load_csv(ROOT / "reports/data_quality/panel_v2_missingness_by_feature_family.csv")
    p0 = load_csv(ROOT / "reports/data_quality/p0_audit_status.csv")
    p0["violations"] = p0["violations"].fillna("")
    p0_table = markdown_table(p0, ["audit", "status", "violations"])
    family_table = markdown_table(family_counts, ["feature_family", "columns"])
    missing_family_table = markdown_table(miss_family, ["feature_family", "columns", "average_missing_share", "max_missing_share", "columns_over_50pct_missing"])
    dict_table = markdown_table(
        dictionary,
        [
            "column",
            "feature_family",
            "plain_english_meaning",
            "source",
            "can_use_in_current_models",
            "metadata_or_audit_only",
            "missingness_caveat",
        ],
    )

    source_files = [
        "docs/CURRENT_STATUS.md",
        "docs/FINAL_SOURCE_OF_TRUTH_INDEX.md",
        "docs/PROJECT_CHRONICLE.md",
        "docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md",
        "docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md",
        "docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md",
        "docs/FINAL_TARGET_HIERARCHY.md",
        "docs/TARGET_DEFINITIONS_FINAL_REVIEW.md",
        "docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md",
        "docs/MISSINGNESS_INDICATOR_POLICY.md",
        "docs/MARKET_HEALTH_INDEX_NOTE.md",
        "docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md",
        "docs/DISTRESS_EVENT_DATE_PROVENANCE.md",
        "docs/BIBLIOGRAPHY.md",
        "docs/references.bib",
        "reports/modeling/",
        "reports/model_tuning/",
        "reports/data_quality/",
        "reports/data_quality/sec_selected_fact_provenance.parquet",
        "reports/data_quality/sec_selected_fact_panel_validation.csv",
        "data/github/firm_panel_v2_schema.csv",
    ]

    return f"""# Master Data, Model, and Target Explainer

Generated: 2026-05-07

This file is the thesis-ready master explanation of the empirical system behind the project. It is intended for direct use in methodology, data, target-definition, modeling, dashboard-artifact, limitations, and appendix sections.

## Source Boundary

This explainer uses the current source-of-truth project materials and saved reports. It does not introduce new data sources, new targets, or new model results.

Source materials used:

{chr(10).join(f"- `{p}`" for p in source_files)}

When the source material does not document a detail precisely, this file states `not documented / requires review`.

## 1. Project Overview

The thesis topic is:

> Navigating Market Shifts: Predictive Insights into Success and Failure Factors Across Industries

The empirical contribution is a reproducible firm-period analytics system for U.S. public companies. The project builds one structured panel from SEC Financial Statement Data Sets, FRED macroeconomic variables, curated global-event context, manually maintained distress-event labels, and industry metadata. The final production panel has 31,702 rows, 190 columns, 540 SEC CIKs, and 540 ticker/display identifiers. Its accounting periods run from 2009-03-31 to 2026-02-28, and its prediction timestamps run from 2009-04-15 to 2026-03-31.

The practical artifact is an interactive Streamlit dashboard plus a GitHub-ready dataset package. The dashboard is best described as a historical decision-support and early-warning analytics artifact. It exposes panel coverage, target composition, model results, firm-level histories, sector comparisons, macro/regime context, global-event windows, and data-quality caveats. It should not be described as a live trading engine, daily bankruptcy oracle, or complete news-intelligence system.

The final scope is deliberately U.S. SEC/FRED/global-event public-company data. HR, ESG, NLP, international datasets, Russian RFSD, Hong Kong/Japan data, paid data, market-price models, and live event feeds are not used in the production panel. They were considered as possible extensions, but they were excluded before submission because they would require new data-cleaning systems, licensing review, cross-country accounting harmonization, language processing, or market microstructure assumptions. The locked scope is stronger for the thesis because it is reproducible, auditable, and already aligned to the title: firm success and failure factors across industries and market shifts.

The core empirical story is not that a model perfectly predicts bankruptcy. The correct story is that predictive analytics is used to identify and compare forward-looking distress, broader financial pressure, and resilience factors. Strict legal distress is retained as a clean rare-event benchmark. Broader failure pressure is the main failure-factor target. Success/resilience is the main positive-outcome counterpart. Firm fundamentals, ratios, and deterioration features carry the strongest economic signal, while macro variables, regime indicators, and global events provide market-shift context and dashboard interpretability.

## Caveat Handling Plan

The caveats are not ignored. They are handled as explicit validity controls:

| Caveat | Handling rule | Thesis position |
| --- | --- | --- |
| Strict event-date provenance remains `REVIEW` | Use strict legal distress only as a rare-event benchmark; continue source-verifying remaining initial-seed events; do not silently upgrade unverified rows. | Safe with disclosure; do not claim a complete verified legal bankruptcy database. |
| SEC concept mapping is conservative, not perfect | Use documented SEC concept mapping, qtrs handling, missingness tables, accounting identity sanity checks, and outlier review. | Safe as audited SEC-FSD extraction; unsafe to claim perfect accounting harmonization. |
| Nulls have multiple meanings | Preserve raw panel nulls; impute only inside model pipelines; keep missing future target components as unknown. | Safe as null-preserving empirical panel; unsafe to treat null as zero or unchanged by default. |
| Missingness indicators can be predictive | Keep indicators only as model auxiliaries after diagnosis; exclude them from economic factor interpretation. | Safe for prediction; unsafe as economic causal claims. |
| Duplicate/amended filing keys exist | Disclose amendment/duplicate audit; no manual panel edits were made. A deterministic rebuild policy is needed if rows are to be dropped. | Safe with disclosure; not a blocker for thesis writing. |
| Structural audit PASS is not scientific proof | Separate structural readiness from empirical validity; rely on prediction-date alignment, leakage audits, temporal validation, target review, robustness, and limitations. | Safe if written as association and decision support, not causal truth. |
| Dashboard screenshot warnings | Use captured screenshots; record chart-library warnings as non-blocking evidence caveats. | Safe as artifact evidence; not a scientific limitation by itself. |
| GitHub/version freeze incomplete | Before final upload, freeze the exact panel, docs, README, requirements, and reproduction instructions. | TODO before submission package, not a reason to change empirical scope. |

## 2. Panel Architecture

Each row means:

> One company, one reported accounting period, observed from the date the SEC filing became available.

The panel is a firm-period table. It does not store disconnected accounting, macro, event, and target datasets separately because the models and dashboard need a single rectangular observation unit. Raw SEC accounting fundamentals, ratios, trend features, macro variables, regime indicators, global-event context, industry metadata, event metadata, and target labels attach to the same firm-period row.

The key time fields are:

- `period_date`: the accounting period end date described by the filing.
- `filed_date`: the date when the SEC filing became available.
- `prediction_date`: the information date from which prediction is allowed.

The production panel uses:

```text
prediction_date = filed_date
prediction_date_source = filed_date for all rows
```

This prevents look-ahead leakage. A filing for a quarter ending on December 31 is often not filed until weeks later. If the model were allowed to use the accounting period end date as the prediction date, it could accidentally behave as if it knew the financial statement before it was publicly available. Using `filed_date` as `prediction_date` aligns the firm information, macro context, event context, target windows, and temporal train/validation/test splits to the date when the information was knowable.

The core panel should not contain a permanent train/test split as a factual column. Modeling scripts derive temporal splits from `prediction_date`: train through 2018, validation from 2019 to 2021, and test from 2022 to 2024. This is more defensible than random row splitting because it evaluates forward-time generalization.

Current feature-family counts:

{family_table}

Current P0 audit status:

{p0_table}

## 3. Full Column Dictionary

The full machine-readable dictionary is also saved at:

```text
reports/documentation/master_column_dictionary.csv
```

`can_use_in_current_models = yes` means the column appears in the saved current model feature lists under `reports/data_quality/model_feature_lists/`. A `no` does not mean the variable could never be used in future research; it means it is not part of the current documented production feature set, or it is a target/metadata/audit field that must not be used as a predictor.

{dict_table}

## 4. SEC Accounting Fundamentals and Ratios

The SEC accounting fundamentals are extracted from SEC Financial Statement Data Sets using a documented concept map. They are not manually typed balance-sheet values. Balance-sheet variables use point-in-time values. Flow variables use single-period values where directly available; when SEC filings report cumulative year-to-date values for Q2, Q3, or Q4, the build logic derives a single-period flow by subtracting the prior cumulative value within the same firm, fiscal year, and variable. If the prior cumulative value is unavailable, the field remains null.

This is important because Q2 and Q3 flow variables are often reported as cumulative values. The flow-standardization pass improved coverage without inventing values. Reported improvements include CapEx missingness falling from about 63.8 percent to about 33.3 percent, operating cash-flow missingness from about 55.6 percent to about 15.7 percent, investing cash-flow missingness from about 55.6 percent to about 15.6 percent, and financing cash-flow missingness from about 55.5 percent to about 15.5 percent.

The current SEC concept-mapping audit is thesis-safe but caveated. It documents mapped tags, qtrs patterns, missingness, accounting identity plausibility, and extreme values. It does not prove perfect harmonization across all firms, years, industries, and accounting practices.

The final polish pass adds row-level selected-fact provenance as a sidecar rather than widening the production panel. `reports/data_quality/sec_selected_fact_provenance.parquet` and `.csv.gz` record the SEC accession number, CIK, standardized variable, selected SEC/XBRL tag, selected value, raw reported value, qtrs value, unit, segment/coreg filters, direct-or-derived `value_method`, and source ZIP. The validation report shows 661,533 selected fact rows, 0 selected-value mismatches above tolerance, and 24 documented exclusions belonging to one invalid timestamp row already excluded from the production panel.

Accounting fundamentals:

{build_accounting_table(schema)}

Financial ratios:

{build_ratio_table(schema)}

Interpretation of ratios must be precise. ROA, margins, leverage/assets, equity/assets, current ratio, cash/assets, R&D intensity, inventory/assets, and receivables/assets are not raw SEC line items. They are engineered ratios derived from SEC fundamentals. This is standard in financial distress and business analytics research, as long as ratios are computed from current or prior information available at the prediction date.

Nulls are preserved. A missing CapEx, R&D, gross profit, debt, inventory, or receivables field does not automatically mean zero. It may reflect non-reporting, non-applicability, concept mapping limits, dimensional facts excluded from consolidated extraction, or unresolved cumulative-flow derivation.

## 5. Firm Trend and Deterioration Features

Trend features are engineered from current and prior firm observations. They are important because distress and resilience are dynamic: a firm that is deteriorating quickly can be riskier than a firm with the same current-level ratio but stable history.

The main trend feature classes are:

- Lag features: `x_lag1 = x` from the prior firm observation.
- Four-observation growth features: `x_growth_4obs = (current x - x from four prior observations) / abs(x from four prior observations)`, where calculable from available values. Exact denominator safeguards are not documented / require review.
- Four-observation change features: `x_change_4obs = current x - x from four prior observations`.
- Prior loss counts: `net_income_negative_count_prior_4obs` counts how many of the prior four firm observations had negative net income.

These features are forward-safe because they use current or prior observations, not future values. They improve the empirical fit because repeated losses, declining profitability, shrinking revenue/assets, rising leverage, worsening liquidity, and margin compression are economically plausible signs of deterioration.

The current factor analysis reports recurring drivers such as ROA, net income, prior negative-income count, net margin and lagged net margin, leverage/assets, equity/assets, total liabilities, lagged leverage, and operating margin. Feature-group interpretation should be preferred over isolated one-feature claims.

## 6. Macro Variables and Regimes

Macro variables come from FRED and are aligned to `prediction_date`. Year-over-year fields use prior-year comparisons. The macro lag audit is `PASS`, so current documentation supports the claim that these values are used as prediction-date context and not as future macro information.

Macro variables:

{build_macro_table()}

Regime indicators convert macro variables into interpretable market states. A regime is a market environment flag, not a target and not a separate dataset. Regimes make the phrase "market shifts" concrete by identifying high-rate, market-stress, tight-credit, inflation-pressure, oil-shock, strong-dollar, demand-slowdown, and crisis-year conditions.

Regime indicators:

{build_regime_table()}

The market-health index is a reporting/dashboard layer built from existing prediction-date-aligned macro, regime, and global-event context. It does not modify the production panel and is not a target. It contains components such as `credit_stress_score`, `rate_pressure_score`, `inflation_pressure_score`, `demand_weakness_score`, `market_volatility_score`, `event_stress_score`, `market_stress_score`, `market_health_score`, and `market_health_regime`. Higher market-stress score means more stressful macro/event conditions. Higher market-health score means healthier macro/event conditions.

The market-health index uses training-period standardization from prediction years 2009-2018. Its latest documented output has 3,319 unique prediction-date rows, 18 audit rows, and `production panel modified: False`. It should be used for dashboard context, sector/regime comparison, and thesis interpretation, not as causal proof that macro conditions dominate firm fundamentals.

## 7. Global-Event Context

The global-event layer is a curated historical event calendar, not a full news/NLP database. It is merged into the production panel as `global_event_context` fields. The current panel has 27 global-event context columns.

Current event types are:

- `financial_crisis`
- `sovereign_debt`
- `natural_disaster`
- `commodity_oil`
- `financial_market`
- `political_policy`
- `trade_policy`
- `pandemic`
- `supply_chain`
- `monetary_inflation`
- `geopolitical_war`
- `banking_stress`

For each prediction date, the panel records active event-window counts and severity sums. The fields include total event count, total severity, type-specific counts, type-specific severities, and `global_event_names`.

The event layer is used as historical market-shift context. It supports questions such as whether sectors behave differently during pandemic, supply-chain, oil, banking-stress, or geopolitical-war windows. It should not be described as live event prediction. The dashboard can update macro/event context more often than SEC filings, but firm fundamentals update only when new filings arrive.

Current evidence says event features are useful for explanation and dashboard analysis, but firm fundamentals, ratios, and deterioration remain the dominant predictive signal. That is a strength, not a failure: the title is about navigating market shifts through predictive insights into success and failure factors, not proving that event labels alone predict bankruptcy.

## 8. Targets

Targets use future information only to label outcomes. They must never be used as model input features. The final thesis uses a target hierarchy because strict formal distress is clean but rare, while success/failure-factor analysis is broader than bankruptcy alone.

Production targets:

{build_targets_table()}

Why the targets are forward-looking:

- `distress_next_4q` looks for a formal event after `prediction_date` and within the forward window.
- `failure_pressure_conservative_v2_next_4obs` examines future firm observations after the current row.
- `success_resilience_next_4q` examines the next four future observations after the current row.

Why missing labels remain null:

- A missing future component means the future outcome is not sufficiently observed.
- Treating unknown future leverage, liability, ROA, or net income as zero or failure would contaminate targets.
- The missingness fix made future success labels missing-aware, so insufficient future information stays null rather than becoming automatic non-success.

Preferred and rejected positioning:

- `distress_next_4q` is preferred as the strict legal benchmark, but rejected as the headline performance target because it is too rare and still has event-date provenance caveats.
- `failure_pressure_conservative_v2_next_4obs` is preferred as the main failure-factor target because it is conservative, learnable, and economically interpretable.
- `success_resilience_next_4q` is preferred as the production success/resilience counterpart because it is missing-aware and empirically strong.
- `industry_relative_resilience_next_4obs`, `stress_resilience_next_4obs`, `recovery_next_4obs`, and `quality_success_cashflow_next_4obs` are validated secondary production outcomes. They add relative resilience, stress resilience, recovery, and cash-flow-supported success dimensions without replacing the three primary targets.
- `failure_pressure_balance_liquidity_next_4obs`, `success_resilience_quality_v2_next_4obs`, `deterioration_next_4obs`, `persistent_resilience_next_6obs`, and `sector_relative_improvement_next_4obs` are useful diagnostic or robustness targets but are not current production panel columns according to the target hierarchy.
- Older random-split and superseded broader-target results must not be cited as final model results.

## 9. Models and Tuning

The modeling workflow uses temporal validation rather than random splitting. Train rows are prediction years through 2018, validation rows are 2019-2021, and test rows are 2022-2024. Candidate choice and threshold selection use validation data only; test metrics are observed after validation selection and should not be used for further tuning.

Production best-model summary:

{best_model_table(best_models)}

Model intuition:

- Logistic regression estimates a linear relationship between features and the log-odds of the target. It is interpretable and useful as a benchmark. The tuning pass varied L2 regularization strength `C`.
- Random forest averages many decision trees trained with randomization. It captures nonlinear effects and interactions. Key hyperparameters include number of trees, maximum depth, minimum samples per leaf, maximum feature sampling, and random seed.
- Extra trees are a randomized tree ensemble used in tuning robustness. They add more randomization in split selection and can improve rare-event ranking.
- Gradient boosting builds trees sequentially, where each new tree focuses on correcting prior errors. Key hyperparameters include number of estimators, learning rate, tree depth, and subsampling.
- Histogram gradient boosting is an efficient boosted-tree implementation using binned features. Key hyperparameters include learning rate, max iterations, max leaf nodes, and L2 regularization.
- XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks. They are not described as AutoGluon or exhaustive AutoML.

Baseline versus controlled tuning:

{build_tuning_table()}

Advanced XGBoost/LightGBM robustness:

{build_advanced_table()}

Metric interpretation:

- ROC-AUC measures ranking quality across thresholds, but it can look optimistic for rare events.
- PR-AUC is more informative for rare positives because it focuses on precision-recall tradeoffs.
- Precision measures how many predicted positives are actually positive.
- Recall measures how many actual positives are found.
- F1 balances precision and recall at the selected threshold.

Strict distress is the rare-event benchmark because it has 207 full-panel positives and 96 test positives. Broader failure pressure is the main failure-factor target because it has enough positives for stable factor analysis and remains economically meaningful. Success/resilience is the success counterpart and should be interpreted separately because it is much less rare.

## 10. Missingness and Imputation

The raw panel preserves null values. The documented null-treatment audit reports 4,863,258 numeric cells, 680,419 preserved numeric null cells, and an overall numeric null share of about 14.0 percent.

Missingness by feature family:

{missing_family_table}

The correct missingness policy is:

- do not treat null as zero by default;
- do not treat null as unchanged by default;
- do not forward-fill the main panel;
- use model-pipeline imputation only inside estimation;
- use missingness indicators as predictive auxiliaries, not economic causes;
- keep unknown future target components as null labels.

Sklearn pipelines may impute numeric missing values with training-split medians and create missingness indicators such as `missingindicator_total_liabilities`. These indicators are model-engineering artifacts. They are not raw SEC variables and are excluded from economic factor interpretation.

The total-liabilities missingness diagnosis found that the old success target was vulnerable: missing future leverage/liability values could become automatic non-success. This was fixed. The rebuilt `success_resilience_next_4q` target has 20,161 known rows, 11,556 unknown rows, and 12,526 positives among known rows. Rows currently zero but revised missing-aware logic says unknown: 0. Known current/revised disagreements: 0.

## 11. Interpretation and Factor Analysis

Feature importance and contribution tables are tools for association-based interpretation. They do not prove causality. They should be read as evidence about which current and prior features help separate future pressure, strict distress, or resilience under the documented modeling setup.

The safest interpretation level is economic feature groups:

- accounting fundamentals;
- financial ratios;
- firm trend/deterioration;
- macro conditions;
- regimes;
- global-event context;
- industry/sector;
- missingness indicators, separated and not economically interpreted.

The current feature-group interpretation excludes missingness indicators from economic-factor shares. The recurring substantive drivers across model outputs include profitability, net income, prior loss counts, margins, leverage/assets, equity/assets, total liabilities, lagged leverage, and operating margin. The thesis should emphasize that firm fundamentals and deterioration dominate, while macro/regime/event features mainly contextualize market shifts and sector behavior.

Permutation or SHAP-style explanations are only thesis-ready if saved outputs exist and are described in the current reports. The current source set includes saved permutation output for success, but not a full SHAP package across all targets. Therefore, if SHAP is mentioned, it should be labeled not documented / requires review unless additional verified outputs are created.

Across industries, regimes, and event windows, the dashboard should be used to compare patterns rather than claim universal laws. For example, oil shocks can have different implications for energy firms than consumer firms. High-rate regimes can matter more for leveraged firms. Event labels provide context, while firm fundamentals determine much of the observed model signal.

## 12. Safe Thesis Claims and Unsafe Claims

Safe claims:

- The project constructs a reproducible U.S. public-company firm-period panel from SEC FSD, FRED macro variables, curated global-event context, distress-event labels, and industry metadata.
- The production panel has 31,702 rows, 190 columns, 540 SEC CIKs, and 540 ticker/display IDs.
- The panel uses `prediction_date = filed_date`, which reduces look-ahead leakage by aligning observations to the date filings became available.
- The project uses temporal validation rather than random splitting for final model claims.
- Strict legal distress is a clean but rare benchmark, not the headline performance target.
- Broader conservative failure pressure is the main failure-factor target.
- Success/resilience is the main positive-outcome counterpart.
- Nulls are preserved in the raw panel and imputed only inside modeling pipelines.
- Missingness indicators may help prediction but are not interpreted as economic causes.
- Firm accounting fundamentals, ratios, and deterioration features provide the strongest current empirical signal.
- Macro variables, regimes, and curated global events provide market-shift context and support dashboard/sector analysis.
- XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks; AutoGluon was not used in production.
- The dashboard is a historical decision-support and early-warning artifact based on latest available filings and aligned macro/event context.

Unsafe claims:

- All strict distress labels are fully verified bankruptcy events.
- The model perfectly predicts bankruptcy.
- The broader failure-pressure target is the same thing as legal bankruptcy.
- The market-health index proves macro conditions cause bankruptcy.
- Macro or global-event variables dominate firm fundamentals in the current results.
- Null accounting values mean zero or unchanged values.
- Missing total liabilities causes success or failure.
- The production workflow used HR, ESG, NLP, market-price features, Russian RFSD, Hong Kong/Japan data, paid datasets, or live event feeds.
- Exhaustive AutoML or AutoGluon optimization was performed.
- SEC tags are perfectly harmonized across all firms, sectors, and years.
- Dashboard visuals alone validate scientific accuracy.

## Appendix Pointers

Use these files as appendix evidence:

- `reports/documentation/master_column_dictionary.csv` for the complete column dictionary.
- `data/github/firm_panel_v2_schema.csv` for schema, dtypes, feature families, and missing shares.
- `reports/data_quality/p0_audit_status.csv` for P0 audit status.
- `reports/data_quality/sec_concept_mapping_summary.csv` for SEC concept coverage.
- `reports/data_quality/panel_v2_missingness_by_feature_family.csv` for missingness by feature family.
- `reports/modeling/*_model_metrics.csv` for model metrics.
- `reports/model_tuning/baseline_vs_tuned_comparison.csv` for controlled tuning.
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md` for XGBoost/LightGBM robustness.
- `docs/BIBLIOGRAPHY.md` and `docs/references.bib` for the curated bibliography.
"""


def main() -> None:
    schema = pd.read_csv(SCHEMA_PATH)
    model_cols = read_feature_columns()
    dictionary = build_column_dictionary(schema, model_cols)
    DICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dictionary.to_csv(DICT_PATH, index=False, quoting=csv.QUOTE_MINIMAL)
    DOC_PATH.write_text(build_markdown(schema, dictionary))
    print(f"Wrote {DICT_PATH.relative_to(ROOT)} with {len(dictionary)} rows")
    print(f"Wrote {DOC_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
