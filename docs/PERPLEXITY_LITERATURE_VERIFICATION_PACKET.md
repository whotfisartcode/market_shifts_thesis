# Perplexity Literature Verification Packet

Prepared for source verification and literature-alignment review. Generated from the local thesis bibliography, literature matrix, source-to-claim map, and critical-evaluation table on 2026-05-12.

## What I Need Perplexity To Verify

Please verify the sources listed in this document for bibliographic accuracy, accessibility, thesis relevance, and safe use in the literature review. For each source, check whether the title/authors/year/journal/DOI or URL are correct, whether full text or a reliable public abstract is accessible, what the paper actually argues, and whether the stated limitation and thesis use below are accurate. Flag any source that is weak, mischaracterized, inaccessible, non-peer-reviewed when presented as peer-reviewed, or poorly aligned with the thesis.

Specific verification questions:

1. Are the citation metadata and DOI/URL correct?
2. Is the source peer-reviewed, official documentation, book, conference paper, report, or other?
3. Is the source accessible enough for thesis writing, preferably open access or with a public full-text/PDF?
4. Does the description accurately summarize what the source contributes?
5. Are the listed limitations fair?
6. Does the source support the stated thesis use without overclaiming?
7. Are there better open-access alternatives for the same claim?

## Thesis And Project Description

The thesis develops a reproducible business-analytics artifact for analyzing and predicting company success and failure factors across industries under changing market conditions. The empirical core is a U.S. public-company firm-period panel built from SEC Financial Statement Data Sets, FRED macroeconomic and financial-market data, manually curated global-event context, and verified distress-event labels.

The production panel uses SEC filing dates as prediction timestamps (`prediction_date = filed_date`) so model inputs and macro/event context are aligned to information available at the prediction date. The current panel contains 31,702 firm-period rows, 190 columns, 540 SEC CIKs/ticker-display IDs, and prediction dates from 2009-04-15 to 2026-03-31. It includes raw SEC accounting fundamentals, derived financial ratios, deterioration/trend features, FRED macro variables, macro-regime indicators, global-event context, industry metadata, and multiple forward-looking target labels.

The target hierarchy separates strict legal distress from broader financial pressure and success/resilience outcomes. Strict legal distress is treated as a rare benchmark. The broader failure-pressure target captures repeated losses, profitability stress, leverage/liquidity pressure, deterioration, and verified formal distress where relevant. Success/resilience targets are financial proxies, not total organizational resilience. The thesis uses temporal validation, leakage/timing audits, feature/factor interpretation, calibration/ranking diagnostics, and a Streamlit dashboard as the artifact layer.

The thesis contribution is not a new universal bankruptcy formula. The contribution is the integrated and audited design: SEC/FRED/global-event firm-period panel, filing-date prediction policy, target hierarchy, temporal validation, interpretable factor analysis across industries and regimes, and dashboard-based decision support. Macro variables and market-health indicators are treated as market-shift context, not proof that macro conditions cause individual firm failure.

Important scope note: Russia/emerging-market sources are being added to strengthen the literature review and future-extension rationale. They do not mean the current empirical model estimates Russian firms unless a Russian firm panel is later built and audited.


## Current Bibliography Quality Summary

- **total_references**: 75 | target: >= 50 | status: PASS | note: Thesis requirement is at least 50 sources.
- **academic_journal_articles**: 58 | target: >= 25 | status: PASS | note: Requirement asks roughly 50-60% academic journal articles; this package exceeds that floor.
- **peer_reviewed_sources**: 62 | target: >= 30 | status: PASS | note: Includes journal articles and peer-reviewed conference papers.
- **english_language_academic_journal_articles**: 57 | target: >= 17 | status: PASS | note: This satisfies the one-third foreign English-language academic journal requirement under the current source set.
- **recent_2020_or_newer_sources**: 27 | target: >= 12 | status: PASS | note: Recent sources are included so the review is not only classical.
- **verified_doi_or_official_pages**: 75 | target: 75 | status: PASS | note: Every row has a DOI, official page, publisher page, or official report URL.
- **sources_with_clear_public_or_official_access_flag**: 14 | target: documented | status: PASS | note: These sources are marked as official/public/open-page accessible.
- **sources_with_unknown_or_access_limited_notes**: 61 | target: explicitly labeled | status: PASS | note: These are not removed; they are labeled in the critical-evaluation table.
- **bucket::Classical firm failure and financial distress prediction**: 11 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Design science, dashboard, and decision-support artifact framing**: 5 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Firm fundamentals, financial ratios, and deterioration features**: 7 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Interpretability and explainable ML**: 7 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Machine learning, rare-event evaluation, and temporal validation**: 15 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Macroeconomic conditions, credit cycles, and market-shift/default context**: 7 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Missing data, data integrity, and accounting-data limitations**: 4 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Official data sources and empirical context**: 8 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Strategic management and resilience framing**: 6 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.
- **bucket::Emerging-market and Russia-specific distress prediction context**: 5 | target: see plan minimums | status: PASS | note: Bucket represented in matrix.

## Source-To-Claim Map

| Claim ID | Thesis Claim | Supporting Citation Keys |
| --- | --- | --- |
| C1 | Financial ratios and accounting fundamentals are valid early-warning inputs, but not a novel idea by themselves. | beaver1966financial; altman1968financial; ohlson1980financial; zmijewski1984methodological; tian2017financial |
| C2 | Firm-period and forward-looking target design are better aligned with early warning than one static firm observation. | shumway2001forecasting; duffie2007multi; bauer2014hazard |
| C3 | Strict legal bankruptcy/distress is rare and should be treated as a benchmark, not the whole success/failure story. | campbell2008distress; tinoco2013financial; dasilas2024machine; zhao2024survey |
| C4 | A broader financial-pressure target is defensible when it is clearly separated from legal bankruptcy. | campbell2008distress; charalambous2022maximizing; tinoco2013financial; billios2024power |
| C5 | ML models are defensible for distress prediction only when benchmarked and temporally validated. | barboza2017machine; lessmann2015benchmarking; dasilas2024machine; zhao2024survey; breiman2001random; friedman2001greedy |
| C6 | PR-AUC and positive-class recall/F1 must be shown for rare or imbalanced targets. | davis2006relationship; saito2015precision; fawcett2006roc; chawla2002smote |
| C7 | Feature importance and SHAP-style explanations describe model behavior, not economic causality. | lundberg2017unified; ribeiro2016trust; guidotti2018survey; molnar2025interpretable; zhang2022xai |
| C8 | Missing values in accounting panels must not be silently converted into zeros or invented persistence. | rubin1976inference; little2019missing; graham2009missing; vanbuuren2018flexible |
| C9 | Macro/credit variables are useful context, but claims that macro dominates firm fundamentals require empirical evidence. | gilchrist2012credit; longstaff2005corporate; bernanke1999financial; tinoco2013financial; chicagofed2026nfci |
| C10 | The artifact can be justified as design science and decision support if it connects data, models, interpretation, and user exploration. | hevner2004design; peffers2007design; chen2012business; shneiderman1996eyes; arnott2014decision |
| C11 | Strategic success/resilience framing is acceptable only if the operational financial proxy is explicit. | barney1991firm; teece1997dynamic; hannan1984structural; duchek2020resilience; hepfer2022organizational; linnenluecke2017resilience |
| C12 | The current thesis novelty is the audited SEC/FRED/global-event firm-period panel plus target hierarchy, temporal validation, interpretation tables, and dashboard artifact. | sec2026financial; sec2024edgarapi; fredapi; fredwhat; hevner2004design; tinoco2013financial; dasilas2024machine |
| C13 | Distress-prediction variables may not transfer cleanly across institutional settings; emerging-market and Russian evidence supports cautious interpretation of accounting, market, and macro predictors. | charalambakis2015developed_emerging; hunter2001failure_risk_russia; afanasev2023default_emerging |
| C14 | Russian bankruptcy-prediction literature suggests external macroeconomic factors and market context can improve or alter firm-failure analysis, but these sources support context/future extension rather than current U.S. model claims. | fedorova2020external_factors_russia; nevredinov2021instrumental_ml; cbr2026financial_stability; gornostaev2022realtime_russia |
| C15 | Russia and the United States should not be treated as interchangeable macro-financial environments; any cross-country extension requires separate data design and validation. | davydov2022us_russian_markets; hunter2001failure_risk_russia; charalambakis2015developed_emerging |

## Priority Sources And Candidate Additions To Verify

This section highlights the latest open-access or scope-expanding sources. Sources already in the current bibliography appear again in the full table below; candidate additions are listed only here until manually approved.

### zhao2024survey
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Zhao, Jinxian and Ouenniche, Jamal and De Smedt, Johannes (2024). *Survey, Classification and Critical Analysis of the Literature on Corporate Bankruptcy and Financial Distress Prediction*. Machine Learning with Applications.
- **DOI/URL:** https://doi.org/10.1016/j.mlwa.2024.100527
- **Why it may help:** Modern literature anchor for the ML/business-failure section.
- **Limitation:** A survey and not a validation of the thesis panel.
- **Access/status note:** metadata_verified_full_text_access_unknown_or_may_be_paywalled; full_text_access_unknown_or_access_limited
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### billios2024power
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Billios, Dimitrios and Seretidou, Dimitra and Stavropoulos, Antonios (2024). *The Power of Numerical Indicators in Predicting Bankruptcy: A Systematic Review*. Journal of Risk and Financial Management.
- **DOI/URL:** https://doi.org/10.3390/jrfm17100433
- **Why it may help:** Modern support that accounting/numerical indicators remain relevant.
- **Limitation:** Review scope is narrow and does not provide the thesis data architecture.
- **Access/status note:** metadata_verified_full_text_access_unknown_or_may_be_paywalled; full_text_access_unknown_or_access_limited
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### hancock2023imbalanced
- **Status:** Candidate addition, not yet in current BibTeX
- **Citation:** Hancock, J. T., Khoshgoftaar, T. M., & Johnson, J. M. (2023). Evaluating classifier performance with highly imbalanced Big Data. Journal of Big Data, 10, 42.
- **DOI/URL:** https://doi.org/10.1186/s40537-023-00724-5
- **Access note:** Open access under CC BY 4.0.
- **Why it may help:** Useful supplement for rare-event and imbalanced-class evaluation.
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### galaitsi2023resilience
- **Status:** Candidate addition, not yet in current BibTeX
- **Citation:** Galaitsi, S. E., Pinigina, E., Keisler, J. M., Pescaroli, G., Keenan, J. M., et al. (2023). Business Continuity Management, Operational Resilience, and Organizational Resilience. International Journal of Disaster Risk Science, 14, 713-721.
- **DOI/URL:** https://doi.org/10.1007/s13753-023-00494-x
- **Access note:** Open access under CC BY 4.0.
- **Why it may help:** Useful accessible resilience source to clarify organizational resilience is broader than this thesis financial proxy.
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### weber2024resilience_mcs
- **Status:** Candidate addition, not yet in current BibTeX
- **Citation:** Weber, M. M., Pedell, B., & Rötzel, P. G. (2024). Resilience-oriented management control systems. Journal of Management Control, 35, 563-620.
- **DOI/URL:** https://doi.org/10.1007/s00187-024-00385-2
- **Access note:** Open access at Springer; PDF also available through EconStor.
- **Why it may help:** Potentially useful for dashboard/decision-support and resilience-management framing.
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### charalambakis2015developed_emerging
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Charalambakis, Evangelos and Garrett, Ian (2015). *On the Prediction of Financial Distress in Developed and Emerging Markets: Does the Choice of Accounting and Market Information Matter? A Comparison of UK and Indian Firms*. Review of Quantitative Finance and Accounting.
- **DOI/URL:** https://doi.org/10.1007/s11156-014-0492-y
- **Why it may help:** Supports the literature-review claim that distress predictors are not perfectly portable across institutional settings and that market-context variables need careful empirical validation.
- **Limitation:** Compares the UK and India, not Russia or the implemented U.S. SEC/FRED panel; it uses a different model family and does not build a dashboard or target hierarchy.
- **Access/status note:** metadata_verified_full_text_access_unknown_or_may_be_paywalled; full_text_access_unknown_or_access_limited
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### hunter2001failure_risk_russia
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Hunter, John and Isachenkova, Natalia (2001). *Failure Risk: A Comparative Study of UK and Russian Firms*. Journal of Policy Modeling.
- **DOI/URL:** https://doi.org/10.1016/S0161-8938(01)00064-3
- **Why it may help:** Supports the contextual claim that Russian firm-failure prediction may require different predictor interpretation and should not simply import Western predictor assumptions.
- **Limitation:** Older transition-economy period, small Russian sample, narrow historical context, and different data environment from the current U.S. SEC/FRED panel.
- **Access/status note:** publisher_page_access_limited; public_working_paper_page_available; full_text_access_unknown_or_access_limited_for_journal_version
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### afanasev2023default_emerging
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Afanasev, Vladislav (2023). *Default Prediction Model for Emerging Capital Market Service Companies*. Journal of Corporate Finance Research.
- **DOI/URL:** https://doi.org/10.17323/j.jcfr.2073-0438.17.1.2023.64-77
- **Why it may help:** Supports a Russia-specific literature paragraph explaining why contextual variables and careful scope limits matter in emerging capital-market settings.
- **Limitation:** Service-sector only; financial-ratio-only design; not a broad cross-industry macro-regime panel; not the same target hierarchy as this thesis.
- **Access/status note:** journal_page_accessible; none_flagged
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### fedorova2020external_factors_russia
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Fedorova, Elena A.; Musienko, Svetlana O.; Fedorov, Fedor Yu. (2020). *Analysis of the External Factors Influence on the Forecasting of Bankruptcy of Russian Companies*. St Petersburg University Journal of Economic Studies.
- **DOI/URL:** https://doi.org/10.21638/spbu05.2020.106
- **Why it may help:** Supports the market-shift/macro-context logic in a Russia-specific setting and helps justify future Russian macro-regime variables.
- **Limitation:** Russian-language source; sector samples and modeling details differ from the current U.S. SEC/FRED design; supports external-factor relevance, not the exact market-health index.
- **Access/status note:** public_full_text_or_article_page_accessible; none_flagged
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### nevredinov2021instrumental_ml
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Nevredinov, Aleksandr R. (2021). *The Instrumental Machine Learning Methods for Corporate Bankruptcy Prediction*. Finance and Credit.
- **DOI/URL:** https://doi.org/10.24891/fc.27.9.2118
- **Why it may help:** Use as a secondary local-context source showing that ML-based bankruptcy prediction is recognized in Russian applied finance literature.
- **Limitation:** Less central than empirical cross-country/Russian sector papers; methodological/applied framing may be weaker for theory; peer-review status should be checked before heavy reliance.
- **Access/status note:** publisher_page_accessible; peer_review_status_unknown_or_needs_manual_check
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### gornostaev2022realtime_russia
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Gornostaev, Dmitry; Ponomarenko, Alexey; Seleznev, Sergei; Sterkhova, Aleksandra (2022). *A Real-Time Historical Database of Macroeconomic Indicators for Russia*. Russian Journal of Money and Finance.
- **DOI/URL:** https://doi.org/10.31477/rjmf.202201.88
- **Why it may help:** Supports timing/revision logic for any future Russian macro-regime extension and reinforces the general thesis emphasis on prediction-date validity.
- **Limitation:** Macro-data infrastructure source, not a firm-level distress model; relevant mainly if a Russian macro panel or future extension is discussed.
- **Access/status note:** open_access_article_page_accessible; none_flagged
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### davydov2022us_russian_markets
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Davydov, A. Yu. (2022). *US and Russian Financial Markets: Comparative Analysis*. Studies on Russian Economic Development.
- **DOI/URL:** https://doi.org/10.1134/S1019331622210080
- **Why it may help:** Use as a secondary macro-financial context source if discussing why Russia and the U.S. should not be treated as interchangeable empirical environments.
- **Limitation:** Financial-market comparison, not firm-level distress prediction; should be background only.
- **Access/status note:** metadata_verified_full_text_access_unknown_or_may_be_paywalled; full_text_access_unknown_or_access_limited
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

### cbr2026financial_stability
- **Status:** In current bibliography / verification requested.
- **Citation metadata:** Bank of Russia (2026). *Financial Stability*. Bank of Russia official financial stability portal.
- **DOI/URL:** https://www.cbr.ru/eng/finstab/
- **Why it may help:** Use only if discussing a possible Russian macro-stability extension or official Russian macro-financial context.
- **Limitation:** Official context source, not peer-reviewed literature and not firm-level distress evidence.
- **Access/status note:** official_public_page_accessible; peer_review_status_unknown_or_not_applicable
- **Ask Perplexity to verify:** Check metadata, access/full text, relevance, and whether it should be kept in the main chapter, appendix, or not used.

## Full Literature Analysis Table

## Bucket: Classical firm failure and financial distress prediction

### beaver1966financial
- **Citation metadata:** Beaver, William H. (1966). *Financial Ratios as Predictors of Failure*. Journal of Accounting Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2307/2490171
- **Current description:** Shows that accounting ratios can contain early warning information before business failure.
- **Main contribution:** Shows that accounting ratios can contain early warning information before business failure.
- **Limitation / critique:** Uses a narrow classical design and does not address modern panel validation or ML.
- **How thesis uses it:** Historical foundation for ratio-based failure signals.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Historical foundation for ratio-based failure signals.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### altman1968financial
- **Citation metadata:** Altman, Edward I. (1968). *Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy*. The Journal of Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/j.1540-6261.1968.tb00843.x
- **Current description:** Introduces the Z-score logic that combines multiple ratios into a failure-risk score.
- **Main contribution:** Introduces the Z-score logic that combines multiple ratios into a failure-risk score.
- **Limitation / critique:** Industry and time-period specificity limit direct use as a modern universal model.
- **How thesis uses it:** Benchmark for classical bankruptcy prediction.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Benchmark for classical bankruptcy prediction.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### merton1974pricing
- **Citation metadata:** Merton, Robert C. (1974). *On the Pricing of Corporate Debt: The Risk Structure of Interest Rates*. The Journal of Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/j.1540-6261.1974.tb03058.x
- **Current description:** Provides a structural market-based theory of default risk.
- **Main contribution:** Provides a structural market-based theory of default risk.
- **Limitation / critique:** Requires market-value and volatility inputs that are outside the current production panel.
- **How thesis uses it:** Future-work comparator only, not an implemented model.
- **Evidence role:** context_or_future_work
- **Safe thesis use:** Future-work comparator only, not an implemented model.
- **Do not use for:** Do not write as an implemented production feature or model.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### ohlson1980financial
- **Citation metadata:** Ohlson, James A. (1980). *Financial Ratios and the Probabilistic Prediction of Bankruptcy*. Journal of Accounting Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2307/2490395
- **Current description:** Moves bankruptcy prediction toward probabilistic modeling with accounting variables.
- **Main contribution:** Moves bankruptcy prediction toward probabilistic modeling with accounting variables.
- **Limitation / critique:** Still a classical statistical model and does not solve sample selection or rare-event challenges alone.
- **How thesis uses it:** Supports logistic benchmark and probability framing.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports logistic benchmark and probability framing.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### zmijewski1984methodological
- **Citation metadata:** Zmijewski, Mark E. (1984). *Methodological Issues Related to the Estimation of Financial Distress Prediction Models*. Journal of Accounting Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2307/2490859
- **Current description:** Highlights sample selection and estimation problems in distress modeling.
- **Main contribution:** Highlights sample selection and estimation problems in distress modeling.
- **Limitation / critique:** Predates modern SEC-scale panels and machine learning.
- **How thesis uses it:** Supports explicit audit and label-construction discussion.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports explicit audit and label-construction discussion.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### altman1997international
- **Citation metadata:** Altman, Edward I. and Narayanan, Paul (1997). *An International Survey of Business Failure Classification Models*. Financial Markets, Institutions & Instruments.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/1468-0416.00010
- **Current description:** Shows that failure prediction is an international, mature field with many country-specific model variants.
- **Main contribution:** Shows that failure prediction is an international, mature field with many country-specific model variants.
- **Limitation / critique:** A survey of pre-modern methods; not a guide to current data engineering or explainable ML.
- **How thesis uses it:** Prevents overclaiming novelty in bankruptcy prediction itself.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Prevents overclaiming novelty in bankruptcy prediction itself.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### shumway2001forecasting
- **Citation metadata:** Shumway, Tyler (2001). *Forecasting Bankruptcy More Accurately: A Simple Hazard Model*. The Journal of Business.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1086/209665
- **Current description:** Argues that bankruptcy prediction should use time-varying panel logic rather than one static observation per firm.
- **Main contribution:** Argues that bankruptcy prediction should use time-varying panel logic rather than one static observation per firm.
- **Limitation / critique:** Hazard modeling is not the implemented model family in this project.
- **How thesis uses it:** Supports firm-period panel and temporal framing.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports firm-period panel and temporal framing.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### hillegeist2004assessing
- **Citation metadata:** Hillegeist, Stephen A. and Keating, Elizabeth K. and Cram, Donald P. and Lundstedt, Kyle G. (2004). *Assessing the Probability of Bankruptcy*. Review of Accounting Studies.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1023/B:RAST.0000013627.90884.b7
- **Current description:** Compares accounting-score approaches with market-based probability estimates.
- **Main contribution:** Compares accounting-score approaches with market-based probability estimates.
- **Limitation / critique:** Market-based variables are not available for every current row in the production accounting panel.
- **How thesis uses it:** Supports limitation/future-work discussion about market-based features.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports limitation/future-work discussion about market-based features.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### bharath2008forecasting
- **Citation metadata:** Bharath, Sreedhar T. and Shumway, Tyler (2008). *Forecasting Default with the Merton Distance to Default Model*. The Review of Financial Studies.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1093/rfs/hhn044
- **Current description:** Evaluates structural distance-to-default ideas against simpler default forecasting inputs.
- **Main contribution:** Evaluates structural distance-to-default ideas against simpler default forecasting inputs.
- **Limitation / critique:** Not implemented because the current production panel is SEC/FRED based.
- **How thesis uses it:** Future-work and limitation source.
- **Evidence role:** context_or_future_work
- **Safe thesis use:** Future-work and limitation source.
- **Do not use for:** Do not write as an implemented production feature or model.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### campbell2008distress
- **Citation metadata:** Campbell, John Y. and Hilscher, Jens and Szilagyi, Jan (2008). *In Search of Distress Risk*. The Journal of Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/j.1540-6261.2008.01416.x
- **Current description:** Shows distress risk is related to profitability, leverage, market conditions, and dynamic firm characteristics.
- **Main contribution:** Shows distress risk is related to profitability, leverage, market conditions, and dynamic firm characteristics.
- **Limitation / critique:** Uses market variables not fully implemented in the current accounting-focused panel.
- **How thesis uses it:** Supports profitability/leverage/deterioration signal interpretation.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports profitability/leverage/deterioration signal interpretation.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### bauer2014hazard
- **Citation metadata:** Bauer, Julian and Agarwal, Vineet (2014). *Are Hazard Models Superior to Traditional Bankruptcy Prediction Approaches? A Comprehensive Test*. Journal of Banking & Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.jbankfin.2013.12.013
- **Current description:** Tests whether hazard approaches outperform traditional models under comparable settings.
- **Main contribution:** Tests whether hazard approaches outperform traditional models under comparable settings.
- **Limitation / critique:** The thesis uses temporal ML classifiers rather than full hazard models.
- **How thesis uses it:** Supports methodological caution and model-comparison framing.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports methodological caution and model-comparison framing.
- **Do not use for:** Do not use to claim bankruptcy prediction itself is novel.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Design science, dashboard, and decision-support artifact framing

### shneiderman1996eyes
- **Citation metadata:** Shneiderman, Ben (1996). *The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations*. Proceedings of the IEEE Symposium on Visual Languages.
- **Source type / peer-review:** peer_reviewed_conference_paper; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1109/VL.1996.545307
- **Current description:** Supports overview, zoom/filter, and details-on-demand logic.
- **Main contribution:** Supports overview, zoom/filter, and details-on-demand logic.
- **Limitation / critique:** Visualization principle, not financial content.
- **How thesis uses it:** Justifies dashboard layout and filters.
- **Evidence role:** artifact_methodology
- **Safe thesis use:** Justifies dashboard layout and filters.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### hevner2004design
- **Citation metadata:** Hevner, Alan R. and March, Salvatore T. and Park, Jinsoo and Ram, Sudha (2004). *Design Science in Information Systems Research*. MIS Quarterly.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2307/25148625
- **Current description:** Frames IT artifacts as legitimate research outputs when designed and evaluated rigorously.
- **Main contribution:** Frames IT artifacts as legitimate research outputs when designed and evaluated rigorously.
- **Limitation / critique:** General IS methodology, not financial distress-specific.
- **How thesis uses it:** Justifies dashboard/panel/model package as an artifact.
- **Evidence role:** artifact_methodology
- **Safe thesis use:** Justifies dashboard/panel/model package as an artifact.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### peffers2007design
- **Citation metadata:** Peffers, Ken and Tuunanen, Tuure and Rothenberger, Marcus A. and Chatterjee, Samir (2007). *A Design Science Research Methodology for Information Systems Research*. Journal of Management Information Systems.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2753/MIS0742-1222240302
- **Current description:** Provides a process model for problem identification, artifact design, demonstration, evaluation, and communication.
- **Main contribution:** Provides a process model for problem identification, artifact design, demonstration, evaluation, and communication.
- **Limitation / critique:** Methodology source, not dashboard evaluation evidence by itself.
- **How thesis uses it:** Structure artifact chapter.
- **Evidence role:** artifact_methodology
- **Safe thesis use:** Structure artifact chapter.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### chen2012business
- **Citation metadata:** Chen, Hsinchun and Chiang, Roger H. L. and Storey, Veda C. (2012). *Business Intelligence and Analytics: From Big Data to Big Impact*. MIS Quarterly.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2307/41703503
- **Current description:** Frames analytics as a business-impact and decision-support discipline.
- **Main contribution:** Frames analytics as a business-impact and decision-support discipline.
- **Limitation / critique:** Broad analytics source, not a distress model paper.
- **How thesis uses it:** Positions thesis under business analytics/big data.
- **Evidence role:** artifact_methodology
- **Safe thesis use:** Positions thesis under business analytics/big data.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### arnott2014decision
- **Citation metadata:** Arnott, David and Pervan, Graham (2014). *A Critical Analysis of Decision Support Systems Research Revisited: The Rise of Design Science*. Journal of Information Technology.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1057/jit.2014.16
- **Current description:** Links decision support systems research with design science approaches.
- **Main contribution:** Links decision support systems research with design science approaches.
- **Limitation / critique:** Methodological source, not empirical distress evidence.
- **How thesis uses it:** Supports dashboard as a decision-support system.
- **Evidence role:** artifact_methodology
- **Safe thesis use:** Supports dashboard as a decision-support system.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Emerging-market and Russia-specific distress prediction context

### hunter2001failure_risk_russia
- **Citation metadata:** Hunter, John and Isachenkova, Natalia (2001). *Failure Risk: A Comparative Study of UK and Russian Firms*. Journal of Policy Modeling.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/S0161-8938(01)00064-3
- **Current description:** Compares company failure risk in UK and Russian firms using accounting ratios and logit modeling.
- **Main contribution:** Provides direct Russia-specific comparative evidence that failure predictors differ between Russian and UK firms, with profitability more dominant in Russia while gearing and liquidity are more prominent in the UK context.
- **Limitation / critique:** Strong Russia-specific fit, but historical and transition-period conditions limit direct generalization to current Russian public companies or the implemented U.S. panel.
- **How thesis uses it:** Supports the contextual claim that Russian firm-failure prediction may require different predictor interpretation and should not simply import Western predictor assumptions.
- **Evidence role:** contextual_extension_literature
- **Safe thesis use:** Use to argue that Russian failure-risk modeling has distinct institutional and accounting-context issues.
- **Do not use for:** Do not cite as evidence that the current thesis estimates Russian firm failure unless a Russian dataset is added.
- **Access status:** publisher_page_access_limited; public_working_paper_page_available
- **Access/unknown flag:** full_text_access_unknown_or_access_limited_for_journal_version
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### charalambakis2015developed_emerging
- **Citation metadata:** Charalambakis, Evangelos and Garrett, Ian (2015). *On the Prediction of Financial Distress in Developed and Emerging Markets: Does the Choice of Accounting and Market Information Matter? A Comparison of UK and Indian Firms*. Review of Quantitative Finance and Accounting.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1007/s11156-014-0492-y
- **Current description:** Compares financial distress prediction in a developed market and an emerging market using accounting and market information.
- **Main contribution:** Shows that the predictive value of accounting and market variables can differ across institutional settings: market variables help in the UK case, while accounting ratios dominate in India.
- **Limitation / critique:** Useful cross-country evidence, but not direct evidence for Russian firms or for the current U.S. production panel.
- **How thesis uses it:** Supports the literature-review claim that distress predictors are not perfectly portable across institutional settings and that market-context variables need careful empirical validation.
- **Evidence role:** contextual_extension_literature
- **Safe thesis use:** Use as a precedent that predictor sets can behave differently across market institutions.
- **Do not use for:** Do not use to claim the thesis empirically tests India, emerging markets generally, or Russia.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### fedorova2020external_factors_russia
- **Citation metadata:** Fedorova, Elena A.; Musienko, Svetlana O.; Fedorov, Fedor Yu. (2020). *Analysis of the External Factors Influence on the Forecasting of Bankruptcy of Russian Companies*. St Petersburg University Journal of Economic Studies.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.21638/spbu05.2020.106
- **Current description:** Analyzes whether external macroeconomic variables improve bankruptcy prediction for Russian companies across several sectors.
- **Main contribution:** Shows that adding external macroeconomic factors such as GDP growth, key rate, exchange rates, CPI, MICEX growth, and unemployment can improve bankruptcy-prediction explanatory capacity for Russian companies relative to internal factors alone.
- **Limitation / critique:** Highly relevant to macro context, but it is not a U.S. SEC/FRED panel study and should not be used as proof for the current model results.
- **How thesis uses it:** Supports the market-shift/macro-context logic in a Russia-specific setting and helps justify future Russian macro-regime variables.
- **Evidence role:** contextual_extension_literature
- **Safe thesis use:** Use to justify why macro and market-shift variables are plausible in Russian bankruptcy-prediction research.
- **Do not use for:** Do not cite as validation of the exact FRED variables or U.S. model outputs.
- **Access status:** public_full_text_or_article_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### nevredinov2021instrumental_ml
- **Citation metadata:** Nevredinov, Aleksandr R. (2021). *The Instrumental Machine Learning Methods for Corporate Bankruptcy Prediction*. Finance and Credit.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: unknown.
- **DOI/URL:** https://doi.org/10.24891/fc.27.9.2118
- **Current description:** Discusses machine-learning instruments for corporate bankruptcy prediction, with attention to data sources and inputs.
- **Main contribution:** Shows that Russian bankruptcy prediction has an active machine-learning methodological stream and discusses data sources, model potential, and input selection for company analysis.
- **Limitation / critique:** Useful context but not a core anchor; should be subordinate to stronger peer-reviewed empirical sources.
- **How thesis uses it:** Use as a secondary local-context source showing that ML-based bankruptcy prediction is recognized in Russian applied finance literature.
- **Evidence role:** supplementary_context_literature
- **Safe thesis use:** Use to show Russian applied-finance interest in ML bankruptcy forecasting.
- **Do not use for:** Do not use as the main evidence that ML outperforms alternatives in this thesis.
- **Access status:** publisher_page_accessible
- **Access/unknown flag:** peer_review_status_unknown_or_needs_manual_check
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### afanasev2023default_emerging
- **Citation metadata:** Afanasev, Vladislav (2023). *Default Prediction Model for Emerging Capital Market Service Companies*. Journal of Corporate Finance Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.17323/j.jcfr.2073-0438.17.1.2023.64-77
- **Current description:** Compares default-prediction model performance for Russian service firms versus a European control group using several ML/statistical methods.
- **Main contribution:** Tests whether financial-data-only default prediction is less accurate for Russian service companies than for developed European controls, finding higher prediction error for Russian firms and suggesting financial ratios alone may be insufficient.
- **Limitation / critique:** Closest recent Russia-specific empirical match, but sector-specific and not macro-regime-aware.
- **How thesis uses it:** Supports a Russia-specific literature paragraph explaining why contextual variables and careful scope limits matter in emerging capital-market settings.
- **Evidence role:** contextual_extension_literature
- **Safe thesis use:** Use to support the idea that Russian firm default prediction may need richer context than financial ratios alone.
- **Do not use for:** Do not generalize its service-sector results to all Russian industries without caveats.
- **Access status:** journal_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Firm fundamentals, financial ratios, and deterioration features

### taffler1983assessment
- **Citation metadata:** Taffler, Richard J. (1983). *The Assessment of Company Solvency and Performance Using a Statistical Model*. Accounting and Business Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1080/00014788.1983.9729767
- **Current description:** Reinforces the long-standing link between solvency, performance, and accounting data.
- **Main contribution:** Reinforces the long-standing link between solvency, performance, and accounting data.
- **Limitation / critique:** Older statistical model; not enough for modern novelty.
- **How thesis uses it:** Background support for solvency and performance indicators.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Background support for solvency and performance indicators.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### platt1994bankruptcy
- **Citation metadata:** Platt, Harlan D. and Platt, Marjorie B. (1994). *Bankruptcy Prediction with Real Variables*. Journal of Business Finance & Accounting.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/j.1468-5957.1994.tb00332.x
- **Current description:** Broadens the distress-prediction feature discussion beyond pure financial-ratio sets.
- **Main contribution:** Broadens the distress-prediction feature discussion beyond pure financial-ratio sets.
- **Limitation / critique:** Feature universe differs from the SEC/FRED panel.
- **How thesis uses it:** Supports using richer firm-period attributes and context variables.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports using richer firm-period attributes and context variables.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### alaminos2016global
- **Citation metadata:** Alaminos, David and del Castillo, Angel and Fernandez, Manuel Angel (2016). *A Global Model for Bankruptcy Prediction*. PLOS ONE.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1371/journal.pone.0166693
- **Current description:** Demonstrates interest in broader, cross-country bankruptcy-prediction models.
- **Main contribution:** Demonstrates interest in broader, cross-country bankruptcy-prediction models.
- **Limitation / critique:** Global model framing does not remove the need for local SEC data auditing.
- **How thesis uses it:** Supports discussion of scope limits and future international extensions.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports discussion of scope limits and future international extensions.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** full_text_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### tian2017financial
- **Citation metadata:** Tian, Shaonan and Yu, Yan (2017). *Financial Ratios and Bankruptcy Predictions: An International Evidence*. International Review of Economics & Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.iref.2017.07.025
- **Current description:** Shows ratio signals can generalize across countries, while still requiring local validation.
- **Main contribution:** Shows ratio signals can generalize across countries, while still requiring local validation.
- **Limitation / critique:** International comparability differs from this U.S. SEC panel.
- **How thesis uses it:** Supports ratio families and warns against country-blind generalization.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports ratio families and warns against country-blind generalization.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### bragoli2022industrial
- **Citation metadata:** Bragoli, Daniela and Ferretti, Camilla and Ganugi, Piero and Marseguerra, Giovanni and Mezzogori, Davide and Zammori, Francesco (2022). *Machine-Learning Models for Bankruptcy Prediction: Do Industrial Variables Matter?*. Spatial Economic Analysis.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1080/17421772.2021.1977377
- **Current description:** Directly motivates industry metadata and sector-aware analysis.
- **Main contribution:** Directly motivates industry metadata and sector-aware analysis.
- **Limitation / critique:** Different geography/data and not the same dashboard artifact.
- **How thesis uses it:** Supports inclusion of industry metadata and sector summaries.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports inclusion of industry metadata and sector summaries.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### valaskova2023postpandemic
- **Citation metadata:** Valaskova, Katarina and Gajdosikova, Dominika and Belas, Jaroslav (2023). *Bankruptcy Prediction in the Post-Pandemic Period: A Case Study of Visegrad Group Countries*. Oeconomia Copernicana.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.24136/oc.2023.007
- **Current description:** Shows renewed post-pandemic interest in firm failure prediction and financial-health monitoring.
- **Main contribution:** Shows renewed post-pandemic interest in firm failure prediction and financial-health monitoring.
- **Limitation / critique:** Country-specific setting and not SEC/FRED scale.
- **How thesis uses it:** Recent context for why distress/resilience analysis remains current after large market shocks.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Recent context for why distress/resilience analysis remains current after large market shocks.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### billios2024power
- **Citation metadata:** Billios, Dimitrios and Seretidou, Dimitra and Stavropoulos, Antonios (2024). *The Power of Numerical Indicators in Predicting Bankruptcy: A Systematic Review*. Journal of Risk and Financial Management.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.3390/jrfm17100433
- **Current description:** Recent review evidence that numerical financial indicators and cash-flow information remain useful for bankruptcy prediction.
- **Main contribution:** Recent review evidence that numerical financial indicators and cash-flow information remain useful for bankruptcy prediction.
- **Limitation / critique:** Review scope is narrow and does not provide the thesis data architecture.
- **How thesis uses it:** Modern support that accounting/numerical indicators remain relevant.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Modern support that accounting/numerical indicators remain relevant.
- **Do not use for:** Do not cite outside the stated data scope or method scope.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Interpretability and explainable ML

### ribeiro2016trust
- **Citation metadata:** Ribeiro, Marco Tulio and Singh, Sameer and Guestrin, Carlos (2016). *"Why Should I Trust You?": Explaining the Predictions of Any Classifier*. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.
- **Source type / peer-review:** peer_reviewed_conference_paper; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1145/2939672.2939778
- **Current description:** Introduces LIME-style local explanations for black-box predictions.
- **Main contribution:** Introduces LIME-style local explanations for black-box predictions.
- **Limitation / critique:** Local explanations can be unstable and do not establish causality.
- **How thesis uses it:** Supports interpretability/trust section.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports interpretability/trust section.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### lundberg2017unified
- **Citation metadata:** Lundberg, Scott M. and Lee, Su-In (2017). *A Unified Approach to Interpreting Model Predictions*. Advances in Neural Information Processing Systems 30.
- **Source type / peer-review:** peer_reviewed_conference_paper; peer-reviewed status: yes.
- **DOI/URL:** https://papers.neurips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions
- **Current description:** Introduces SHAP as a unified additive explanation approach.
- **Main contribution:** Introduces SHAP as a unified additive explanation approach.
- **Limitation / critique:** Explanations are not causal proof.
- **How thesis uses it:** Supports feature-contribution interpretation language.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports feature-contribution interpretation language.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** full_text_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### guidotti2018survey
- **Citation metadata:** Guidotti, Riccardo and Monreale, Anna and Ruggieri, Salvatore and Turini, Franco and Giannotti, Fosca and Pedreschi, Dino (2018). *A Survey of Methods for Explaining Black Box Models*. ACM Computing Surveys.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1145/3236009
- **Current description:** Provides a broad taxonomy of black-box explanation methods.
- **Main contribution:** Provides a broad taxonomy of black-box explanation methods.
- **Limitation / critique:** General XAI survey, not finance-specific.
- **How thesis uses it:** Supports XAI method classification and caution.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports XAI method classification and caution.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### bussmann2021explainable
- **Citation metadata:** Bussmann, Niklas and Giudici, Paolo and Marinelli, Dimitri and Papenbrock, Jochen (2021). *Explainable Machine Learning in Credit Risk Management*. Computational Economics.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1007/s10614-020-10042-0
- **Current description:** Connects explainable ML to financial-risk management practice.
- **Main contribution:** Connects explainable ML to financial-risk management practice.
- **Limitation / critique:** Credit-risk context is related but not identical to firm failure/resilience.
- **How thesis uses it:** Finance-specific XAI support.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Finance-specific XAI support.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### gramegna2021shap
- **Citation metadata:** Gramegna, Alex and Giudici, Paolo (2021). *SHAP and LIME: An Evaluation of Discriminative Power in Credit Risk*. Frontiers in Artificial Intelligence.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.3389/frai.2021.752558
- **Current description:** Evaluates SHAP and LIME in a financial-risk setting.
- **Main contribution:** Evaluates SHAP and LIME in a financial-risk setting.
- **Limitation / critique:** Credit risk, not SEC corporate distress labels.
- **How thesis uses it:** Additional finance-specific XAI reference.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Additional finance-specific XAI reference.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** full_text_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### zhang2022xai
- **Citation metadata:** Zhang, Zijiao and Wu, Chong and Qu, Shiyou and Chen, Xiaofang (2022). *An Explainable Artificial Intelligence Approach for Financial Distress Prediction*. Information Processing & Management.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.ipm.2022.102988
- **Current description:** Directly links XAI to financial distress prediction.
- **Main contribution:** Directly links XAI to financial distress prediction.
- **Limitation / critique:** Specific method/data differ from this thesis.
- **How thesis uses it:** Direct support for interpretable financial-distress modeling.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Direct support for interpretable financial-distress modeling.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### molnar2025interpretable
- **Citation metadata:** Molnar, Christoph (2025). *Interpretable Machine Learning: A Guide for Making Black Box Models Explainable*. Self-published open book.
- **Source type / peer-review:** book; peer-reviewed status: unknown.
- **DOI/URL:** https://christophm.github.io/interpretable-ml-book/
- **Current description:** Clear practical reference for permutation importance, SHAP, PDP/ALE, and interpretation limits.
- **Main contribution:** Clear practical reference for permutation importance, SHAP, PDP/ALE, and interpretation limits.
- **Limitation / critique:** Book/reference source, not a peer-reviewed journal article.
- **How thesis uses it:** Practical interpretation guide.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Practical interpretation guide.
- **Do not use for:** Do not use to claim feature importance proves causality.
- **Access status:** full_text_or_public_page_accessible
- **Access/unknown flag:** peer_review_status_unknown_or_not_applicable
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Machine learning, rare-event evaluation, and temporal validation

### breiman2001random
- **Citation metadata:** Breiman, Leo (2001). *Random Forests*. Machine Learning.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1023/A:1010933404324
- **Current description:** Foundational source for random forests.
- **Main contribution:** Foundational source for random forests.
- **Limitation / critique:** Algorithm paper, not finance-specific.
- **How thesis uses it:** Cite for model method.
- **Evidence role:** method_foundation
- **Safe thesis use:** Cite for model method.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### friedman2001greedy
- **Citation metadata:** Friedman, Jerome H. (2001). *Greedy Function Approximation: A Gradient Boosting Machine*. The Annals of Statistics.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1214/aos/1013203451
- **Current description:** Foundational source for gradient boosting.
- **Main contribution:** Foundational source for gradient boosting.
- **Limitation / critique:** Algorithm paper, not finance-specific.
- **How thesis uses it:** Cite for gradient boosting method.
- **Evidence role:** method_foundation
- **Safe thesis use:** Cite for gradient boosting method.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### chawla2002smote
- **Citation metadata:** Chawla, Nitesh V. and Bowyer, Kevin W. and Hall, Lawrence O. and Kegelmeyer, W. Philip (2002). *SMOTE: Synthetic Minority Over-Sampling Technique*. Journal of Artificial Intelligence Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1613/jair.953
- **Current description:** Introduces a major class-imbalance method.
- **Main contribution:** Introduces a major class-imbalance method.
- **Limitation / critique:** Synthetic oversampling can distort time-ordered financial panels if used carelessly.
- **How thesis uses it:** Discuss as an imbalance method considered conceptually but not central.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Discuss as an imbalance method considered conceptually but not central.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### davis2006relationship
- **Citation metadata:** Davis, Jesse and Goadrich, Mark (2006). *The Relationship between Precision-Recall and ROC Curves*. Proceedings of the 23rd International Conference on Machine Learning.
- **Source type / peer-review:** peer_reviewed_conference_paper; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1145/1143844.1143874
- **Current description:** Shows how precision-recall and ROC views differ.
- **Main contribution:** Shows how precision-recall and ROC views differ.
- **Limitation / critique:** General ML evaluation paper, not finance-specific.
- **How thesis uses it:** Supports PR-curve interpretation.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports PR-curve interpretation.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### fawcett2006roc
- **Citation metadata:** Fawcett, Tom (2006). *An Introduction to ROC Analysis*. Pattern Recognition Letters.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.patrec.2005.10.010
- **Current description:** Explains ROC analysis and related evaluation concepts.
- **Main contribution:** Explains ROC analysis and related evaluation concepts.
- **Limitation / critique:** ROC-AUC can remain optimistic for rare positives.
- **How thesis uses it:** Use with PR-AUC sources to discuss metric tradeoffs.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Use with PR-AUC sources to discuss metric tradeoffs.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### burez2009handling
- **Citation metadata:** Burez, Jonathan and Van den Poel, Dirk (2009). *Handling Class Imbalance in Customer Churn Prediction*. Expert Systems with Applications.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.eswa.2009.05.027
- **Current description:** Shows class imbalance is a practical predictive-modeling issue beyond one domain.
- **Main contribution:** Shows class imbalance is a practical predictive-modeling issue beyond one domain.
- **Limitation / critique:** Churn is not distress; use only for general imbalance logic.
- **How thesis uses it:** Secondary support for imbalance handling concerns.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Secondary support for imbalance handling concerns.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### pedregosa2011scikit
- **Citation metadata:** Pedregosa, Fabian and Varoquaux, Gael and Gramfort, Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel, Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss, Ron and Dubourg, Vincent and VanderPlas, Jake and Passos, Alexandre and Cournapeau, David and Brucher, Matthieu and Perrot, Matthieu and Duchesnay, Edouard (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://www.jmlr.org/papers/v12/pedregosa11a.html
- **Current description:** Citable source for the modeling software ecosystem used in Python.
- **Main contribution:** Citable source for the modeling software ecosystem used in Python.
- **Limitation / critique:** Software citation, not a theory source.
- **How thesis uses it:** Cite for implementation reproducibility.
- **Evidence role:** method_foundation
- **Safe thesis use:** Cite for implementation reproducibility.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** full_text_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### lessmann2015benchmarking
- **Citation metadata:** Lessmann, Stefan and Baesens, Bart and Seow, Hsin-Vonn and Thomas, Lyn C. (2015). *Benchmarking State-of-the-Art Classification Algorithms for Credit Scoring: An Update of Research*. European Journal of Operational Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.ejor.2015.05.030
- **Current description:** Provides modern classification benchmarking evidence in a related financial-risk domain.
- **Main contribution:** Provides modern classification benchmarking evidence in a related financial-risk domain.
- **Limitation / critique:** Credit scoring is not identical to SEC-based firm failure/resilience.
- **How thesis uses it:** Supports comparing multiple model families rather than relying on one algorithm.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports comparing multiple model families rather than relying on one algorithm.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### saito2015precision
- **Citation metadata:** Saito, Takaya and Rehmsmeier, Marc (2015). *The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets*. PLOS ONE.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1371/journal.pone.0118432
- **Current description:** Directly argues for precision-recall plots under class imbalance.
- **Main contribution:** Directly argues for precision-recall plots under class imbalance.
- **Limitation / critique:** General ML evaluation source, not distress-specific.
- **How thesis uses it:** Justifies PR-AUC for strict distress and broader pressure targets.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Justifies PR-AUC for strict distress and broader pressure targets.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** full_text_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### barboza2017machine
- **Citation metadata:** Barboza, Flavio and Kimura, Herbert and Altman, Edward (2017). *Machine Learning Models and Bankruptcy Prediction*. Expert Systems with Applications.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.eswa.2017.04.006
- **Current description:** Shows ML methods can improve bankruptcy-prediction performance relative to classical methods in some settings.
- **Main contribution:** Shows ML methods can improve bankruptcy-prediction performance relative to classical methods in some settings.
- **Limitation / critique:** Performance gains depend on data, validation, and target definition.
- **How thesis uses it:** Core support for random forest and gradient boosting benchmarks.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Core support for random forest and gradient boosting benchmarks.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### kim2020corporate
- **Citation metadata:** Kim, Minjun and Cho, Seonghoon and Ryu, Doojin (2020). *Corporate Default Predictions Using Machine Learning: Literature Review*. Sustainability.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.3390/su12166325
- **Current description:** Reviews machine-learning approaches to corporate default prediction.
- **Main contribution:** Reviews machine-learning approaches to corporate default prediction.
- **Limitation / critique:** Review-level evidence; not a direct empirical benchmark for this thesis.
- **How thesis uses it:** Additional recent ML/default review source.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Additional recent ML/default review source.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### charalambous2022maximizing
- **Citation metadata:** Charalambous, Chris and Martzoukos, Spiros H. and Taoushianis, Zenon (2022). *Estimating Corporate Bankruptcy Forecasting Models by Maximizing Discriminatory Power*. Review of Quantitative Finance and Accounting.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1007/s11156-021-00995-0
- **Current description:** Shows that optimizing discriminatory power can improve out-of-sample bankruptcy and financial-distress forecasts.
- **Main contribution:** Shows that optimizing discriminatory power can improve out-of-sample bankruptcy and financial-distress forecasts.
- **Limitation / critique:** Does not provide this thesis dashboard artifact.
- **How thesis uses it:** Supports dashboard and metric interpretation beyond accuracy.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports dashboard and metric interpretation beyond accuracy.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### sun2023company
- **Citation metadata:** Sun, Xiaoxiao (2023). *Company Failure Prediction with Machine Learning*. ECAI 2023: Frontiers in Artificial Intelligence and Applications.
- **Source type / peer-review:** peer_reviewed_conference_paper; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.3233/FAIA230838
- **Current description:** Recent conference evidence that company-failure prediction remains an ML problem.
- **Main contribution:** Recent conference evidence that company-failure prediction remains an ML problem.
- **Limitation / critique:** Conference paper and not a replacement for journal review sources.
- **How thesis uses it:** Optional recent ML context.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Optional recent ML context.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### dasilas2024machine
- **Citation metadata:** Dasilas, Apostolos and Rigani, Anna (2024). *Machine Learning Techniques in Bankruptcy Prediction: A Systematic Literature Review*. Expert Systems with Applications.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.eswa.2024.124761
- **Current description:** Current synthesis of ML bankruptcy-prediction research and common design choices.
- **Main contribution:** Current synthesis of ML bankruptcy-prediction research and common design choices.
- **Limitation / critique:** A review; it does not supply this thesis dataset or artifact.
- **How thesis uses it:** Main recent review source to show the field is current.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Main recent review source to show the field is current.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### zhao2024survey
- **Citation metadata:** Zhao, Jinxian and Ouenniche, Jamal and De Smedt, Johannes (2024). *Survey, Classification and Critical Analysis of the Literature on Corporate Bankruptcy and Financial Distress Prediction*. Machine Learning with Applications.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.mlwa.2024.100527
- **Current description:** Recent critical survey that situates bankruptcy and financial distress prediction as an active statistical and AI research area.
- **Main contribution:** Recent critical survey that situates bankruptcy and financial distress prediction as an active statistical and AI research area.
- **Limitation / critique:** A survey and not a validation of the thesis panel.
- **How thesis uses it:** Modern literature anchor for the ML/business-failure section.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Modern literature anchor for the ML/business-failure section.
- **Do not use for:** Do not use to claim algorithm choice alone creates thesis novelty.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Macroeconomic conditions, credit cycles, and market-shift/default context

### bernanke1999financial
- **Citation metadata:** Bernanke, Ben S. and Gertler, Mark and Gilchrist, Simon (1999). *The Financial Accelerator in a Quantitative Business Cycle Framework*. Handbook of Macroeconomics.
- **Source type / peer-review:** book_chapter; peer-reviewed status: unknown.
- **DOI/URL:** https://doi.org/10.1016/S1574-0048(99)10034-X
- **Current description:** Explains how credit frictions can amplify business-cycle shocks.
- **Main contribution:** Explains how credit frictions can amplify business-cycle shocks.
- **Limitation / critique:** Macro theory, not a firm-level empirical model.
- **How thesis uses it:** Theoretical support for macro-regime framing.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Theoretical support for macro-regime framing.
- **Do not use for:** Do not use to claim macro variables dominate without empirical support.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited; peer_review_status_unknown_or_not_applicable
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### longstaff2005corporate
- **Citation metadata:** Longstaff, Francis A. and Mithal, Sanjay and Neis, Eric (2005). *Corporate Yield Spreads: Default Risk or Liquidity? New Evidence from the Credit Default Swap Market*. The Journal of Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/j.1540-6261.2005.00797.x
- **Current description:** Shows corporate spreads reflect both default and liquidity components.
- **Main contribution:** Shows corporate spreads reflect both default and liquidity components.
- **Limitation / critique:** Market spread decomposition, not accounting-panel construction.
- **How thesis uses it:** Supports caution in interpreting macro/credit variables.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports caution in interpreting macro/credit variables.
- **Do not use for:** Do not use to claim macro variables dominate without empirical support.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### duffie2007multi
- **Citation metadata:** Duffie, Darrell and Saita, Leandro and Wang, Ke (2007). *Multi-Period Corporate Default Prediction with Stochastic Covariates*. Journal of Financial Economics.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.jfineco.2005.10.011
- **Current description:** Links corporate default prediction to time-varying firm and macro-financial covariates.
- **Main contribution:** Links corporate default prediction to time-varying firm and macro-financial covariates.
- **Limitation / critique:** Different event definition and model design than the current SEC/FRED panel.
- **How thesis uses it:** Supports dynamic macro-context variables and forward horizons.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports dynamic macro-context variables and forward horizons.
- **Do not use for:** Do not use to claim macro variables dominate without empirical support.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### gilchrist2012credit
- **Citation metadata:** Gilchrist, Simon and Zakrajsek, Egon (2012). *Credit Spreads and Business Cycle Fluctuations*. American Economic Review.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1257/aer.102.4.1692
- **Current description:** Shows credit spreads contain business-cycle information.
- **Main contribution:** Shows credit spreads contain business-cycle information.
- **Limitation / critique:** Macro-finance source, not firm SEC accounting by itself.
- **How thesis uses it:** Supports credit-spread and financial-conditions variables.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Supports credit-spread and financial-conditions variables.
- **Do not use for:** Do not use to claim macro variables dominate without empirical support.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### tinoco2013financial
- **Citation metadata:** Tinoco, Mario H. and Wilson, Nick (2013). *Financial Distress and Bankruptcy Prediction among Listed Companies Using Accounting, Market and Macroeconomic Variables*. International Review of Financial Analysis.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1016/j.irfa.2013.02.013
- **Current description:** Directly supports combining accounting, market, and macroeconomic variables for listed-company distress prediction.
- **Main contribution:** Directly supports combining accounting, market, and macroeconomic variables for listed-company distress prediction.
- **Limitation / critique:** Does not provide the current thesis artifact, target hierarchy, or dashboard.
- **How thesis uses it:** Core support for the SEC plus FRED design.
- **Evidence role:** core_or_supporting_literature
- **Safe thesis use:** Core support for the SEC plus FRED design.
- **Do not use for:** Do not use to claim macro variables dominate without empirical support.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### davydov2022us_russian_markets
- **Citation metadata:** Davydov, A. Yu. (2022). *US and Russian Financial Markets: Comparative Analysis*. Studies on Russian Economic Development.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1134/S1019331622210080
- **Current description:** Compares U.S. and Russian financial markets at the market-structure/context level.
- **Main contribution:** Provides background evidence that Russian and U.S. financial markets differ structurally, supporting caution when transferring market-shift assumptions across countries.
- **Limitation / critique:** Not a corporate bankruptcy paper; weak if used as direct distress-prediction evidence.
- **How thesis uses it:** Use as a secondary macro-financial context source if discussing why Russia and the U.S. should not be treated as interchangeable empirical environments.
- **Evidence role:** background_context_literature
- **Safe thesis use:** Use for general cross-market context only.
- **Do not use for:** Do not use to claim Russian macro variables improve firm-level failure prediction.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### chicagofed2026nfci
- **Citation metadata:** Federal Reserve Bank of Chicago (2026). *National Financial Conditions Index*. Federal Reserve Bank of Chicago.
- **Source type / peer-review:** official_data_documentation; peer-reviewed status: no.
- **DOI/URL:** https://www.chicagofed.org/research/data/nfci/current-data
- **Current description:** Official documentation for NFCI-style financial-condition context.
- **Main contribution:** Official documentation for NFCI-style financial-condition context.
- **Limitation / critique:** Index context, not firm-level causality.
- **How thesis uses it:** Supports market-health/financial-conditions interpretation.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Supports market-health/financial-conditions interpretation.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** official_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Missing data, data integrity, and accounting-data limitations

### rubin1976inference
- **Citation metadata:** Rubin, Donald B. (1976). *Inference and Missing Data*. Biometrika.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1093/biomet/63.3.581
- **Current description:** Introduces central missing-data mechanism concepts.
- **Main contribution:** Introduces central missing-data mechanism concepts.
- **Limitation / critique:** General statistical theory; not an accounting filing guide.
- **How thesis uses it:** Theoretical foundation for missingness treatment.
- **Evidence role:** data_integrity_methodology
- **Safe thesis use:** Theoretical foundation for missingness treatment.
- **Do not use for:** Do not use to justify filling missing SEC values with invented facts.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### graham2009missing
- **Citation metadata:** Graham, John W. (2009). *Missing Data Analysis: Making It Work in the Real World*. Annual Review of Psychology.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1146/annurev.psych.58.110405.085530
- **Current description:** Practical review of missing-data risks and approaches.
- **Main contribution:** Practical review of missing-data risks and approaches.
- **Limitation / critique:** Not accounting-specific.
- **How thesis uses it:** Supports pragmatic missingness diagnostics.
- **Evidence role:** data_integrity_methodology
- **Safe thesis use:** Supports pragmatic missingness diagnostics.
- **Do not use for:** Do not use to justify filling missing SEC values with invented facts.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### vanbuuren2018flexible
- **Citation metadata:** van Buuren, Stef (2018). *Flexible Imputation of Missing Data*. CRC Press.
- **Source type / peer-review:** book; peer-reviewed status: unknown.
- **DOI/URL:** https://doi.org/10.1201/9780429492259
- **Current description:** Practical reference for imputation approaches.
- **Main contribution:** Practical reference for imputation approaches.
- **Limitation / critique:** The thesis mostly avoids aggressive imputation, so cite for context rather than implementation.
- **How thesis uses it:** Explains why imputation is an option but not automatically appropriate.
- **Evidence role:** data_integrity_methodology
- **Safe thesis use:** Explains why imputation is an option but not automatically appropriate.
- **Do not use for:** Do not use to justify filling missing SEC values with invented facts.
- **Access status:** metadata_verified_full_text_access_unknown_or_book_access_limited
- **Access/unknown flag:** full_text_access_unknown_or_access_limited; peer_review_status_unknown_or_not_applicable
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### little2019missing
- **Citation metadata:** Little, Roderick J. A. and Rubin, Donald B. (2019). *Statistical Analysis with Missing Data*. Wiley.
- **Source type / peer-review:** book; peer-reviewed status: unknown.
- **DOI/URL:** https://doi.org/10.1002/9781119482260
- **Current description:** Foundational treatment of missing-data mechanisms and analysis.
- **Main contribution:** Foundational treatment of missing-data mechanisms and analysis.
- **Limitation / critique:** General statistics book, not SEC-specific.
- **How thesis uses it:** Supports missingness policy and refusal to invent null values.
- **Evidence role:** data_integrity_methodology
- **Safe thesis use:** Supports missingness policy and refusal to invent null values.
- **Do not use for:** Do not use to justify filling missing SEC values with invented facts.
- **Access status:** metadata_verified_full_text_access_unknown_or_book_access_limited
- **Access/unknown flag:** full_text_access_unknown_or_access_limited; peer_review_status_unknown_or_not_applicable
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Official data sources and empirical context

### gornostaev2022realtime_russia
- **Citation metadata:** Gornostaev, Dmitry; Ponomarenko, Alexey; Seleznev, Sergei; Sterkhova, Aleksandra (2022). *A Real-Time Historical Database of Macroeconomic Indicators for Russia*. Russian Journal of Money and Finance.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.31477/rjmf.202201.88
- **Current description:** Describes a Bank of Russia real-time historical database of macroeconomic indicators and the importance of data vintages.
- **Main contribution:** Documents a Russian macroeconomic vintage database and shows that revisions can be substantial, supporting the importance of using information available at the time rather than revised data.
- **Limitation / critique:** Important for macro timing, but not evidence that macro variables predict firm failure by themselves.
- **How thesis uses it:** Supports timing/revision logic for any future Russian macro-regime extension and reinforces the general thesis emphasis on prediction-date validity.
- **Evidence role:** official_data_and_method_context
- **Safe thesis use:** Use to support careful macro-data timing and Russian macro-data availability.
- **Do not use for:** Do not cite as firm-level bankruptcy evidence.
- **Access status:** open_access_article_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### sec2024edgarapi
- **Citation metadata:** U.S. Securities and Exchange Commission (2024). *EDGAR Application Programming Interfaces*. SEC.gov.
- **Source type / peer-review:** official_data_documentation; peer-reviewed status: no.
- **DOI/URL:** https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- **Current description:** Official EDGAR API reference for SEC-company metadata and filings context.
- **Main contribution:** Official EDGAR API reference for SEC-company metadata and filings context.
- **Limitation / critique:** Documentation, not model evidence.
- **How thesis uses it:** Cite for reproducibility and data-access context.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Cite for reproducibility and data-access context.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** official_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### fed2025financialstability
- **Citation metadata:** Board of Governors of the Federal Reserve System (2025). *Financial Stability Report*. Federal Reserve Board.
- **Source type / peer-review:** official_report; peer-reviewed status: no.
- **DOI/URL:** https://www.federalreserve.gov/publications/financial-stability-report.htm
- **Current description:** Provides official context for macro-financial vulnerabilities and corporate/credit conditions.
- **Main contribution:** Provides official context for macro-financial vulnerabilities and corporate/credit conditions.
- **Limitation / critique:** Contextual report, not a firm-level prediction paper.
- **How thesis uses it:** Recent context source for market shifts and credit conditions.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Recent context source for market shifts and credit conditions.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** official_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### spglobal2025bankruptcies
- **Citation metadata:** S&P Global Market Intelligence (2025). *U.S. Corporate Bankruptcy Filings*. S&P Global Market Intelligence.
- **Source type / peer-review:** industry_report; peer-reviewed status: no.
- **DOI/URL:** https://www.spglobal.com/market-intelligence/en/news-insights/latest-news-headlines/us-bankruptcy-tracker
- **Current description:** Recent industry context showing corporate distress remains relevant.
- **Main contribution:** Recent industry context showing corporate distress remains relevant.
- **Limitation / critique:** Industry report and not part of the production training data.
- **How thesis uses it:** Context only, not model source.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Context only, not model source.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** public_publisher_page_accessible_full_report_may_require_access
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### cbr2026financial_stability
- **Citation metadata:** Bank of Russia (2026). *Financial Stability*. Bank of Russia official financial stability portal.
- **Source type / peer-review:** official_data_documentation; peer-reviewed status: not_applicable.
- **DOI/URL:** https://www.cbr.ru/eng/finstab/
- **Current description:** Official Bank of Russia source for financial-stability monitoring, stress testing, and macroprudential context.
- **Main contribution:** Defines and documents the Bank of Russia financial-stability monitoring context, including shocks, vulnerabilities, resilience, and macroprudential/stress-testing materials.
- **Limitation / critique:** Not an academic paper; use as contextual data documentation only.
- **How thesis uses it:** Use only if discussing a possible Russian macro-stability extension or official Russian macro-financial context.
- **Evidence role:** official_data_and_context_documentation
- **Safe thesis use:** Use to cite Russian financial-stability context and potential macro-regime source material.
- **Do not use for:** Do not treat as peer-reviewed evidence for firm-level failure prediction.
- **Access status:** official_public_page_accessible
- **Access/unknown flag:** peer_review_status_unknown_or_not_applicable
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### fredapi
- **Citation metadata:** Federal Reserve Bank of St. Louis (2026). *FRED API*. FRED Documentation.
- **Source type / peer-review:** official_data_documentation; peer-reviewed status: no.
- **DOI/URL:** https://fred.stlouisfed.org/docs/api/fred/
- **Current description:** Official source for FRED macro-data retrieval.
- **Main contribution:** Official source for FRED macro-data retrieval.
- **Limitation / critique:** Documentation, not a theory source.
- **How thesis uses it:** Primary macro-data source citation.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Primary macro-data source citation.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** official_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### fredwhat
- **Citation metadata:** Federal Reserve Bank of St. Louis (2026). *What Is FRED?*. FRED Help.
- **Source type / peer-review:** official_data_documentation; peer-reviewed status: no.
- **DOI/URL:** https://fredhelp.stlouisfed.org/fred/about/about-fred/what-is-fred/
- **Current description:** Describes FRED as a source for economic data.
- **Main contribution:** Describes FRED as a source for economic data.
- **Limitation / critique:** Background documentation only.
- **How thesis uses it:** Basic source description in data chapter.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Basic source description in data chapter.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** official_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### sec2026financial
- **Citation metadata:** U.S. Securities and Exchange Commission (2026). *Financial Statement Data Sets*. SEC.gov.
- **Source type / peer-review:** official_data_documentation; peer-reviewed status: no.
- **DOI/URL:** https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets
- **Current description:** Official source for SEC Financial Statement Data Sets used to build the panel.
- **Main contribution:** Official source for SEC Financial Statement Data Sets used to build the panel.
- **Limitation / critique:** Official documentation, not peer-reviewed theory.
- **How thesis uses it:** Primary data source citation.
- **Evidence role:** data_or_context_source
- **Safe thesis use:** Primary data source citation.
- **Do not use for:** Do not use as peer-reviewed theory or model-performance evidence.
- **Access status:** official_or_public_page_accessible
- **Access/unknown flag:** none_flagged
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Bucket: Strategic management and resilience framing

### hannan1984structural
- **Citation metadata:** Hannan, Michael T. and Freeman, John (1984). *Structural Inertia and Organizational Change*. American Sociological Review.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.2307/2095567
- **Current description:** Explains why organizations may have difficulty adapting under environmental shifts.
- **Main contribution:** Explains why organizations may have difficulty adapting under environmental shifts.
- **Limitation / critique:** Sociological theory, not financial ratio modeling.
- **How thesis uses it:** Frames failure under market shifts conceptually.
- **Evidence role:** theoretical_framing
- **Safe thesis use:** Frames failure under market shifts conceptually.
- **Do not use for:** Do not use as direct proof of measured financial resilience.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### barney1991firm
- **Citation metadata:** Barney, Jay (1991). *Firm Resources and Sustained Competitive Advantage*. Journal of Management.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1177/014920639101700108
- **Current description:** Frames persistent firm differences and resource advantages.
- **Main contribution:** Frames persistent firm differences and resource advantages.
- **Limitation / critique:** Does not directly measure SEC ratios or failure targets.
- **How thesis uses it:** High-level success/resilience framing only.
- **Evidence role:** theoretical_framing
- **Safe thesis use:** High-level success/resilience framing only.
- **Do not use for:** Do not use as direct proof of measured financial resilience.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### teece1997dynamic
- **Citation metadata:** Teece, David J. and Pisano, Gary and Shuen, Amy (1997). *Dynamic Capabilities and Strategic Management*. Strategic Management Journal.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1002/(SICI)1097-0266(199708)18:7%3C509::AID-SMJ882%3E3.0.CO;2-Z
- **Current description:** Explains adaptation and capability renewal under changing environments.
- **Main contribution:** Explains adaptation and capability renewal under changing environments.
- **Limitation / critique:** The thesis measures financial signals, not capabilities directly.
- **How thesis uses it:** Frames market shifts and adaptation without overclaiming unobserved capabilities.
- **Evidence role:** theoretical_framing
- **Safe thesis use:** Frames market shifts and adaptation without overclaiming unobserved capabilities.
- **Do not use for:** Do not use as direct proof of measured financial resilience.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### linnenluecke2017resilience
- **Citation metadata:** Linnenluecke, Martina K. (2017). *Resilience in Business and Management Research: A Review of Influential Publications and a Research Agenda*. International Journal of Management Reviews.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1111/ijmr.12076
- **Current description:** Reviews resilience concepts in business and management literature.
- **Main contribution:** Reviews resilience concepts in business and management literature.
- **Limitation / critique:** Broad review; not a direct measurement recipe for SEC data.
- **How thesis uses it:** Literature anchor for resilience framing.
- **Evidence role:** theoretical_framing
- **Safe thesis use:** Literature anchor for resilience framing.
- **Do not use for:** Do not use as direct proof of measured financial resilience.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### duchek2020resilience
- **Citation metadata:** Duchek, Stephanie (2020). *Organizational Resilience: A Capability-Based Conceptualization*. Business Research.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1007/s40685-019-0085-7
- **Current description:** Conceptualizes resilience as capabilities for anticipation, coping, and adaptation.
- **Main contribution:** Conceptualizes resilience as capabilities for anticipation, coping, and adaptation.
- **Limitation / critique:** Does not provide financial-target definitions for public firms.
- **How thesis uses it:** Supports naming the success target as resilience with caveats.
- **Evidence role:** theoretical_framing
- **Safe thesis use:** Supports naming the success target as resilience with caveats.
- **Do not use for:** Do not use as direct proof of measured financial resilience.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

### hepfer2022organizational
- **Citation metadata:** Hepfer, Martin and Lawrence, Thomas B. (2022). *The Heterogeneity of Organizational Resilience: Exploring Functional, Operational and Strategic Resilience*. Organization Theory.
- **Source type / peer-review:** academic_journal_article; peer-reviewed status: yes.
- **DOI/URL:** https://doi.org/10.1177/26317877221074701
- **Current description:** Differentiates forms of resilience rather than treating resilience as one simple outcome.
- **Main contribution:** Differentiates forms of resilience rather than treating resilience as one simple outcome.
- **Limitation / critique:** Not a financial prediction model.
- **How thesis uses it:** Supports careful wording around success/resilience target.
- **Evidence role:** theoretical_framing
- **Safe thesis use:** Supports careful wording around success/resilience target.
- **Do not use for:** Do not use as direct proof of measured financial resilience.
- **Access status:** metadata_verified_full_text_access_unknown_or_may_be_paywalled
- **Access/unknown flag:** full_text_access_unknown_or_access_limited
- **Verification request:** Check metadata, access/full-text availability, whether the source really supports this thesis use, and whether the limitation is fair.

## Desired Perplexity Output Format

Please return a table with these columns: citation_key, metadata_status, access_status, peer_review_status, summary_accuracy, thesis_alignment, safe_use_revision, limitation_revision, keep_or_replace, suggested_open_access_alternative, notes.

Also provide a short prioritized list of the 20-30 strongest sources to read closely before final thesis submission, emphasizing open-access or full-text-accessible sources.
