# SEC Concept Mapping Audit

Updated: 2026-05-10

This audit documents the SEC Financial Statement Data Set concept mapping used for thesis-critical accounting variables. It does not claim perfect accounting taxonomy across all firms and industries; it documents conservative tag choices, coverage, and caveats.

## Outputs

- `reports/data_quality/sec_concept_mapping_summary.csv`
- `reports/data_quality/sec_concept_coverage_by_year_form_sector.csv`
- `reports/data_quality/accounting_identity_sanity_summary.csv`
- `reports/data_quality/extreme_accounting_outlier_review.csv`

## Highest Missingness Among Key Concepts

- `noncurrent_liabilities`: missing share 0.872; mapped tags: LiabilitiesNoncurrent.
- `r_and_d_expense`: missing share 0.730; mapped tags: ResearchAndDevelopmentExpense; ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost; ResearchAndDevelopmentCost; ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost.
- `gross_profit`: missing share 0.698; mapped tags: GrossProfit.
- `sg_and_a`: missing share 0.509; mapped tags: SellingGeneralAndAdministrativeExpense.
- `inventory`: missing share 0.468; mapped tags: InventoryNet.
- `short_term_debt`: missing share 0.390; mapped tags: DebtCurrent; LongTermDebtCurrent; LongTermDebtAndCapitalLeaseObligationsCurrent; ShortTermBorrowings.
- `capex`: missing share 0.352; mapped tags: PaymentsToAcquirePropertyPlantAndEquipment; CapitalExpenditures.
- `total_liabilities`: missing share 0.327; mapped tags: Liabilities.

## Method Caveats

- SEC tags differ across firms, years, industries, and filer practices.
- Flow variables may be reported as current-quarter or cumulative values; the build pipeline standardizes flows before panel output.
- Row-level `value_method` is retained in the selected-fact provenance sidecar; the final panel stores selected standardized values only.
- Outliers are reported for interpretation and review, not silently deleted.
- Missing values remain missing unless deterministic transformations in the build pipeline create ratios or lags from available inputs.

## Thesis Wording

Use: "Accounting variables were mapped from SEC FSD tags using a documented concept map and audited for coverage, qtrs patterns, missingness, accounting identity plausibility, and extreme values."

Do not use: "All SEC accounting tags are perfectly harmonized across all firms and years."
