#!/usr/bin/env python3
"""Smoke-check the GitHub package from included artifacts only."""

from __future__ import annotations

import csv
import py_compile
import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "reports/project_audit/github_package_smoke_test_results.csv"

REQUIRED_FILES = [
    "README.md",
    "COMMITTEE_PACKAGE.md",
    "DEPLOYMENT.md",
    "REPRODUCIBILITY.md",
    "requirements.txt",
    "app/dashboard.py",
    "app/requirements.txt",
    "data/github/README.md",
    "data/github/firm_panel_v2.csv.gz",
    "data/github/firm_panel_v2.parquet",
    "data/github/firm_panel_v2_schema.csv",
    "reports/modeling/panel_v2_model_metrics.csv",
    "reports/modeling/panel_v2_feature_importance.csv",
    "reports/modeling/panel_v2_temporal_split_summary.csv",
    "reports/modeling/calibration_metrics.csv",
    "reports/modeling/threshold_ranking_metrics.csv",
    "reports/target_lab/validated_secondary_target_profiles.csv",
    "reports/target_lab/exploratory_reason_code_summary.csv",
    "reports/target_lab/exploratory_feature_level_importance.csv",
    "reports/target_lab/exploratory_feature_direction_effects.csv",
    "reports/target_lab/exploratory_feature_group_importance.csv",
    "reports/target_tweak_experiments/dashboard_best_target_rows.csv",
    "reports/target_tweak_experiments/dashboard_feature_set_performance.csv",
    "reports/target_tweak_experiments/dashboard_factor_group_best_models.csv",
    "reports/figures/dashboard/overview.png",
    "scripts/data/download_sec_fsd_zips.py",
]

REQUIRED_MODULES = [
    "pandas",
    "numpy",
    "pyarrow",
    "altair",
    "sklearn",
    "streamlit",
    "joblib",
    "xgboost",
    "lightgbm",
]


def main() -> None:
    rows: list[dict[str, str]] = []

    def add(check: str, status: str, detail: str = "") -> None:
        rows.append({"check": check, "status": status, "detail": detail})

    add("python_version", "INFO", sys.version.replace("\n", " "))

    for module in REQUIRED_MODULES:
        try:
            __import__(module)
            add(f"import_{module}", "PASS")
        except Exception as exc:  # noqa: BLE001
            add(f"import_{module}", "FAIL", f"{type(exc).__name__}: {exc}")

    for rel_path in REQUIRED_FILES:
        path = PROJECT_ROOT / rel_path
        add(f"exists_{rel_path}", "PASS" if path.exists() else "FAIL", rel_path)

    try:
        parquet_panel = pd.read_parquet(PROJECT_ROOT / "data/github/firm_panel_v2.parquet")
        csv_panel = pd.read_csv(PROJECT_ROOT / "data/github/firm_panel_v2.csv.gz", low_memory=False)
        schema = pd.read_csv(PROJECT_ROOT / "data/github/firm_panel_v2_schema.csv")
        add("load_packaged_parquet_panel", "PASS", str(parquet_panel.shape))
        add("load_packaged_csv_panel", "PASS", str(csv_panel.shape))
        add("load_packaged_schema", "PASS", str(schema.shape))
        add(
            "csv_parquet_shape_match",
            "PASS" if csv_panel.shape == parquet_panel.shape else "FAIL",
            f"csv={csv_panel.shape}; parquet={parquet_panel.shape}",
        )
        add(
            "schema_covers_panel_columns",
            "PASS" if set(parquet_panel.columns).issubset(set(schema["column"])) else "FAIL",
            f"panel_columns={len(parquet_panel.columns)}; schema_columns={schema['column'].nunique()}",
        )
    except Exception as exc:  # noqa: BLE001
        add("load_packaged_panel_or_schema", "FAIL", f"{type(exc).__name__}: {exc}")

    compile_failures = []
    tracked_paths = subprocess.check_output(["git", "ls-files"], cwd=PROJECT_ROOT, text=True).splitlines()
    python_paths = sorted(
        PROJECT_ROOT / rel_path
        for rel_path in tracked_paths
        if rel_path.endswith(".py") and (rel_path.startswith("scripts/") or rel_path.startswith("app/"))
    )
    for path in python_paths:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:  # noqa: BLE001
            compile_failures.append(f"{path.relative_to(PROJECT_ROOT)}: {type(exc).__name__}: {exc}")
    add("compile_scripts_and_dashboard", "PASS" if not compile_failures else "FAIL", "; ".join(compile_failures[:5]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "status", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    failed = [row for row in rows if row["status"] == "FAIL"]
    print(f"GitHub package smoke check complete; failures={len(failed)}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
