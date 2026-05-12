#!/usr/bin/env python3
"""Run XGBoost and LightGBM robustness experiments without overwriting production models."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from train_panel_v2_models import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_preprocessor,
    choose_threshold,
    evaluate,
    load_panel,
    make_splits,
    predict_proba,
    validate_features,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = PROJECT_ROOT / "reports/model_tuning_advanced"
MODELING_REPORT_ROOT = PROJECT_ROOT / "reports/modeling"
SKLEARN_TUNING_SUMMARY = PROJECT_ROOT / "reports/model_tuning/model_tuning_summary.csv"

PRODUCTION_TARGETS = [
    "distress_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "success_resilience_next_4q",
]

SEEDS = [42, 202, 777]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    model_family: str
    params: dict
    seed: int


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return ""
    headers = [str(col) for col in frame.columns]
    rows = frame.astype(str).values.tolist()
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |")
    return "\n".join(output)


def candidate_grid() -> list[Candidate]:
    candidates: list[Candidate] = []

    xgb_configs = [
        {
            "n_estimators": 250,
            "max_depth": 2,
            "learning_rate": 0.04,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "min_child_weight": 5,
        },
        {
            "n_estimators": 400,
            "max_depth": 3,
            "learning_rate": 0.03,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "reg_lambda": 2.0,
            "reg_alpha": 0.05,
            "min_child_weight": 8,
        },
        {
            "n_estimators": 600,
            "max_depth": 3,
            "learning_rate": 0.02,
            "subsample": 0.75,
            "colsample_bytree": 0.75,
            "reg_lambda": 4.0,
            "reg_alpha": 0.1,
            "min_child_weight": 10,
        },
        {
            "n_estimators": 350,
            "max_depth": 4,
            "learning_rate": 0.035,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_lambda": 3.0,
            "reg_alpha": 0.05,
            "min_child_weight": 6,
        },
    ]
    for i, params in enumerate(xgb_configs, start=1):
        for seed in SEEDS:
            candidates.append(
                Candidate(
                    candidate_id=f"xgboost_cfg{i}_seed{seed}",
                    model_family="xgboost",
                    params=params,
                    seed=seed,
                )
            )

    lgbm_configs = [
        {
            "n_estimators": 250,
            "num_leaves": 15,
            "learning_rate": 0.04,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "min_child_samples": 40,
        },
        {
            "n_estimators": 400,
            "num_leaves": 31,
            "learning_rate": 0.03,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "reg_lambda": 2.0,
            "reg_alpha": 0.05,
            "min_child_samples": 60,
        },
        {
            "n_estimators": 600,
            "num_leaves": 31,
            "learning_rate": 0.02,
            "subsample": 0.75,
            "colsample_bytree": 0.75,
            "reg_lambda": 4.0,
            "reg_alpha": 0.1,
            "min_child_samples": 80,
        },
        {
            "n_estimators": 350,
            "num_leaves": 63,
            "learning_rate": 0.035,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_lambda": 3.0,
            "reg_alpha": 0.05,
            "min_child_samples": 60,
        },
    ]
    for i, params in enumerate(lgbm_configs, start=1):
        for seed in SEEDS:
            candidates.append(
                Candidate(
                    candidate_id=f"lightgbm_cfg{i}_seed{seed}",
                    model_family="lightgbm",
                    params=params,
                    seed=seed,
                )
            )

    return candidates


def class_ratio(y: pd.Series) -> float:
    positives = int(y.sum())
    negatives = int(len(y) - positives)
    if positives == 0:
        return 1.0
    return negatives / positives


def build_candidate(candidate: Candidate, scale_pos_weight: float) -> Pipeline:
    params = dict(candidate.params)
    if candidate.model_family == "xgboost":
        estimator = XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            n_jobs=-1,
            random_state=candidate.seed,
            scale_pos_weight=scale_pos_weight,
            **params,
        )
    elif candidate.model_family == "lightgbm":
        estimator = LGBMClassifier(
            objective="binary",
            n_jobs=-1,
            random_state=candidate.seed,
            scale_pos_weight=scale_pos_weight,
            verbosity=-1,
            **params,
        )
    else:
        raise ValueError(f"Unknown model family: {candidate.model_family}")

    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", estimator),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run XGBoost and LightGBM robustness experiments.")
    parser.add_argument("--targets", nargs="+", default=PRODUCTION_TARGETS)
    parser.add_argument("--max-candidates", type=int, default=None, help="Optional cap for smoke testing.")
    return parser.parse_args()


def fit_and_score_target(target: str, candidates: list[Candidate]) -> pd.DataFrame:
    target_dir = REPORT_ROOT / target
    target_dir.mkdir(parents=True, exist_ok=True)

    df = load_panel(target)
    splits = make_splits(df)
    features = validate_features(df, NUMERIC_FEATURES + CATEGORICAL_FEATURES)

    x_train = splits["train"][features]
    y_train = splits["train"][target].astype(int)
    x_val = splits["validation"][features]
    y_val = splits["validation"][target].astype(int)
    x_test = splits["test"][features]
    y_test = splits["test"][target].astype(int)
    spw = class_ratio(y_train)

    metrics: list[dict] = []
    failures: list[dict] = []

    for idx, candidate in enumerate(candidates, start=1):
        start = perf_counter()
        print(f"[{target}] {idx}/{len(candidates)} {candidate.candidate_id}")
        try:
            model = build_candidate(candidate, spw)
            model.fit(x_train, y_train)
            val_proba = predict_proba(model, x_val)
            threshold = choose_threshold(y_val.to_numpy(), val_proba)
            elapsed = perf_counter() - start

            for split_name, x_split, y_split in [
                ("train", x_train, y_train),
                ("validation", x_val, y_val),
                ("test", x_test, y_test),
            ]:
                proba = predict_proba(model, x_split)
                row = evaluate(candidate.candidate_id, split_name, y_split.to_numpy(), proba, threshold)
                row.update(
                    {
                        "target": target,
                        "model_family": candidate.model_family,
                        "seed": candidate.seed,
                        "params_json": json.dumps(candidate.params, sort_keys=True),
                        "scale_pos_weight": spw,
                        "fit_seconds": round(elapsed, 3),
                    }
                )
                metrics.append(row)
        except Exception as exc:  # noqa: BLE001 - write failure row for auditability
            failures.append(
                {
                    "target": target,
                    "candidate_id": candidate.candidate_id,
                    "model_family": candidate.model_family,
                    "seed": candidate.seed,
                    "params_json": json.dumps(candidate.params, sort_keys=True),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )

    metrics_frame = pd.DataFrame(metrics)
    metrics_frame.to_csv(target_dir / "candidate_metrics.csv", index=False)

    failure_columns = ["target", "candidate_id", "model_family", "seed", "params_json", "error_type", "error_message"]
    pd.DataFrame(failures, columns=failure_columns).to_csv(target_dir / "candidate_failures.csv", index=False)

    validation = (
        metrics_frame[metrics_frame["split"] == "validation"]
        .sort_values(["pr_auc", "f1", "roc_auc"], ascending=False)
        .copy()
    )
    test = (
        metrics_frame[metrics_frame["split"] == "test"]
        .sort_values(["pr_auc", "f1", "roc_auc"], ascending=False)
        .copy()
    )
    validation.to_csv(target_dir / "validation_leaderboard.csv", index=False)
    test.to_csv(target_dir / "test_leaderboard_observed_not_selected_on.csv", index=False)

    best_id = validation.iloc[0]["model"]
    best_rows = metrics_frame[metrics_frame["model"] == best_id].copy()
    best_rows.to_csv(target_dir / "best_by_validation_metrics.csv", index=False)
    (target_dir / "best_by_validation.json").write_text(
        json.dumps(best_rows.to_dict(orient="records"), indent=2),
        encoding="utf-8",
    )

    return metrics_frame


def summarize(all_metrics: pd.DataFrame, candidates: list[Candidate]) -> pd.DataFrame:
    summary_rows = []
    for target, group in all_metrics.groupby("target"):
        validation = group[group["split"] == "validation"].sort_values(["pr_auc", "f1", "roc_auc"], ascending=False)
        chosen = validation.iloc[0]["model"]
        test_row = group[(group["model"] == chosen) & (group["split"] == "test")].iloc[0]
        summary_rows.append(
            {
                "target": target,
                "chosen_by_validation_candidate": chosen,
                "model_family": test_row["model_family"],
                "test_rows": test_row["rows"],
                "test_positives": test_row["positives"],
                "test_roc_auc": test_row["roc_auc"],
                "test_pr_auc": test_row["pr_auc"],
                "test_precision": test_row["precision"],
                "test_recall": test_row["recall"],
                "test_f1": test_row["f1"],
                "threshold_from_validation": test_row["threshold"],
            }
        )

    summary = pd.DataFrame(summary_rows).sort_values("target")
    summary.to_csv(REPORT_ROOT / "advanced_boosting_summary.csv", index=False)

    candidate_rows = [
        {
            "candidate_id": c.candidate_id,
            "model_family": c.model_family,
            "seed": c.seed,
            "params_json": json.dumps(c.params, sort_keys=True),
        }
        for c in candidates
    ]
    pd.DataFrame(candidate_rows).to_csv(REPORT_ROOT / "candidate_grid.csv", index=False)
    write_comparison(summary)
    write_protocol(summary, candidates)
    return summary


def write_comparison(summary: pd.DataFrame) -> None:
    sklearn_summary = pd.DataFrame()
    if SKLEARN_TUNING_SUMMARY.exists():
        sklearn_summary = pd.read_csv(SKLEARN_TUNING_SUMMARY)

    rows = []
    for row in summary.to_dict(orient="records"):
        target = row["target"]
        baseline_path = MODELING_REPORT_ROOT / f"panel_v2_{target}_best_model.json"
        baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}
        sklearn_row = pd.Series(dtype=object)
        if not sklearn_summary.empty:
            match = sklearn_summary[sklearn_summary["target"] == target]
            if not match.empty:
                sklearn_row = match.iloc[0]

        rows.append(
            {
                "target": target,
                "production_baseline_model": baseline.get("model"),
                "baseline_test_pr_auc": baseline.get("pr_auc"),
                "baseline_test_f1": baseline.get("f1"),
                "sklearn_tuned_candidate": sklearn_row.get("chosen_by_validation_candidate"),
                "sklearn_tuned_pr_auc": sklearn_row.get("test_pr_auc"),
                "sklearn_tuned_f1": sklearn_row.get("test_f1"),
                "advanced_boosting_candidate": row["chosen_by_validation_candidate"],
                "advanced_family": row["model_family"],
                "advanced_test_pr_auc": row["test_pr_auc"],
                "advanced_test_f1": row["test_f1"],
                "advanced_delta_vs_baseline_pr_auc": (
                    row["test_pr_auc"] - baseline["pr_auc"] if "pr_auc" in baseline else None
                ),
                "advanced_delta_vs_baseline_f1": row["test_f1"] - baseline["f1"] if "f1" in baseline else None,
                "advanced_delta_vs_sklearn_tuned_pr_auc": (
                    row["test_pr_auc"] - sklearn_row["test_pr_auc"] if "test_pr_auc" in sklearn_row else None
                ),
                "advanced_delta_vs_sklearn_tuned_f1": (
                    row["test_f1"] - sklearn_row["test_f1"] if "test_f1" in sklearn_row else None
                ),
            }
        )

    pd.DataFrame(rows).to_csv(REPORT_ROOT / "advanced_vs_existing_comparison.csv", index=False)


def write_protocol(summary: pd.DataFrame, candidates: list[Candidate]) -> None:
    counts = pd.Series([c.model_family for c in candidates]).value_counts().sort_index()
    lines = [
        "# Advanced Boosting Experiment Protocol",
        "",
        "Last updated: 2026-05-08",
        "",
        "This is an advanced benchmark layer for XGBoost and LightGBM. It does not overwrite production models.",
        "",
        "## Protocol",
        "",
        "- Data source: `data/processed/panel_v2/firm_panel_v2.csv.gz`.",
        "- Split policy: train <= 2018, validation 2019-2021, test 2022-2024.",
        "- Candidate selection uses validation data only.",
        "- Thresholds are selected on validation data using F1.",
        "- Final test metrics are observed after validation selection and must not be used for further tuning.",
        "- Class imbalance is handled with train-split `scale_pos_weight`.",
        "",
        "## Candidate Counts",
        "",
        markdown_table(counts.rename_axis("model_family").reset_index(name="candidate_configs")),
        "",
        "## Validation-Selected Summary",
        "",
        markdown_table(summary),
        "",
        "## Thesis Wording",
        "",
        "Safe claim: XGBoost and LightGBM were tested as advanced boosted-tree robustness benchmarks using the same temporal validation protocol.",
        "",
        "Unsafe claim: do not call the result AutoML or exhaustive search. This is a controlled advanced boosting benchmark.",
        "",
    ]
    (REPORT_ROOT / "ADVANCED_BOOSTING_PROTOCOL.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    candidates = candidate_grid()
    if args.max_candidates is not None:
        candidates = candidates[: args.max_candidates]

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    all_frames = []
    for target in args.targets:
        all_frames.append(fit_and_score_target(target, candidates))
    all_metrics = pd.concat(all_frames, ignore_index=True)
    all_metrics.to_csv(REPORT_ROOT / "all_candidate_metrics.csv", index=False)
    summarize(all_metrics, candidates)


if __name__ == "__main__":
    main()
