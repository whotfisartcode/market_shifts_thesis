# Introduction And Research Gap Draft

Last updated: 2026-05-06

## Draft Research Problem

Companies do not fail or succeed only because of one accounting ratio, one macroeconomic shock, or one industry condition. Their observed outcomes emerge from firm-level financial structure, profitability, liquidity, operating performance, sector exposure, and changing market conditions. For public companies, SEC filings and macroeconomic data make it possible to study these relationships at firm-period level, but the analytical problem is difficult: legal bankruptcy is rare, broader deterioration is not always legally observable, macro conditions change over time, and machine-learning models can easily become opaque or temporally invalid.

## Literature-Backed Gap

Prior research gives strong foundations. Classical studies established financial-ratio failure prediction. Later work introduced probabilistic, hazard, market-based, and macro-augmented distress models. Recent literature applies machine learning to bankruptcy, credit scoring, default, and business failure prediction. Explainable-AI research provides methods for interpreting black-box models, and design-science research supports the creation of analytical artifacts.

The gap is not that nobody has studied bankruptcy prediction. The field is mature. The gap addressed here is narrower and more practical: many studies stop at a single distress definition, a limited validation design, or a model-results table. This thesis builds a reproducible business-analytics artifact that combines an audited SEC/FRED/global-event firm-period panel, multiple forward-looking target definitions, temporal validation, factor interpretation, and a dashboard for exploration.

## Proposed Contribution Statement

This thesis contributes a reproducible predictive-analytics workflow for examining company success and failure factors across industries under market shifts. The empirical artifact combines SEC accounting fundamentals, derived ratios and deterioration indicators, FRED macro variables, regime and global-event context, strict legal distress labels, a broader financial-pressure target, and a success/resilience target. The modeling approach treats strict legal distress as a rare-event benchmark, uses broader financial pressure as the main failure-factor target, and uses success/resilience as the positive outcome counterpart. Results are interpreted through model metrics, feature groups, and an interactive dashboard rather than presented as a real-time bankruptcy oracle.

## Claims To Keep Safe

- The thesis studies predictive factors and decision support, not causal proof of why every company fails.
- Strict legal distress is a benchmark; broader financial pressure is not legal bankruptcy.
- Financial resilience is an operational proxy, not the full strategic-management concept of resilience.
- Macro/regime/event fields contextualize market shifts; they do not automatically dominate firm fundamentals.
- Feature importance explains model behavior; it does not prove economic causation.
