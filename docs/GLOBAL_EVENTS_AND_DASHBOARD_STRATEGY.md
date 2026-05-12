# Global Events and Dashboard Strategy

Updated: 2026-05-12

Current status note: this strategy remains valid as a methodology/dashboard note. Panel dimensions have been refreshed after later rebuilds and the validated-secondary target promotion; current production facts are controlled by `docs/FINAL_ACCEPTANCE_REPORT_20260512.md` and `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`.

## Recommendation

Add global events, but do it in two layers:

1. Curated global-event calendar for the thesis and dashboard.
2. Optional external event database integration later, if time remains.

This keeps the work defensible before the deadline. A full raw global-news/event-data build would be a second data project.

## Implemented Now

Created:

```text
config/global_event_calendar_seed.csv
```

Merged into:

```text
data/processed/panel_v2/firm_panel_v2.parquet
data/github/firm_panel_v2.parquet
```

New feature family:

```text
global_event_context
```

Current production panel after later SEC mapping/caveat-resolution rebuilds and target-label promotion:

- 31,702 rows
- 190 columns
- 27 global-event context columns

Event types included:

- `financial_crisis`
- `sovereign_debt`
- `natural_disaster`
- `commodity_oil`
- `financial_market`
- `political_policy`
- `trade_policy`
- `pandemic`
- `supply_chain`
- `monetary_inflation`
- `geopolitical_war`
- `banking_stress`

Generated:

```text
reports/modeling/panel_v2_global_event_sector_summary.csv
reports/figures/modeling/panel_v2_distress_share_by_global_event_type.png
```

## Why This Fits the Thesis

The title says "market shifts." Macro variables capture continuous economic conditions, but global events capture discrete shocks.

Useful thesis framing:

> Global events are treated as historically observed market-shift regimes. The analysis compares firm and sector behavior across event windows, rather than claiming that every event can be forecast in advance.

This is stronger than a generic dashboard because it lets the output answer questions like:

- Which sectors showed elevated distress labels during commodity oil shocks?
- Which sectors had weaker resilience during pandemic and supply-chain event windows?
- Did banking stress windows affect financial firms differently from consumer or industrial firms?
- Did firm-level deterioration matter more than the event label itself?

## Empirical Effect So Far

Before the later SEC flow-standardization pass, the event layer helped slightly for nonlinear rare-event ranking:

- best event-aware random forest ablation PR-AUC: about 0.175;
- previous firm + macro + regime random forest PR-AUC: about 0.175;
- firm-only random forest PR-AUC: about 0.167.

After the flow-standardization pass, the strongest ablation is currently firm-only. This does not make the event layer useless; it means global events should be used mainly for sector/event explanation and dashboard analysis, not as the core economic mechanism.

Interpretation:

- global events are useful for dashboard and historical explanation;
- they do not replace firm fundamentals;
- linear models became worse with event flags, so event indicators should be treated cautiously in modeling.

## Possible External Global Event Data Sources

### GDELT

Best fit if we want an automated global event feed.

Pros:

- global event/news coverage;
- event categories through CAMEO codes;
- location and time information;
- high-frequency updates;
- useful for a future live event layer.

Cons:

- very large;
- media-coverage bias;
- requires aggregation and normalization;
- raw download across many years can become too big before the deadline.

Recommended use:

- not as raw firm-level input now;
- optionally aggregate selected event categories by quarter and geography;
- dashboard layer first, model robustness later.

### ACLED

Best fit for political violence, conflict, demonstrations, and strategic developments.

Pros:

- cleaner event definitions than raw news scraping;
- date, location, event type, fatalities;
- good for conflict/protest/geopolitical risk.

Cons:

- registration/API access;
- coverage is uneven historically across regions;
- narrower than "global business events."

Recommended use:

- optional supplement for conflict/geopolitical event windows;
- not the main event dataset before the deadline.

### EM-DAT

Best fit for natural and technological disasters.

Pros:

- long historical coverage;
- standardized disaster classifications;
- impact measures.

Cons:

- free access requires registration;
- event types are disasters, not broad market events;
- less useful for trade wars, banking stress, or monetary shocks.

Recommended use:

- optional disaster robustness layer;
- not necessary for the core thesis.

## Dashboard Direction

The dashboard should not pretend to be a fully live daily accounting system. SEC accounting data updates when firms file, and filings lag the actual period.

Better artifact:

> A historical market-shift and early-warning dashboard.

Core dashboard modes:

1. Historical event analyzer.
   Select event type, sector, period, and target. Show distress share, resilience share, ROA, leverage, cash/assets, and firm examples.

2. Firm early-warning view.
   Show latest available filing score, top contributing factors, current macro/regime/event context, and historical trajectory.

3. Sector stress monitor.
   Compare sectors across macro regimes and global event windows.

4. Data/reproducibility view.
   Show panel shape, feature families, target definitions, and source links.

Live format:

- macro/event context can update daily or weekly;
- firm fundamentals update when new SEC filings arrive;
- model predictions should be labeled "as of latest available filing."

Correct wording:

> The dashboard is not a real-time trading system. It is a reproducible decision-support artifact that combines latest available filings with higher-frequency macro and event context.

## RFSD / Russian Data

If RFSD means Russian company financial statement data, do not merge it into the main training panel before the deadline unless the user already has a clean file.

Reasons:

- different disclosure regime and accounting standards;
- language and metadata cleaning;
- currency conversion;
- industry mapping;
- event and bankruptcy-label matching;
- high risk of weakening the empirical chapter.

Recommended compromise:

- keep the main SEC/FRED/global-event panel as the thesis empirical core;
- if Russian data arrives cleanly, add a separate dashboard tab or appendix case study;
- do not retrain the main model on mixed U.S./Russian data before submission.
