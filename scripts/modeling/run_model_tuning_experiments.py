#!/usr/bin/env python3
"""Run controlled hyperparameter tuning experiments without overwriting production models."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from train_panel_v2_models import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_preprocessor,
    choose_threshold,
    class_weight_sample,
    evaluate,
    load_panel,
    make_splits,
    predict_proba,
    validate_features,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = PROJECT_ROOT / "reports/model_tuning"
MODELING_REPORT_ROOT = PROJECT_ROOT / "reports/modeling"

PRODUCTION_TARGETS = [
    "distress_next_4q",
    "failure_pressure_conservative_v2_next_4obs",
    "success_resilience_next_4q",
]

BASELINE_BEST_MODEL_FILES = {
    target: MODELING_REPORT_ROOT / f"panel_v2_{target}_best_model.json"
    for target in PRODUCTION_TARGETS
}

SEEDS = [42, 202, 777]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    model_family: str
    params: dict
    seed: int | None = None
    sample_weighted: bool = False


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


def build_candidate(candidate: Candidate) -> Pipeline:
    params = dict(candidate.params)
    if candidate.model_family == "logistic_l2":
        estimator = LogisticRegression(
            max_iter=2500,
            solver="liblinear",
            class_weight="balanced",
            random_state=candidate.seed or 42,
            **params,
        )
    elif candidate.model_family == "random_forest":
        estimator = RandomForestClassifier(
            random_state=candidate.seed,
            n_jobs=-1,
            class_weight="balanced_subsample",
            **params,
        )
    elif candidate.model_family == "extra_trees":
        estimator = ExtraTreesClassifier(
            random_state=candidate.seed,
            n_jobs=-1,
            class_weight="balanced",
            **params,
        )
    elif candidate.model_family == "gradient_boosting":
        estimator = GradientBoostingClassifier(random_state=candidate.seed, **params)
    elif candidate.model_family == "hist_gradient_boosting":
        estimator = HistGradientBoostingClassifier(
            random_state=candidate.seed or 42,
            early_stopping=False,
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


def candidate_grid() -> list[Candidate]:
    candidates: list[Candidate] = []

    for c in [0.05, 0.2, 1.0, 5.0]:
        candidates.append(
            Candidate(
                candidate_id=f"logistic_l2_C{c:g}",
                model_family="logistic_l2",
                params={"C": c},
                seed=42,
            )
        )

    rf_configs = [
        {"n_estimators": 250, "max_depth": None, "min_samples_leaf": 5, "max_features": "sqrt"},
        {"n_estimators": 400, "max_depth": 8, "min_samples_leaf": 10, "max_features": "sqrt"},
        {"n_estimators": 500, "max_depth": 14, "min_samples_leaf": 5, "max_features": 0.5},
    ]
    for i, params in enumerate(rf_configs, start=1):
        for seed in SEEDS:
            candidates.append(
                Candidate(
                    candidate_id=f"random_forest_cfg{i}_seed{seed}",
                    model_family="random_forest",
                    params=params,
                    seed=seed,
                )
            )

    et_configs = [
        {"n_estimators": 300, "max_depth": None, "min_samples_leaf": 5, "max_features": "sqrt"},
        {"n_estimators": 500, "max_depth": 10, "min_samples_leaf": 8, "max_features": "sqrt"},
        {"n_estimators": 500, "max_depth": 16, "min_samples_leaf": 4, "max_features": 0.5},
    ]
    for i, params in enumerate(et_configs, start=1):
        for seed in SEEDS:
            candidates.append(
                Candidate(
                    candidate_id=f"extra_trees_cfg{i}_seed{seed}",
                    model_family="extra_trees",
                    params=params,
                    seed=seed,
                )
            )

    gb_configs = [
        {"n_estimators": 180, "learning_rate": 0.04, "max_depth": 2, "subsample": 0.85},
        {"n_estimators": 250, "learning_rate": 0.04, "max_depth": 3, "subsample": 0.85},
        {"n_estimators": 350, "learning_rate": 0.025, "max_depth": 3, "subsample": 0.85},
    ]
    for i, params in enumerate(gb_configs, start=1):
        for seed in SEEDS:
            candidates.append(
                Candidate(
                    candidate_id=f"gradient_boosting_cfg{i}_seed{seed}",
                    model_family="gradient_boosting",
                    params=params,
                    seed=seed,
                    sample_weighted=True,
                )
            )

    hgb_configs = [
        {"max_iter": 180, "learning_rate": 0.04, "max_leaf_nodes": 15, "l2_regularization": 0.0},
        {"max_iter": 250, "learning_rate": 0.03, "max_leaf_nodes": 31, "l2_regularization": 0.05},
        {"max_iter": 350, "learning_rate": 0.02, "max_leaf_nodes": 31, "l2_regularization": 0.1},
        {"max_iter": 250, "learning_rate": 0.04, "max_leaf_nodes": 63, "l2_regularization": 0.1},
    ]
    for i, params in enumerate(hgb_configs, start=1):
        candidates.append(
            Candidate(
                candidate_id=f"hist_gradient_boosting_cfg{i}",
                model_family="hist_gradient_boosting",
                params=params,
                seed=42,
                sample_weighted=True,
            )
        )

    return candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run controlled tuning experiments for production targets.")
    parser.add_argument(
        "--targets",
        nargs="+",
        default=PRODUCTION_TARGETS,
        help="Target columns to tune.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=None,
        help="Optional cap for quick smoke runs.",
    )
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

    metrics: list[dict] = []
    failures: list[dict] = []

    for idx, candidate in enumerate(candidates, start=1):
        start = perf_counter()
        print(f"[{target}] {idx}/{len(candidates)} {candidate.candidate_id}")
        try:
            model = build_candidate(candidate)
            fit_kwargs = {}
            if candidate.sample_weighted:
                fit_kwargs["model__sample_weight"] = class_weight_sample(y_train)
            model.fit(x_train, y_train, **fit_kwargs)

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
                        "sample_weighted": candidate.sample_weighted,
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

    if failures:
        pd.DataFrame(failures).to_csv(target_dir / "candidate_failures.csv", index=False)
    else:
        pd.DataFrame(
            columns=["target", "candidate_id", "model_family", "seed", "params_json", "error_type", "error_message"]
        ).to_csv(target_dir / "candidate_failures.csv", index=False)

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


def write_protocol(all_metrics: pd.DataFrame, candidates: list[Candidate]) -> None:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

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
    summary.to_csv(REPORT_ROOT / "model_tuning_summary.csv", index=False)
    write_baseline_comparison(summary)

    candidate_rows = [
        {
            "candidate_id": c.candidate_id,
            "model_family": c.model_family,
            "seed": c.seed,
            "sample_weighted": c.sample_weighted,
            "params_json": json.dumps(c.params, sort_keys=True),
        }
        for c in candidates
    ]
    pd.DataFrame(candidate_rows).to_csv(REPORT_ROOT / "candidate_grid.csv", index=False)

    lines = [
        "# Model Tuning Protocol",
        "",
        "Last updated: 2026-05-08",
        "",
        "This is a controlled robustness/tuning experiment. It does not overwrite the production models in `models/panel_v2/` and should be written as a supplementary model-development check.",
        "",
        "## Protocol",
        "",
        "- Data source: `data/processed/panel_v2/firm_panel_v2.csv.gz`.",
        "- Split policy: train <= 2018, validation 2019-2021, test 2022-2024.",
        "- Candidate selection uses validation data only.",
        "- Thresholds are selected on validation data using F1.",
        "- Final test metrics are observed after validation selection and must not be used for further tuning.",
        "- Missingness indicators created by the imputer may help prediction, but they should not be interpreted as economic factors.",
        "",
        "## Candidate Families",
        "",
        "- logistic regression with different regularization strengths;",
        "- random forest with multiple depths/leaves/features and seeds;",
        "- extra trees with multiple depths/leaves/features and seeds;",
        "- gradient boosting with multiple learning-rate/tree-depth settings and seeds;",
        "- histogram gradient boosting with multiple learning-rate/leaf/regularization settings.",
        "",
        "This protocol covers the sklearn-based tuning layer. XGBoost and LightGBM are handled separately in `reports/model_tuning_advanced/`; AutoGluon and CatBoost are not part of the production evidence unless deliberately installed, rerun, and documented.",
        "",
        "## Summary",
        "",
        markdown_table(summary),
        "",
        "## Thesis Wording",
        "",
        "Safe claim: the thesis did not rely on a single one-off model run. It used baseline temporal-validation models, target experiments, seed checks, feature-set ablations, and a controlled hyperparameter-tuning robustness pass.",
        "",
        "Unsafe claim: do not say exhaustive global hyperparameter optimization was performed. The correct wording is controlled/random-grid robustness tuning under time and reproducibility constraints.",
        "",
    ]
    (REPORT_ROOT / "MODEL_TUNING_PROTOCOL.md").write_text("\n".join(lines), encoding="utf-8")


def write_baseline_comparison(summary: pd.DataFrame) -> None:
    rows = []
    for row in summary.to_dict(orient="records"):
        target = row["target"]
        baseline_path = BASELINE_BEST_MODEL_FILES.get(target)
        if baseline_path is None or not baseline_path.exists():
            continue

        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "target": target,
                "production_baseline_model": baseline["model"],
                "baseline_test_roc_auc": baseline["roc_auc"],
                "baseline_test_pr_auc": baseline["pr_auc"],
                "baseline_test_precision": baseline["precision"],
                "baseline_test_recall": baseline["recall"],
                "baseline_test_f1": baseline["f1"],
                "validation_selected_tuned_candidate": row["chosen_by_validation_candidate"],
                "tuned_family": row["model_family"],
                "tuned_test_roc_auc": row["test_roc_auc"],
                "tuned_test_pr_auc": row["test_pr_auc"],
                "tuned_test_precision": row["test_precision"],
                "tuned_test_recall": row["test_recall"],
                "tuned_test_f1": row["test_f1"],
                "delta_pr_auc": row["test_pr_auc"] - baseline["pr_auc"],
                "delta_f1": row["test_f1"] - baseline["f1"],
            }
        )

    pd.DataFrame(rows).to_csv(REPORT_ROOT / "baseline_vs_tuned_comparison.csv", index=False)


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
    write_protocol(all_metrics, candidates)


if __name__ == "__main__":
    main()
