# SEC Harmonization Hardening Review 2026-05-12

This is a non-mutating audit. It scans unmapped SEC Financial Statement Data Set tags near thesis-critical accounting concepts and applies strict admission rules before any concept-map change.

## Scope

- Selected thesis-universe CIKs only.
- 10-K, 10-K/A, 10-Q, and 10-Q/A filings only.
- Consolidated facts only: empty `segments` and empty `coreg`.
- Valid production units only: USD, shares, USD/shares, or pure.
- Current-period facts only: `ddate == period`.
- No production panel, model output, or concept-map file was changed.

## Strict Admission Rules

- Candidate tags must have the same economic meaning as the canonical variable.
- Balance-sheet candidates must mostly use `qtrs = 0` and appear in balance/equity statement contexts.
- Flow candidates must mostly use `qtrs` 1 through 4 and appear in the expected income-statement or cash-flow context.
- Component, tax, lease, fair-value, related-party, deferred, other, sector-specific, or non-total tags are rejected as direct mappings.
- `LiabilitiesAndStockholdersEquity` remains rejected as a `total_liabilities` substitute.
- Review-only means not accepted for direct promotion; it only identifies candidates for possible manual row-level accounting review.
- Ambiguous revenue, capex, debt, restricted-cash, receivable, and operating-cash-flow variants are review-only or rejected, not automatic additions.

## Status Summary

| candidate_variable | strict_admission_status | tags | eligible_facts | max_firms |
| --- | --- | --- | --- | --- |
| capex | REJECT | 305 | 39040 | 222 |
| capex | REVIEW_ONLY | 371 | 56915 | 433 |
| cash_equivalents | REJECT | 325 | 59317 | 507 |
| cash_equivalents | REVIEW_ONLY | 51 | 11466 | 133 |
| cash_flow_operating | REJECT | 64 | 12980 | 195 |
| cash_flow_operating | REVIEW_ONLY | 71 | 9118 | 304 |
| current_assets_liabilities | REJECT | 143 | 71106 | 289 |
| debt | REJECT | 1765 | 133211 | 377 |
| debt | REVIEW_ONLY | 243 | 12313 | 39 |
| equity | REJECT | 163 | 38639 | 540 |
| equity | REVIEW_ONLY | 36 | 2054 | 11 |
| inventory | REJECT | 143 | 3650 | 54 |
| inventory | REVIEW_ONLY | 69 | 6652 | 34 |
| receivables | REJECT | 850 | 70774 | 315 |
| receivables | REVIEW_ONLY | 180 | 11555 | 52 |
| total_liabilities | REJECT | 1680 | 230971 | 540 |
| total_revenue | REJECT | 849 | 74570 | 189 |
| total_revenue | REVIEW_ONLY | 460 | 27357 | 41 |

## Top Review-Only Candidates

| tag | candidate_variable | eligible_facts | firms | stmt_contexts | qtrs_distribution | strict_admission_reason |
| --- | --- | --- | --- | --- | --- | --- |
| PaymentsToAcquireBusinessesNetOfCashAcquired | capex | 13214 | 433 | CF;UN | 0:1;1:2579;2:3075;3:3435;4:4116;5:3;6:3;7:2 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| ProceedsFromSaleOfPropertyPlantAndEquipment | capex | 7354 | 272 | BS;CF;UN | 0:2;1:1609;2:1754;3:1858;4:2129;9:1;10:1 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| PaymentsToAcquireProductiveAssets | capex | 5984 | 153 | CF;IS;UN | 1:1616;2:1442;3:1432;4:1487;5:1;6:2;7:1;8:1;9:1;10:1 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | cash_flow_operating | 5859 | 304 | CF;CI;IS;UN | 1:1437;2:1411;3:1458;4:1552;29:1 | possible operating-cash-flow variant, but not promoted without row-level statement review |
| PaymentsToAcquireInvestments | capex | 4674 | 181 | CF;UN | 1:1106;2:1145;3:1179;4:1244 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| CapitalExpendituresIncurredButNotYetPaid | capex | 4035 | 157 | BS;CF;UN | 0:1;1:1009;2:975;3:981;4:1069 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| PaymentsToAcquireMarketableSecurities | capex | 2911 | 109 | CF;UN | 1:709;2:692;3:709;4:801 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| RestrictedCashAndCashEquivalentsAtCarryingValue | cash_equivalents | 2906 | 133 | BS;CF;UN | 0:2906 | near critical concept but not accepted by strict automated rules |
| PaymentsToAcquireIntangibleAssets | capex | 2656 | 128 | BS;CF;UN | 0:1;1:594;2:616;3:657;4:770;17:2;18:2;19:2;20:2;21:3;22:1;24:1;25:1;26:1;27:1;28:1;29:1 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| PaymentsToAcquireEquityMethodInvestments | capex | 2030 | 135 | CF;UN | 0:1;1:402;2:470;3:530;4:627 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| PaymentsToAcquireShortTermInvestments | capex | 1973 | 97 | CF;UN | 1:473;2:458;3:478;4:564 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| RestrictedCashAndCashEquivalents | cash_equivalents | 1971 | 90 | BS;CF;IS;UN | 0:1971 | near critical concept but not accepted by strict automated rules |
| PaymentsToAcquireHeldToMaturitySecurities | capex | 1539 | 60 | CF | 1:328;2:383;3:397;4:431 | possible capex fallback, but component/non-cash variants must not be mapped directly |
| RestrictedCashAndCashEquivalentsNoncurrent | cash_equivalents | 1188 | 79 | BS;CF;UN | 0:1188 | near critical concept but not accepted by strict automated rules |
| AccountsNotesAndLoansReceivableNetCurrent | receivables | 1071 | 26 | BS;CF;UN | 0:1071 | near critical concept but not accepted by strict automated rules |

## Top Rejected Candidates

| tag | candidate_variable | eligible_facts | firms | stmt_contexts | qtrs_distribution | strict_admission_reason |
| --- | --- | --- | --- | --- | --- | --- |
| LiabilitiesAndStockholdersEquity | equity | 31604 | 540 | BS;IS;UN | 0:31604 | not total liabilities; includes equity |
| LiabilitiesAndStockholdersEquity | total_liabilities | 31604 | 540 | BS;IS;UN | 0:31604 | not total liabilities; includes equity |
| OtherLiabilitiesNoncurrent | total_liabilities | 22360 | 429 | BS;IS;UN | 0:22360 | tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept |
| CashAndCashEquivalentsPeriodIncreaseDecrease | cash_equivalents | 16182 | 501 | CF;UN | 1:3987;2:4065;3:4005;4:4072;5:1;6:1;7:1;9:1;10:4;11:2;12:4;13:3;14:2;15:2;16:2;17:2;18:2;19:2;20:3;21:3;22:2;23:1;24:1;25:2;26:2;27:3;28:5;30:1;31:1 | balance-sheet candidate does not mostly use qtrs=0 |
| IncreaseDecreaseInAccountsReceivable | receivables | 14951 | 315 | BS;CF;IS;UN | 0:2;1:3687;2:3627;3:3590;4:4027;10:2;11:1;12:3;13:2;14:1;15:1;16:1;17:1;18:1;19:1;20:1;21:1;30:1;31:1 | balance-sheet candidate does not mostly use qtrs=0 |
| OtherAssetsCurrent | current_assets_liabilities | 13546 | 289 | BS;CF;IS;UN | 0:13546 | tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept |
| RepaymentsOfLongTermDebt | debt | 13361 | 356 | CF;UN | 0:5;1:2989;2:3292;3:3419;4:3656 | balance-sheet candidate does not mostly use qtrs=0 |
| CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect | cash_equivalents | 13140 | 507 | BS;CF;UN | 0:1;1:3384;2:3238;3:3243;4:3274 | balance-sheet candidate does not mostly use qtrs=0 |
| ProceedsFromIssuanceOfLongTermDebt | debt | 11600 | 377 | CF;UN | 0:3;1:2217;2:2766;3:3070;4:3544 | balance-sheet candidate does not mostly use qtrs=0 |
| AccruedLiabilitiesCurrent | current_assets_liabilities | 10541 | 242 | BS;UN | 0:10541 | tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept |
| AccruedLiabilitiesCurrent | total_liabilities | 10541 | 242 | BS;UN | 0:10541 | tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept |
| PrepaidExpenseAndOtherAssetsCurrent | current_assets_liabilities | 10375 | 238 | BS;CI;EQ;UN | 0:10375 | tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept |
| EffectOfExchangeRateOnCashAndCashEquivalents | cash_equivalents | 10155 | 320 | BS;CF;UN | 1:2531;2:2520;3:2506;4:2596;30:1;31:1 | balance-sheet candidate does not mostly use qtrs=0 |
| IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | total_liabilities | 10133 | 223 | BS;CF;IS;UN | 0:1;1:2486;2:2445;3:2431;4:2741;10:2;11:1;12:3;13:2;14:1;15:1;16:1;17:2;18:2;19:2;20:2;21:3;22:1;24:1;25:1;26:1;27:1;28:1;29:1 | balance-sheet candidate does not mostly use qtrs=0 |
| AllowanceForDoubtfulAccountsReceivableCurrent | receivables | 10063 | 251 | BS;CF;CI;EQ;IS;UN | 0:10063 | tag name indicates component, sector-specific, fair-value, tax, lease, or other non-total concept |

## Decision Boundary

No unmapped tag was accepted automatically by this audit. Any future addition should be treated as a new controlled data-engineering change, not as a documentation-only correction.

This audit is designed to identify whether a late-stage harmonization improvement is worth a full rebuild. A candidate should only be promoted if it survives manual row-level review and the full downstream acceptance chain: panel rebuild, selected-fact provenance, P0 audits, target profiles, model consistency, calibration/ranking, dashboard screenshots, and source-of-truth refresh.

Current thesis-safe position remains: SEC concept mapping is conservative, audited, and closer to harmonized after review, but not perfect taxonomy harmonization.
