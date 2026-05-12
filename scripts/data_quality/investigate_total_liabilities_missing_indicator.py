#!/usr/bin/env python3
"""Investigate total-liabilities missingness and missing-indicator target risk."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modeling.train_panel_v2_models import CATEGORICAL_FEATURES, NUMERIC_FEATURES, validate_features  # noqa: E402


PANEL_PATH = PROJECT_ROOT / "data/processed/panel_v2/firm_panel_v2.csv.gz"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"
MODEL_REPORT_DIR = PROJECT_ROOT / "reports/modeling"

SUCCESS_TARGET = "success_resilience_next_4q"
DISTRESS_TARGET = "distress_next_4q"
DATE_COLS = ["period_date", "filed_date", "prediction_date", "event_date"]

RELATED_FIELDS = [
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "leverage_assets",
    "equity_assets",
    "current_ratio",
    "cash_assets",
]


class DropNamedFeatures:
    """Drop transformed sklearn columns by exact name after preprocessing."""

    def __init__(self, drop_names: set[str]):
        self.drop_names = drop_names

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        keep = [index for index, name in enumerate(self.feature_names_in_) if name not in self.drop_names]
        return x[:, keep]

    def set_feature_names(self, names: list[str]) -> "DropNamedFeatures":
        self.feature_names_in_ = names
        return self


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, low_memory=False)
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in set(NUMERIC_FEATURES + RELATED_FIELDS + [SUCCESS_TARGET, DISTRESS_TARGET, "post_event_flag"]):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def add_split(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    year = df["prediction_date"].dt.year
    df["temporal_split"] = "unused"
    df.loc[year <= 2018, "temporal_split"] = "train"
    df.loc[year.between(2019, 2021), "temporal_split"] = "validation"
    df.loc[year.between(2022, 2024), "temporal_split"] = "test"
    return df


def modeling_frame(df: pd.DataFrame, target: str) -> pd.DataFrame:
    out = df[df["prediction_date"].dt.year.between(2009, 2024)].copy()
    out = out[out["post_event_flag"].fillna(0).astype(int) == 0].copy()
    out = out[out[target].notna()].copy()
    out[target] = out[target].astype(int)
    return out


def split_frame(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    year = df["prediction_date"].dt.year
    return {
        "train": df[year <= 2018].copy(),
        "validation": df[year.between(2019, 2021)].copy(),
        "test": df[year.between(2022, 2024)].copy(),
    }


def write_origin() -> None:
    text = [
        "missingindicator_total_liabilities origin",
        "",
        "The raw panel does not contain a column named missingindicator_total_liabilities.",
        "It is generated inside the sklearn preprocessing pipeline by SimpleImputer(add_indicator=True).",
        "The indicator equals 1 when total_liabilities is missing before median imputation.",
        "It can be useful for predictive performance, but it is not an SEC accounting variable and must not be interpreted as a direct economic factor.",
    ]
    (REPORT_DIR / "missingindicator_total_liabilities_origin.txt").write_text("\n".join(text) + "\n", encoding="utf-8")


def summarize_missingness(df: pd.DataFrame) -> None:
    rows = []

    def add_group(grouping: str, frame: pd.DataFrame, value: object) -> None:
        missing = frame["total_liabilities"].isna()
        rows.append(
            {
                "grouping": grouping,
                "group_value": value,
                "rows": len(frame),
                "missing_total_liabilities_rows": int(missing.sum()),
                "missing_total_liabilities_share": float(missing.mean()) if len(frame) else np.nan,
                "distress_next_4q_share": frame[DISTRESS_TARGET].mean(),
                "success_resilience_next_4q_share": frame[SUCCESS_TARGET].mean(),
            }
        )

    add_group("overall", df, "all")
    for grouping in [
        "temporal_split",
        "prediction_year",
        "Sector",
        "form",
        "afs",
        "sec_zip",
        "cohort",
        "post_event_flag",
        DISTRESS_TARGET,
        SUCCESS_TARGET,
    ]:
        if grouping not in df.columns:
            continue
        for value, group in df.groupby(grouping, dropna=False):
            add_group(grouping, group, value)

    pd.DataFrame(rows).to_csv(REPORT_DIR / "total_liabilities_missingness_diagnostic.csv", index=False)

    firm = (
        df.groupby(["cik", "ticker"], dropna=False)
        .agg(
            rows=("adsh", "count"),
            missing_total_liabilities_rows=("total_liabilities", lambda s: int(s.isna().sum())),
            first_prediction_date=("prediction_date", "min"),
            last_prediction_date=("prediction_date", "max"),
            distress_next_4q_rows=(DISTRESS_TARGET, "sum"),
            success_resilience_next_4q_rows=(SUCCESS_TARGET, "sum"),
        )
        .reset_index()
    )
    firm["missing_total_liabilities_share"] = firm["missing_total_liabilities_rows"] / firm["rows"]
    firm = firm.sort_values(["missing_total_liabilities_share", "rows"], ascending=[False, False])
    firm.to_csv(REPORT_DIR / "total_liabilities_missingness_by_firm.csv", index=False)


def related_fields_audit(df: pd.DataFrame) -> None:
    rows = []
    for field in RELATED_FIELDS:
        if field not in df.columns:
            continue
        values = pd.to_numeric(df[field], errors="coerce")
        rows.append(
            {
                "field": field,
                "rows": len(df),
                "missing_rows": int(values.isna().sum()),
                "missing_share": float(values.isna().mean()),
                "zero_rows": int((values == 0).sum()),
                "negative_rows": int((values < 0).sum()),
                "p01": values.quantile(0.01),
                "median": values.median(),
                "p99": values.quantile(0.99),
            }
        )
    pd.DataFrame(rows).to_csv(REPORT_DIR / "total_liabilities_related_fields_audit.csv", index=False)


def derivation_audit(df: pd.DataFrame) -> None:
    frame = df[["ticker", "cik", "prediction_date", "total_assets", "total_equity", "total_liabilities"]].copy()
    frame["derived_total_liabilities"] = frame["total_assets"] - frame["total_equity"]
    frame["derivation_available"] = frame["total_assets"].notna() & frame["total_equity"].notna()
    frame["reported_available"] = frame["total_liabilities"].notna()
    both = frame["derivation_available"] & frame["reported_available"]
    frame["absolute_difference"] = np.nan
    frame.loc[both, "absolute_difference"] = (
        frame.loc[both, "derived_total_liabilities"] - frame.loc[both, "total_liabilities"]
    ).abs()
    denominator = frame["total_liabilities"].abs().replace(0, np.nan)
    frame["relative_difference"] = frame["absolute_difference"] / denominator
    frame["candidate_fill_when_missing_reported"] = frame["derivation_available"] & ~frame["reported_available"]
    frame.to_csv(REPORT_DIR / "total_liabilities_derivation_feasibility.csv", index=False)

    close = frame.loc[both, "relative_difference"].le(0.01) | frame.loc[both, "absolute_difference"].le(1_000_000)
    lines = [
        "Total liabilities derivation feasibility",
        "",
        f"Rows: {len(frame):,}",
        f"Rows with reported total_liabilities: {int(frame['reported_available'].sum()):,}",
        f"Rows with total_assets and total_equity available: {int(frame['derivation_available'].sum()):,}",
        f"Rows with both reported and derivable values: {int(both.sum()):,}",
        f"Rows where total_liabilities is missing but derivation is available: {int(frame['candidate_fill_when_missing_reported'].sum()):,}",
        f"Median absolute difference where both exist: {frame.loc[both, 'absolute_difference'].median():,.2f}",
        f"Median relative difference where both exist: {frame.loc[both, 'relative_difference'].median():.6f}",
        f"Share close by <=1% relative difference or <=$1m absolute difference: {float(close.mean()) if len(close) else np.nan:.4f}",
        "",
        "Recommendation: do not silently fill the production panel until reviewed. If used, derived liabilities should be a separate documented field or a controlled parser improvement.",
    ]
    (REPORT_DIR / "total_liabilities_derivation_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def success_target_missingness_audit(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["cik", "prediction_date", "period_date", "filed_date"]).copy()
    grouped = df.groupby("cik", group_keys=False)
    rows = []
    component_rows = []

    future_health_valid = []
    future_healthy_strict = []
    for step in range(1, 5):
        net_income = grouped["net_income"].shift(-step)
        roa = grouped["roa"].shift(-step)
        leverage = grouped["leverage_assets"].shift(-step)
        valid = net_income.notna() & roa.notna() & leverage.notna()
        healthy = valid & (net_income > 0) & (roa > 0) & leverage.between(0, 0.85, inclusive="both")
        future_health_valid.append(valid.astype(int))
        future_healthy_strict.append(healthy.astype(int))
        component_rows.append(
            {
                "future_step": step,
                "net_income_missing_rows": int(net_income.isna().sum()),
                "roa_missing_rows": int(roa.isna().sum()),
                "leverage_assets_missing_rows": int(leverage.isna().sum()),
                "all_health_components_available_rows": int(valid.sum()),
                "strict_healthy_rows": int(healthy.sum()),
            }
        )

    valid_count = pd.concat(future_health_valid, axis=1).sum(axis=1)
    strict_healthy_count = pd.concat(future_healthy_strict, axis=1).sum(axis=1)
    revised = pd.Series(pd.NA, index=df.index, dtype="Int64")
    enough_valid = valid_count >= 3
    revised.loc[enough_valid] = ((strict_healthy_count.loc[enough_valid] >= 3) & (df.loc[enough_valid, "formal_distress_firm"].fillna(0).astype(int) == 0)).astype("Int64")

    current = df[SUCCESS_TARGET].astype("Int64")
    df["success_resilience_next_4q_revised_missing_aware"] = revised
    df["future_health_valid_count_4obs"] = valid_count
    df["future_healthy_strict_count_4obs"] = strict_healthy_count
    comparable = current.notna() & revised.notna()
    current_zero_revised_unknown = (current.notna() & (current == 0) & revised.isna())
    current_unknown_revised_unknown = current.isna() & revised.isna()
    known_disagreement_count = int((current.loc[comparable] != revised.loc[comparable]).sum())
    target_definition_issue_active = int(current_zero_revised_unknown.sum()) > 0 or known_disagreement_count > 0
    rows.extend(component_rows)
    rows.extend(
        [
            {"future_step": "all", "metric": "rows", "value": len(df)},
            {"future_step": "all", "metric": "current_success_positive_rows", "value": int(current.fillna(0).sum())},
            {"future_step": "all", "metric": "current_unknown_rows", "value": int(current.isna().sum())},
            {"future_step": "all", "metric": "revised_known_rows", "value": int(revised.notna().sum())},
            {"future_step": "all", "metric": "revised_unknown_rows", "value": int(revised.isna().sum())},
            {"future_step": "all", "metric": "revised_success_positive_rows", "value": int(revised.fillna(0).sum())},
            {"future_step": "all", "metric": "current_zero_revised_unknown_rows", "value": int(current_zero_revised_unknown.sum())},
            {"future_step": "all", "metric": "current_unknown_revised_unknown_rows", "value": int(current_unknown_revised_unknown.sum())},
            {"future_step": "all", "metric": "current_revised_disagreement_known_rows", "value": known_disagreement_count},
        ]
    )
    pd.DataFrame(rows).to_csv(REPORT_DIR / "success_resilience_target_missingness_audit.csv", index=False)

    if target_definition_issue_active:
        diagnosis = [
            "The current `success_resilience_next_4q` target is missingness-sensitive. It is based on future `healthy_current` flags, and `healthy_current` treats missing leverage/ROA/net-income components as not healthy because boolean comparisons with missing values evaluate to false.",
            "",
            "This means rows with missing future leverage/liabilities can become target=0 rather than unknown. The strong association between `missingindicator_total_liabilities` and the success target confirms this is a real target-definition risk.",
        ]
        recommendation = "Revise the production success target logic so unknown future health components remain unknown instead of becoming automatic non-success. Retrain success models after the target fix. Keep missingness indicators out of economic factor interpretation plots."
        status = "Target issue active"
    else:
        diagnosis = [
            "The rebuilt `success_resilience_next_4q` target is missing-aware. Future rows without enough observed net-income, ROA, and leverage/assets components remain null instead of becoming automatic non-success.",
            "",
            "The pre-fix audit confirmed that `missingindicator_total_liabilities` was partly proxying for this target-definition problem. In the rebuilt panel, the indicator may still be useful as a predictive/reporting-pattern feature, but it must not be interpreted as a direct economic success factor.",
        ]
        recommendation = "Keep the missing-aware production target. Missingness indicators may remain in predictive models after diagnosis, but economic interpretation tables and plots should separate or exclude them."
        status = "Target issue fixed"

    lines = [
        "# Success Resilience Target Definition Review",
        "",
        f"Status: {status}",
        "",
        "## Diagnosis",
        "",
        *diagnosis,
        "",
        "## Missing-Aware Alternative",
        "",
        "A safer target should require at least three future observations where net income, ROA, and leverage/assets are all available. Rows without enough future component coverage should remain null for the forward success target.",
        "",
        "## Current Audit Counts",
        "",
        f"- Current success positives: {int(current.fillna(0).sum()):,}",
        f"- Current unknown rows: {int(current.isna().sum()):,}",
        f"- Revised known rows: {int(revised.notna().sum()):,}",
        f"- Revised unknown rows: {int(revised.isna().sum()):,}",
        f"- Revised success positives: {int(revised.fillna(0).sum()):,}",
        f"- Rows currently 0 but revised unknown: {int(current_zero_revised_unknown.sum()):,}",
        f"- Rows currently unknown and revised unknown: {int(current_unknown_revised_unknown.sum()):,}",
        f"- Known current/revised disagreements: {known_disagreement_count:,}",
        "",
        "## Recommendation",
        "",
        recommendation,
    ]
    (REPORT_DIR / "success_resilience_target_definition_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return df


def build_preprocessor(features: list[str], add_indicator: bool = True) -> ColumnTransformer:
    numeric = [feature for feature in features if feature in NUMERIC_FEATURES]
    categorical = [feature for feature in features if feature in CATEGORICAL_FEATURES]
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median", add_indicator=add_indicator)),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
        ],
        remainder="drop",
    )


def build_model(model_name: str, features: list[str], add_indicator: bool = True) -> Pipeline:
    if model_name == "logistic_l2":
        estimator = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear", random_state=42)
    elif model_name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=250,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        )
    elif model_name == "gradient_boosting":
        estimator = GradientBoostingClassifier(n_estimators=180, learning_rate=0.04, max_depth=3, random_state=42)
    else:
        raise ValueError(model_name)
    return Pipeline([("preprocess", build_preprocessor(features, add_indicator=add_indicator)), ("model", estimator)])


def threshold(y_true: np.ndarray, proba: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    if len(thresholds) == 0:
        return 0.5
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(f1))])


def evaluate(y_true: np.ndarray, proba: np.ndarray, cutoff: float) -> dict[str, float]:
    pred = (proba >= cutoff).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, proba) if len(np.unique(y_true)) > 1 else np.nan,
        "pr_auc": average_precision_score(y_true, proba) if len(np.unique(y_true)) > 1 else np.nan,
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
    }


def make_missing_flags(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    numeric = [feature for feature in features if feature in NUMERIC_FEATURES]
    return df[numeric].isna().astype(int).add_prefix("missing__")


def run_ablation(df: pd.DataFrame, target: str, output_path: Path) -> None:
    base_features = validate_features(df, NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    variants = {
        "current_with_missing_indicators": {"features": base_features, "add_indicator": True, "manual_missing_flags": False},
        "all_missing_indicators_removed": {"features": base_features, "add_indicator": False, "manual_missing_flags": False},
        "total_liabilities_and_indicator_removed": {
            "features": [feature for feature in base_features if feature != "total_liabilities"],
            "add_indicator": True,
            "manual_missing_flags": False,
        },
        "economic_features_only": {"features": base_features, "add_indicator": False, "manual_missing_flags": False},
        "missing_indicators_only": {"features": base_features, "add_indicator": False, "manual_missing_flags": True},
    }
    # The single-indicator removal case is approximated with a manual missingness
    # matrix for all numeric fields except total_liabilities plus all economic values.
    variants["only_missingindicator_total_liabilities_removed"] = {
        "features": base_features,
        "add_indicator": False,
        "manual_missing_flags_except_total_liabilities": True,
    }

    rows = []
    data = modeling_frame(df, target)
    splits = split_frame(data)
    for variant_name, spec in variants.items():
        for model_name in ["logistic_l2", "random_forest", "gradient_boosting"]:
            if spec.get("manual_missing_flags"):
                x_train = make_missing_flags(splits["train"], spec["features"])
                x_val = make_missing_flags(splits["validation"], spec["features"])
                x_test = make_missing_flags(splits["test"], spec["features"])
                if model_name == "logistic_l2":
                    model = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear", random_state=42)
                elif model_name == "random_forest":
                    model = RandomForestClassifier(n_estimators=250, min_samples_leaf=5, class_weight="balanced_subsample", random_state=42, n_jobs=-1)
                else:
                    model = GradientBoostingClassifier(n_estimators=180, learning_rate=0.04, max_depth=3, random_state=42)
            elif spec.get("manual_missing_flags_except_total_liabilities"):
                flags = [
                    feature
                    for feature in spec["features"]
                    if feature in NUMERIC_FEATURES and feature != "total_liabilities"
                ]
                train_flags = make_missing_flags(splits["train"], flags)
                val_flags = make_missing_flags(splits["validation"], flags)
                test_flags = make_missing_flags(splits["test"], flags)
                econ_features = spec["features"]
                pre = build_preprocessor(econ_features, add_indicator=False)
                pre.fit(splits["train"][econ_features])
                x_train = np.hstack([pre.transform(splits["train"][econ_features]), train_flags.to_numpy()])
                x_val = np.hstack([pre.transform(splits["validation"][econ_features]), val_flags.to_numpy()])
                x_test = np.hstack([pre.transform(splits["test"][econ_features]), test_flags.to_numpy()])
                if model_name == "logistic_l2":
                    model = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear", random_state=42)
                elif model_name == "random_forest":
                    model = RandomForestClassifier(n_estimators=250, min_samples_leaf=5, class_weight="balanced_subsample", random_state=42, n_jobs=-1)
                else:
                    model = GradientBoostingClassifier(n_estimators=180, learning_rate=0.04, max_depth=3, random_state=42)
            else:
                features = spec["features"]
                x_train = splits["train"][features]
                x_val = splits["validation"][features]
                x_test = splits["test"][features]
                model = build_model(model_name, features, add_indicator=spec["add_indicator"])

            y_train = splits["train"][target].astype(int)
            y_val = splits["validation"][target].astype(int)
            y_test = splits["test"][target].astype(int)
            model.fit(x_train, y_train)
            val_proba = model.predict_proba(x_val)[:, 1]
            cutoff = threshold(y_val.to_numpy(), val_proba)
            test_proba = model.predict_proba(x_test)[:, 1]
            row = {
                "target": target,
                "variant": variant_name,
                "model": model_name,
                "train_rows": len(y_train),
                "validation_rows": len(y_val),
                "test_rows": len(y_test),
                "test_positives": int(y_test.sum()),
                "threshold": cutoff,
            }
            row.update(evaluate(y_test.to_numpy(), test_proba, cutoff))
            rows.append(row)

    pd.DataFrame(rows).to_csv(output_path, index=False)


def permutation_importance_success(df: pd.DataFrame) -> None:
    target = SUCCESS_TARGET
    data = modeling_frame(df, target)
    features = validate_features(data, NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    splits = split_frame(data)
    pre = build_preprocessor(features, add_indicator=True)
    x_train = pre.fit_transform(splits["train"][features])
    x_test = pre.transform(splits["test"][features])
    y_train = splits["train"][target].astype(int)
    y_test = splits["test"][target].astype(int)
    names = pre.get_feature_names_out()
    model = GradientBoostingClassifier(n_estimators=180, learning_rate=0.04, max_depth=3, random_state=42)
    model.fit(x_train, y_train)
    result = permutation_importance(
        model,
        x_test,
        y_test,
        scoring="average_precision",
        n_repeats=5,
        random_state=42,
        n_jobs=1,
    )
    out = pd.DataFrame(
        {
            "feature": names,
            "permutation_importance_mean": result.importances_mean,
            "permutation_importance_std": result.importances_std,
        }
    ).sort_values("permutation_importance_mean", ascending=False)
    out.to_csv(MODEL_REPORT_DIR / "success_permutation_importance.csv", index=False)


def final_diagnosis() -> None:
    ablation = pd.read_csv(MODEL_REPORT_DIR / "success_missing_indicator_ablation.csv")
    success_review = (REPORT_DIR / "success_resilience_target_definition_review.md").read_text(encoding="utf-8")
    best = ablation.sort_values("pr_auc", ascending=False).head(8)
    issue_fixed = "Status: Target issue fixed" in success_review
    target_finding = (
        "The production `success_resilience_next_4q` target has been rebuilt with missing-aware logic. The original audit finding remains important historically: before the fix, missing future leverage/liability values could be converted into non-success labels."
        if issue_fixed
        else "The current success target is vulnerable to missingness contamination because missing future leverage/liability values can make future `healthy_current` false rather than unknown."
    )
    target_recommendation = (
        "- Keep the missing-aware success target and rerun success models from the rebuilt panel."
        if issue_fixed
        else "- Revise production success target logic so missing future health components become unknown when too few future component observations exist."
    )
    lines = [
        "# Missing Indicator Total Liabilities Diagnosis",
        "",
        "## Finding",
        "",
        "`missingindicator_total_liabilities` is generated by the model preprocessing pipeline, not by the SEC panel. It is a missingness flag from `SimpleImputer(add_indicator=True)`.",
        "",
        target_finding,
        "",
        "## Best Success Missingness Ablation Rows",
        "",
        frame_as_markdown(best),
        "",
        "## Recommendation",
        "",
        target_recommendation,
        "- Keep model missingness indicators only as predictive auxiliaries after target repair.",
        "- Exclude missingness indicators from economic-factor interpretation plots.",
        "- Report missingness indicators separately as reporting/data-availability effects.",
        "",
        "## Target Review Excerpt",
        "",
        success_review,
    ]
    (REPORT_DIR / "missingindicator_total_liabilities_diagnosis.md").write_text("\n".join(lines), encoding="utf-8")


def frame_as_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    table = frame.copy()
    for col in table.columns:
        if pd.api.types.is_float_dtype(table[col]):
            table[col] = table[col].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
        else:
            table[col] = table[col].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(table.columns)
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in table.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(rows)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = add_split(load_panel())
    write_origin()
    summarize_missingness(df)
    related_fields_audit(df)
    derivation_audit(df)
    reviewed = success_target_missingness_audit(df)
    run_ablation(reviewed, SUCCESS_TARGET, MODEL_REPORT_DIR / "success_missing_indicator_ablation.csv")
    run_ablation(reviewed, DISTRESS_TARGET, MODEL_REPORT_DIR / "distress_missing_indicator_ablation.csv")
    permutation_importance_success(reviewed)
    final_diagnosis()
    print("Wrote total-liabilities missing-indicator investigation outputs")


if __name__ == "__main__":
    main()
