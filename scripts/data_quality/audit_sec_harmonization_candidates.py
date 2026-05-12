#!/usr/bin/env python3
"""Audit unmapped SEC FSD tags near thesis-critical accounting concepts.

This is a non-mutating harmonization hardening pass. It scans the raw SEC
Financial Statement Data Set ZIPs for the selected thesis universe using the
same eligibility boundary as the production builder: selected CIKs, 10-K/10-Q
forms, consolidated facts only, valid units, and `ddate == period`.

The script does not change the concept map or the production panel. It produces
candidate-tag evidence and applies strict admission rules so late-stage mapping
changes are limited to clearly equivalent accounting concepts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import re
from zipfile import ZipFile

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZIP_DIR = PROJECT_ROOT / "data/raw/sec_fsd_zips"
CONFIG_DIR = PROJECT_ROOT / "config"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"
DOCS_DIR = PROJECT_ROOT / "docs"

UNIVERSE_PATH = CONFIG_DIR / "universe_v2_draft.csv"
CONCEPT_MAP_PATH = CONFIG_DIR / "sec_fsd_concept_map.csv"

FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
VALID_UOMS = {"USD", "shares", "USD/shares", "pure"}

CRITICAL_VARIABLE_PATTERNS = {
    "total_liabilities": re.compile(r"liabilit", re.IGNORECASE),
    "debt": re.compile(
        r"debt|borrowings|notespayable|commercialpaper|financelease|capitallease",
        re.IGNORECASE,
    ),
    "total_revenue": re.compile(r"revenue|sales", re.IGNORECASE),
    "cash_flow_operating": re.compile(
        r"operatingactivities|operatingcash|cashprovidedbyusedinoperating",
        re.IGNORECASE,
    ),
    "capex": re.compile(
        r"paymentstoacquire|capitalexpenditure|propertyplantandequipment|purchaseofproperty",
        re.IGNORECASE,
    ),
    "equity": re.compile(
        r"stockholdersequity|shareholdersequity|partnerscapital|membersequity|memberscapital",
        re.IGNORECASE,
    ),
    "current_assets_liabilities": re.compile(r"assetscurrent|liabilitiescurrent", re.IGNORECASE),
    "receivables": re.compile(r"receivable", re.IGNORECASE),
    "cash_equivalents": re.compile(r"cashandcash|cashequivalents|restrictedcash", re.IGNORECASE),
    "inventory": re.compile(r"inventory", re.IGNORECASE),
}

BALANCE_VARIABLES = {
    "total_liabilities",
    "debt",
    "equity",
    "current_assets_liabilities",
    "receivables",
    "cash_equivalents",
    "inventory",
}
FLOW_VARIABLES = {"total_revenue", "cash_flow_operating", "capex"}

COMPONENT_OR_UNSAFE_PATTERNS = re.compile(
    "|".join(
        [
            "Accrued",
            "Allowance",
            "AvailableForSale",
            "Benefit",
            "Commitments",
            "Contingenc",
            "Contract",
            "Customer",
            "Deferred",
            "Derivative",
            "Discontinued",
            "FairValue",
            "FinanceLease",
            "IncomeTax",
            "Interest",
            "Lease",
            "Noncontrolling",
            "Other",
            "Pension",
            "RelatedParty",
            "Restructuring",
            "Retirement",
            "Tax",
            "TemporaryEquity",
            "TreasuryStock",
            "Unrecognized",
            "Warrant",
        ]
    ),
    re.IGNORECASE,
)

EXPLICIT_REJECT_TAGS = {
    "LiabilitiesAndStockholdersEquity": "not total liabilities; includes equity",
    "CommitmentsAndContingencies": "not an accounting amount usable as liabilities",
}


@dataclass
class TagStats:
    eligible_facts: int = 0
    firms: set[int] = field(default_factory=set)
    submissions: set[str] = field(default_factory=set)
    forms: set[str] = field(default_factory=set)
    fps: set[str] = field(default_factory=set)
    uoms: set[str] = field(default_factory=set)
    qtrs: Counter = field(default_factory=Counter)
    min_period: int | None = None
    max_period: int | None = None
    nonzero_values: int = 0
    negative_values: int = 0
    positive_values: int = 0
    stmt_contexts: set[str] = field(default_factory=set)
    labels: set[str] = field(default_factory=set)


def quarter_from_zip(path: Path) -> str:
    return path.stem.lower()


def read_universe_ciks() -> set[int]:
    universe = pd.read_csv(UNIVERSE_PATH)
    keep = universe["include_status"].isin(["include_legacy_core", "include_if_num_tags_parse"])
    universe = universe.loc[keep].copy()
    universe["cik"] = universe["cik"].astype("Int64")
    return set(universe["cik"].dropna().astype(int))


def read_sub(path: Path, selected_ciks: set[int]) -> pd.DataFrame:
    with ZipFile(path) as zf:
        with zf.open("sub.txt") as handle:
            sub = pd.read_csv(
                handle,
                sep="\t",
                dtype={
                    "adsh": "string",
                    "cik": "Int64",
                    "form": "string",
                    "period": "Int64",
                    "fy": "Int64",
                    "fp": "string",
                    "filed": "Int64",
                },
                usecols=lambda col: col in {"adsh", "cik", "form", "period", "fy", "fp", "filed"},
            )
    sub = sub[sub["cik"].isin(selected_ciks)]
    sub = sub[sub["form"].isin(FORMS)]
    sub = sub.dropna(subset=["adsh", "period"])
    sub["sec_zip"] = quarter_from_zip(path)
    return sub


def candidate_variables_for_tag(tag: str) -> list[str]:
    return [
        variable
        for variable, pattern in CRITICAL_VARIABLE_PATTERNS.items()
        if pattern.search(tag)
    ]


def read_candidate_pre_context(path: Path, adsh_values: set[str], mapped_tags: set[str]) -> dict[str, tuple[set[str], set[str]]]:
    if not adsh_values:
        return {}
    with ZipFile(path) as zf:
        with zf.open("pre.txt") as handle:
            pre = pd.read_csv(
                handle,
                sep="\t",
                dtype={"adsh": "string", "tag": "string", "stmt": "string", "plabel": "string"},
                usecols=lambda col: col in {"adsh", "tag", "stmt", "plabel"},
            )
    pre = pre[pre["adsh"].isin(adsh_values)]
    pre = pre[~pre["tag"].isin(mapped_tags)]
    pre = pre[pre["tag"].map(lambda value: bool(candidate_variables_for_tag(str(value))))]
    contexts: dict[str, tuple[set[str], set[str]]] = {}
    for tag, group in pre.groupby("tag"):
        stmt_values = set(group["stmt"].dropna().astype(str))
        labels = set(group["plabel"].dropna().astype(str).head(5))
        contexts[tag] = (stmt_values, labels)
    return contexts


def read_candidate_num_chunks(path: Path, sub: pd.DataFrame, mapped_tags: set[str]) -> pd.DataFrame:
    if sub.empty:
        return pd.DataFrame()
    sub_lookup = sub[["adsh", "cik", "form", "period", "fy", "fp", "filed", "sec_zip"]].copy()
    adsh_values = set(sub_lookup["adsh"].astype(str))
    chunks = []

    with ZipFile(path) as zf:
        with zf.open("num.txt") as handle:
            reader = pd.read_csv(
                handle,
                sep="\t",
                dtype={
                    "adsh": "string",
                    "tag": "string",
                    "ddate": "Int64",
                    "qtrs": "Int64",
                    "uom": "string",
                    "segments": "string",
                    "coreg": "string",
                    "value": "float64",
                },
                usecols=lambda col: col in {"adsh", "tag", "ddate", "qtrs", "uom", "segments", "coreg", "value"},
                chunksize=250_000,
            )
            for chunk in reader:
                chunk = chunk[chunk["adsh"].isin(adsh_values)]
                if chunk.empty:
                    continue
                chunk = chunk[~chunk["tag"].isin(mapped_tags)]
                chunk = chunk[chunk["tag"].map(lambda value: bool(candidate_variables_for_tag(str(value))))]
                if chunk.empty:
                    continue
                chunk = chunk[chunk["value"].notna()]
                chunk["segments"] = chunk["segments"].fillna("")
                chunk["coreg"] = chunk["coreg"].fillna("")
                chunk = chunk[(chunk["segments"] == "") & (chunk["coreg"] == "")]
                chunk = chunk[chunk["uom"].isin(VALID_UOMS)]
                if chunk.empty:
                    continue
                chunk = chunk.merge(sub_lookup, on="adsh", how="inner")
                chunk = chunk[chunk["ddate"].eq(chunk["period"]).fillna(False)]
                if not chunk.empty:
                    chunks.append(chunk)

    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks, ignore_index=True)


def update_stats(stats: dict[str, TagStats], num: pd.DataFrame, pre_contexts: dict[str, tuple[set[str], set[str]]]) -> None:
    for tag, group in num.groupby("tag"):
        item = stats.setdefault(str(tag), TagStats())
        item.eligible_facts += len(group)
        item.firms.update(group["cik"].dropna().astype(int).tolist())
        item.submissions.update(group["adsh"].dropna().astype(str).tolist())
        item.forms.update(group["form"].dropna().astype(str).tolist())
        item.fps.update(group["fp"].dropna().astype(str).tolist())
        item.uoms.update(group["uom"].dropna().astype(str).tolist())
        item.qtrs.update(group["qtrs"].dropna().astype(int).tolist())
        periods = group["period"].dropna().astype(int)
        if not periods.empty:
            period_min = int(periods.min())
            period_max = int(periods.max())
            item.min_period = period_min if item.min_period is None else min(item.min_period, period_min)
            item.max_period = period_max if item.max_period is None else max(item.max_period, period_max)
        values = group["value"].dropna()
        item.nonzero_values += int((values != 0).sum())
        item.negative_values += int((values < 0).sum())
        item.positive_values += int((values > 0).sum())

    for tag, (stmts, labels) in pre_contexts.items():
        item = stats.setdefault(str(tag), TagStats())
        item.stmt_contexts.update(stmts)
        item.labels.update(labels)


def qtrs_share(item: TagStats, qtrs_value: int) -> float:
    total = sum(item.qtrs.values())
    if total == 0:
        return 0.0
    return item.qtrs.get(qtrs_value, 0) / total


def classify_candidate(tag: str, variable: str, item: TagStats) -> tuple[str, str]:
    if tag in EXPLICIT_REJECT_TAGS:
        return "REJECT", EXPLICIT_REJECT_TAGS[tag]

    stmt_contexts = item.stmt_contexts
    qtrs0 = qtrs_share(item, 0)
    flow_qtrs = sum(count for qtrs, count in item.qtrs.items() if qtrs in {1, 2, 3, 4})
    qtrs_total = sum(item.qtrs.values())
    flow_share = flow_qtrs / qtrs_total if qtrs_total else 0.0

    if variable in BALANCE_VARIABLES:
        if qtrs_total and qtrs0 < 0.95:
            return "REJECT", "balance-sheet candidate does not mostly use qtrs=0"
        if stmt_contexts and not (stmt_contexts & {"BS", "EQ"}):
            return "REJECT", f"balance-sheet candidate appears outside BS/EQ contexts: {sorted(stmt_contexts)}"

    if variable in FLOW_VARIABLES:
        if qtrs_total and flow_share < 0.95:
            return "REJECT", "flow candidate does not mostly use qtrs in 1..4"
        expected_stmt = {"total_revenue": "IS", "cash_flow_operating": "CF", "capex": "CF"}[variable]
        if stmt_contexts and expected_stmt not in stmt_contexts:
            return "REJECT", f"flow candidate lacks expected {expected_stmt} statement context: {sorted(stmt_contexts)}"

    if COMPONENT_OR_UNSAFE_PATTERNS.search(tag):
        return "REJECT", "tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept"

    if variable == "total_liabilities" and tag != "Liabilities":
        return "REJECT", "no broad direct total-liabilities synonym; use reported Liabilities only"

    if variable == "current_assets_liabilities":
        return "REJECT", "current assets/liabilities direct tags are already mapped; remaining tags are variants/components"

    if variable == "cash_flow_operating" and tag != "NetCashProvidedByUsedInOperatingActivities":
        return "REVIEW_ONLY", "possible operating-cash-flow variant, but not promoted without row-level statement review"

    if variable == "total_revenue":
        return "REVIEW_ONLY", "possible revenue fallback, but requires manual sector/tag review before any mapping change"

    if variable == "capex":
        return "REVIEW_ONLY", "possible capex fallback, but component/non-cash variants must not be mapped directly"

    return "REVIEW_ONLY", "near critical concept but not accepted by strict automated rules"


def build_rows(stats: dict[str, TagStats]) -> pd.DataFrame:
    rows = []
    for tag, item in sorted(stats.items()):
        variables = candidate_variables_for_tag(tag)
        if item.eligible_facts == 0:
            continue
        for variable in variables:
            status, reason = classify_candidate(tag, variable, item)
            rows.append(
                {
                    "tag": tag,
                    "candidate_variable": variable,
                    "strict_admission_status": status,
                    "strict_admission_reason": reason,
                    "eligible_facts": item.eligible_facts,
                    "firms": len(item.firms),
                    "submissions": len(item.submissions),
                    "forms": ";".join(sorted(item.forms)),
                    "fps": ";".join(sorted(item.fps)),
                    "uoms": ";".join(sorted(item.uoms)),
                    "qtrs_distribution": ";".join(f"{key}:{value}" for key, value in sorted(item.qtrs.items())),
                    "stmt_contexts": ";".join(sorted(item.stmt_contexts)),
                    "sample_labels": " | ".join(sorted(item.labels)[:5]),
                    "first_period": item.min_period,
                    "last_period": item.max_period,
                    "positive_values": item.positive_values,
                    "negative_values": item.negative_values,
                    "nonzero_values": item.nonzero_values,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["strict_admission_status", "candidate_variable", "eligible_facts", "firms"],
        ascending=[True, True, False, False],
    )


def write_summary_doc(candidate_rows: pd.DataFrame, summary: pd.DataFrame) -> None:
    top_rejects = (
        candidate_rows[candidate_rows["strict_admission_status"].eq("REJECT")]
        .sort_values(["eligible_facts", "firms"], ascending=False)
        .head(15)
    )
    review_rows = candidate_rows[candidate_rows["strict_admission_status"].eq("REVIEW_ONLY")]
    top_review = review_rows.sort_values(["eligible_facts", "firms"], ascending=False).head(15)

    lines = [
        "# SEC Harmonization Hardening Review 2026-05-12",
        "",
        "This is a non-mutating audit. It scans unmapped SEC Financial Statement Data Set tags near thesis-critical accounting concepts and applies strict admission rules before any concept-map change.",
        "",
        "## Scope",
        "",
        "- Selected thesis-universe CIKs only.",
        "- 10-K, 10-K/A, 10-Q, and 10-Q/A filings only.",
        "- Consolidated facts only: empty `segments` and empty `coreg`.",
        "- Valid production units only: USD, shares, USD/shares, or pure.",
        "- Current-period facts only: `ddate == period`.",
        "- No production panel, model output, or concept-map file was changed.",
        "",
        "## Strict Admission Rules",
        "",
        "- Candidate tags must have the same economic meaning as the canonical variable.",
        "- Balance-sheet candidates must mostly use `qtrs = 0` and appear in balance/equity statement contexts.",
        "- Flow candidates must mostly use `qtrs` 1 through 4 and appear in the expected income-statement or cash-flow context.",
        "- Component, tax, lease, fair-value, related-party, deferred, other, sector-specific, or non-total tags are rejected as direct mappings.",
        "- `LiabilitiesAndStockholdersEquity` remains rejected as a `total_liabilities` substitute.",
        "- Review-only means not accepted for direct promotion; it only identifies candidates for possible manual row-level accounting review.",
        "- Ambiguous revenue, capex, debt, restricted-cash, receivable, and operating-cash-flow variants are review-only or rejected, not automatic additions.",
        "",
        "## Status Summary",
        "",
        markdown_table(summary),
        "",
        "## Top Review-Only Candidates",
        "",
    ]
    if top_review.empty:
        lines.append("No review-only candidates were found under the current filters.")
    else:
        lines.append(markdown_table(top_review[report_cols()]))

    lines.extend(["", "## Top Rejected Candidates", ""])
    if top_rejects.empty:
        lines.append("No rejected candidates were found under the current filters.")
    else:
        lines.append(markdown_table(top_rejects[report_cols()]))

    lines.extend(
        [
            "",
            "## Decision Boundary",
            "",
            "No unmapped tag was accepted automatically by this audit. Any future addition should be treated as a new controlled data-engineering change, not as a documentation-only correction.",
            "",
            "This audit is designed to identify whether a late-stage harmonization improvement is worth a full rebuild. A candidate should only be promoted if it survives manual row-level review and the full downstream acceptance chain: panel rebuild, selected-fact provenance, P0 audits, target profiles, model consistency, calibration/ranking, dashboard screenshots, and source-of-truth refresh.",
            "",
            "Current thesis-safe position remains: SEC concept mapping is conservative, audited, and closer to harmonized after review, but not perfect taxonomy harmonization.",
            "",
        ]
    )
    (DOCS_DIR / "SEC_HARMONIZATION_HARDENING_REVIEW_20260512.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def report_cols() -> list[str]:
    return [
        "tag",
        "candidate_variable",
        "eligible_facts",
        "firms",
        "stmt_contexts",
        "qtrs_distribution",
        "strict_admission_reason",
    ]


def markdown_table(df: pd.DataFrame) -> str:
    """Render a small Markdown table without the optional tabulate package."""
    if df.empty:
        return ""
    clean = df.copy().fillna("")
    columns = list(clean.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in clean.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "/") for col in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    concept_map = pd.read_csv(CONCEPT_MAP_PATH)
    mapped_tags = set(concept_map["tag"].astype(str))
    selected_ciks = read_universe_ciks()
    zip_paths = sorted(path for path in ZIP_DIR.glob("*.zip") if path.name[:4].isdigit())
    stats: dict[str, TagStats] = {}

    for index, path in enumerate(zip_paths, start=1):
        sub = read_sub(path, selected_ciks)
        if sub.empty:
            continue
        adsh_values = set(sub["adsh"].astype(str))
        pre_contexts = read_candidate_pre_context(path, adsh_values, mapped_tags)
        num = read_candidate_num_chunks(path, sub, mapped_tags)
        if not num.empty or pre_contexts:
            update_stats(stats, num, pre_contexts)
        if index % 10 == 0:
            print(f"Audited {index}/{len(zip_paths)} ZIPs")

    candidate_rows = build_rows(stats)
    candidate_path = REPORT_DIR / "sec_harmonization_candidate_tag_audit.csv"
    candidate_rows.to_csv(candidate_path, index=False)

    summary = (
        candidate_rows.groupby(["candidate_variable", "strict_admission_status"], dropna=False)
        .agg(
            tags=("tag", "nunique"),
            eligible_facts=("eligible_facts", "sum"),
            max_firms=("firms", "max"),
        )
        .reset_index()
        .sort_values(["candidate_variable", "strict_admission_status"])
    )
    summary_path = REPORT_DIR / "sec_harmonization_candidate_summary.csv"
    summary.to_csv(summary_path, index=False)
    write_summary_doc(candidate_rows, summary)

    print(f"Wrote {candidate_path.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {summary_path.relative_to(PROJECT_ROOT)}")
    print("Wrote docs/SEC_HARMONIZATION_HARDENING_REVIEW_20260512.md")


if __name__ == "__main__":
    main()
