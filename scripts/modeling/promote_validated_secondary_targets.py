#!/usr/bin/env python3
"""Promote validated secondary target labels into the production panel files.

This is a controlled post-build step. It reads the already frozen SEC/FRED panel,
recomputes the validated secondary targets with the audited target-lab functions,
copies only the four approved target columns into the production panel, refreshes
schema/sample/package copies, and writes a promotion audit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modeling.run_exploratory_target_lab import (  # noqa: E402
    add_exploratory_targets,
    add_market_health_v2_features,
)
from scripts.sec_fsd.build_panel_v2 import classify_schema_column  # noqa: E402


PROCESSED_DIR = PROJECT_ROOT / "data/processed/panel_v2"
GITHUB_DIR = PROJECT_ROOT / "data/github"
SAMPLE_DIR = PROJECT_ROOT / "data/samples"
REPORT_DIR = PROJECT_ROOT / "reports/target_lab"

PANEL_CSV_GZ = PROCESSED_DIR / "firm_panel_v2.csv.gz"
PANEL_CSV = PROCESSED_DIR / "firm_panel_v2.csv"
PANEL_PARQUET = PROCESSED_DIR / "firm_panel_v2.parquet"
GITHUB_CSV_GZ = GITHUB_DIR / "firm_panel_v2.csv.gz"
GITHUB_PARQUET = GITHUB_DIR / "firm_panel_v2.parquet"
GITHUB_SCHEMA = GITHUB_DIR / "firm_panel_v2_schema.csv"
SAMPLE_PANEL = SAMPLE_DIR / "firm_panel_v2_sample.csv"
SAMPLE_SCHEMA = SAMPLE_DIR / "firm_panel_v2_schema.csv"

PROMOTED_TARGETS = [
    "industry_relative_resilience_next_4obs",
    "stress_resilience_next_4obs",
    "recovery_next_4obs",
    "quality_success_cashflow_next_4obs",
]

DATE_COLS = ["period_date", "filed_date", "prediction_date", "event_date"]


def load_panel() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_CSV_GZ, low_memory=False)
    for col in DATE_COLS:
        if col in panel.columns:
            panel[col] = pd.to_datetime(panel[col], errors="coerce")
    return panel.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).reset_index(drop=True)


def target_profiles(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    model_frame = panel[panel["prediction_date"].dt.year.between(2009, 2024)].copy()
    split_masks = {
        "all_rows": pd.Series(True, index=panel.index),
        "all_model_years": pd.Series(False, index=panel.index),
        "train": pd.Series(False, index=panel.index),
        "validation": pd.Series(False, index=panel.index),
        "test": pd.Series(False, index=panel.index),
    }
    split_masks["all_model_years"].loc[model_frame.index] = True
    split_masks["train"].loc[model_frame[model_frame["prediction_date"].dt.year <= 2018].index] = True
    split_masks["validation"].loc[
        model_frame[model_frame["prediction_date"].dt.year.between(2019, 2021)].index
    ] = True
    split_masks["test"].loc[model_frame[model_frame["prediction_date"].dt.year.between(2022, 2024)].index] = True

    for target in PROMOTED_TARGETS:
        values_all = panel[target]
        for split_name, mask in split_masks.items():
            split = panel.loc[mask]
            values = split[target]
            known = values.notna()
            positives = int(values.fillna(0).astype(int).sum())
            rows.append(
                {
                    "target": target,
                    "split": split_name,
                    "rows": int(len(split)),
                    "known_rows": int(known.sum()),
                    "unknown_rows": int((~known).sum()),
                    "positives": positives,
                    "positive_share_known": positives / known.sum() if known.sum() else pd.NA,
                    "firms_with_known": int(split.loc[known, "cik"].nunique()),
                    "firms_with_positive": int(split.loc[values.fillna(0).astype(int) == 1, "cik"].nunique()),
                }
            )
        rows.append(
            {
                "target": target,
                "split": "post_event_known_rows",
                "rows": int(panel["post_event_flag"].fillna(0).astype(int).sum()),
                "known_rows": int(values_all[panel["post_event_flag"].fillna(0).astype(int) == 1].notna().sum()),
                "unknown_rows": pd.NA,
                "positives": pd.NA,
                "positive_share_known": pd.NA,
                "firms_with_known": pd.NA,
                "firms_with_positive": pd.NA,
            }
        )
    return pd.DataFrame(rows)


def build_schema(panel: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column": panel.columns,
            "dtype": [str(dtype) for dtype in panel.dtypes],
            "feature_family": [classify_schema_column(col) for col in panel.columns],
            "missing_share": [panel[col].isna().mean() for col in panel.columns],
        }
    )


def write_outputs(panel: pd.DataFrame, schema: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    GITHUB_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    panel.to_csv(PANEL_CSV_GZ, index=False, compression="gzip")
    panel.to_csv(PANEL_CSV, index=False)
    panel.to_parquet(PANEL_PARQUET, index=False)
    panel.to_csv(GITHUB_CSV_GZ, index=False, compression="gzip")
    panel.to_parquet(GITHUB_PARQUET, index=False)

    sample = panel.sort_values(["ticker", "prediction_date", "period_date"]).groupby("ticker", group_keys=False).head(2).head(500)
    sample.to_csv(SAMPLE_PANEL, index=False)
    schema.to_csv(SAMPLE_SCHEMA, index=False)
    schema.to_csv(GITHUB_SCHEMA, index=False)


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    text_frame = frame.copy()
    for col in text_frame.columns:
        text_frame[col] = text_frame[col].map(lambda value: "" if pd.isna(value) else str(value))
    lines = [
        "| " + " | ".join(text_frame.columns) + " |",
        "| " + " | ".join(["---"] * len(text_frame.columns)) + " |",
    ]
    for _, row in text_frame.iterrows():
        lines.append("| " + " | ".join(row.astype(str).tolist()) + " |")
    return "\n".join(lines)


def write_audit(panel_before: pd.DataFrame, panel_after: pd.DataFrame, schema: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    profile = target_profiles(panel_after)
    profile.to_csv(REPORT_DIR / "validated_secondary_target_profiles.csv", index=False)

    rows = [
        {
            "check": "row_count_preserved",
            "status": "PASS" if len(panel_before) == len(panel_after) else "FAIL",
            "detail": f"before={len(panel_before)}; after={len(panel_after)}",
        },
        {
            "check": "column_count_expected",
            "status": "PASS" if panel_after.shape[1] == panel_before.shape[1] + len([t for t in PROMOTED_TARGETS if t not in panel_before.columns]) else "FAIL",
            "detail": f"before={panel_before.shape[1]}; after={panel_after.shape[1]}",
        },
        {
            "check": "schema_matches_panel",
            "status": "PASS" if set(schema["column"]) == set(panel_after.columns) and len(schema) == panel_after.shape[1] else "FAIL",
            "detail": f"schema_rows={len(schema)}; panel_columns={panel_after.shape[1]}",
        },
        {
            "check": "promoted_targets_schema_family",
            "status": "PASS"
            if set(schema.loc[schema["column"].isin(PROMOTED_TARGETS), "feature_family"]) == {"target_label"}
            else "FAIL",
            "detail": "; ".join(
                f"{row.column}={row.feature_family}"
                for row in schema.loc[schema["column"].isin(PROMOTED_TARGETS), ["column", "feature_family"]].itertuples(index=False)
            ),
        },
        {
            "check": "post_event_rows_null_for_promoted_targets",
            "status": "PASS"
            if all(
                panel_after.loc[panel_after["post_event_flag"].fillna(0).astype(int) == 1, target].isna().all()
                for target in PROMOTED_TARGETS
            )
            else "FAIL",
            "detail": "; ".join(
                f"{target}={int(panel_after.loc[panel_after['post_event_flag'].fillna(0).astype(int) == 1, target].notna().sum())}"
                for target in PROMOTED_TARGETS
            ),
        },
    ]

    for target in PROMOTED_TARGETS:
        values = panel_after[target]
        known = int(values.notna().sum())
        positives = int(values.fillna(0).astype(int).sum())
        rows.append(
            {
                "check": f"{target}_profile",
                "status": "PASS" if known >= 1_000 and positives >= 50 else "FAIL",
                "detail": f"known={known}; positives={positives}; positive_share={positives / known if known else pd.NA}",
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(REPORT_DIR / "validated_secondary_target_promotion_audit.csv", index=False)

    profile_model = profile[profile["split"] == "all_model_years"].copy()
    profile_md = markdown_table(profile_model[["target", "known_rows", "positives", "positive_share_known", "firms_with_positive"]])
    audit_md = markdown_table(audit)
    (REPORT_DIR / "validated_secondary_target_promotion_audit_summary.md").write_text(
        "\n".join(
            [
                "# Validated Secondary Target Promotion Audit",
                "",
                "Generated by `scripts/modeling/promote_validated_secondary_targets.py`.",
                "",
                "The production panel was updated in place by copying only the four validated secondary target labels. "
                "No robustness-extension or diagnostic targets were promoted.",
                "",
                f"- Rows: {panel_after.shape[0]:,}",
                f"- Columns: {panel_after.shape[1]:,}",
                f"- Promoted targets: {', '.join(PROMOTED_TARGETS)}",
                "",
                "## Promotion Checks",
                "",
                audit_md,
                "",
                "## Model-Year Profiles",
                "",
                profile_md,
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    panel_before = load_panel()
    extension_frame, _coverage = add_market_health_v2_features(panel_before.copy())
    extension_frame = add_exploratory_targets(extension_frame)

    panel_after = panel_before.copy()
    for target in PROMOTED_TARGETS:
        if target not in extension_frame.columns:
            raise ValueError(f"Missing computed target: {target}")
        panel_after[target] = extension_frame[target].astype("Int64")

    schema = build_schema(panel_after)
    write_outputs(panel_after, schema)
    write_audit(panel_before, panel_after, schema)
    print(f"Promoted {len(PROMOTED_TARGETS)} targets into production panel: {panel_after.shape}")


if __name__ == "__main__":
    main()
