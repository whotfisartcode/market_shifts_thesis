# SEC Mapping Polish 2026-05-09

This note documents the final SEC concept-map improvement pass. It is thesis-facing evidence and should be read together with `docs/SEC_CONCEPT_MAPPING_AUDIT.md`, `reports/data_quality/sec_selected_fact_provenance.parquet`, `reports/data_quality/sec_selected_fact_provenance.csv.gz`, and `reports/data_quality/sec_selected_fact_provenance_summary.csv`.

## Official Basis

The mapping policy follows the SEC Financial Statement Data Sets documentation:

- SEC FSD data are extracted from XBRL submissions and provided as flattened tab-delimited data sets.
- The data are "as filed" by registrants and are not guaranteed by the SEC to be error-free or complete.
- `NUM` rows contain numeric facts with `ddate`, `qtrs`, `uom`, `segments`, `coreg`, and `value`.
- `qtrs = 0` is used for point-in-time facts, while positive `qtrs` values describe duration facts.
- The 2024 reprocessing note says the newer Financial Statement Data Sets use rendered primary-statement data and include the `segments` field in `NUM`.

Sources:

- SEC Financial Statement Data Sets page: https://www.sec.gov/dera/data/financial-statement-data-sets.html
- SEC Financial Statement Data Sets documentation PDF: https://www.sec.gov/files/financial-statement-data-sets.pdf

## What Changed

The concept map was expanded conservatively:

| Variable | Added tags | Reason |
| --- | --- | --- |
| `long_term_debt` | `LongTermDebtNoncurrent`; `LongTermDebtAndCapitalLeaseObligations` | These are common balance-sheet debt tags and materially improve debt coverage. |
| `short_term_debt` | `DebtCurrent`; `LongTermDebtCurrent`; `LongTermDebtAndCapitalLeaseObligationsCurrent` | These better capture current debt/current maturities than only `ShortTermBorrowings`. |
| `noncurrent_liabilities` | `LiabilitiesNoncurrent` | Added as a separate field, not as a replacement for total liabilities. |
| `accounts_receivable` | `ReceivablesNetCurrent`; `AccountsReceivableNet` | Current/broad receivables fallbacks improve receivables coverage. |
| `r_and_d_expense` | `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost` | Conservative R&D fallback. |
| `total_revenue` | `RevenueFromContractWithCustomerIncludingAssessedTax` | Low-priority fallback when cleaner revenue tags are absent. |

## What Was Deliberately Not Changed

- `LiabilitiesAndStockholdersEquity` was not mapped to `total_liabilities`; it is not total liabilities.
- `total_liabilities` was not silently filled as `Assets - Equity`; previous feasibility checks showed too many mismatches for that to be treated as reported truth.
- Component inventory tags were not summed into `inventory`.
- Component capex tags such as `CapitalExpendituresIncurredButNotYetPaid` were not treated as cash capex.
- Industry-specific or component revenue tags were not broadly promoted into total revenue.

## Coverage Effect

After rebuilding the panel:

- `long_term_debt` missingness improved to 27.1%;
- `short_term_debt` missingness improved to 39.0%;
- `accounts_receivable` missingness improved to 24.8%;
- `r_and_d_expense` missingness improved to 73.0%;
- `total_revenue` missingness improved to 10.6%.

The SEC mapping-polish rebuild initially produced 31,717 rows, 186 columns, 540 CIKs, and 540 ticker/display IDs. A later 2026-05-09 caveat-resolution rebuild applied deterministic same-information-date duplicate handling and source-aware accounting null controls; the 2026-05-10 validated-secondary target promotion preserved 31,702 rows and increased the current production panel to 190 columns.

## Validation Result

Post-polish validation:

- P0 audits: all PASS;
- selected SEC facts: 700,844;
- selected facts with `ddate != period`: 0;
- selected-value mismatches above tolerance: 0;
- documented panel-comparison exclusions: 25;
- numeric infinities: 0.

## Thesis-Safe Wording

Use:

"SEC accounting variables were mapped through a documented concept map, filtered to current-period facts (`ddate = period`), standardized for flow-period reporting, and audited with a row-level selected-fact provenance sidecar."

Do not use:

"The SEC mapping is perfect" or "all accounting values are fully harmonized across all firms and years."
