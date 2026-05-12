# Russia and Emerging-Market Literature Additions

Last updated: 2026-05-12

## Purpose

This note documents the addition-worthy Russia, emerging-market, and cross-market sources that can strengthen the literature review. These sources should be used as a contextual extension layer. They do not change the implemented empirical scope of the thesis unless a Russian firm panel is later constructed and audited.

Current empirical scope remains:

- U.S. public-company SEC/FRED/global-event firm-period panel;
- prediction-date policy based on SEC filing dates;
- U.S. macro variables from FRED;
- dashboard and model outputs based on the current production panel.

The added sources are useful because they sharpen the literature gap: predictors of firm distress are not always portable across countries, Russian firm-failure prediction has its own evidence base, and Russian macro-financial context would require separate official data and validation.

## Scope-Control Wording

Safe wording:

> Prior literature suggests that distress-prediction variables may behave differently across institutional settings. Evidence from developed versus emerging markets, and from Russian firm-failure studies, supports caution when transferring accounting, market, or macro predictors from one country to another. This thesis therefore treats macro-market context explicitly, while limiting empirical claims to the implemented U.S. SEC/FRED panel.

Unsafe wording:

> This thesis empirically compares Russian and U.S. firms.

Unsafe unless a Russian dataset is actually built:

> The model predicts Russian company failure.

## Added Sources

| Key | Source | Priority | Thesis role |
| --- | --- | --- | --- |
| `charalambakis2015developed_emerging` | Charalambakis and Garrett (2015), UK vs India financial distress prediction | High | Cross-country predictor portability |
| `hunter2001failure_risk_russia` | Hunter and Isachenkova (2001), UK vs Russian firm failure | Very high | Russia-specific cross-country bridge |
| `afanasev2023default_emerging` | Afanasev (2023), Russian service-firm default prediction | Very high | Recent Russian empirical default-prediction evidence |
| `fedorova2020external_factors_russia` | Fedorova, Musienko, and Fedorov (2020), external factors in Russian bankruptcy prediction | Very high | Russian macro/external-factor evidence |
| `nevredinov2021instrumental_ml` | Nevredinov (2021), ML methods for corporate bankruptcy prediction | Medium | Russian ML-method context |
| `gornostaev2022realtime_russia` | Gornostaev et al. (2022), Russian real-time macro database | High | Russian macro-data timing and revision logic |
| `davydov2022us_russian_markets` | Davydov (2022), U.S. and Russian financial markets comparison | Medium | Background market-structure context |
| `cbr2026financial_stability` | Bank of Russia financial-stability portal | High as official source | Russian macro-financial stability context |

## Detailed Literature Analysis

### `charalambakis2015developed_emerging`

**Full source:** Charalambakis, E., and Garrett, I. (2015). *On the Prediction of Financial Distress in Developed and Emerging Markets: Does the Choice of Accounting and Market Information Matter? A Comparison of UK and Indian Firms*. Review of Quantitative Finance and Accounting. DOI: https://doi.org/10.1007/s11156-014-0492-y

**What the paper is about:**  
The paper compares financial distress prediction in a developed market and an emerging market. It examines whether accounting and market-driven variables that work in one institutional setting also work in another. The source reports that a hazard model combining book leverage and market variables performs well for UK firms, while market variables fail to predict bankruptcy in the Indian setting and accounting ratios are more useful.

**Why it matters:**  
It gives the thesis a direct citation for the idea that distress predictors are context-dependent. This is useful because the thesis combines firm fundamentals with macro/regime context and avoids claiming that one universal predictor set works everywhere.

**Limitations:**  
The paper compares the UK and India, not Russia and the United States. It uses a different research design from the current thesis and does not build a dashboard, SEC/FRED panel, or target hierarchy.

**Safe thesis use:**  
Use this source to support the statement that accounting, market, and macro predictors may have different predictive content across institutional settings.

**Do not use for:**  
Do not cite it as evidence that the current thesis empirically covers India, emerging markets generally, or Russia.

### `hunter2001failure_risk_russia`

**Full source:** Hunter, J., and Isachenkova, N. (2001). *Failure Risk: A Comparative Study of UK and Russian Firms*. Journal of Policy Modeling, 23(5), 511-521. DOI: https://doi.org/10.1016/S0161-8938(01)00064-3

**What the paper is about:**  
The paper compares failure risk in UK and Russian firms using accounting-based predictors and logit modeling. It is especially useful because it directly includes Russian firms. The reported logic is that Russian failure risk in the transition setting was more strongly connected to profitability, while UK failure risk relied more on familiar developed-market predictors such as gearing and liquidity.

**Why it matters:**  
This is one of the strongest additions because it directly supports the claim that Russian firm-failure predictors can differ from developed-market predictors. It also helps justify why any Russian extension should not simply copy U.S. or UK variable assumptions.

**Limitations:**  
The Russian evidence comes from the 1990s transition period and uses a small, historically specific sample. The source is not a modern Russian public-company panel and is not evidence from the current SEC/FRED dataset.

**Safe thesis use:**  
Use this as a Russia-specific bridge source in the literature gap: Russian firm-failure prediction exists, but its predictors and institutional setting differ from developed-market contexts.

**Do not use for:**  
Do not cite it as proof that the current U.S. model predicts Russian firms.

### `afanasev2023default_emerging`

**Full source:** Afanasev, V. (2023). *Default Prediction Model for Emerging Capital Market Service Companies*. Journal of Corporate Finance Research, 17(1), 64-77. DOI: https://doi.org/10.17323/j.jcfr.2073-0438.17.1.2023.64-77

**What the paper is about:**  
The paper tests default-prediction models for Russian service companies and compares them with a developed European control group. It uses logistic regression, random forest, and k-nearest neighbors on 404 Russian firms and 304 European firms. The central result is that prediction error is higher for Russian firms, suggesting that financial-ratio-only default prediction may be insufficient for Russian service firms.

**Why it matters:**  
This is the best recent Russia-specific empirical source among the additions. It supports the argument that Russian default prediction is feasible but may require contextual or non-financial information beyond traditional financial ratios.

**Limitations:**  
The paper focuses on service firms, not all sectors. It compares financial-data-only prediction rather than a broad macro-regime-aware firm-period panel. It does not define the same target hierarchy used in this thesis.

**Safe thesis use:**  
Use it to support a paragraph on Russian default-prediction evidence and why a future Russian extension would need careful data design.

**Do not use for:**  
Do not generalize its service-sector conclusion to all Russian industries without a caveat.

### `fedorova2020external_factors_russia`

**Full source:** Fedorova, E. A., Musienko, S. O., and Fedorov, F. Yu. (2020). *Analysis of the External Factors Influence on the Forecasting of Bankruptcy of Russian Companies*. St Petersburg University Journal of Economic Studies, 36(1), 117-133. DOI: https://doi.org/10.21638/spbu05.2020.106

**What the paper is about:**  
The paper studies whether external macroeconomic variables improve bankruptcy prediction for Russian companies. It considers sectors including construction, manufacturing, and trade, and includes external variables such as GDP growth, key rate, exchange-rate movements, CPI, MICEX growth, and unemployment. The reported conclusion is that including external-factor variables improves explanatory capacity compared with models based only on internal company variables.

**Why it matters:**  
This is the most directly relevant addition for the thesis's market-shift framing in a Russian context. It supports the idea that macro/external factors can matter for bankruptcy prediction and that a Russian extension should not ignore macro-financial conditions.

**Limitations:**  
It is a Russian-language source and uses Russian sector samples and binary-choice models, not the current U.S. SEC/FRED production panel. It supports the general logic of macro context, not the exact FRED variables or market-health-index construction.

**Safe thesis use:**  
Use it to say that Russian bankruptcy literature has found value in adding macro/external factors to firm-level predictors.

**Do not use for:**  
Do not cite it as validation of the current U.S. model's macro features or market-health score.

### `nevredinov2021instrumental_ml`

**Full source:** Nevredinov, A. R. (2021). *The Instrumental Machine Learning Methods for Corporate Bankruptcy Prediction*. Finance and Credit, 27(9), 2118-2138. DOI: https://doi.org/10.24891/fc.27.9.2118

**What the paper is about:**  
The paper discusses machine-learning instruments for corporate bankruptcy prediction, including data sources, forecasting-model potential, and input selection for company analysis.

**Why it matters:**  
It helps show that Russian applied-finance literature already recognizes ML-based bankruptcy prediction. That prevents the thesis from overstating novelty as merely "using machine learning".

**Limitations:**  
It appears more methodological and applied than the stronger empirical papers above. Its peer-review status and full-text details should be checked before relying on it heavily.

**Safe thesis use:**  
Use as a secondary Russian ML-context source.

**Do not use for:**  
Do not make it the main evidence that ML outperforms classical methods in the thesis.

### `gornostaev2022realtime_russia`

**Full source:** Gornostaev, D., Ponomarenko, A., Seleznev, S., and Sterkhova, A. (2022). *A Real-Time Historical Database of Macroeconomic Indicators for Russia*. Russian Journal of Money and Finance, 81(1), 88-103. DOI: https://doi.org/10.31477/rjmf.202201.88

**What the paper is about:**  
The paper documents a real-time historical database of Russian macroeconomic indicators. It focuses on data vintages and revisions, showing that the data available at a given point in time can differ from later revised values.

**Why it matters:**  
The current thesis already emphasizes prediction-date validity and no future information leakage. This source gives a Russia-specific macro-data equivalent: any future Russian macro extension should use or at least discuss real-time data availability and revisions.

**Limitations:**  
It is a macro-data infrastructure source, not a firm-level bankruptcy prediction paper.

**Safe thesis use:**  
Use to support the importance of historically valid macro data for any Russia-focused extension.

**Do not use for:**  
Do not cite as evidence that Russian macro variables predict firm failure.

### `davydov2022us_russian_markets`

**Full source:** Davydov, A. Yu. (2022). *US and Russian Financial Markets: Comparative Analysis*. Studies on Russian Economic Development. DOI: https://doi.org/10.1134/S1019331622210080

**What the paper is about:**  
The paper compares U.S. and Russian financial markets. It is useful mainly as background for structural market differences rather than as firm-level distress-prediction evidence.

**Why it matters:**  
It can support the general claim that U.S. and Russian market conditions should not be treated as interchangeable. This is useful if the thesis discusses future cross-country extensions or why U.S. SEC/FRED evidence should be scoped carefully.

**Limitations:**  
It is not a corporate bankruptcy or firm-distress paper. Full-text accessibility may be limited.

**Safe thesis use:**  
Use sparingly in background discussion about market-structure differences.

**Do not use for:**  
Do not use as direct evidence for failure prediction.

### `cbr2026financial_stability`

**Full source:** Bank of Russia. (2026). *Financial Stability*. Official financial-stability portal. URL: https://www.cbr.ru/eng/finstab/

**What the source is about:**  
This official portal contains Bank of Russia financial-stability materials, including reviews, macroprudential policy, stress-testing context, financial-stability analytics, and related monitoring.

**Why it matters:**  
It provides official Russian macro-financial context and possible source material for a future Russian market-shift or stress-regime layer.

**Limitations:**  
This is not a peer-reviewed academic paper and not firm-level distress evidence.

**Safe thesis use:**  
Use as official context or data-source support if discussing Russian macro-financial monitoring.

**Do not use for:**  
Do not treat it as academic evidence that macro variables predict individual company failure.

## Recommended Literature-Review Placement

Add a short subsection after the existing macro/market-shift literature discussion:

### Cross-Country and Russian Context

Suggested prose:

> A related limitation in the distress-prediction literature is that predictor sets may not transfer cleanly across countries. Charalambakis and Garrett (2015) show that accounting and market variables have different predictive value in the UK and India. Russia-specific evidence points in the same direction: Hunter and Isachenkova (2001) find different failure-risk predictors for UK and Russian firms, while Afanasev (2023) finds higher prediction error for Russian service firms than for a developed European control group when using financial data. Fedorova, Musienko, and Fedorov (2020) further show that Russian bankruptcy-prediction models can benefit from external macroeconomic factors. These sources support the broader argument that market context and institutional setting matter, while also motivating a clear limitation: the present empirical implementation is based on a U.S. SEC/FRED panel, and Russian evidence is used for contextual comparison and future research rather than as part of the current model estimation.

## Updated Source-To-Claim Logic

The additions support three new claim groups:

- `C13`: Distress-prediction variables may not transfer cleanly across institutional settings.
- `C14`: Russian bankruptcy-prediction literature suggests external macroeconomic factors and market context can improve or alter firm-failure analysis, but these sources support context/future extension rather than current U.S. model claims.
- `C15`: Russia and the United States should not be treated as interchangeable macro-financial environments; any cross-country extension requires separate data design and validation.

