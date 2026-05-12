#!/usr/bin/env python3
"""Create a broad local audit of the thesis project workspace."""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
import math
import os
import py_compile
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = PROJECT_ROOT / "reports/project_audit"
REPORT_ROOT.mkdir(parents=True, exist_ok=True)

SKIP_DIR_PARTS = {"__pycache__"}
CORE_PANEL = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.parquet"
GITHUB_PANEL = PROJECT_ROOT / "data/github/firm_panel_v2.parquet"
SCHEMA_PATH = PROJECT_ROOT / "data/github/firm_panel_v2_schema.csv"
BLACKLIST_PATH = PROJECT_ROOT / "config/model_feature_blacklist.csv"

PRODUCTION_MODEL_TARGETS = [
    "distress_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "success_resilience_next_4q",
    "industry_relative_resilience_next_4obs",
    "stress_resilience_next_4obs",
    "recovery_next_4obs",
    "quality_success_cashflow_next_4obs",
]


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def classify(path: Path) -> str:
    parts = path.relative_to(PROJECT_ROOT).parts
    name = path.name
    suffix = path.suffix.lower()
    if name == ".DS_Store" or suffix == ".pyc" or "__pycache__" in parts:
        return "system_junk"
    if parts[0] == "data":
        if len(parts) > 2 and parts[1] == "raw":
            return "raw_data"
        if len(parts) > 2 and parts[1] == "github":
            return "github_dataset_package"
        if len(parts) > 2 and parts[1] == "samples":
            return "sample_data"
        if len(parts) > 2 and parts[1] == "processed":
            return "processed_data"
        return "data"
    if parts[0] == "reports":
        if len(parts) > 1 and parts[1] == "figures":
            return "figures"
        return "report_output"
    if parts[0] == "docs":
        if len(parts) > 1 and parts[1] == "_redundant":
            return "archived_doc"
        return "current_doc"
    if parts[0] == "scripts":
        if len(parts) > 1 and parts[1] == "legacy_parsers":
            return "legacy_code"
        return "code"
    if parts[0] == "app":
        return "dashboard_code"
    if parts[0] == "config":
        return "config"
    if parts[0] == "models":
        return "model_artifact"
    if parts[0] == "notebooks":
        return "notebook"
    if parts[0] == "_archive":
        return "archive"
    return "project_root"


def iter_files() -> list[Path]:
    files = []
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_file():
            files.append(path)
    return sorted(files)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        keys = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def inventory(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        stat = path.stat()
        rows.append(
            {
                "path": rel(path),
                "top_dir": path.relative_to(PROJECT_ROOT).parts[0],
                "category": classify(path),
                "extension": path.suffix.lower() or "[none]",
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 3),
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "file_inventory.csv", index=False)
    return frame


def audit_python(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        if path.suffix.lower() != ".py":
            continue
        status = "PASS"
        error = ""
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:  # noqa: BLE001 - audit output should keep exact failure
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        rows.append({"path": rel(path), "category": classify(path), "status": status, "error": error})
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "python_compile_audit.csv", index=False)
    return frame


def audit_json(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        if path.suffix.lower() not in {".json", ".ipynb"}:
            continue
        status = "PASS"
        error = ""
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        rows.append({"path": rel(path), "category": classify(path), "status": status, "error": error})
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "json_notebook_audit.csv", index=False)
    return frame


def quick_csv_audit(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        if path.suffix.lower() != ".csv" and not path.name.endswith(".csv.gz"):
            continue
        status = "PASS"
        columns = None
        sample_rows = None
        error = ""
        try:
            sample = pd.read_csv(path, nrows=5, low_memory=False)
            columns = len(sample.columns)
            sample_rows = len(sample)
            if columns == 0:
                status = "REVIEW"
                error = "No columns parsed"
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "path": rel(path),
                "category": classify(path),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
                "status": status,
                "sample_rows_read": sample_rows,
                "columns": columns,
                "error": error,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "csv_quick_audit.csv", index=False)
    return frame


def audit_parquet(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        if path.suffix.lower() != ".parquet":
            continue
        status = "PASS"
        rows_count = None
        columns = None
        error = ""
        try:
            df = pd.read_parquet(path)
            rows_count = len(df)
            columns = len(df.columns)
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "path": rel(path),
                "category": classify(path),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
                "status": status,
                "rows": rows_count,
                "columns": columns,
                "error": error,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "parquet_audit.csv", index=False)
    return frame


def audit_zip_inventory(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        if path.suffix.lower() != ".zip":
            continue
        status = "PASS"
        members = None
        error = ""
        try:
            with zipfile.ZipFile(path) as zf:
                members = len(zf.infolist())
                required = {"sub.txt", "num.txt", "pre.txt", "tag.txt"}
                lower_names = {Path(info.filename).name.lower() for info in zf.infolist()}
                missing = sorted(required - lower_names)
                if missing:
                    status = "REVIEW"
                    error = f"Missing expected SEC files: {missing}"
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "path": rel(path),
                "category": classify(path),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
                "status": status,
                "members": members,
                "error": error,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "zip_quick_audit.csv", index=False)
    return frame


def audit_panel() -> dict:
    result: dict = {"status": "PASS"}
    if not CORE_PANEL.exists():
        return {"status": "FAIL", "error": f"Missing {CORE_PANEL}"}

    df = pd.read_parquet(CORE_PANEL)
    result.update(
        {
            "rows": len(df),
            "columns": len(df.columns),
            "ciks": int(df["cik"].nunique()) if "cik" in df else None,
            "tickers": int(df["ticker"].nunique()) if "ticker" in df else None,
            "duplicate_ticker_prediction_period_rows": int(
                df.duplicated([c for c in ["ticker", "prediction_date", "period_date"] if c in df.columns]).sum()
            ),
        }
    )
    numeric = df.select_dtypes(include=["number"])
    if numeric.empty:
        result["infinite_numeric_values"] = 0
    else:
        numeric_values = numeric.to_numpy(dtype=float, na_value=np.nan)
        result["infinite_numeric_values"] = int(np.isinf(numeric_values).sum())
    for target in PRODUCTION_MODEL_TARGETS:
        if target in df.columns:
            result[f"{target}_known"] = int(df[target].notna().sum())
            result[f"{target}_positive"] = int(df[target].fillna(0).sum())
            result[f"{target}_missing"] = int(df[target].isna().sum())

    if SCHEMA_PATH.exists():
        schema = pd.read_csv(SCHEMA_PATH)
        schema_col = "column" if "column" in schema.columns else schema.columns[0]
        schema_cols = set(schema[schema_col].astype(str))
        panel_cols = set(df.columns)
        result["schema_columns"] = len(schema_cols)
        result["schema_missing_panel_columns"] = len(schema_cols - panel_cols)
        result["panel_columns_missing_schema_rows"] = len(panel_cols - schema_cols)

    if GITHUB_PANEL.exists():
        github = pd.read_parquet(GITHUB_PANEL)
        result["github_panel_rows"] = len(github)
        result["github_panel_columns"] = len(github.columns)
        result["github_panel_shape_matches_core"] = (
            len(github) == len(df) and len(github.columns) == len(df.columns)
        )

    pd.DataFrame([result]).to_csv(REPORT_ROOT / "core_panel_audit.csv", index=False)
    return result


def audit_model_outputs() -> pd.DataFrame:
    rows = []
    for target in PRODUCTION_MODEL_TARGETS:
        metrics_path = PROJECT_ROOT / f"reports/modeling/panel_v2_{target}_model_metrics.csv"
        best_path = PROJECT_ROOT / f"reports/modeling/panel_v2_{target}_best_model.json"
        status = "PASS"
        error = ""
        best_model = None
        best_pr_auc = None
        recomputed_best = None
        try:
            metrics = pd.read_csv(metrics_path)
            best = json.loads(best_path.read_text(encoding="utf-8"))
            test = metrics[metrics["split"] == "test"].sort_values("pr_auc", ascending=False)
            recomputed = test.iloc[0].to_dict()
            best_model = best.get("model")
            best_pr_auc = best.get("pr_auc")
            recomputed_best = recomputed.get("model")
            if best_model != recomputed_best or abs(float(best_pr_auc) - float(recomputed.get("pr_auc"))) > 1e-12:
                status = "FAIL"
                error = "Best-model JSON does not match highest test PR-AUC row"
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "target": target,
                "status": status,
                "best_model_json": best_model,
                "best_pr_auc_json": best_pr_auc,
                "recomputed_best_model": recomputed_best,
                "error": error,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "model_output_consistency_audit.csv", index=False)
    return frame


def audit_feature_blacklist() -> pd.DataFrame:
    rows = []
    blacklist = set()
    if BLACKLIST_PATH.exists():
        bl = pd.read_csv(BLACKLIST_PATH)
        blacklist = set(bl[bl.columns[0]].dropna().astype(str))
    for path in (PROJECT_ROOT / "reports/data_quality/model_feature_lists").glob("*_features.csv"):
        try:
            features = pd.read_csv(path)
            col = "column" if "column" in features.columns else features.columns[0]
            overlap = sorted(set(features[col].dropna().astype(str)) & blacklist)
            rows.append(
                {
                    "path": rel(path),
                    "status": "PASS" if not overlap else "FAIL",
                    "feature_count": len(features),
                    "blacklist_overlap_count": len(overlap),
                    "blacklist_overlap": ";".join(overlap),
                }
            )
        except Exception as exc:  # noqa: BLE001
            rows.append({"path": rel(path), "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "feature_blacklist_audit.csv", index=False)
    return frame


PATH_REF_RE = re.compile(
    r"(?P<path>(?:docs|reports|scripts|data|config|app|models|notebooks)"
    r"(?:/[A-Za-z0-9_.()\-]+)*/?|requirements\.txt|README\.md)"
)


def strip_fenced_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def is_local_reference_match(text: str, start: int) -> bool:
    if start == 0:
        return True
    previous = text[start - 1]
    return previous.isspace() or previous in {"`", "'", '"', "(", "[", "{", "<", ":"}


def audit_doc_references(files: list[Path]) -> pd.DataFrame:
    rows = []
    for path in files:
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        rel_path = rel(path)
        if rel_path.startswith("docs/_redundant/") or rel_path == "reports/project_audit/doc_reference_todo.md":
            continue
        text = strip_fenced_code_blocks(path.read_text(encoding="utf-8", errors="ignore"))
        for match in PATH_REF_RE.finditer(text):
            if not is_local_reference_match(text, match.start()):
                continue
            ref = match.group("path").strip().rstrip(".,);`")
            if ref.startswith("reports/figures/") and " " in ref:
                # Legacy figure names with spaces are often partial regex captures; skip noisy false positives.
                continue
            target = PROJECT_ROOT / ref
            if not target.exists():
                rows.append(
                    {
                        "source": rel(path),
                        "reference": ref,
                        "status": "BROKEN",
                    }
                )
    frame = pd.DataFrame(rows, columns=["source", "reference", "status"])
    frame.to_csv(REPORT_ROOT / "doc_reference_audit.csv", index=False)
    return frame


def audit_requirements() -> pd.DataFrame:
    mapping = {
        "pandas": "pandas",
        "numpy": "numpy",
        "pyarrow": "pyarrow",
        "altair": "altair",
        "scikit-learn": "sklearn",
        "matplotlib": "matplotlib",
        "seaborn": "seaborn",
        "requests": "requests",
        "pyyaml": "yaml",
        "streamlit": "streamlit",
        "joblib": "joblib",
        "xgboost": "xgboost",
        "lightgbm": "lightgbm",
    }
    rows = []
    for package, module in mapping.items():
        rows.append(
            {
                "package": package,
                "module": module,
                "installed": importlib.util.find_spec(module) is not None,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "dependency_import_audit.csv", index=False)
    return frame


def audit_configs() -> pd.DataFrame:
    required = [
        "config/sec_fsd_concept_map.csv",
        "config/model_feature_blacklist.csv",
        "config/distress_event_dates.csv",
        "config/fred_series_catalog.csv",
        "config/global_event_calendar_seed.csv",
        "config/universe_v2_draft_expanded_150.csv",
    ]
    rows = []
    for ref_path in required:
        path = PROJECT_ROOT / ref_path
        status = "PASS" if path.exists() else "FAIL"
        rows.append({"path": ref_path, "status": status, "size_bytes": path.stat().st_size if path.exists() else None})
    frame = pd.DataFrame(rows)
    frame.to_csv(REPORT_ROOT / "required_config_audit.csv", index=False)
    return frame


def summarize(inventory_frame: pd.DataFrame, audits: dict[str, pd.DataFrame | dict]) -> None:
    summary_rows = []
    summary_rows.append({"metric": "total_files", "value": len(inventory_frame)})
    summary_rows.append({"metric": "total_size_gb", "value": round(inventory_frame["size_bytes"].sum() / (1024**3), 3)})
    for category, count in inventory_frame["category"].value_counts().sort_index().items():
        summary_rows.append({"metric": f"files_category_{category}", "value": int(count)})
    for top_dir, size in inventory_frame.groupby("top_dir")["size_bytes"].sum().sort_values(ascending=False).items():
        summary_rows.append({"metric": f"size_mb_topdir_{top_dir}", "value": round(size / (1024 * 1024), 3)})

    for name, audit in audits.items():
        if isinstance(audit, pd.DataFrame) and "status" in audit.columns:
            status_counts = audit["status"].fillna("UNKNOWN").value_counts().sort_index()
            for status, count in status_counts.items():
                summary_rows.append({"metric": f"{name}_{status}", "value": int(count)})
            if name == "doc_references" and "BROKEN" not in status_counts:
                summary_rows.append({"metric": "doc_references_BROKEN", "value": 0})
    write_csv(REPORT_ROOT / "audit_summary_metrics.csv", summary_rows, ["metric", "value"])


def main() -> None:
    files = iter_files()
    inventory_frame = inventory(files)
    audits: dict[str, pd.DataFrame | dict] = {
        "python_compile": audit_python(files),
        "json_notebook": audit_json(files),
        "csv_quick": quick_csv_audit(files),
        "parquet": audit_parquet(files),
        "zip_quick": audit_zip_inventory(files),
        "core_panel": audit_panel(),
        "model_output_consistency": audit_model_outputs(),
        "feature_blacklist": audit_feature_blacklist(),
        "doc_references": audit_doc_references(files),
        "dependency_import": audit_requirements(),
        "required_config": audit_configs(),
    }
    summarize(inventory_frame, audits)
    print(f"Wrote audit outputs to {REPORT_ROOT}")


if __name__ == "__main__":
    main()
