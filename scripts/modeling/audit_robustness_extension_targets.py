#!/usr/bin/env python3
"""Audit robustness-extension target construction without changing panel data."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modeling.run_exploratory_target_lab import (  # noqa: E402
    add_exploratory_targets,
    add_financial_quality_features,
    add_market_health_v2_features,
    build_features,
    clean_financial_quality_extremes,
    load_panel,
)


OUT_DIR = PROJECT_ROOT / "reports/target_lab"
AUDIT_CSV = OUT_DIR / "robustness_extension_target_audit.csv"
SUMMARY_MD = OUT_DIR / "robustness_extension_target_audit_summary.md"

TARGETS = [
    "sector_relative_improvement_next_4obs",
    "persistent_resilience_next_6obs",
]


def shifts(df: pd.DataFrame, column: str, horizon: int) -> list[pd.Series]:
    grouped = df.groupby("cik", group_keys=False)[column]
    return [grouped.shift(-step) for step in range(1, horizon + 1)]


def valid_count(parts: list[pd.Series]) -> pd.Series:
    return pd.concat([part.notna().astype(int) for part in parts], axis=1).sum(axis=1)


def load_extension_frame() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    base = load_panel()
    df = add_financial_quality_features(base)
    df = clean_financial_quality_extremes(df)
    df, _coverage = add_market_health_v2_features(df)
    df = add_exploratory_targets(df)
    return base, df, build_features(df)


def expected_sector_relative_improvement(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    roa = shifts(df, "roa", 4)
    margin = shifts(df, "net_margin", 4)
    roa_median = shifts(df, "sector_year_roa_median", 4)
    margin_median = shifts(df, "sector_year_net_margin_median", 4)
    adsh = shifts(df, "adsh", 4)

    relative_valid_parts = []
    relative_above_parts = []
    for index in range(4):
        relative_valid = (
            (roa[index].notna() & roa_median[index].notna())
            | (margin[index].notna() & margin_median[index].notna())
        )
        above_sector = (
            (roa[index].notna() & roa_median[index].notna() & (roa[index] > roa_median[index]))
            | (margin[index].notna() & margin_median[index].notna() & (margin[index] > margin_median[index]))
        )
        relative_valid_parts.append(relative_valid.astype(int))
        relative_above_parts.append((relative_valid & above_sector).astype(int))

    relative_valid_count = pd.concat(relative_valid_parts, axis=1).sum(axis=1)
    relative_above_count = pd.concat(relative_above_parts, axis=1).sum(axis=1)

    current_roa_valid = df["roa"].notna() & df["sector_year_roa_median"].notna()
    current_margin_valid = df["net_margin"].notna() & df["sector_year_net_margin_median"].notna()
    current_relative_valid = current_roa_valid | current_margin_valid
    current_above_any_peer_median = (
        (current_roa_valid & (df["roa"] > df["sector_year_roa_median"]))
        | (current_margin_valid & (df["net_margin"] > df["sector_year_net_margin_median"]))
    )
    currently_below_peer_median = current_relative_valid & ~current_above_any_peer_median

    formal_4q = df["distress_next_4q"].fillna(0).astype(int).eq(1)
    post_event = df["post_event_flag"].fillna(0).astype(int).eq(1)
    enough_future_observations = valid_count(adsh).ge(3)
    expected_known = (
        currently_below_peer_median
        & (((relative_valid_count >= 3) & enough_future_observations) | formal_4q)
        & ~post_event
    )
    expected_positive = currently_below_peer_median & relative_above_count.ge(2) & ~formal_4q
    return expected_known, expected_positive, currently_below_peer_median, relative_valid_count, relative_above_count


def expected_persistent_resilience(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    net_income = shifts(df, "net_income", 6)
    roa = shifts(df, "roa", 6)
    leverage = shifts(df, "leverage_assets", 6)
    adsh = shifts(df, "adsh", 6)

    healthy_parts = []
    health_valid_parts = []
    for index in range(6):
        valid = net_income[index].notna() & roa[index].notna() & leverage[index].notna()
        healthy = (net_income[index] > 0) & (roa[index] > 0) & leverage[index].between(0, 0.85, inclusive="both")
        health_valid_parts.append(valid.astype(int))
        healthy_parts.append((valid & healthy).astype(int))

    health_valid_count = pd.concat(health_valid_parts, axis=1).sum(axis=1)
    healthy_count = pd.concat(healthy_parts, axis=1).sum(axis=1)
    days_to_event = pd.to_numeric(df["days_to_event"], errors="coerce")
    formal_6q = (
        df["formal_distress_firm"].fillna(0).astype(int).eq(1)
        & days_to_event.gt(0)
        & days_to_event.le(684)
    )
    post_event = df["post_event_flag"].fillna(0).astype(int).eq(1)
    enough_future_observations = valid_count(adsh).ge(5)
    expected_known = (((health_valid_count >= 5) & enough_future_observations) | formal_6q) & ~post_event
    expected_positive = healthy_count.ge(5) & ~formal_6q
    return expected_known, expected_positive, health_valid_count, healthy_count


def add_check(rows: list[dict[str, object]], check: str, mask: pd.Series, severity: str = "blocking") -> None:
    rows.append(
        {
            "audit_section": "invariant",
            "check": check,
            "severity": severity,
            "violations": int(mask.fillna(False).sum()),
            "status": "PASS" if int(mask.fillna(False).sum()) == 0 else "FAIL",
            "value": np.nan,
            "note": "",
        }
    )


def add_metric(rows: list[dict[str, object]], check: str, value: object, note: str = "") -> None:
    rows.append(
        {
            "audit_section": "metric",
            "check": check,
            "severity": "info",
            "violations": np.nan,
            "status": "INFO",
            "value": value,
            "note": note,
        }
    )


def audit() -> pd.DataFrame:
    base, df, features = load_extension_frame()
    rows: list[dict[str, object]] = []

    production_new_cols = [target for target in TARGETS if target in base.columns]
    add_metric(rows, "production_panel_new_target_columns", ";".join(production_new_cols), "Should be empty.")
    add_metric(rows, "production_panel_column_count", len(base.columns), "Production panel should remain 190 columns after secondary-target promotion.")

    forbidden_patterns = [
        "next_",
        "future_",
        "distress",
        "event_date",
        "days_to_event",
        "post_event",
        "formal_distress",
        "near_distress",
        "target",
        "sector_year_",
    ]
    forbidden_features = [feature for feature in features if any(pattern in feature for pattern in forbidden_patterns)]
    add_metric(rows, "model_feature_count", len(features), "Exploratory model feature count.")
    add_metric(rows, "forbidden_model_feature_hits", ";".join(forbidden_features), "Should be empty.")

    improve_known, improve_positive, currently_below, relative_valid_count, relative_above_count = (
        expected_sector_relative_improvement(df)
    )
    persistent_known, persistent_positive, health_valid_count, healthy_count = expected_persistent_resilience(df)

    improve = df["sector_relative_improvement_next_4obs"]
    persistent = df["persistent_resilience_next_6obs"]
    formal_4q = df["distress_next_4q"].fillna(0).astype(int).eq(1)
    days_to_event = pd.to_numeric(df["days_to_event"], errors="coerce")
    formal_6q = (
        df["formal_distress_firm"].fillna(0).astype(int).eq(1)
        & days_to_event.gt(0)
        & days_to_event.le(684)
    )
    post_event = df["post_event_flag"].fillna(0).astype(int).eq(1)

    add_check(rows, "improvement_any_known_outside_expected_known", improve.notna() & ~improve_known)
    add_check(rows, "improvement_expected_known_but_null", improve_known & improve.isna())
    add_check(rows, "improvement_positive_not_expected_positive", improve.fillna(0).astype(int).eq(1) & ~improve_positive)
    add_check(rows, "improvement_positive_with_strict_4q_distress", improve.fillna(0).astype(int).eq(1) & formal_4q)
    add_check(rows, "improvement_known_on_post_event_row", improve.notna() & post_event)
    add_check(
        rows,
        "improvement_positive_not_currently_below_peer_median",
        improve.fillna(0).astype(int).eq(1) & ~currently_below,
    )
    add_check(
        rows,
        "improvement_positive_less_than_two_future_above_peer",
        improve.fillna(0).astype(int).eq(1) & relative_above_count.lt(2),
    )
    add_check(
        rows,
        "improvement_known_nonformal_less_than_three_relative_valid",
        improve.notna() & ~formal_4q & relative_valid_count.lt(3),
    )

    add_check(rows, "persistent_any_known_outside_expected_known", persistent.notna() & ~persistent_known)
    add_check(rows, "persistent_expected_known_but_null", persistent_known & persistent.isna())
    add_check(
        rows,
        "persistent_positive_not_expected_positive",
        persistent.fillna(0).astype(int).eq(1) & ~persistent_positive,
    )
    add_check(
        rows,
        "persistent_positive_with_strict_6q_distress",
        persistent.fillna(0).astype(int).eq(1) & formal_6q,
    )
    add_check(rows, "persistent_known_on_post_event_row", persistent.notna() & post_event)
    add_check(
        rows,
        "persistent_positive_less_than_five_healthy_future_obs",
        persistent.fillna(0).astype(int).eq(1) & healthy_count.lt(5),
    )
    add_check(
        rows,
        "persistent_known_nonformal_less_than_five_health_valid",
        persistent.notna() & ~formal_6q & health_valid_count.lt(5),
    )

    model_frame = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    for target in TARGETS:
        values = model_frame[target]
        known = values.notna()
        positives = int(values.fillna(0).astype(int).sum())
        add_metric(rows, f"{target}_known_rows_model_years", int(known.sum()))
        add_metric(rows, f"{target}_positive_rows_model_years", positives)
        add_metric(
            rows,
            f"{target}_positive_share_known_model_years",
            positives / int(known.sum()) if int(known.sum()) else np.nan,
        )

    group_sizes = (
        model_frame.groupby(["Sector", "prediction_year"], dropna=False)
        .size()
        .rename("sector_year_rows")
        .reset_index()
    )
    known_improve = model_frame[model_frame["sector_relative_improvement_next_4obs"].notna()].merge(
        group_sizes,
        on=["Sector", "prediction_year"],
        how="left",
    )
    add_metric(
        rows,
        "improvement_known_rows_sector_year_group_lt_10",
        int((known_improve["sector_year_rows"] < 10).sum()),
        "Tiny peer groups support robustness-only classification.",
    )
    add_metric(
        rows,
        "improvement_known_rows_sector_year_group_lt_20",
        int((known_improve["sector_year_rows"] < 20).sum()),
        "Tiny peer groups support robustness-only classification.",
    )

    overlap_pairs = [
        ("persistent_resilience_next_6obs", "success_resilience_next_4q"),
        ("persistent_resilience_next_6obs", "quality_success_cashflow_next_4obs"),
        ("sector_relative_improvement_next_4obs", "industry_relative_resilience_next_4obs"),
        ("sector_relative_improvement_next_4obs", "recovery_next_4obs"),
    ]
    for left, right in overlap_pairs:
        sub = model_frame[model_frame[left].notna() & model_frame[right].notna()].copy()
        add_metric(rows, f"overlap_rows__{left}__vs__{right}", len(sub))
        if not sub.empty:
            left_values = sub[left].astype(int)
            right_values = sub[right].astype(int)
            add_metric(rows, f"agreement__{left}__vs__{right}", float(left_values.eq(right_values).mean()))
            if left_values.nunique() > 1 and right_values.nunique() > 1:
                add_metric(rows, f"correlation__{left}__vs__{right}", float(left_values.corr(right_values)))

    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    text = df.copy()
    for column in text.columns:
        if pd.api.types.is_numeric_dtype(text[column]):
            text[column] = text[column].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
        else:
            text[column] = text[column].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(text.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in text.iterrows():
        lines.append("| " + " | ".join(row[column].replace("|", "\\|") for column in headers) + " |")
    return "\n".join(lines)


def write_summary(audit_frame: pd.DataFrame) -> None:
    invariant = audit_frame[audit_frame["audit_section"] == "invariant"].copy()
    metrics = audit_frame[audit_frame["audit_section"] == "metric"].copy()
    failed = invariant[invariant["status"] != "PASS"].copy()
    target_metrics = metrics[metrics["check"].str.contains("known_rows|positive_rows|positive_share", regex=True)].copy()
    caveat_metrics = metrics[
        metrics["check"].isin(
            [
                "production_panel_new_target_columns",
                "production_panel_column_count",
                "forbidden_model_feature_hits",
                "improvement_known_rows_sector_year_group_lt_10",
                "improvement_known_rows_sector_year_group_lt_20",
                "agreement__persistent_resilience_next_6obs__vs__success_resilience_next_4q",
                "correlation__persistent_resilience_next_6obs__vs__success_resilience_next_4q",
                "agreement__sector_relative_improvement_next_4obs__vs__industry_relative_resilience_next_4obs",
                "correlation__sector_relative_improvement_next_4obs__vs__industry_relative_resilience_next_4obs",
            ]
        )
    ].copy()

    lines = [
        "# Robustness Extension Target Audit Summary",
        "",
        "Generated by `scripts/modeling/audit_robustness_extension_targets.py`.",
        "",
        "This audit verifies target-construction invariants for `sector_relative_improvement_next_4obs` and `persistent_resilience_next_6obs`. It does not change the production panel, target definitions, model outputs, or dashboard files.",
        "",
        "## Verdict",
        "",
        "PASS: no blocking target-construction invariant violations were found." if failed.empty else "FAIL: one or more blocking invariant checks failed.",
        "",
        "## Invariant Checks",
        "",
        markdown_table(invariant[["check", "status", "violations"]]),
        "",
        "## Target Counts",
        "",
        markdown_table(target_metrics[["check", "value"]]),
        "",
        "## Scientific Caveat Metrics",
        "",
        markdown_table(caveat_metrics[["check", "value", "note"]]),
        "",
        "## Interpretation",
        "",
        "- `sector_relative_improvement_next_4obs` is mechanically valid and useful for dynamic peer catch-up robustness analysis.",
        "- `persistent_resilience_next_6obs` is mechanically valid and useful for long-horizon resilience sensitivity analysis.",
        "- Neither target is a production target or a replacement for the four validated secondary production outcomes.",
        "- `sector_relative_improvement_next_4obs` uses an OR rule over ROA and net margin, and a small number of known labels are based on tiny sector-year peer groups. This supports robustness-only treatment.",
        "- `persistent_resilience_next_6obs` overlaps strongly with `success_resilience_next_4q`, so its contribution is durability confirmation rather than a separate primary outcome.",
    ]
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit_frame = audit()
    audit_frame.to_csv(AUDIT_CSV, index=False)
    write_summary(audit_frame)
    failures = audit_frame[(audit_frame["audit_section"] == "invariant") & (audit_frame["status"] != "PASS")]
    if failures.empty:
        print(f"PASS: wrote robustness extension target audit to {AUDIT_CSV}")
    else:
        print(f"FAIL: wrote robustness extension target audit to {AUDIT_CSV}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
