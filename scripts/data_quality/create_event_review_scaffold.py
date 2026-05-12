#!/usr/bin/env python3
"""Create event-date provenance and event-review classification scaffolds.

The script does not change target labels or `config/distress_event_dates.csv`.
It makes the remaining manual verification work explicit.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = PROJECT_ROOT / "config/universe_v2_draft.csv"
EVENT_DATES_PATH = PROJECT_ROOT / "config/distress_event_dates.csv"
CURRENT_AUDIT_PATH = PROJECT_ROOT / "reports/data_quality/distress_event_date_audit.csv"
OUT_DIR = PROJECT_ROOT / "reports/data_quality"


KNOWN_TRANSACTION_HINTS = {
    "ACTIVISION BLIZZARD": "merger_acquisition_candidate",
    "VMWARE": "merger_acquisition_candidate",
    "PIONEER NATURAL RESOURCES": "merger_acquisition_candidate",
    "HAWAIIAN HOLDINGS": "merger_acquisition_candidate",
    "CEDAR FAIR": "merger_acquisition_candidate",
    "WORLD WRESTLING": "merger_acquisition_candidate",
    "CITRIX": "merger_acquisition_candidate",
    "KANSAS CITY SOUTHERN": "merger_acquisition_candidate",
    "CIMAREX": "merger_acquisition_candidate",
    "VONAGE": "merger_acquisition_candidate",
    "COVANTA": "merger_acquisition_candidate",
}

DISTRESS_HINTS = {
    "RITE AID": "formal_distress_candidate",
    "SUNPOWER": "formal_distress_candidate",
    "ACORDA": "formal_distress_candidate",
    "PENNSYLVANIA REAL ESTATE": "formal_distress_candidate",
    "CONNS": "formal_distress_candidate",
    "EBIX": "formal_distress_candidate",
    "VERTEX ENERGY": "formal_distress_candidate",
    "UNIT CORP": "formal_distress_candidate",
}


VERIFIED_EVENT_SOURCES = {
    "RITE AID": {
        "event_date": "2023-10-15",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://www.sec.gov/Archives/edgar/data/84129/000155837023016503/rad-20230902x10q.htm",
        "source_title": "Rite Aid Form 10-Q disclosure of voluntary Chapter 11 petitions",
    },
    "SUNPOWER": {
        "event_date": "2024-08-05",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://docs.justia.com/cases/federal/district-courts/new-york/nysdce/1%3A2023cv05627/601416/28",
        "source_title": "Court order noting SunPower Chapter 11 petitions filed August 5, 2024",
    },
    "ACORDA": {
        "event_date": "2024-04-01",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1008848/000095017024039674/acor-20240331.htm",
        "source_title": "Acorda Therapeutics Form 8-K bankruptcy disclosure",
    },
    "PENNSYLVANIA REAL ESTATE": {
        "event_date": "2023-12-10",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://www.preit.com/restructuring/",
        "source_title": "PREIT restructuring page describing Chapter 11 petition",
    },
    "CONNS": {
        "event_date": "2024-07-23",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://www.sidley.com/en/newslanding/newsannouncements/2025/08/sidley-secures-confirmation-of-conn-chapter-11-plan",
        "source_title": "Sidley announcement noting Conn's Chapter 11 filing date",
    },
    "EBIX": {
        "event_date": "2023-12-17",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://www.sidley.com/en/newslanding/newsannouncements/2023/12/sidley-represents-software-company-ebix-in-chapter-11-filing",
        "source_title": "Sidley announcement noting Ebix Chapter 11 filing date",
    },
    "VERTEX ENERGY": {
        "event_date": "2024-09-24",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://www.sec.gov/Archives/edgar/data/890447/000199937125000470/vtnrq_8k-012125.htm",
        "source_title": "Vertex Energy Form 8-K disclosure of Chapter 11 petitions",
    },
    "UNIT CORP": {
        "event_date": "2020-05-22",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_url": "https://unitcorp.com/restructuring/",
        "source_title": "Unit Corporation restructuring page describing Chapter 11 filing",
    },
}


def classify_review_row(row: pd.Series) -> tuple[str, str]:
    text = " ".join(
        str(row.get(col, ""))
        for col in ["ticker", "shortname", "sec_name", "notes"]
        if pd.notna(row.get(col, ""))
    ).upper()

    for pattern, label in DISTRESS_HINTS.items():
        if pattern in text:
            return label, "local_name_hint_requires_source_verification"

    for pattern, label in KNOWN_TRANSACTION_HINTS.items():
        if pattern in text:
            return label, "local_name_hint_likely_transaction_requires_source_verification"

    return "uncertain_review", "coverage_ended_requires_manual_source_review"


def find_verified_source(row: pd.Series) -> dict[str, str] | None:
    text = " ".join(
        str(row.get(col, ""))
        for col in ["ticker", "shortname", "sec_name", "notes"]
        if pd.notna(row.get(col, ""))
    ).upper()
    for pattern, payload in VERIFIED_EVENT_SOURCES.items():
        if pattern in text:
            return payload
    return None


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    universe = pd.read_csv(UNIVERSE_PATH)
    events = pd.read_csv(EVENT_DATES_PATH, parse_dates=["event_date"])
    configured_event_keys = set(
        zip(events["ticker"].astype(str), events["event_date"].dt.strftime("%Y-%m-%d"))
    )

    event_review = universe[universe["cohort"].eq("expansion_event_review")].copy()
    classifications = event_review.apply(classify_review_row, axis=1, result_type="expand")
    event_review["provisional_event_class"] = classifications[0]
    event_review["classification_basis"] = classifications[1]
    event_review["source_url"] = pd.NA
    event_review["source_title"] = pd.NA
    event_review["source_checked_date"] = "2026-05-05"
    event_review["recommended_event_date"] = pd.NA
    event_review["recommended_event_type"] = pd.NA
    event_review["recommended_event_label"] = pd.NA
    event_review["manual_review_status"] = "needs_source_review"
    event_review["strict_distress_label_action"] = "do_not_label_until_verified"

    for index, row in event_review.iterrows():
        source = find_verified_source(row)
        if not source:
            continue
        event_review.loc[index, "provisional_event_class"] = "formal_distress_source_verified"
        event_review.loc[index, "classification_basis"] = "external_source_review_2026_05_05"
        event_review.loc[index, "source_url"] = source["source_url"]
        event_review.loc[index, "source_title"] = source["source_title"]
        event_review.loc[index, "recommended_event_date"] = source["event_date"]
        event_review.loc[index, "recommended_event_type"] = source["event_type"]
        event_review.loc[index, "recommended_event_label"] = source["event_label"]
        event_key = (str(row["ticker"]), source["event_date"])
        if event_key in configured_event_keys:
            event_review.loc[index, "provisional_event_class"] = "formal_distress_source_verified_in_config"
            event_review.loc[index, "manual_review_status"] = "source_verified_in_config"
            event_review.loc[index, "strict_distress_label_action"] = "already_added_to_config"
        else:
            event_review.loc[index, "manual_review_status"] = "source_verified_candidate"
            event_review.loc[index, "strict_distress_label_action"] = "candidate_to_add_after_production_decision"

    review_cols = [
        "ticker",
        "cik",
        "shortname",
        "sec_name",
        "Sector",
        "Industry",
        "first_period",
        "last_period",
        "provisional_event_class",
        "classification_basis",
        "source_url",
        "source_title",
        "source_checked_date",
        "recommended_event_date",
        "recommended_event_type",
        "recommended_event_label",
        "manual_review_status",
        "strict_distress_label_action",
        "notes",
    ]
    event_review[review_cols].to_csv(OUT_DIR / "event_review_firm_classification_scaffold.csv", index=False)

    current_audit = pd.read_csv(CURRENT_AUDIT_PATH) if CURRENT_AUDIT_PATH.exists() else pd.DataFrame()
    provenance = events.copy()
    provenance["source_url"] = pd.NA
    provenance["source_title"] = pd.NA
    provenance["source_checked_date"] = pd.NA
    provenance["manual_review_status"] = provenance["verification_status"].map(
        lambda status: "needs_source_review" if status == "initial_seed" else "reviewed"
    )
    provenance["strict_distress_label_action"] = "not_strict_formal_distress"
    provenance.loc[
        provenance["event_label"].eq("formal_distress") & provenance["verification_status"].eq("initial_seed"),
        "strict_distress_label_action",
    ] = "eligible_if_source_verified"
    provenance.loc[
        provenance["event_label"].eq("formal_distress") & provenance["verification_status"].ne("initial_seed"),
        "strict_distress_label_action",
    ] = "included_in_strict_distress_label"

    if not current_audit.empty:
        audit_cols = ["ticker", "panel_rows", "distress_next_4q_rows", "post_event_rows", "issues"]
        merge_cols = [col for col in audit_cols if col in current_audit.columns]
        provenance = provenance.merge(current_audit[merge_cols], on="ticker", how="left")

    provenance.to_csv(OUT_DIR / "final_distress_event_date_audit.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "item": "existing_event_rows",
                "count": len(events),
                "status": "needs_source_review_for_initial_seed_rows",
            },
            {
                "item": "event_review_expansion_firms",
                "count": len(event_review),
                "status": "not_labeled_until_verified",
            },
            {
                "item": "provisional_formal_distress_candidates",
                "count": int(event_review["provisional_event_class"].eq("formal_distress_candidate").sum()),
                "status": "requires_external_source",
            },
            {
                "item": "source_verified_formal_distress_candidates",
                "count": int(event_review["manual_review_status"].eq("source_verified_candidate").sum()),
                "status": "ready_for_config_update_after_production_decision",
            },
            {
                "item": "source_verified_formal_distress_in_config",
                "count": int(event_review["manual_review_status"].eq("source_verified_in_config").sum()),
                "status": "already_added_to_strict_event_date_config",
            },
            {
                "item": "provisional_merger_or_transaction_candidates",
                "count": int(event_review["provisional_event_class"].eq("merger_acquisition_candidate").sum()),
                "status": "do_not_label_as_distress_without_source_evidence",
            },
        ]
    )
    summary.to_csv(OUT_DIR / "event_review_scaffold_summary.csv", index=False)

    print(f"Wrote {len(event_review):,} event-review classification scaffold rows")
    print(f"Wrote {len(provenance):,} distress event provenance rows")


if __name__ == "__main__":
    main()
