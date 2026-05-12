# Success Resilience Target Definition Review

Status: Target issue fixed

## Diagnosis

The rebuilt `success_resilience_next_4q` target is missing-aware. Future rows without enough observed net-income, ROA, and leverage/assets components remain null instead of becoming automatic non-success.

The pre-fix audit confirmed that `missingindicator_total_liabilities` was partly proxying for this target-definition problem. In the rebuilt panel, the indicator may still be useful as a predictive/reporting-pattern feature, but it must not be interpreted as a direct economic success factor.

## Missing-Aware Alternative

A safer target should require at least three future observations where net income, ROA, and leverage/assets are all available. Rows without enough future component coverage should remain null for the forward success target.

## Current Audit Counts

- Current success positives: 12,519
- Current unknown rows: 11,550
- Revised known rows: 20,152
- Revised unknown rows: 11,550
- Revised success positives: 12,519
- Rows currently 0 but revised unknown: 0
- Rows currently unknown and revised unknown: 11,550
- Known current/revised disagreements: 0

## Recommendation

Keep the missing-aware production target. Missingness indicators may remain in predictive models after diagnosis, but economic interpretation tables and plots should separate or exclude them.
