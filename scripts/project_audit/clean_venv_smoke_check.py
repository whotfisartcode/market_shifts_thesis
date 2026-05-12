#!/usr/bin/env python3
"""Run a clean-virtualenv package smoke check from processed data."""

from __future__ import annotations

import csv
import py_compile
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "reports/project_audit/clean_venv_smoke_test_results.csv"


def main() -> None:
    rows: list[dict] = []

    def add(check: str, status: str, detail: str = "") -> None:
        rows.append({"check": check, "status": status, "detail": detail})

    add("python_executable", "INFO", sys.executable)
    for module in ["pandas", "numpy", "pyarrow", "altair", "sklearn", "streamlit", "xgboost", "lightgbm"]:
        try:
            __import__(module)
            add(f"import_{module}", "PASS")
        except Exception as exc:  # noqa: BLE001
            add(f"import_{module}", "FAIL", f"{type(exc).__name__}: {exc}")

    try:
        core = pd.read_parquet(PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.parquet")
        github = pd.read_parquet(PROJECT_ROOT / "data/github/firm_panel_v2.parquet")
        add("load_core_panel", "PASS", f"{core.shape}")
        add("load_github_panel", "PASS", f"{github.shape}")
        add("core_github_equal", "PASS" if core.equals(github) else "FAIL", str(core.equals(github)))
    except Exception as exc:  # noqa: BLE001
        add("panel_load_or_equality", "FAIL", f"{type(exc).__name__}: {exc}")

    failures = []
    for path in sorted((PROJECT_ROOT / "scripts").glob("**/*.py")) + sorted((PROJECT_ROOT / "app").glob("**/*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.relative_to(PROJECT_ROOT)}: {type(exc).__name__}: {exc}")
    add("compile_scripts_and_dashboard", "PASS" if not failures else "FAIL", "; ".join(failures[:5]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "status", "detail"])
        writer.writeheader()
        writer.writerows(rows)

    failed = [row for row in rows if row["status"] == "FAIL"]
    print(f"Clean venv smoke check complete; failures={len(failed)}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
