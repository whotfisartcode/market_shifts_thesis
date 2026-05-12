#!/usr/bin/env python3
"""Run P0 thesis audits for prediction timing, leakage, and event labels."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.sec_fsd.build_panel_v2 import (  # noqa: E402
    GLOBAL_EVENT_CALENDAR_PATH,
    fred_series_to_merge,
    read_fred_series,
)


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
EVENT_DATES_PATH = PROJECT_ROOT / "config/distress_event_dates.csv"
BLACKLIST_PATH = PROJECT_ROOT / "config/model_feature_blacklist.csv"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"
FEATURE_LIST_DIR = REPORT_DIR / "model_feature_lists"

DISTRESS_TARGETS = ["distress_next_2q", "distress_next_4q", "distress_next_8q", "broad_distress_next_4q"]


def load_panel() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in ["period_date", "filed_date", "prediction_date", "event_date"]:
        if col in panel.columns:
            panel[col] = pd.to_datetime(panel[col], errors="coerce")
    if "prediction_date" not in panel.columns:
        raise ValueError("Panel is missing prediction_date. Rebuild it with scripts/sec_fsd/build_panel_v2.py.")
    return panel


def write_md(path: Path, title: str, lines: list[str]) -> None:
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def prediction_timestamp_audit(panel: pd.DataFrame) -> dict[str, object]:
    lag_days = (panel["prediction_date"] - panel["period_date"]).dt.days
    rows = [
        {"check": "rows", "value": len(panel)},
        {"check": "missing_period_date_rows", "value": int(panel["period_date"].isna().sum())},
        {"check": "missing_filed_date_rows", "value": int(panel["filed_date"].isna().sum())},
        {"check": "missing_prediction_date_rows", "value": int(panel["prediction_date"].isna().sum())},
        {"check": "filed_date_prediction_rows", "value": int((panel["prediction_date_source"] == "filed_date").sum())},
        {
            "check": "period_date_fallback_prediction_rows",
            "value": int((panel["prediction_date_source"] == "period_date_fallback").sum()),
        },
        {"check": "prediction_before_period_rows", "value": int((lag_days < 0).sum())},
        {"check": "median_days_period_to_prediction", "value": float(lag_days.median())},
        {"check": "p90_days_period_to_prediction", "value": float(lag_days.quantile(0.9))},
        {"check": "max_days_period_to_prediction", "value": float(lag_days.max())},
        {"check": "first_prediction_date", "value": panel["prediction_date"].min()},
        {"check": "last_prediction_date", "value": panel["prediction_date"].max()},
    ]
    out = pd.DataFrame(rows)
    out.to_csv(REPORT_DIR / "prediction_timestamp_audit.csv", index=False)

    status = "PASS" if out.loc[out["check"] == "prediction_before_period_rows", "value"].iloc[0] == 0 else "REVIEW"
    write_md(
        REPORT_DIR / "prediction_timestamp_audit_summary.md",
        "Prediction Timestamp Audit",
        [
            f"Status: {status}",
            "",
            "The panel now uses `prediction_date = filed_date` where available and falls back to `period_date` only when filing date is missing.",
            f"Rows using period-date fallback: {int((panel['prediction_date_source'] == 'period_date_fallback').sum())}.",
            f"Median days from accounting period end to prediction timestamp: {float(lag_days.median()):.1f}.",
        ],
    )
    return {"audit": "prediction_timestamp", "status": status}


def distress_event_date_audit(panel: pd.DataFrame) -> dict[str, object]:
    events = pd.read_csv(EVENT_DATES_PATH, parse_dates=["event_date"]) if EVENT_DATES_PATH.exists() else pd.DataFrame()
    if events.empty:
        pd.DataFrame([{"issue": "event_date_config_missing_or_empty"}]).to_csv(
            REPORT_DIR / "distress_event_date_audit.csv",
            index=False,
        )
        return {"audit": "distress_event_dates", "status": "FAIL"}

    if "event_lookup_tickers" in panel.columns:
        lookup_panel = panel[
            ["ticker", "event_lookup_tickers", "adsh", "prediction_date", "distress_next_4q", "post_event_flag"]
        ].copy()
        lookup_panel["event_lookup_ticker"] = (
            lookup_panel["event_lookup_tickers"].fillna(lookup_panel["ticker"]).astype(str).str.split(";")
        )
        lookup_panel = lookup_panel.explode("event_lookup_ticker")
        lookup_panel["event_lookup_ticker"] = lookup_panel["event_lookup_ticker"].astype(str).str.strip()
        lookup_panel = lookup_panel[lookup_panel["event_lookup_ticker"].ne("")]
    else:
        lookup_panel = panel[
            ["ticker", "adsh", "prediction_date", "distress_next_4q", "post_event_flag"]
        ].copy()
        lookup_panel["event_lookup_ticker"] = lookup_panel["ticker"]

    coverage = (
        lookup_panel.groupby("event_lookup_ticker", dropna=False)
        .agg(
            panel_rows=("adsh", "count"),
            matched_panel_tickers=("ticker", lambda values: ";".join(sorted(set(values.dropna().astype(str))))),
            first_prediction_date=("prediction_date", "min"),
            last_prediction_date=("prediction_date", "max"),
            distress_next_4q_rows=("distress_next_4q", "sum"),
            post_event_rows=("post_event_flag", "sum"),
        )
        .reset_index()
    )
    duplicates = events["ticker"].value_counts()
    rows = []
    for _, event in events.iterrows():
        ticker = event["ticker"]
        matched = coverage[coverage["event_lookup_ticker"] == ticker]
        first_prediction = matched["first_prediction_date"].iloc[0] if not matched.empty else pd.NaT
        last_prediction = matched["last_prediction_date"].iloc[0] if not matched.empty else pd.NaT
        p0_issues = []
        coverage_notes = []
        event_label = event.get("event_label", pd.NA)
        verification = str(event.get("verification_status", ""))
        is_formal = str(event_label) == "formal_distress"
        if pd.isna(event["event_date"]):
            p0_issues.append("missing_event_date")
        if is_formal and not verification.startswith("source_verified"):
            p0_issues.append("formal_event_not_source_verified")
        if duplicates.get(ticker, 0) > 1:
            p0_issues.append("duplicate_event_ticker")
        if matched.empty:
            p0_issues.append("ticker_not_in_panel")
        elif pd.notna(event["event_date"]):
            if pd.notna(first_prediction) and event["event_date"] < first_prediction:
                coverage_notes.append("event_before_first_prediction")
            if pd.notna(last_prediction) and event["event_date"] > last_prediction:
                coverage_notes.append("event_after_last_prediction")
        if not is_formal:
            coverage_notes.append("non_strict_context_event")
        rows.append(
            {
                "ticker": ticker,
                "event_date": event["event_date"],
                "event_type": event.get("event_type", pd.NA),
                "event_label": event_label,
                "verification_status": verification,
                "matched_panel_tickers": matched["matched_panel_tickers"].iloc[0] if not matched.empty else pd.NA,
                "panel_rows": int(matched["panel_rows"].iloc[0]) if not matched.empty else 0,
                "first_prediction_date": first_prediction,
                "last_prediction_date": last_prediction,
                "distress_next_4q_rows": int(matched["distress_next_4q_rows"].iloc[0]) if not matched.empty else 0,
                "post_event_rows": int(matched["post_event_rows"].iloc[0]) if not matched.empty else 0,
                "p0_issues": ";".join(p0_issues),
                "coverage_notes": ";".join(coverage_notes),
                "issues": ";".join([*p0_issues, *coverage_notes]),
            }
        )

    audit = pd.DataFrame(rows).sort_values(["issues", "ticker"], ascending=[False, True])
    audit.to_csv(REPORT_DIR / "distress_event_date_audit.csv", index=False)

    p0_issue_rows = int(audit["p0_issues"].astype(str).ne("").sum())
    coverage_note_rows = int(audit["coverage_notes"].astype(str).ne("").sum())
    formal_seed_rows = int(
        (
            audit["event_label"].eq("formal_distress")
            & audit["verification_status"].eq("initial_seed")
        ).sum()
    )
    context_seed_rows = int(
        (
            audit["event_label"].ne("formal_distress")
            & audit["verification_status"].eq("initial_seed")
        ).sum()
    )
    status = "PASS" if p0_issue_rows == 0 else "REVIEW"
    write_md(
        REPORT_DIR / "distress_event_date_audit_summary.md",
        "Distress Event-Date Audit",
        [
            f"Status: {status}",
            "",
            f"Event rows audited: {len(audit)}.",
            f"Formal distress rows still marked `initial_seed`: {formal_seed_rows}.",
            f"Non-strict context rows still marked `initial_seed`: {context_seed_rows}.",
            f"Rows with P0 provenance issues: {p0_issue_rows}.",
            f"Rows with panel-coverage notes: {coverage_note_rows}.",
            "Coverage notes such as event dates before the first prediction row or after the last filed row are documented separately from source-provenance defects.",
        ],
    )
    return {"audit": "distress_event_dates", "status": status}


def load_blacklist() -> dict[str, str]:
    if not BLACKLIST_PATH.exists():
        return {}
    df = pd.read_csv(BLACKLIST_PATH)
    reason_col = "reason" if "reason" in df.columns else df.columns[-1]
    return dict(zip(df[df.columns[0]].astype(str), df[reason_col].astype(str)))


def normalize_feature_name(feature: str) -> str:
    raw = feature.replace("num__", "").replace("cat__", "")
    raw = raw.replace("missingindicator_", "")
    for prefix in ["Sector_", "form_", "afs_"]:
        if raw.startswith(prefix):
            return prefix[:-1]
    return raw


def leakage_audit() -> dict[str, object]:
    blacklist = load_blacklist()
    feature_files = sorted(FEATURE_LIST_DIR.glob("*.csv"))
    rows = []
    if not feature_files:
        rows.append(
            {
                "feature_file": pd.NA,
                "column": pd.NA,
                "normalized_column": pd.NA,
                "blacklisted": pd.NA,
                "reason": "no_feature_list_files_found",
            }
        )
    for path in feature_files:
        df = pd.read_csv(path)
        feature_col = "column" if "column" in df.columns else "feature"
        for _, row in df.iterrows():
            feature = str(row[feature_col])
            normalized = normalize_feature_name(feature)
            reason = blacklist.get(normalized, "")
            rows.append(
                {
                    "feature_file": path.name,
                    "column": feature,
                    "normalized_column": normalized,
                    "blacklisted": bool(reason),
                    "reason": reason,
                }
            )

    audit = pd.DataFrame(rows)
    audit.to_csv(REPORT_DIR / "leakage_audit.csv", index=False)
    violations = int(audit["blacklisted"].fillna(False).sum()) if "blacklisted" in audit else 0
    status = "PASS" if violations == 0 and feature_files else "REVIEW"
    return {"audit": "leakage", "status": status, "violations": violations}


def macro_lag_audit(panel: pd.DataFrame) -> dict[str, object]:
    prediction_dates = (
        panel[["prediction_date"]]
        .dropna()
        .drop_duplicates()
        .sort_values("prediction_date")
    )
    rows = []
    for path, transforms in fred_series_to_merge():
        fred = read_fred_series(path, transforms)
        if fred.empty:
            rows.append({"series_id": path.stem, "matched_prediction_dates": 0, "future_date_violations": np.nan})
            continue
        merged = pd.merge_asof(
            prediction_dates,
            fred[["fred_date"]].dropna().sort_values("fred_date"),
            left_on="prediction_date",
            right_on="fred_date",
            direction="backward",
        )
        lag_days = (merged["prediction_date"] - merged["fred_date"]).dt.days
        rows.append(
            {
                "series_id": path.stem,
                "prediction_dates": len(prediction_dates),
                "matched_prediction_dates": int(merged["fred_date"].notna().sum()),
                "unmatched_prediction_dates": int(merged["fred_date"].isna().sum()),
                "future_date_violations": int((merged["fred_date"] > merged["prediction_date"]).sum()),
                "median_source_lag_days": float(lag_days.median()),
                "max_source_lag_days": float(lag_days.max()),
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(REPORT_DIR / "macro_lag_audit.csv", index=False)
    violations = int(audit["future_date_violations"].fillna(0).sum())
    return {"audit": "macro_lag", "status": "PASS" if violations == 0 else "FAIL", "violations": violations}


def global_event_timing_audit(panel: pd.DataFrame) -> dict[str, object]:
    if not GLOBAL_EVENT_CALENDAR_PATH.exists():
        pd.DataFrame([{"issue": "global_event_calendar_missing"}]).to_csv(
            REPORT_DIR / "global_event_timing_audit.csv",
            index=False,
        )
        return {"audit": "global_event_timing", "status": "REVIEW"}

    events = pd.read_csv(GLOBAL_EVENT_CALENDAR_PATH, parse_dates=["event_start", "event_end"])
    panel = panel.copy().reset_index(drop=True)
    rows = []
    for event_type, group in events.groupby("event_type", dropna=False):
        event_type = str(event_type)
        count_col = f"global_event_{event_type}_count"
        severity_col = f"global_event_{event_type}_severity"
        expected_count = pd.Series(0, index=panel.index)
        expected_severity = pd.Series(0.0, index=panel.index)
        for _, event in group.iterrows():
            mask = panel["prediction_date"].between(event["event_start"], event["event_end"], inclusive="both")
            severity = float(event["severity_1_5"]) if pd.notna(event["severity_1_5"]) else 1.0
            expected_count.loc[mask] += 1
            expected_severity.loc[mask] += severity

        if count_col not in panel.columns:
            rows.append(
                {
                    "event_type": event_type,
                    "rows_with_actual_count": 0,
                    "rows_with_expected_count": int((expected_count > 0).sum()),
                    "count_mismatches": int((expected_count > 0).sum()),
                    "severity_mismatches": np.nan,
                    "issue": "missing_panel_event_columns",
                }
            )
            continue

        actual_count = panel[count_col].fillna(0).astype(float)
        actual_severity = panel[severity_col].fillna(0).astype(float) if severity_col in panel.columns else pd.Series(0.0, index=panel.index)
        rows.append(
            {
                "event_type": event_type,
                "rows_with_actual_count": int((actual_count > 0).sum()),
                "rows_with_expected_count": int((expected_count > 0).sum()),
                "count_mismatches": int((actual_count != expected_count).sum()),
                "severity_mismatches": int((~np.isclose(actual_severity, expected_severity)).sum()),
                "issue": "",
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(REPORT_DIR / "global_event_timing_audit.csv", index=False)
    violations = int(audit["count_mismatches"].fillna(0).sum() + audit["severity_mismatches"].fillna(0).sum())
    return {"audit": "global_event_timing", "status": "PASS" if violations == 0 else "FAIL", "violations": violations}


def post_event_row_audit(panel: pd.DataFrame) -> dict[str, object]:
    if "post_event_flag" not in panel.columns:
        pd.DataFrame([{"issue": "post_event_flag_missing"}]).to_csv(REPORT_DIR / "post_event_row_audit.csv", index=False)
        return {"audit": "post_event_rows", "status": "FAIL"}

    post = panel["post_event_flag"].fillna(0).astype(int) == 1
    rows = [
        {"check": "total_rows", "value": len(panel)},
        {"check": "post_event_rows", "value": int(post.sum())},
    ]
    for target in DISTRESS_TARGETS:
        if target in panel.columns:
            rows.append(
                {
                    "check": f"{target}_positive_rows_after_event",
                    "value": int(panel.loc[post, target].fillna(0).astype(int).sum()),
                }
            )
    audit = pd.DataFrame(rows)
    audit.to_csv(REPORT_DIR / "post_event_row_audit.csv", index=False)
    post_target_positives = int(
        audit[audit["check"].str.endswith("_positive_rows_after_event")]["value"].astype(int).sum()
    )
    return {
        "audit": "post_event_rows",
        "status": "PASS" if post_target_positives == 0 else "FAIL",
        "violations": post_target_positives,
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    statuses = [
        prediction_timestamp_audit(panel),
        distress_event_date_audit(panel),
        leakage_audit(),
        macro_lag_audit(panel),
        global_event_timing_audit(panel),
        post_event_row_audit(panel),
    ]
    status_frame = pd.DataFrame(statuses)
    status_frame.to_csv(REPORT_DIR / "p0_audit_status.csv", index=False)
    write_md(
        REPORT_DIR / "p0_audit_summary.md",
        "P0 Audit Summary",
        [
            "| Audit | Status |",
            "| --- | --- |",
            *[f"| {row['audit']} | {row['status']} |" for row in statuses],
            "",
            "A `REVIEW` status means the audit ran and produced a defensible artifact, but manual verification or interpretation is still needed.",
        ],
    )
    print(status_frame.to_string(index=False))


if __name__ == "__main__":
    main()
