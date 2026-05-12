# PCG / PGNPQ Duplicate CIK Note

Updated: 2026-05-08

Current status note, 2026-05-12: the alias-collapse finding remains resolved in the current 31,702 x 190 production panel. The original target-recompute check covered the three primary production targets at the time of the fix; current model-output consistency checks pass for all seven production targets after validated-secondary target promotion.

## Finding

The 2026-05-08 manual audit found one duplicated SEC CIK mapped to two ticker/display IDs:

| cik | ticker/display IDs | issue |
| --- | --- | --- |
| 1004980 | `PCG`, `PGNPQ` | Same SEC filings duplicated as two firm histories; `PGNPQ` has the formal 2019 distress label while parallel `PCG` rows do not. |

This is not a broad universe problem. It affects one CIK, but it matters because it creates contradictory labels for identical firm-period accounting features.

## Why It Happened

`PCG` existed in the legacy/core large-cap universe. `PGNPQ` was also added as a distress candidate for the 2019 PG&E bankruptcy event. Both rows point to the same SEC CIK, so the universe-to-panel merge duplicated the same SEC filing history under two ticker/display IDs.

## Scientific Impact Before Fix

- Row count is inflated by 67 duplicated firm-period rows.
- Strict distress labels conflict across duplicated rows before the 2019 event.
- One failure-pressure target recomputation mismatch is caused by this duplicated CIK sequence.
- Temporal split and leakage controls still pass, but the panel is not perfectly firm-unique.

## Implemented Code-Level Fix

The panel builder now applies the intended policy before SEC parsing:

- `PCG` remains the primary display ticker for `CIK 1004980`;
- `PGNPQ` is preserved in `ticker_aliases` and `event_lookup_tickers`;
- target construction searches event dates across ticker aliases, so the `PGNPQ` formal bankruptcy event is inherited by the single `PCG`/CIK history;
- the alias policy writes `reports/data_quality/duplicate_cik_alias_resolution.csv` during the panel rebuild.

Validation after rebuild:

- universe after alias collapse has 540 rows and 540 CIKs;
- `CIK 1004980` has `ticker = PCG`, `ticker_aliases = PCG;PGNPQ`, and `event_lookup_tickers = PCG;PGNPQ`;
- targeted target-logic validation on the single `PCG` history attaches `event_source_ticker = PGNPQ`, `event_date = 2019-01-29`, and source-verified formal distress metadata;
- the same targeted validation yields 67 single-history rows, 5 strict `distress_next_4q` positives, and 29 post-event rows for `CIK 1004980`;
- production Parquet/CSV exports now include this fix after the 2026-05-08 rebuild;
- the current production panel has 540 CIKs and 540 ticker/display IDs;
- target recomputation had 0 mismatches across the three primary production targets at the alias-collapse checkpoint.
- current model-output consistency has 0 best-model mismatches across all seven production targets.

Completed follow-up action:

1. Temporal models were rerun.
2. Feature-group interpretation, dashboard screenshots, rendered dashboard audit, and final documentation metrics were refreshed.

## Thesis Wording

Safe caveat:

> One CIK-level ticker/display duplication (`PCG`/`PGNPQ`) was identified during final audit. The production builder now collapses the duplicate into one `PCG`/CIK history while preserving `PGNPQ` as alias/event-source metadata for the 2019 PG&E bankruptcy event. This is disclosed as an alias-handling control rather than treated as a remaining label inconsistency.

Unsafe wording:

> Every ticker alias in the source universe is a separate economic firm.
