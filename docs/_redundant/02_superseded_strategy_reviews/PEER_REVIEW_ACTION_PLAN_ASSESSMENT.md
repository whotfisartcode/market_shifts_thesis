# GPT-5.5 Pro Peer Review Assessment

Source file:

```text
/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/codex_peer_review_action_plan.json
```

Read on: 2026-05-04

## Verdict

The review is useful and mostly correct.

The core warning is right:

> Freeze the empirical design, stop adding scope, audit timing/leakage, and convert the existing pipeline into thesis-ready evidence.

I agree with the review's general grade estimate:

- current state is no longer a weak/non-empirical thesis;
- still not safe until timing, leakage, event-date, and dashboard-output issues are audited;
- likely thesis strength depends more on careful claims and documentation than on another small model improvement.

## Important Stale Points

The JSON was created before the latest data-integrity pass.

Stale or superseded items:

- It says flow variables may still mix quarterly and annual `qtrs`.
- We have since standardized flow variables to single-period values where SEC cumulative facts allow derivation.
- It reports success test positives as 2,088; latest rerun after the flow fix has 2,061.
- It reports event-aware random forest ablation as the best PR-AUC; latest rerun after the flow fix has firm-only random forest as the strongest ablation by PR-AUC.

Current interpretation after our latest rerun:

- firm accounting fundamentals and deterioration dominate;
- macro/regime/global-event context is still useful for market-shift explanation and dashboard analysis;
- global events should not be claimed as causal or as a fully automated event database.

## Valid P0 Items

These should be treated as required before final dashboard/screenshots/writing:

1. `P0_01_prediction_date_audit`
   The reviewer is right. SEC filing data is not publicly available at `period_date`; it becomes available at `filed_date`. We must audit or change the prediction timestamp.

2. `P0_02_event_date_audit`
   Correct. Distress event dates are currently useful but not final-proof. They need exact/approximate/manual-review status.

3. `P0_03_leakage_audit`
   Correct. We already removed `cohort`, but we need saved feature lists and a machine-readable blacklist audit.

4. `P0_04_macro_event_timing_audit`
   Correct. Macro and event predictors should be available no later than the prediction timestamp if used in predictive models.

5. `P0_05_post_event_row_policy`
   Correct. Post-event observations should not be treated as normal pre-event early-warning rows.

## Valid P1 Items

These are useful after P0:

- threshold tuning on validation only;
- precision@k, recall@k, and lift@k for distress watchlist framing;
- weighted/unweighted model comparison;
- deterioration feature audit;
- robustness target comparisons.

The rare-event framing should emphasize ranking and early warning, not binary accuracy.

## Valid P2 Items

These should become the final deliverable sequence:

- thesis-ready tables;
- thesis-ready figures;
- dashboard refinement;
- dashboard screenshots;
- `reports/RUN_STATUS.md`.

## Decisions

Accepted:

- no new core data sources;
- no GDELT/ACLED/EM-DAT pipeline before submission;
- no Russian/RFSD merge into the main model before submission;
- no 10-K NLP;
- no random split;
- no test-set threshold tuning;
- no invented outputs.

Modified:

- The review says macro/event context gives modest incremental rare-event ranking value. Latest result is more conservative: macro/event context is primarily explanatory after the flow fix, while firm-only random forest currently ranks rare distress best.

## Immediate Next Step

Start with P0 audits, in this order:

1. prediction timestamp audit;
2. event date audit;
3. leakage audit;
4. macro/event timing audit;
5. post-event row policy.

Only after those pass should the dashboard be redesigned and screenshotted.
