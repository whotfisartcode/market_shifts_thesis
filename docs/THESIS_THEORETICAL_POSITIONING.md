# Thesis Theoretical Positioning

Last updated: 2026-05-06

## Final Position

The thesis should be positioned as business analytics / applied predictive analytics with a design-science artifact. It is not pure finance theory, not pure strategic-management theory, and not a pure machine-learning benchmark paper.

## Theoretical Layers

1. Strategic-management framing:
   - firms face changing environments;
   - resources, capabilities, inertia, and resilience help explain why outcomes differ;
   - this layer motivates the title and the practical question.

2. Financial distress and accounting prediction:
   - ratios, profitability, liquidity, leverage, and deterioration signals are established early-warning inputs;
   - strict bankruptcy is rare and methodologically difficult;
   - this layer justifies the SEC accounting panel and target hierarchy.

3. Macro/market-shift context:
   - credit conditions, rates, inflation, market stress, oil shocks, and crisis periods affect the environment in which firms operate;
   - this layer justifies FRED variables, regimes, market-health context, and event overlays.

4. Machine learning and evaluation:
   - random forest and gradient boosting can model nonlinear interactions;
   - rare-event metrics and temporal validation are necessary;
   - this layer justifies the modeling design.

5. Explainability and design science:
   - the result must be usable and explainable;
   - feature/factor interpretation and dashboard exploration turn the model outputs into an artifact.

## Exact Novelty Wording

The novelty is not a new bankruptcy algorithm. The defensible novelty is the integration of:

- an audited SEC/FRED/global-event firm-period panel;
- filing-date prediction timestamps;
- strict distress, broader financial-pressure, and success/resilience target hierarchy;
- temporal validation and leakage controls;
- interpretable factor-group analysis;
- a dashboard artifact for company, sector, macro/regime, and outcome exploration.

## Boundary Conditions

- The panel is U.S. public-company oriented because SEC data are accessible and reproducible.
- Russian/private-company data are discussed only as a limitation, not as missing implementation.
- Global events are curated context fields, not a complete live event-feed system.
- Dashboard output is decision support based on latest available filings, not daily live prediction.
