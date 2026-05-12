# Legal Full-Text Access and Reading Notes

Last updated: 2026-05-12

## Purpose

This note records what has been legally checked, downloaded, read, and summarized for thesis writing. It separates three things that should not be confused:

- citation metadata verified;
- legal full-text or article-page access found;
- enough full text read to discuss methods/results in the thesis.

The automated audit uses Unpaywall and official source URLs only. It does not use piracy, shadow libraries, or personal browser extensions.

## Outputs Created

| Output | Path |
| --- | --- |
| Full legal-access audit | `reports/literature/legal_full_text_access_audit.csv` |
| Retrieval checklist | `reports/literature/full_text_retrieval_checklist.csv` |
| Legal PDFs downloaded | `reports/literature/legal_full_text_pdfs/` |
| Extracted text from legal PDFs | `reports/literature/legal_full_text_extracts/` |
| Reproducible audit script | `scripts/docs/audit_legal_full_text_access.py` |

## Access Audit Summary

The Unpaywall-based audit checked all 75 bibliography entries.

| Access bucket | Count | Meaning |
| --- | ---: | --- |
| `open_access_pdf_downloaded` | 10 | Legal OA PDF was downloaded and text was extracted locally. |
| `open_access_landing_page_no_pdf` | 9 | Legal OA/article landing page exists, but no direct PDF URL was provided by Unpaywall. |
| `open_access_pdf_download_failed` | 11 | Legal OA PDF URL exists, but automated download failed because of publisher blocking, timeout, or non-PDF response. Manual browser download may still work. |
| `not_open_access_by_unpaywall` | 33 | Unpaywall marks it closed; use university library/VPN, author repository, ResearchGate request, or author email. |
| `non_doi_or_official_url_manual_check` | 11 | Official/documentation/web sources that need manual page checks rather than DOI checks. |
| `unpaywall_lookup_failed` | 1 | Unpaywall lookup failed; manual check required. |

## Local Full-Text PDFs Downloaded

| Key | Evidence level | Thesis use |
| --- | --- | --- |
| `afanasev2023default_emerging` | Full legal PDF downloaded and extracted | Russian service-firm default prediction and emerging-market caution. |
| `alaminos2016global` | Full legal PDF downloaded and extracted | Global bankruptcy prediction and cross-country scope caveats. |
| `bussmann2021explainable` | Full legal PDF downloaded and extracted | Finance-specific XAI and SHAP-style interpretability. |
| `charalambous2022maximizing` | Full legal PDF downloaded and extracted | Bankruptcy/discriminatory-power model evaluation. |
| `chawla2002smote` | Full legal PDF downloaded and extracted | Class imbalance and oversampling context. |
| `duchek2020resilience` | Full legal PDF downloaded and extracted | Resilience theory and caveat that resilience is broader than financial proxies. |
| `gornostaev2022realtime_russia` | Full legal PDF downloaded and extracted | Russian macro-data vintages and timing validity. |
| `gramegna2021shap` | Full legal PDF downloaded and extracted | SHAP/LIME in credit-risk interpretability. |
| `saito2015precision` | Full legal PDF downloaded and extracted | PR curves for imbalanced classification. |
| `shneiderman1996eyes` | Legal PDF downloaded, but extraction returned no readable text | Dashboard/visual analytics source; manual visual reading required. |

## Priority Sources Open Enough To Discuss Now

These sources are open enough to discuss in thesis prose, subject to normal careful citation.

| Key | Access status | Can discuss details? | Notes |
| --- | --- | --- | --- |
| `zhao2024survey` | ScienceDirect open access article page under Creative Commons license | Yes, based on open article page; manually download PDF if desired | Strong recent survey on corporate bankruptcy and financial distress prediction. |
| `billios2024power` | MDPI open access article page and PDF link | Yes, based on open article page; automated PDF blocked but page is readable | Systematic review of numerical indicators and bankruptcy prediction. |
| `afanasev2023default_emerging` | Full OA PDF downloaded | Yes | Best recent Russia-specific default-prediction source. |
| `fedorova2020external_factors_russia` | CyberLeninka public abstract/page; OA PDF URL exists but automated download timed out | Yes at abstract/results-summary level; manually download for full detailed discussion | Russian evidence that macro/external factors improve bankruptcy prediction. |
| `saito2015precision` | Full OA PDF downloaded | Yes | Strong support for PR-AUC/PR curves under class imbalance. |
| `duchek2020resilience` | Full OA PDF downloaded | Yes | Strong support for careful resilience framing. |
| `charalambous2022maximizing` | Full OA PDF downloaded | Yes | Useful for bankruptcy model evaluation and discriminatory power. |
| `bussmann2021explainable` | Full OA PDF downloaded | Yes | Finance-specific XAI support. |
| `gramegna2021shap` | Full OA PDF downloaded | Yes | SHAP/LIME and credit-risk interpretability. |
| `gornostaev2022realtime_russia` | Full OA PDF downloaded | Yes | Useful for Russian macro-data timing and real-time-vintage logic. |

## Detailed Reading Notes

### `zhao2024survey`

**Source:** Zhao, J., Ouenniche, J., and De Smedt, J. (2024). *Survey, classification and critical analysis of the literature on corporate bankruptcy and financial distress prediction*. Machine Learning with Applications, 15, 100527. DOI: https://doi.org/10.1016/j.mlwa.2024.100527

**Access read:** Open access ScienceDirect article page. The page states it is open access under a Creative Commons license and provides title, authors, DOI, abstract, keywords, and data availability.

**What it is about:**  
This is a recent survey and classification paper on corporate bankruptcy and financial distress prediction. It covers definitions of bankruptcy and financial distress, statistical and AI prediction methodologies, preprocessing, feature selection, model implementation, classifier performance criteria, and performance-evaluation methods.

**Thesis use:**  
Use as one of the main recent literature anchors. It supports the claim that financial distress and bankruptcy prediction remain active research areas, that target definitions differ across studies, and that model choice must be discussed together with preprocessing, features, and evaluation metrics.

**Limitations:**  
It is a survey, not an empirical validation of the current SEC/FRED panel. The article page also says the authors do not have permission to share data, so it should not be used as a reproducible data source.

**Safe sentence:**  
Recent survey work classifies bankruptcy and financial-distress prediction research across definitions, preprocessing choices, feature-selection methods, model families, and evaluation metrics, reinforcing the need for explicit target definitions and validation design.

### `billios2024power`

**Source:** Billios, D., Seretidou, D., and Stavropoulos, A. (2024). *The Power of Numerical Indicators in Predicting Bankruptcy: A Systematic Review*. Journal of Risk and Financial Management, 17(10), 433. DOI: https://doi.org/10.3390/jrfm17100433

**Access read:** MDPI open access article page. The page identifies the article as an open-access review and provides the abstract, methodology, results, and conclusion sections in HTML. The PDF URL exists but automated download returned HTTP 403.

**What it is about:**  
The article systematically reviews numerical indicators used to predict company bankruptcy through statistical models. It follows PRISMA and includes ten primary studies. It emphasizes that numerical indicators and cash-flow indicators can support bankruptcy prediction, while also noting that model stability can depend on country/economic context.

**Thesis use:**  
Use to support the accounting/numerical-indicator feature families: profitability, liquidity, leverage, cash-flow measures, and financial ratios. It is also useful for explaining why the thesis separates legal bankruptcy, financial distress, and broader financial pressure.

**Limitations:**  
The review focuses on statistical models and numerical indicators, not the full ML/dashboard artifact. It excludes machine-learning methods from its main review design, so it should not be used as the main ML-method citation.

**Safe sentence:**  
Systematic-review evidence supports the continuing relevance of numerical financial indicators and cash-flow measures for bankruptcy prediction, while warning that models built in one economic setting should not be assumed stable across changing country conditions.

### `afanasev2023default_emerging`

**Source:** Afanasev, V. (2023). *Default Prediction Model for Emerging Capital Market Service Companies*. Journal of Corporate Finance Research, 17(1), 64-77. DOI: https://doi.org/10.17323/j.jcfr.2073-0438.17.1.2023.64-77

**Access read:** Full legal PDF downloaded from the journal page and text extracted locally.

**What it is about:**  
The paper tests whether financial-data-based default prediction works less well for Russian service firms than for service firms in developed European markets. It uses logistic regression, random forest, and k-nearest neighbors on 404 Russian firms and 304 European control firms.

**Main findings relevant to thesis:**  
The paper finds higher prediction error for Russian firms than for the European control group, with reported accuracy around 55-73 percent for Russian firms and 72-81 percent for developed European firms. The author argues that financial ratios may be weaker indicators for Russian service firms and suggests that non-financial factors could improve classification.

**Thesis use:**  
Use as the strongest recent Russia-specific default-prediction source. It supports a literature-gap argument that Russian prediction settings may require different variables or additional context beyond financial ratios.

**Limitations:**  
It covers service firms only, not all sectors. It is financial-ratio focused and does not build a macro-regime-aware firm-period panel. It should not be generalized to all Russian companies without caveat.

**Safe sentence:**  
Recent Russian service-sector evidence suggests that default prediction based only on financial indicators may be less accurate in Russian firms than in developed European controls, supporting caution about transferring predictor sets across institutional settings.

### `fedorova2020external_factors_russia`

**Source:** Fedorova, E. A., Musienko, S. O., and Fedorov, F. Yu. (2020). *Analysis of the External Factors Influence on the Forecasting of Bankruptcy of Russian Companies*. St Petersburg University Journal of Economic Studies, 36(1), 117-133. DOI: https://doi.org/10.21638/spbu05.2020.106

**Access read:** Public CyberLeninka abstract/page and source metadata. Legal OA PDF URL exists, but automated download timed out.

**What it is about:**  
The paper analyzes whether external macroeconomic factors improve bankruptcy prediction for Russian companies. The public abstract describes construction, manufacturing, and trading-company samples and binary-choice models with internal and external factor blocks.

**Main findings relevant to thesis:**  
The source reports that adding external factors significantly increased explanatory capacity compared with internal-factor-only models. External factors include GDP growth, key rate, dollar/euro exchange-rate changes, CPI, MICEX index growth, and unemployment.

**Thesis use:**  
Use as Russia-specific support for the macro-market-shift logic. It helps justify why a Russian extension should include macro/external context instead of only accounting ratios.

**Limitations:**  
Use this at abstract/results-summary level unless the full PDF is manually downloaded and read. It is Russian-language and not an empirical validation of the current U.S. FRED panel or the market-health index.

**Safe sentence:**  
Russian bankruptcy-prediction evidence also indicates that external macroeconomic factors can improve explanatory capacity relative to internal company variables alone, although this supports contextual relevance rather than direct validation of the U.S. SEC/FRED model.

### `charalambous2022maximizing`

**Source:** Charalambous, C., Martzoukos, S. H., and Taoushianis, Z. (2022). *Estimating Corporate Bankruptcy Forecasting Models by Maximizing Discriminatory Power*. Review of Quantitative Finance and Accounting. DOI: https://doi.org/10.1007/s11156-021-00995-0

**Access read:** Full legal Springer PDF downloaded and text extracted.

**What it is about:**  
The paper proposes estimating bankruptcy-forecasting models by maximizing discriminatory power measured by AUROC. It compares this approach against traditional logistic and neural-network estimation in out-of-sample settings.

**Main findings relevant to thesis:**  
The paper reports that models trained to maximize AUROC outperform traditional methods in discriminatory power, information content, and economic impact. It studies bankruptcy one year ahead, bankruptcy two years ahead, and financial distress as a harder pre-bankruptcy condition.

**Thesis use:**  
Use to support model-evaluation discussion, especially the idea that bankruptcy and distress forecasting should be evaluated out-of-sample and by discriminatory performance, not just fitted probability quality.

**Limitations:**  
It emphasizes AUROC. In this thesis, strict distress is rare, so PR-AUC and recall/precision remain important alongside ROC-AUC. Do not use this paper to justify ignoring class imbalance.

**Safe sentence:**  
Recent bankruptcy-forecasting work emphasizes out-of-sample discriminatory power, but in rare-event settings such as strict legal distress, ROC-oriented evaluation should be complemented by precision-recall metrics.

### `saito2015precision`

**Source:** Saito, T., and Rehmsmeier, M. (2015). *The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets*. PLOS ONE. DOI: https://doi.org/10.1371/journal.pone.0118432

**Access read:** Full legal PLOS PDF downloaded and text extracted.

**What it is about:**  
The paper compares ROC plots and precision-recall plots for imbalanced binary classification.

**Main findings relevant to thesis:**  
The paper argues that ROC plots can be visually misleading under heavy class imbalance, while PR curves more directly express the reliability of positive predictions because precision measures the fraction of true positives among predicted positives.

**Thesis use:**  
Use as a core metric citation for strict distress and broader pressure targets. It directly supports reporting PR-AUC, precision, recall, F1, and positive-class behavior instead of relying only on ROC-AUC.

**Limitations:**  
The paper is not finance-specific. It supports evaluation methodology, not economic interpretation.

**Safe sentence:**  
Because strict legal distress is rare, precision-recall evaluation is more informative than ROC-only reporting for judging whether positive distress predictions are practically reliable.

### `duchek2020resilience`

**Source:** Duchek, S. (2020). *Organizational Resilience: A Capability-Based Conceptualization*. Business Research, 13, 215-246. DOI: https://doi.org/10.1007/s40685-019-0085-7

**Access read:** Full legal Springer PDF downloaded and text extracted.

**What it is about:**  
The paper conceptualizes organizational resilience as a meta-capability built around anticipation, coping, and adaptation. It emphasizes that resilience involves capabilities and processes, not a single financial outcome.

**Main findings relevant to thesis:**  
The paper supports the idea that resilience is complex and multidimensional. It helps prevent overclaiming: the thesis can measure financial resilience proxies, but not total organizational resilience.

**Thesis use:**  
Use in the strategic/resilience framing section. It supports naming a success/resilience target only if the thesis clearly states that the operational measure is financial and accounting-based.

**Limitations:**  
It is conceptual, not a financial-distress prediction paper. It does not provide SEC-ratio target definitions.

**Safe sentence:**  
Organizational resilience is a broader capability-based process involving anticipation, coping, and adaptation; therefore, this thesis uses the narrower term financial resilience when discussing accounting-based success proxies.

### `gornostaev2022realtime_russia`

**Source:** Gornostaev, D., Ponomarenko, A., Seleznev, S., and Sterkhova, A. (2022). *A Real-Time Historical Database of Macroeconomic Indicators for Russia*. Russian Journal of Money and Finance, 81(1), 88-103. DOI: https://doi.org/10.31477/rjmf.202201.88

**Access read:** Full legal PDF downloaded and text extracted.

**What it is about:**  
The paper documents a real-time historical database of Russian macroeconomic indicators and explains why data vintages matter for model evaluation and policy decisions.

**Main findings relevant to thesis:**  
The paper emphasizes that analysts should reconstruct what information was available at the time, because later-revised macro data can differ from real-time data. This is directly aligned with the thesis prediction-date policy.

**Thesis use:**  
Use to support the general methodological principle that macro variables should be aligned to information available at prediction time. It is especially relevant for any future Russian macro-regime extension.

**Limitations:**  
It is not a firm-failure study. It supports timing integrity and macro-data infrastructure, not bankruptcy causality.

**Safe sentence:**  
Russian macro-data vintage research reinforces the importance of using information available at the prediction date rather than relying uncritically on later-revised macroeconomic series.

### `bussmann2021explainable`

**Source:** Bussmann, N., Giudici, P., Marinelli, D., and Papenbrock, J. (2021). *Explainable Machine Learning in Credit Risk Management*. Computational Economics. DOI: https://doi.org/10.1007/s10614-020-10042-0

**Access read:** Full legal Springer PDF downloaded and text extracted.

**What it is about:**  
The paper proposes an explainable AI approach for credit-risk management. It applies Shapley-value explanations and correlation networks to group predictions by similar explanatory structures.

**Main findings relevant to thesis:**  
The source supports the idea that black-box AI is problematic in regulated financial services and that post-hoc explanation methods can help interpret financial-risk predictions.

**Thesis use:**  
Use to support finance-specific explainability and the dashboard's factor/contribution interpretation layer.

**Limitations:**  
It is credit-risk and peer-to-peer lending oriented, not SEC corporate distress/resilience. Use it as adjacent finance-XAI evidence.

**Safe sentence:**  
Finance-specific XAI literature supports the need to explain model predictions, but explanations should be treated as model-behavior diagnostics rather than causal proof.

### `gramegna2021shap`

**Source:** Gramegna, A., and Giudici, P. (2021). *SHAP and LIME: An Evaluation of Discriminative Power in Credit Risk*. Frontiers in Artificial Intelligence. DOI: https://doi.org/10.3389/frai.2021.752558

**Access read:** Full legal PDF downloaded and text extracted.

**What it is about:**  
The paper discusses SHAP and LIME in credit-risk modeling and connects predictive accuracy with interpretability tools.

**Main findings relevant to thesis:**  
It supports using explainability methods in financial-risk contexts while also recognizing the prediction-interpretability tradeoff.

**Thesis use:**  
Use as a secondary finance-XAI reference alongside Bussmann et al., Lundberg and Lee, Ribeiro et al., and Guidotti et al.

**Limitations:**  
It is credit risk, not corporate failure prediction, and its methods/data differ from this thesis.

**Safe sentence:**  
Credit-risk XAI studies show why financial prediction models need interpretable outputs, but such tools explain model logic rather than proving economic causality.

### `chawla2002smote`

**Source:** Chawla, N. V., Bowyer, K. W., Hall, L. O., and Kegelmeyer, W. P. (2002). *SMOTE: Synthetic Minority Over-Sampling Technique*. Journal of Artificial Intelligence Research. DOI: https://doi.org/10.1613/jair.953

**Access read:** Full legal PDF downloaded and text extracted.

**What it is about:**  
The paper introduces SMOTE, a synthetic minority oversampling method for imbalanced classification.

**Main findings relevant to thesis:**  
SMOTE creates synthetic minority-class examples and, in the paper's experiments, can improve classifier performance in ROC space when combined with under-sampling.

**Thesis use:**  
Use as general class-imbalance background. It helps show that imbalance methods exist, but it does not require the thesis to use oversampling.

**Limitations:**  
SMOTE can distort time-ordered financial panels if applied carelessly. This thesis should not imply that synthetic oversampling was central unless it is actually used and audited.

**Safe sentence:**  
Class-imbalance methods such as SMOTE exist, but in temporally ordered firm panels they must be used cautiously because synthetic examples can complicate time-valid evaluation.

### `alaminos2016global`

**Source:** Alaminos, D., del Castillo, A., and Fernandez, M. A. (2016). *A Global Model for Bankruptcy Prediction*. PLOS ONE. DOI: https://doi.org/10.1371/journal.pone.0166693

**Access read:** Full legal PLOS PDF downloaded and text extracted.

**What it is about:**  
The paper builds bankruptcy prediction models across Asia, Europe, America, and global samples using logistic regression.

**Main findings relevant to thesis:**  
It supports the idea that cross-country bankruptcy prediction is a recognized research direction, but it also makes scope and transferability important.

**Thesis use:**  
Use as future-work or scope-context evidence. It can support why a global or Russia/U.S. extension would be valuable.

**Limitations:**  
The current thesis is not a global bankruptcy model. Do not use this paper to imply that the current U.S. SEC/FRED panel generalizes globally.

**Safe sentence:**  
Global bankruptcy-prediction research motivates cross-country extensions, but the current thesis deliberately limits empirical claims to the implemented U.S. panel.

## Sources To Retrieve Through University Library Or Manual Browser

Priority paywalled or manually blocked sources:

| Key | Why needed | Retrieval route |
| --- | --- | --- |
| `tinoco2013financial` | Core source for combining accounting, market, and macro variables in listed-company distress prediction. | University library/VPN via Elsevier DOI; author manuscript search. |
| `barboza2017machine` | Core ML bankruptcy source. | University library/VPN via Elsevier DOI; ResearchGate or author request. |
| `dasilas2024machine` | Recent systematic review of ML bankruptcy prediction. | University library/VPN via Elsevier DOI. |
| `charalambakis2015developed_emerging` | Developed vs emerging market comparison. | Springer/university access; University of Manchester page; author request. |
| `hunter2001failure_risk_russia` | Russia-specific comparative failure-risk source. | ScienceDirect/university access; Brunel repository working-paper page. |
| `zhang2022xai` | Direct XAI for financial distress prediction. | Elsevier/university access; author manuscript search. |
| `altman1968financial`, `ohlson1980financial`, `beaver1966financial` | Classical foundations. | JSTOR/university access. |
| `shumway2001forecasting`, `campbell2008distress` | Dynamic panel/hazard and distress-risk context. | University access; SSRN/author pages for working papers. |

## Author Email Template

Subject: Request for article copy for master thesis research

Dear Professor [Surname],

I am writing my master thesis on firm financial distress and resilience prediction using an audited SEC/FRED firm-period panel, macro-regime context, temporal validation, and interpretable machine-learning outputs. Your paper, "[Paper Title]", is highly relevant to my literature review, especially for [specific reason].

Would it be possible to receive a copy of the paper for academic use?

Best regards,  
[Your Name]

## Writing Rule For The Thesis

Use detailed method/result discussion only for sources that are:

- full-text read;
- openly accessible and readable through an official article page;
- or retrieved through university/VPN and then manually added to the workspace.

For metadata-only or abstract-only sources, use high-level claims only and avoid detailed statements about models, samples, coefficients, or exact results unless the full text is read.

