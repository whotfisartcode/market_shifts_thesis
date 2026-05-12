# Final Decision Plan 2026-05-05

Updated: 2026-05-05

Source:

```text
/Users/whotfisart/codex/Thesis work/_external_inputs/02_ai_reviews_and_strategy_plans/final_codex_decision_plan_20260505_1.json
```

## Accepted Direction

The project will move in this direction:

1. Do a controlled final production pass, not broad scope expansion.
2. Keep strict `distress_next_4q` as the clean legal distress benchmark.
3. Verify existing distress dates and +150 event-review firms before adding any strict distress positives.
4. Promote at most one broader failure-pressure target only if implementation and audits are clean.
5. Build a market-health index from existing macro/regime/global-event data as a context layer.
6. Treat market-price data as an optional separate audit branch only.
7. Defer CHS and Merton distance-to-default to future research unless simple market data passes mapping, coverage, and leakage checks.

## Production Guardrails

- Do not manually edit production panel files.
- Do not label event-review firms as distress without source evidence.
- Do not call broader financial-pressure targets bankruptcy.
- Do not present missingness indicators as economic causes.
- Do not merge market-price features into production before mapping, coverage, temporal alignment, and leakage audits pass.
- If a P0 audit fails after a production change, stop and document the failure before final model training.

## Current Implementation Status

Completed:

- created event-date provenance scaffold;
- created event-review classification scaffold;
- created market-health index script and documentation;
- ran the market-health index from existing panel-aligned macro/event fields;
- source-verified eight event-review formal distress candidates;
- added those eight source-verified formal distress events to `config/distress_event_dates.csv`;
- rebuilt the production panel and GitHub dataset copies;
- reran P0 audits, integrity audit, target profiles, production models, ablation, analysis outputs, broader target experiments, and target-tweak experiments;
- recorded this decision plan in status and chronicle.

Not yet done:

- no broader target has been promoted into the production panel;
- no market-price feature has been downloaded or merged.

Generated outputs:

```text
reports/data_quality/final_distress_event_date_audit.csv
reports/data_quality/event_review_firm_classification_scaffold.csv
reports/data_quality/event_review_scaffold_summary.csv
reports/data_quality/market_health_index_audit.csv
reports/modeling/market_health_index_by_prediction_date.csv
reports/modeling/market_health_by_year_regime_sector.csv
reports/figures/modeling/market_health_index_timeseries.png
```

Current event-review scaffold summary:

- 75 event-review expansion firms remain separated from production labels;
- 8 source-verified formal distress candidates have been added to the strict event-date config;
- 11 likely merger/transaction candidates should not be labeled as distress without contrary source evidence;
- 0 unverified formal distress candidates are currently being treated as usable labels.

## Current Priority Order

1. Review/fill event-date provenance and event-review classifications.
2. Decide whether to promote one broader failure-pressure target.
3. Use the market-health index for dashboard/context.
4. If another production change happens, rerun audits/models/reports.
5. Keep market data as a separate audit branch only.
6. Freeze final outputs and write thesis.
