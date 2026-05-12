# Literature Review Draft

Last updated: 2026-05-06

This draft is intentionally citation-heavy and conservative. It is designed to be expanded into the thesis Chapter 2, not pasted as final prose without adaptation to the university format.

## 2.1 Strategic Problem: Success, Failure, Adaptation, and Resilience

The thesis title is broader than bankruptcy prediction. It concerns success and failure factors across industries under changing market conditions. Strategic-management literature helps frame that problem, but it must be used carefully. The resource-based view argues that durable firm differences can be connected to resources and capabilities (Barney, 1991). Dynamic-capabilities theory extends that logic to changing environments by emphasizing adaptation and renewal (Teece, Pisano, and Shuen, 1997). Organizational ecology adds a competing caution: firms may be constrained by structural inertia, so environmental change can expose organizations that cannot adjust quickly enough (Hannan and Freeman, 1984).

Resilience literature is also relevant, but it does not give a simple accounting formula for success. Linnenluecke (2017) shows that resilience is a broad and multi-stream construct in business and management research. Duchek (2020) conceptualizes organizational resilience as a capability-based process, while Hepfer and Lawrence (2022) distinguish different forms of resilience rather than treating it as one outcome. Therefore, this thesis should not claim to measure total organizational resilience. The defensible claim is narrower: the empirical panel measures financial resilience and financial pressure through observable accounting fundamentals, ratios, trend features, macro/regime context, and forward-looking labels.

## 2.2 Classical Financial Distress Prediction

Financial distress and bankruptcy prediction have a long empirical tradition. Beaver (1966) showed that financial ratios can carry predictive information about failure. Altman (1968) combined ratios in a discriminant model, creating the well-known Z-score tradition. Ohlson (1980) moved the field toward probabilistic bankruptcy prediction with logit methods, while Zmijewski (1984) emphasized methodological issues such as sample selection and model-estimation bias. These sources justify the use of accounting fundamentals and ratios, but they also make clear that ratio-based failure prediction is not novel by itself.

Later research broadened the modeling problem. Shumway (2001) criticized static bankruptcy-prediction designs and proposed a hazard-model framing, which is important for this thesis because the current dataset is a firm-period panel rather than a single cross-section. Campbell, Hilscher, and Szilagyi (2008) treated distress risk as a dynamic condition linked to profitability, leverage, and market context. Tinoco and Wilson (2013) directly support combining accounting, market, and macroeconomic variables for listed-company distress and bankruptcy prediction. At the same time, market-based default models such as Merton (1974), Hillegeist et al. (2004), and Bharath and Shumway (2008) show that accounting variables are only one part of the default-risk literature. Since the present production panel does not implement distance-to-default or full market-price variables, those sources should be used as methodological context and future work, not as implemented empirical evidence.

The first clear gap follows from this literature: bankruptcy prediction is mature, but many studies still force the empirical problem into one target definition. Strict legal distress is clean but rare. Broader financial pressure can capture deterioration before or outside legal bankruptcy, while success/resilience can capture the opposite side of firm outcomes. The thesis contribution is therefore not a new bankruptcy formula; it is a structured target hierarchy applied to an audited firm-period panel.

## 2.3 Machine Learning in Bankruptcy, Credit, and Financial Distress Prediction

Recent literature confirms that the topic remains current. Lessmann et al. (2015) benchmark modern classification algorithms for credit scoring, a related financial-risk task. Barboza, Kimura, and Altman (2017) show that machine-learning models can perform strongly in bankruptcy prediction. Kim, Cho, and Ryu (2020), Dasilas and Rigani (2024), and Zhao, Ouenniche, and De Smedt (2024) show that corporate default, bankruptcy, and business-failure prediction remain active ML research areas. These recent review papers are important because they prevent the literature review from relying only on 1960s-1980s distress models.

The implemented model families are also standard. Random forests are grounded in Breiman (2001), gradient boosting in Friedman (2001), and the Python implementation ecosystem can be cited through Pedregosa et al. (2011). However, the literature also warns that algorithm choice alone is not enough. A high ROC-AUC on a random split would not prove a useful early-warning system if the split leaks future information, if the positive class is extremely rare, or if the target is not economically interpretable. This is why the thesis should stress prediction dates, temporal validation, leakage audits, and target definitions before presenting model metrics.

## 2.4 Firm Fundamentals, Deterioration Features, and Broader Financial Pressure

The empirical feature design is consistent with the literature because financial ratios and fundamentals remain relevant in recent work. Tian and Yu (2017) provide international evidence on financial ratios and bankruptcy prediction. Billios, Seretidou, and Stavropoulos (2024) review the power and limits of numerical indicators in bankruptcy prediction. Valaskova, Gajdosikova, and Belas (2023) demonstrate that bankruptcy-risk prediction remains relevant after the pandemic period in Visegrad countries. Bragoli et al. (2022) add support for industry context by studying whether industrial variables matter in ML bankruptcy prediction.

The thesis uses these sources to justify profitability, leverage, liquidity, margins, cash-flow, revenue trend, prior loss, and deterioration features. Return on assets, for example, is not a raw SEC tag but a derived financial ratio built from accounting data. It is still a valid feature because the literature has long used ratios as interpretable financial signals. The writing should explain this distinction: raw facts, derived ratios, lag/change features, macro variables, regime indicators, and metadata are different feature families.

The broader failure-pressure target should be presented as a response to the limitation of strict legal bankruptcy. It is not a claim that every pressured firm legally failed. It is a forward-looking operational label that captures repeated losses, profitability stress, leverage/liquidity pressure, deterioration, and formal distress where verified. This target is useful for factor analysis because it provides more positive cases than rare strict legal distress, but it must remain separate from bankruptcy in the text.

## 2.5 Market Shifts: Macro Regimes, Credit Conditions, and Global-Event Context

Market shifts are theoretically relevant because firms operate inside macro-financial conditions. Bernanke, Gertler, and Gilchrist (1999) explain how credit frictions can amplify business-cycle shocks. Gilchrist and Zakrajsek (2012) show that credit spreads contain business-cycle information. Longstaff, Mithal, and Neis (2005) caution that credit spreads contain default-risk and liquidity components, so interpretation must be careful. Tinoco and Wilson (2013) provide direct distress-prediction support for combining accounting, market, and macro variables.

Official sources support the actual data layer. SEC Financial Statement Data Sets and EDGAR APIs document the accounting/filing source. FRED documentation supports the macro time-series source. Chicago Fed NFCI documentation and Federal Reserve financial-stability reports support financial-conditions context. These sources justify macro/regime/event variables as market-shift context, not as guaranteed causal explanations. If the empirical results show firm fundamentals dominate feature importance, the thesis should say that. The macro layer still has value in dashboard exploration, regime segmentation, and interpretation of time periods such as crises, inflation shocks, oil shocks, or credit tightening.

## 2.6 Evaluation Challenges: Rare Events, Temporal Validation, Class Imbalance, and Interpretability

Strict legal distress is a rare event in the current panel. Therefore, the evaluation literature matters. Fawcett (2006) explains ROC analysis, but Davis and Goadrich (2006) and Saito and Rehmsmeier (2015) show why precision-recall analysis is especially important when the positive class is rare. Chawla et al. (2002) introduced SMOTE as a major imbalance method, while Burez and Van den Poel (2009) show class imbalance as a wider predictive-modeling problem. The thesis does not need to use oversampling as the main story; it needs to show that rare-event evaluation is understood. PR-AUC, recall, precision, F1, and temporal test positives should be reported alongside ROC-AUC.

Interpretability is equally important. Lundberg and Lee (2017) introduced SHAP as a unified explanation framework, Ribeiro et al. (2016) introduced local explanation logic, and Guidotti et al. (2018) survey black-box explanation methods. Finance-specific explainability sources such as Bussmann et al. (2021), Gramegna and Giudici (2021), and Zhang et al. (2022) support the need to explain financial-risk models. Molnar (2025) provides practical guidance on how to interpret tools like permutation importance and SHAP carefully. The thesis should use feature importance and factor-group tables to discuss model behavior, not to assert causality.

Missing-data methodology also supports the project's integrity choices. Rubin (1976), Little and Rubin (2019), Graham (2009), and van Buuren (2018) show that missingness has mechanisms and consequences. In SEC filing data, missing values may mean a concept was not filed, was not applicable, was filed under another tag, or could not be derived for a quarter. Therefore, missing values should not be silently converted to zero or assumed unchanged. The current thesis choice to audit missingness, retain nulls, and separate missingness indicators from economic interpretation is defensible.

## 2.7 Research Gap and Thesis Contribution

The final research gap should be written precisely. Prior literature has strong classical models, modern ML models, macro/default-risk research, XAI methods, and design-science methodology. What is still useful in this thesis is the combination of these elements into one reproducible business-analytics artifact:

- an audited SEC/FRED/global-event firm-period panel;
- prediction timestamps anchored to SEC filing dates;
- a strict legal distress benchmark;
- a broader financial-pressure target for the main failure-factor analysis;
- a success/resilience target as the positive counterpart;
- temporal validation and leakage controls;
- feature/factor interpretation across industries and regimes;
- a Streamlit dashboard that exposes the panel, targets, macro comparison, and model results.

The thesis should be honest about limits. Strict legal distress remains rare and is not a complete legal-bankruptcy database, even though the current formal strict-distress event rows have source-provenance records. Broader financial pressure is not bankruptcy. Resilience is measured through financial proxies, not through all organizational capabilities. Macro and event variables provide context, not automatic causality. These limitations do not weaken the thesis if they are written clearly; they make the contribution more defensible.
