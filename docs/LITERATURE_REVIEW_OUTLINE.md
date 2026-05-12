# Literature Review Outline

Last updated: 2026-05-06

## 2.1 Strategic Problem: Success, Failure, Adaptation, and Resilience

- Start with the strategic-management problem: firms face changing environments, and outcomes differ because resources, capabilities, inertia, and resilience differ.
- Use Barney (1991), Teece et al. (1997), Hannan and Freeman (1984), Linnenluecke (2017), Duchek (2020), and Hepfer and Lawrence (2022).
- Narrow the construct: this thesis does not measure the full strategic concept of resilience. It operationalizes a financial proxy using accounting fundamentals, forward success/resilience labels, broader financial pressure, and strict legal distress.

## 2.2 Classical Financial Distress Prediction

- Review Beaver (1966), Altman (1968), Ohlson (1980), Zmijewski (1984), Shumway (2001), Campbell et al. (2008), Tinoco and Wilson (2013), and related market/default models.
- Critical point: this is a mature field; the thesis must not claim that bankruptcy prediction is new.
- Gap: prior work often focuses on one distress definition or static formulation; this thesis builds a hierarchy of strict distress, broader pressure, and success/resilience.

## 2.3 Machine Learning in Bankruptcy, Credit, and Financial Distress Prediction

- Use Lessmann et al. (2015), Barboza et al. (2017), Kim et al. (2020), Dasilas and Rigani (2024), Zhao et al. (2024), and core algorithm papers.
- Explain why random forest and gradient boosting are reasonable nonlinear benchmarks.
- Critique: higher model performance is not enough if validation is random, target leakage is uncontrolled, or outputs are not interpretable.

## 2.4 Firm Fundamentals, Deterioration Features, and Broader Financial Pressure

- Connect ratios and fundamentals to deterioration features: profitability, margins, leverage, liquidity, revenue/cash-flow dynamics, prior loss counts, and lagged/change variables.
- Use Tian and Yu (2017), Billios et al. (2024), Valaskova et al. (2023), Bragoli et al. (2022), and Tinoco and Wilson (2013).
- Justify broader financial pressure as a distinct empirical outcome, not a rebranding of legal bankruptcy.

## 2.5 Market Shifts: Macro Regimes, Credit Conditions, and Global-Event Context

- Use Bernanke et al. (1999), Gilchrist and Zakrajsek (2012), Longstaff et al. (2005), Tinoco and Wilson (2013), Chicago Fed NFCI documentation, FRED documentation, and Federal Reserve financial-stability context.
- Make a restrained claim: macro variables provide context and possible incremental signal; they are not automatically the dominant cause.

## 2.6 Evaluation Challenges: Rare Events, Temporal Validation, Class Imbalance, and Interpretability

- Use Fawcett (2006), Davis and Goadrich (2006), Saito and Rehmsmeier (2015), Chawla et al. (2002), and Charalambous et al. (2022).
- Explain why strict legal distress should be read through PR-AUC and recall/F1, not only ROC-AUC.
- Use Lundberg and Lee (2017), Ribeiro et al. (2016), Guidotti et al. (2018), Molnar (2025), Bussmann et al. (2021), Gramegna and Giudici (2021), and Zhang et al. (2022) for interpretability.

## 2.7 Research Gap and Thesis Contribution

- State directly: the thesis is not just another bankruptcy-prediction model.
- Contribution: a reproducible audited SEC/FRED/global-event firm-period panel; prediction-date policy tied to SEC filing dates; target hierarchy; temporal validation; interpretable feature/factor analysis; dashboard artifact.
- Remaining caveat: strict distress is source-curated and rare, not a complete legal-bankruptcy database; this should be reported transparently.
