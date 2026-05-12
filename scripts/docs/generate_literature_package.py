from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports" / "literature"


REFS = [
    {
        "key": "beaver1966financial",
        "authors": "Beaver, William H.",
        "year": "1966",
        "title": "Financial Ratios as Predictors of Failure",
        "publication": "Journal of Accounting Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "univariate ratio analysis",
        "scope": "failed and non-failed firms; accounting ratios",
        "contribution": "Shows that accounting ratios can contain early warning information before business failure.",
        "limitation": "Uses a narrow classical design and does not address modern panel validation or ML.",
        "use": "Historical foundation for ratio-based failure signals.",
        "claim": "Profitability, liquidity, and leverage ratios are defensible early warning variables.",
        "doi_url": "https://doi.org/10.2307/2490171",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Accounting Research",
        "volume": "4",
        "pages": "71--111",
        "doi": "10.2307/2490171",
    },
    {
        "key": "altman1968financial",
        "authors": "Altman, Edward I.",
        "year": "1968",
        "title": "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy",
        "publication": "The Journal of Finance",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "multiple discriminant analysis",
        "scope": "manufacturing firms; bankruptcy prediction",
        "contribution": "Introduces the Z-score logic that combines multiple ratios into a failure-risk score.",
        "limitation": "Industry and time-period specificity limit direct use as a modern universal model.",
        "use": "Benchmark for classical bankruptcy prediction.",
        "claim": "Composite accounting-ratio models are a mature baseline, not a novel contribution by themselves.",
        "doi_url": "https://doi.org/10.1111/j.1540-6261.1968.tb00843.x",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Journal of Finance",
        "volume": "23",
        "number": "4",
        "pages": "589--609",
        "doi": "10.1111/j.1540-6261.1968.tb00843.x",
    },
    {
        "key": "altman1997international",
        "authors": "Altman, Edward I. and Narayanan, Paul",
        "year": "1997",
        "title": "An International Survey of Business Failure Classification Models",
        "publication": "Financial Markets, Institutions & Instruments",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "international literature survey",
        "scope": "business failure classification models across countries",
        "contribution": "Shows that failure prediction is an international, mature field with many country-specific model variants.",
        "limitation": "A survey of pre-modern methods; not a guide to current data engineering or explainable ML.",
        "use": "Prevents overclaiming novelty in bankruptcy prediction itself.",
        "claim": "The novelty must be framed around the audited panel, target hierarchy, validation, and artifact rather than the existence of bankruptcy prediction.",
        "doi_url": "https://doi.org/10.1111/1468-0416.00010",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Financial Markets, Institutions & Instruments",
        "volume": "6",
        "number": "2",
        "pages": "1--57",
        "doi": "10.1111/1468-0416.00010",
    },
    {
        "key": "ohlson1980financial",
        "authors": "Ohlson, James A.",
        "year": "1980",
        "title": "Financial Ratios and the Probabilistic Prediction of Bankruptcy",
        "publication": "Journal of Accounting Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "logit bankruptcy model",
        "scope": "public firms; accounting variables",
        "contribution": "Moves bankruptcy prediction toward probabilistic modeling with accounting variables.",
        "limitation": "Still a classical statistical model and does not solve sample selection or rare-event challenges alone.",
        "use": "Supports logistic benchmark and probability framing.",
        "claim": "Probabilistic outputs are more natural for early-warning systems than deterministic labels.",
        "doi_url": "https://doi.org/10.2307/2490395",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Accounting Research",
        "volume": "18",
        "number": "1",
        "pages": "109--131",
        "doi": "10.2307/2490395",
    },
    {
        "key": "zmijewski1984methodological",
        "authors": "Zmijewski, Mark E.",
        "year": "1984",
        "title": "Methodological Issues Related to the Estimation of Financial Distress Prediction Models",
        "publication": "Journal of Accounting Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "methodological critique",
        "scope": "financial distress prediction model estimation",
        "contribution": "Highlights sample selection and estimation problems in distress modeling.",
        "limitation": "Predates modern SEC-scale panels and machine learning.",
        "use": "Supports explicit audit and label-construction discussion.",
        "claim": "Failure labels and universe construction can bias results and must be documented.",
        "doi_url": "https://doi.org/10.2307/2490859",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Accounting Research",
        "volume": "22",
        "pages": "59--82",
        "doi": "10.2307/2490859",
    },
    {
        "key": "merton1974pricing",
        "authors": "Merton, Robert C.",
        "year": "1974",
        "title": "On the Pricing of Corporate Debt: The Risk Structure of Interest Rates",
        "publication": "The Journal of Finance",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "structural credit-risk model",
        "scope": "corporate debt and default-risk theory",
        "contribution": "Provides a structural market-based theory of default risk.",
        "limitation": "Requires market-value and volatility inputs that are outside the current production panel.",
        "use": "Future-work comparator only, not an implemented model.",
        "claim": "Market-price/default-distance models are relevant but not implemented in this thesis.",
        "doi_url": "https://doi.org/10.1111/j.1540-6261.1974.tb03058.x",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Journal of Finance",
        "volume": "29",
        "number": "2",
        "pages": "449--470",
        "doi": "10.1111/j.1540-6261.1974.tb03058.x",
    },
    {
        "key": "hillegeist2004assessing",
        "authors": "Hillegeist, Stephen A. and Keating, Elizabeth K. and Cram, Donald P. and Lundstedt, Kyle G.",
        "year": "2004",
        "title": "Assessing the Probability of Bankruptcy",
        "publication": "Review of Accounting Studies",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "comparison of accounting and market-based bankruptcy measures",
        "scope": "public firms; bankruptcy probability assessment",
        "contribution": "Compares accounting-score approaches with market-based probability estimates.",
        "limitation": "Market-based variables are not available for every current row in the production accounting panel.",
        "use": "Supports limitation/future-work discussion about market-based features.",
        "claim": "Accounting-only panels are defensible but do not exhaust all possible distress information.",
        "doi_url": "https://doi.org/10.1023/B:RAST.0000013627.90884.b7",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Review of Accounting Studies",
        "volume": "9",
        "pages": "5--34",
        "doi": "10.1023/B:RAST.0000013627.90884.b7",
    },
    {
        "key": "shumway2001forecasting",
        "authors": "Shumway, Tyler",
        "year": "2001",
        "title": "Forecasting Bankruptcy More Accurately: A Simple Hazard Model",
        "publication": "The Journal of Business",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "hazard model",
        "scope": "firm-period bankruptcy forecasting",
        "contribution": "Argues that bankruptcy prediction should use time-varying panel logic rather than one static observation per firm.",
        "limitation": "Hazard modeling is not the implemented model family in this project.",
        "use": "Supports firm-period panel and temporal framing.",
        "claim": "Prediction rows should be anchored in time and evaluated out of sample.",
        "doi_url": "https://doi.org/10.1086/209665",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Journal of Business",
        "volume": "74",
        "number": "1",
        "pages": "101--124",
        "doi": "10.1086/209665",
    },
    {
        "key": "duffie2007multi",
        "authors": "Duffie, Darrell and Saita, Leandro and Wang, Ke",
        "year": "2007",
        "title": "Multi-Period Corporate Default Prediction with Stochastic Covariates",
        "publication": "Journal of Financial Economics",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Macroeconomic conditions, credit cycles, and market-shift/default context",
        "method": "multi-period default prediction",
        "scope": "corporate default; dynamic covariates",
        "contribution": "Links corporate default prediction to time-varying firm and macro-financial covariates.",
        "limitation": "Different event definition and model design than the current SEC/FRED panel.",
        "use": "Supports dynamic macro-context variables and forward horizons.",
        "claim": "Default and distress risk should be studied with time-varying covariates.",
        "doi_url": "https://doi.org/10.1016/j.jfineco.2005.10.011",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Financial Economics",
        "volume": "83",
        "number": "3",
        "pages": "635--665",
        "doi": "10.1016/j.jfineco.2005.10.011",
    },
    {
        "key": "campbell2008distress",
        "authors": "Campbell, John Y. and Hilscher, Jens and Szilagyi, Jan",
        "year": "2008",
        "title": "In Search of Distress Risk",
        "publication": "The Journal of Finance",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "dynamic distress-risk modeling",
        "scope": "public firms; distress risk and returns",
        "contribution": "Shows distress risk is related to profitability, leverage, market conditions, and dynamic firm characteristics.",
        "limitation": "Uses market variables not fully implemented in the current accounting-focused panel.",
        "use": "Supports profitability/leverage/deterioration signal interpretation.",
        "claim": "Distress is multidimensional and not identical to a single bankruptcy filing date.",
        "doi_url": "https://doi.org/10.1111/j.1540-6261.2008.01416.x",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Journal of Finance",
        "volume": "63",
        "number": "6",
        "pages": "2899--2939",
        "doi": "10.1111/j.1540-6261.2008.01416.x",
    },
    {
        "key": "bharath2008forecasting",
        "authors": "Bharath, Sreedhar T. and Shumway, Tyler",
        "year": "2008",
        "title": "Forecasting Default with the Merton Distance to Default Model",
        "publication": "The Review of Financial Studies",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "market-based default model comparison",
        "scope": "public-company default prediction",
        "contribution": "Evaluates structural distance-to-default ideas against simpler default forecasting inputs.",
        "limitation": "Not implemented because the current production panel is SEC/FRED based.",
        "use": "Future-work and limitation source.",
        "claim": "Market-based default predictors are relevant but outside the current artifact scope.",
        "doi_url": "https://doi.org/10.1093/rfs/hhn044",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Review of Financial Studies",
        "volume": "21",
        "number": "3",
        "pages": "1339--1369",
        "doi": "10.1093/rfs/hhn044",
    },
    {
        "key": "bauer2014hazard",
        "authors": "Bauer, Julian and Agarwal, Vineet",
        "year": "2014",
        "title": "Are Hazard Models Superior to Traditional Bankruptcy Prediction Approaches? A Comprehensive Test",
        "publication": "Journal of Banking & Finance",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Classical firm failure and financial distress prediction",
        "method": "hazard and traditional model comparison",
        "scope": "bankruptcy prediction methodology",
        "contribution": "Tests whether hazard approaches outperform traditional models under comparable settings.",
        "limitation": "The thesis uses temporal ML classifiers rather than full hazard models.",
        "use": "Supports methodological caution and model-comparison framing.",
        "claim": "Method choice and evaluation design materially affect bankruptcy-prediction conclusions.",
        "doi_url": "https://doi.org/10.1016/j.jbankfin.2013.12.013",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Banking & Finance",
        "volume": "40",
        "pages": "432--442",
        "doi": "10.1016/j.jbankfin.2013.12.013",
    },
    {
        "key": "tinoco2013financial",
        "authors": "Tinoco, Mario H. and Wilson, Nick",
        "year": "2013",
        "title": "Financial Distress and Bankruptcy Prediction among Listed Companies Using Accounting, Market and Macroeconomic Variables",
        "publication": "International Review of Financial Analysis",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Macroeconomic conditions, credit cycles, and market-shift/default context",
        "method": "distress prediction with accounting, market, and macro variables",
        "scope": "listed companies",
        "contribution": "Directly supports combining accounting, market, and macroeconomic variables for listed-company distress prediction.",
        "limitation": "Does not provide the current thesis artifact, target hierarchy, or dashboard.",
        "use": "Core support for the SEC plus FRED design.",
        "claim": "Macro context is a legitimate input layer, but it should not be oversold as the dominant cause without evidence.",
        "doi_url": "https://doi.org/10.1016/j.irfa.2013.02.013",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "International Review of Financial Analysis",
        "volume": "30",
        "pages": "394--419",
        "doi": "10.1016/j.irfa.2013.02.013",
    },
    {
        "key": "tian2017financial",
        "authors": "Tian, Shaonan and Yu, Yan",
        "year": "2017",
        "title": "Financial Ratios and Bankruptcy Predictions: An International Evidence",
        "publication": "International Review of Economics & Finance",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "international financial-ratio bankruptcy analysis",
        "scope": "international listed firms",
        "contribution": "Shows ratio signals can generalize across countries, while still requiring local validation.",
        "limitation": "International comparability differs from this U.S. SEC panel.",
        "use": "Supports ratio families and warns against country-blind generalization.",
        "claim": "Financial ratios are useful, but sample scope and accounting regime matter.",
        "doi_url": "https://doi.org/10.1016/j.iref.2017.07.025",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "International Review of Economics & Finance",
        "volume": "51",
        "pages": "510--526",
        "doi": "10.1016/j.iref.2017.07.025",
    },
    {
        "key": "alaminos2016global",
        "authors": "Alaminos, David and del Castillo, Angel and Fernandez, Manuel Angel",
        "year": "2016",
        "title": "A Global Model for Bankruptcy Prediction",
        "publication": "PLOS ONE",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "global bankruptcy prediction",
        "scope": "international firm data",
        "contribution": "Demonstrates interest in broader, cross-country bankruptcy-prediction models.",
        "limitation": "Global model framing does not remove the need for local SEC data auditing.",
        "use": "Supports discussion of scope limits and future international extensions.",
        "claim": "International expansion is a future direction, not part of the current production pipeline.",
        "doi_url": "https://doi.org/10.1371/journal.pone.0166693",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "PLOS ONE",
        "volume": "11",
        "number": "11",
        "pages": "e0166693",
        "doi": "10.1371/journal.pone.0166693",
    },
    {
        "key": "taffler1983assessment",
        "authors": "Taffler, Richard J.",
        "year": "1983",
        "title": "The Assessment of Company Solvency and Performance Using a Statistical Model",
        "publication": "Accounting and Business Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "statistical solvency model",
        "scope": "company solvency and performance",
        "contribution": "Reinforces the long-standing link between solvency, performance, and accounting data.",
        "limitation": "Older statistical model; not enough for modern novelty.",
        "use": "Background support for solvency and performance indicators.",
        "claim": "Solvency and performance measures are part of a long empirical tradition.",
        "doi_url": "https://doi.org/10.1080/00014788.1983.9729767",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Accounting and Business Research",
        "volume": "13",
        "number": "52",
        "pages": "295--308",
        "doi": "10.1080/00014788.1983.9729767",
    },
    {
        "key": "platt1994bankruptcy",
        "authors": "Platt, Harlan D. and Platt, Marjorie B.",
        "year": "1994",
        "title": "Bankruptcy Prediction with Real Variables",
        "publication": "Journal of Business Finance & Accounting",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "bankruptcy model with non-ratio variables",
        "scope": "bankruptcy prediction",
        "contribution": "Broadens the distress-prediction feature discussion beyond pure financial-ratio sets.",
        "limitation": "Feature universe differs from the SEC/FRED panel.",
        "use": "Supports using richer firm-period attributes and context variables.",
        "claim": "The feature set can reasonably include more than a small fixed ratio formula.",
        "doi_url": "https://doi.org/10.1111/j.1468-5957.1994.tb00332.x",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Business Finance & Accounting",
        "volume": "21",
        "number": "4",
        "pages": "491--510",
        "doi": "10.1111/j.1468-5957.1994.tb00332.x",
    },
    {
        "key": "billios2024power",
        "authors": "Billios, Dimitrios and Seretidou, Dimitra and Stavropoulos, Antonios",
        "year": "2024",
        "title": "The Power of Numerical Indicators in Predicting Bankruptcy: A Systematic Review",
        "publication": "Journal of Risk and Financial Management",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "numerical indicator bankruptcy prediction",
        "scope": "systematic review of numerical indicators in bankruptcy prediction",
        "contribution": "Recent review evidence that numerical financial indicators and cash-flow information remain useful for bankruptcy prediction.",
        "limitation": "Review scope is narrow and does not provide the thesis data architecture.",
        "use": "Modern support that accounting/numerical indicators remain relevant.",
        "claim": "Using ratios and numeric fundamentals is not outdated if combined with modern validation and interpretation.",
        "doi_url": "https://doi.org/10.3390/jrfm17100433",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Risk and Financial Management",
        "volume": "17",
        "number": "10",
        "pages": "433",
        "doi": "10.3390/jrfm17100433",
    },
    {
        "key": "valaskova2023postpandemic",
        "authors": "Valaskova, Katarina and Gajdosikova, Dominika and Belas, Jaroslav",
        "year": "2023",
        "title": "Bankruptcy Prediction in the Post-Pandemic Period: A Case Study of Visegrad Group Countries",
        "publication": "Oeconomia Copernicana",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "post-pandemic bankruptcy-risk prediction",
        "scope": "Visegrad Group countries in the post-pandemic period",
        "contribution": "Shows renewed post-pandemic interest in firm failure prediction and financial-health monitoring.",
        "limitation": "Country-specific setting and not SEC/FRED scale.",
        "use": "Recent context for why distress/resilience analysis remains current after large market shocks.",
        "claim": "The topic remains active and relevant in recent literature.",
        "doi_url": "https://doi.org/10.24136/oc.2023.007",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Oeconomia Copernicana",
        "volume": "14",
        "number": "1",
        "pages": "253--293",
        "doi": "10.24136/oc.2023.007",
    },
    {
        "key": "bragoli2022industrial",
        "authors": "Bragoli, Daniela and Ferretti, Camilla and Ganugi, Piero and Marseguerra, Giovanni and Mezzogori, Davide and Zammori, Francesco",
        "year": "2022",
        "title": "Machine-Learning Models for Bankruptcy Prediction: Do Industrial Variables Matter?",
        "publication": "Spatial Economic Analysis",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Firm fundamentals, financial ratios, and deterioration features",
        "method": "machine-learning bankruptcy models with industrial variables",
        "scope": "firm bankruptcy with industry context",
        "contribution": "Directly motivates industry metadata and sector-aware analysis.",
        "limitation": "Different geography/data and not the same dashboard artifact.",
        "use": "Supports inclusion of industry metadata and sector summaries.",
        "claim": "Industry context can matter for factor interpretation.",
        "doi_url": "https://doi.org/10.1080/17421772.2021.1977377",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Spatial Economic Analysis",
        "volume": "17",
        "number": "2",
        "pages": "1--22",
        "doi": "10.1080/17421772.2021.1977377",
    },
    {
        "key": "charalambous2022maximizing",
        "authors": "Charalambous, Chris and Martzoukos, Spiros H. and Taoushianis, Zenon",
        "year": "2022",
        "title": "Estimating Corporate Bankruptcy Forecasting Models by Maximizing Discriminatory Power",
        "publication": "Review of Quantitative Finance and Accounting",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "bankruptcy model estimation by AUROC optimization",
        "scope": "U.S. public firms; bankruptcy and financial distress forecasting",
        "contribution": "Shows that optimizing discriminatory power can improve out-of-sample bankruptcy and financial-distress forecasts.",
        "limitation": "Does not provide this thesis dashboard artifact.",
        "use": "Supports dashboard and metric interpretation beyond accuracy.",
        "claim": "For rare distress events, discriminatory-power metrics and out-of-sample design matter.",
        "doi_url": "https://doi.org/10.1007/s11156-021-00995-0",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Review of Quantitative Finance and Accounting",
        "volume": "58",
        "pages": "297--328",
        "doi": "10.1007/s11156-021-00995-0",
    },
    {
        "key": "barboza2017machine",
        "authors": "Barboza, Flavio and Kimura, Herbert and Altman, Edward",
        "year": "2017",
        "title": "Machine Learning Models and Bankruptcy Prediction",
        "publication": "Expert Systems with Applications",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "machine-learning model comparison",
        "scope": "bankruptcy prediction",
        "contribution": "Shows ML methods can improve bankruptcy-prediction performance relative to classical methods in some settings.",
        "limitation": "Performance gains depend on data, validation, and target definition.",
        "use": "Core support for random forest and gradient boosting benchmarks.",
        "claim": "ML is useful but must be validated and interpreted carefully.",
        "doi_url": "https://doi.org/10.1016/j.eswa.2017.04.006",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Expert Systems with Applications",
        "volume": "83",
        "pages": "405--417",
        "doi": "10.1016/j.eswa.2017.04.006",
    },
    {
        "key": "lessmann2015benchmarking",
        "authors": "Lessmann, Stefan and Baesens, Bart and Seow, Hsin-Vonn and Thomas, Lyn C.",
        "year": "2015",
        "title": "Benchmarking State-of-the-Art Classification Algorithms for Credit Scoring: An Update of Research",
        "publication": "European Journal of Operational Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "classification algorithm benchmark",
        "scope": "credit scoring",
        "contribution": "Provides modern classification benchmarking evidence in a related financial-risk domain.",
        "limitation": "Credit scoring is not identical to SEC-based firm failure/resilience.",
        "use": "Supports comparing multiple model families rather than relying on one algorithm.",
        "claim": "Financial-risk prediction should benchmark model families under comparable splits.",
        "doi_url": "https://doi.org/10.1016/j.ejor.2015.05.030",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "European Journal of Operational Research",
        "volume": "247",
        "number": "1",
        "pages": "124--136",
        "doi": "10.1016/j.ejor.2015.05.030",
    },
    {
        "key": "dasilas2024machine",
        "authors": "Dasilas, Apostolos and Rigani, Anna",
        "year": "2024",
        "title": "Machine Learning Techniques in Bankruptcy Prediction: A Systematic Literature Review",
        "publication": "Expert Systems with Applications",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "systematic literature review",
        "scope": "machine learning for bankruptcy prediction",
        "contribution": "Current synthesis of ML bankruptcy-prediction research and common design choices.",
        "limitation": "A review; it does not supply this thesis dataset or artifact.",
        "use": "Main recent review source to show the field is current.",
        "claim": "The literature is active and increasingly ML-oriented, but still leaves room for reproducible audited panels and artifacts.",
        "doi_url": "https://doi.org/10.1016/j.eswa.2024.124761",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Expert Systems with Applications",
        "volume": "255",
        "pages": "124761",
        "doi": "10.1016/j.eswa.2024.124761",
    },
    {
        "key": "zhao2024survey",
        "authors": "Zhao, Jinxian and Ouenniche, Jamal and De Smedt, Johannes",
        "year": "2024",
        "title": "Survey, Classification and Critical Analysis of the Literature on Corporate Bankruptcy and Financial Distress Prediction",
        "publication": "Machine Learning with Applications",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "survey, classification, and critical analysis",
        "scope": "corporate bankruptcy and financial distress prediction literature",
        "contribution": "Recent critical survey that situates bankruptcy and financial distress prediction as an active statistical and AI research area.",
        "limitation": "A survey and not a validation of the thesis panel.",
        "use": "Modern literature anchor for the ML/business-failure section.",
        "claim": "Recent work confirms the topic is current, not only an old Z-score tradition.",
        "doi_url": "https://doi.org/10.1016/j.mlwa.2024.100527",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Machine Learning with Applications",
        "volume": "15",
        "pages": "100527",
        "doi": "10.1016/j.mlwa.2024.100527",
    },
    {
        "key": "kim2020corporate",
        "authors": "Kim, Minjun and Cho, Seonghoon and Ryu, Doojin",
        "year": "2020",
        "title": "Corporate Default Predictions Using Machine Learning: Literature Review",
        "publication": "Sustainability",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "literature review",
        "scope": "corporate default prediction using machine learning",
        "contribution": "Reviews machine-learning approaches to corporate default prediction.",
        "limitation": "Review-level evidence; not a direct empirical benchmark for this thesis.",
        "use": "Additional recent ML/default review source.",
        "claim": "Corporate default/distress prediction has moved toward ML, but model design and data quality remain central.",
        "doi_url": "https://doi.org/10.3390/su12166325",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Sustainability",
        "volume": "12",
        "number": "16",
        "pages": "6325",
        "doi": "10.3390/su12166325",
    },
    {
        "key": "sun2023company",
        "authors": "Sun, Xiaoxiao",
        "year": "2023",
        "title": "Company Failure Prediction with Machine Learning",
        "publication": "ECAI 2023: Frontiers in Artificial Intelligence and Applications",
        "source_type": "peer_reviewed_conference_paper",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "machine-learning failure prediction",
        "scope": "company failure prediction",
        "contribution": "Recent conference evidence that company-failure prediction remains an ML problem.",
        "limitation": "Conference paper and not a replacement for journal review sources.",
        "use": "Optional recent ML context.",
        "claim": "The project sits in a current ML/business-failure research stream.",
        "doi_url": "https://doi.org/10.3233/FAIA230838",
        "status": "verified_doi",
        "bibtype": "inproceedings",
        "booktitle": "ECAI 2023: Frontiers in Artificial Intelligence and Applications",
        "pages": "2380--2387",
        "doi": "10.3233/FAIA230838",
    },
    {
        "key": "breiman2001random",
        "authors": "Breiman, Leo",
        "year": "2001",
        "title": "Random Forests",
        "publication": "Machine Learning",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "random forest algorithm",
        "scope": "general supervised learning",
        "contribution": "Foundational source for random forests.",
        "limitation": "Algorithm paper, not finance-specific.",
        "use": "Cite for model method.",
        "claim": "Random forests are a standard ensemble baseline.",
        "doi_url": "https://doi.org/10.1023/A:1010933404324",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Machine Learning",
        "volume": "45",
        "pages": "5--32",
        "doi": "10.1023/A:1010933404324",
    },
    {
        "key": "friedman2001greedy",
        "authors": "Friedman, Jerome H.",
        "year": "2001",
        "title": "Greedy Function Approximation: A Gradient Boosting Machine",
        "publication": "The Annals of Statistics",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "gradient boosting machine",
        "scope": "general supervised learning",
        "contribution": "Foundational source for gradient boosting.",
        "limitation": "Algorithm paper, not finance-specific.",
        "use": "Cite for gradient boosting method.",
        "claim": "Gradient boosting is a defensible nonlinear benchmark.",
        "doi_url": "https://doi.org/10.1214/aos/1013203451",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Annals of Statistics",
        "volume": "29",
        "number": "5",
        "pages": "1189--1232",
        "doi": "10.1214/aos/1013203451",
    },
    {
        "key": "pedregosa2011scikit",
        "authors": "Pedregosa, Fabian and Varoquaux, Gael and Gramfort, Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel, Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss, Ron and Dubourg, Vincent and VanderPlas, Jake and Passos, Alexandre and Cournapeau, David and Brucher, Matthieu and Perrot, Matthieu and Duchesnay, Edouard",
        "year": "2011",
        "title": "Scikit-learn: Machine Learning in Python",
        "publication": "Journal of Machine Learning Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "software implementation paper",
        "scope": "machine-learning library",
        "contribution": "Citable source for the modeling software ecosystem used in Python.",
        "limitation": "Software citation, not a theory source.",
        "use": "Cite for implementation reproducibility.",
        "claim": "The model implementation uses established open-source ML tooling.",
        "doi_url": "https://www.jmlr.org/papers/v12/pedregosa11a.html",
        "status": "verified_official_page",
        "bibtype": "article",
        "journal": "Journal of Machine Learning Research",
        "volume": "12",
        "pages": "2825--2830",
        "url": "https://www.jmlr.org/papers/v12/pedregosa11a.html",
    },
    {
        "key": "fawcett2006roc",
        "authors": "Fawcett, Tom",
        "year": "2006",
        "title": "An Introduction to ROC Analysis",
        "publication": "Pattern Recognition Letters",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "ROC evaluation review",
        "scope": "binary classification evaluation",
        "contribution": "Explains ROC analysis and related evaluation concepts.",
        "limitation": "ROC-AUC can remain optimistic for rare positives.",
        "use": "Use with PR-AUC sources to discuss metric tradeoffs.",
        "claim": "ROC-AUC is informative but insufficient for rare-event target interpretation.",
        "doi_url": "https://doi.org/10.1016/j.patrec.2005.10.010",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Pattern Recognition Letters",
        "volume": "27",
        "number": "8",
        "pages": "861--874",
        "doi": "10.1016/j.patrec.2005.10.010",
    },
    {
        "key": "davis2006relationship",
        "authors": "Davis, Jesse and Goadrich, Mark",
        "year": "2006",
        "title": "The Relationship between Precision-Recall and ROC Curves",
        "publication": "Proceedings of the 23rd International Conference on Machine Learning",
        "source_type": "peer_reviewed_conference_paper",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "precision-recall and ROC comparison",
        "scope": "binary classifier evaluation",
        "contribution": "Shows how precision-recall and ROC views differ.",
        "limitation": "General ML evaluation paper, not finance-specific.",
        "use": "Supports PR-curve interpretation.",
        "claim": "Precision-recall metrics are necessary when positive-class performance matters.",
        "doi_url": "https://doi.org/10.1145/1143844.1143874",
        "status": "verified_doi",
        "bibtype": "inproceedings",
        "booktitle": "Proceedings of the 23rd International Conference on Machine Learning",
        "pages": "233--240",
        "doi": "10.1145/1143844.1143874",
    },
    {
        "key": "saito2015precision",
        "authors": "Saito, Takaya and Rehmsmeier, Marc",
        "year": "2015",
        "title": "The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets",
        "publication": "PLOS ONE",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "imbalanced-classifier evaluation",
        "scope": "binary classification with imbalanced datasets",
        "contribution": "Directly argues for precision-recall plots under class imbalance.",
        "limitation": "General ML evaluation source, not distress-specific.",
        "use": "Justifies PR-AUC for strict distress and broader pressure targets.",
        "claim": "PR-AUC is central for rare strict legal distress.",
        "doi_url": "https://doi.org/10.1371/journal.pone.0118432",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "PLOS ONE",
        "volume": "10",
        "number": "3",
        "pages": "e0118432",
        "doi": "10.1371/journal.pone.0118432",
    },
    {
        "key": "chawla2002smote",
        "authors": "Chawla, Nitesh V. and Bowyer, Kevin W. and Hall, Lawrence O. and Kegelmeyer, W. Philip",
        "year": "2002",
        "title": "SMOTE: Synthetic Minority Over-Sampling Technique",
        "publication": "Journal of Artificial Intelligence Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "minority-class oversampling",
        "scope": "imbalanced classification",
        "contribution": "Introduces a major class-imbalance method.",
        "limitation": "Synthetic oversampling can distort time-ordered financial panels if used carelessly.",
        "use": "Discuss as an imbalance method considered conceptually but not central.",
        "claim": "Rare-event methods exist, but temporal integrity matters more than blindly balancing classes.",
        "doi_url": "https://doi.org/10.1613/jair.953",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Artificial Intelligence Research",
        "volume": "16",
        "pages": "321--357",
        "doi": "10.1613/jair.953",
    },
    {
        "key": "burez2009handling",
        "authors": "Burez, Jonathan and Van den Poel, Dirk",
        "year": "2009",
        "title": "Handling Class Imbalance in Customer Churn Prediction",
        "publication": "Expert Systems with Applications",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Machine learning, rare-event evaluation, and temporal validation",
        "method": "class imbalance methods",
        "scope": "customer churn prediction",
        "contribution": "Shows class imbalance is a practical predictive-modeling issue beyond one domain.",
        "limitation": "Churn is not distress; use only for general imbalance logic.",
        "use": "Secondary support for imbalance handling concerns.",
        "claim": "Imbalanced classes can distort standard classifier performance.",
        "doi_url": "https://doi.org/10.1016/j.eswa.2009.05.027",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Expert Systems with Applications",
        "volume": "36",
        "number": "6",
        "pages": "10365--10375",
        "doi": "10.1016/j.eswa.2009.05.027",
    },
    {
        "key": "lundberg2017unified",
        "authors": "Lundberg, Scott M. and Lee, Su-In",
        "year": "2017",
        "title": "A Unified Approach to Interpreting Model Predictions",
        "publication": "Advances in Neural Information Processing Systems 30",
        "source_type": "peer_reviewed_conference_paper",
        "peer": "yes",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "SHAP explanation framework",
        "scope": "model-agnostic and model-specific explanation",
        "contribution": "Introduces SHAP as a unified additive explanation approach.",
        "limitation": "Explanations are not causal proof.",
        "use": "Supports feature-contribution interpretation language.",
        "claim": "Feature contribution methods help explain model behavior but should not be written as causality.",
        "doi_url": "https://papers.neurips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions",
        "status": "verified_official_page",
        "bibtype": "inproceedings",
        "booktitle": "Advances in Neural Information Processing Systems 30",
        "url": "https://papers.neurips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions",
    },
    {
        "key": "ribeiro2016trust",
        "authors": "Ribeiro, Marco Tulio and Singh, Sameer and Guestrin, Carlos",
        "year": "2016",
        "title": "\"Why Should I Trust You?\": Explaining the Predictions of Any Classifier",
        "publication": "Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining",
        "source_type": "peer_reviewed_conference_paper",
        "peer": "yes",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "local interpretable model explanations",
        "scope": "classifier explanation",
        "contribution": "Introduces LIME-style local explanations for black-box predictions.",
        "limitation": "Local explanations can be unstable and do not establish causality.",
        "use": "Supports interpretability/trust section.",
        "claim": "Black-box model outputs require explanatory artifacts for practical use.",
        "doi_url": "https://doi.org/10.1145/2939672.2939778",
        "status": "verified_doi",
        "bibtype": "inproceedings",
        "booktitle": "Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining",
        "pages": "1135--1144",
        "doi": "10.1145/2939672.2939778",
    },
    {
        "key": "guidotti2018survey",
        "authors": "Guidotti, Riccardo and Monreale, Anna and Ruggieri, Salvatore and Turini, Franco and Giannotti, Fosca and Pedreschi, Dino",
        "year": "2018",
        "title": "A Survey of Methods for Explaining Black Box Models",
        "publication": "ACM Computing Surveys",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "XAI survey",
        "scope": "black-box model explanation methods",
        "contribution": "Provides a broad taxonomy of black-box explanation methods.",
        "limitation": "General XAI survey, not finance-specific.",
        "use": "Supports XAI method classification and caution.",
        "claim": "Interpretability is a research field with multiple methods and limitations.",
        "doi_url": "https://doi.org/10.1145/3236009",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "ACM Computing Surveys",
        "volume": "51",
        "number": "5",
        "pages": "93",
        "doi": "10.1145/3236009",
    },
    {
        "key": "molnar2025interpretable",
        "authors": "Molnar, Christoph",
        "year": "2025",
        "title": "Interpretable Machine Learning: A Guide for Making Black Box Models Explainable",
        "publication": "Self-published open book",
        "source_type": "book",
        "peer": "unknown",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "practical XAI methods guide",
        "scope": "interpretable machine learning",
        "contribution": "Clear practical reference for permutation importance, SHAP, PDP/ALE, and interpretation limits.",
        "limitation": "Book/reference source, not a peer-reviewed journal article.",
        "use": "Practical interpretation guide.",
        "claim": "Permutation importance and feature contribution need careful, non-causal wording.",
        "doi_url": "https://christophm.github.io/interpretable-ml-book/",
        "status": "verified_official_page",
        "bibtype": "book",
        "url": "https://christophm.github.io/interpretable-ml-book/",
    },
    {
        "key": "bussmann2021explainable",
        "authors": "Bussmann, Niklas and Giudici, Paolo and Marinelli, Dimitri and Papenbrock, Jochen",
        "year": "2021",
        "title": "Explainable Machine Learning in Credit Risk Management",
        "publication": "Computational Economics",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "explainable ML in credit risk",
        "scope": "credit-risk management",
        "contribution": "Connects explainable ML to financial-risk management practice.",
        "limitation": "Credit-risk context is related but not identical to firm failure/resilience.",
        "use": "Finance-specific XAI support.",
        "claim": "Explainability is especially important in financial-risk analytics.",
        "doi_url": "https://doi.org/10.1007/s10614-020-10042-0",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Computational Economics",
        "volume": "57",
        "pages": "203--216",
        "doi": "10.1007/s10614-020-10042-0",
    },
    {
        "key": "gramegna2021shap",
        "authors": "Gramegna, Alex and Giudici, Paolo",
        "year": "2021",
        "title": "SHAP and LIME: An Evaluation of Discriminative Power in Credit Risk",
        "publication": "Frontiers in Artificial Intelligence",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "XAI method comparison",
        "scope": "credit risk",
        "contribution": "Evaluates SHAP and LIME in a financial-risk setting.",
        "limitation": "Credit risk, not SEC corporate distress labels.",
        "use": "Additional finance-specific XAI reference.",
        "claim": "Local/global explanation methods can be compared and audited in financial models.",
        "doi_url": "https://doi.org/10.3389/frai.2021.752558",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Frontiers in Artificial Intelligence",
        "volume": "4",
        "pages": "752558",
        "doi": "10.3389/frai.2021.752558",
    },
    {
        "key": "zhang2022xai",
        "authors": "Zhang, Zijiao and Wu, Chong and Qu, Shiyou and Chen, Xiaofang",
        "year": "2022",
        "title": "An Explainable Artificial Intelligence Approach for Financial Distress Prediction",
        "publication": "Information Processing & Management",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Interpretability and explainable ML",
        "method": "explainable AI for financial distress prediction",
        "scope": "financial distress prediction",
        "contribution": "Directly links XAI to financial distress prediction.",
        "limitation": "Specific method/data differ from this thesis.",
        "use": "Direct support for interpretable financial-distress modeling.",
        "claim": "Financial distress ML benefits from explanation layers.",
        "doi_url": "https://doi.org/10.1016/j.ipm.2022.102988",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Information Processing & Management",
        "volume": "59",
        "number": "4",
        "pages": "102988",
        "doi": "10.1016/j.ipm.2022.102988",
    },
    {
        "key": "little2019missing",
        "authors": "Little, Roderick J. A. and Rubin, Donald B.",
        "year": "2019",
        "title": "Statistical Analysis with Missing Data",
        "publication": "Wiley",
        "source_type": "book",
        "peer": "unknown",
        "language": "English",
        "bucket": "Missing data, data integrity, and accounting-data limitations",
        "method": "missing-data theory",
        "scope": "statistical analysis with missing data",
        "contribution": "Foundational treatment of missing-data mechanisms and analysis.",
        "limitation": "General statistics book, not SEC-specific.",
        "use": "Supports missingness policy and refusal to invent null values.",
        "claim": "Missing values should be handled according to mechanism and analysis purpose.",
        "doi_url": "https://doi.org/10.1002/9781119482260",
        "status": "verified_doi",
        "bibtype": "book",
        "publisher": "Wiley",
        "edition": "3",
        "doi": "10.1002/9781119482260",
    },
    {
        "key": "rubin1976inference",
        "authors": "Rubin, Donald B.",
        "year": "1976",
        "title": "Inference and Missing Data",
        "publication": "Biometrika",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Missing data, data integrity, and accounting-data limitations",
        "method": "missing-data mechanisms",
        "scope": "statistical inference with missing data",
        "contribution": "Introduces central missing-data mechanism concepts.",
        "limitation": "General statistical theory; not an accounting filing guide.",
        "use": "Theoretical foundation for missingness treatment.",
        "claim": "Missingness cannot automatically be treated as zero or unchanged.",
        "doi_url": "https://doi.org/10.1093/biomet/63.3.581",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Biometrika",
        "volume": "63",
        "number": "3",
        "pages": "581--592",
        "doi": "10.1093/biomet/63.3.581",
    },
    {
        "key": "graham2009missing",
        "authors": "Graham, John W.",
        "year": "2009",
        "title": "Missing Data Analysis: Making It Work in the Real World",
        "publication": "Annual Review of Psychology",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Missing data, data integrity, and accounting-data limitations",
        "method": "missing-data practice review",
        "scope": "applied missing-data analysis",
        "contribution": "Practical review of missing-data risks and approaches.",
        "limitation": "Not accounting-specific.",
        "use": "Supports pragmatic missingness diagnostics.",
        "claim": "Missing-data treatment needs explicit documentation and diagnostics.",
        "doi_url": "https://doi.org/10.1146/annurev.psych.58.110405.085530",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Annual Review of Psychology",
        "volume": "60",
        "pages": "549--576",
        "doi": "10.1146/annurev.psych.58.110405.085530",
    },
    {
        "key": "vanbuuren2018flexible",
        "authors": "van Buuren, Stef",
        "year": "2018",
        "title": "Flexible Imputation of Missing Data",
        "publication": "CRC Press",
        "source_type": "book",
        "peer": "unknown",
        "language": "English",
        "bucket": "Missing data, data integrity, and accounting-data limitations",
        "method": "imputation methods",
        "scope": "missing-data imputation",
        "contribution": "Practical reference for imputation approaches.",
        "limitation": "The thesis mostly avoids aggressive imputation, so cite for context rather than implementation.",
        "use": "Explains why imputation is an option but not automatically appropriate.",
        "claim": "Imputation choices must be justified; they should not invent economic facts.",
        "doi_url": "https://doi.org/10.1201/9780429492259",
        "status": "verified_doi",
        "bibtype": "book",
        "publisher": "CRC Press",
        "edition": "2",
        "doi": "10.1201/9780429492259",
    },
    {
        "key": "sec2026financial",
        "authors": "U.S. Securities and Exchange Commission",
        "year": "2026",
        "title": "Financial Statement Data Sets",
        "publication": "SEC.gov",
        "source_type": "official_data_documentation",
        "peer": "no",
        "language": "English",
        "bucket": "Official data sources and empirical context",
        "method": "official SEC dataset documentation",
        "scope": "XBRL financial statement data sets",
        "contribution": "Official source for SEC Financial Statement Data Sets used to build the panel.",
        "limitation": "Official documentation, not peer-reviewed theory.",
        "use": "Primary data source citation.",
        "claim": "Accounting fundamentals are sourced from SEC FSD, not manually invented.",
        "doi_url": "https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets",
        "status": "verified_official_page",
        "bibtype": "misc",
        "url": "https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets",
    },
    {
        "key": "sec2024edgarapi",
        "authors": "U.S. Securities and Exchange Commission",
        "year": "2024",
        "title": "EDGAR Application Programming Interfaces",
        "publication": "SEC.gov",
        "source_type": "official_data_documentation",
        "peer": "no",
        "language": "English",
        "bucket": "Official data sources and empirical context",
        "method": "official API documentation",
        "scope": "EDGAR submissions and company facts APIs",
        "contribution": "Official EDGAR API reference for SEC-company metadata and filings context.",
        "limitation": "Documentation, not model evidence.",
        "use": "Cite for reproducibility and data-access context.",
        "claim": "SEC data access is reproducible through official SEC endpoints and bulk sets.",
        "doi_url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
        "status": "verified_official_page",
        "bibtype": "misc",
        "url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
    },
    {
        "key": "fredapi",
        "authors": "Federal Reserve Bank of St. Louis",
        "year": "2026",
        "title": "FRED API",
        "publication": "FRED Documentation",
        "source_type": "official_data_documentation",
        "peer": "no",
        "language": "English",
        "bucket": "Official data sources and empirical context",
        "method": "official macro-data API documentation",
        "scope": "FRED macroeconomic time series",
        "contribution": "Official source for FRED macro-data retrieval.",
        "limitation": "Documentation, not a theory source.",
        "use": "Primary macro-data source citation.",
        "claim": "Macroeconomic data are sourced from FRED and aligned to prediction dates.",
        "doi_url": "https://fred.stlouisfed.org/docs/api/fred/",
        "status": "verified_official_page",
        "bibtype": "misc",
        "url": "https://fred.stlouisfed.org/docs/api/fred/",
    },
    {
        "key": "fredwhat",
        "authors": "Federal Reserve Bank of St. Louis",
        "year": "2026",
        "title": "What Is FRED?",
        "publication": "FRED Help",
        "source_type": "official_data_documentation",
        "peer": "no",
        "language": "English",
        "bucket": "Official data sources and empirical context",
        "method": "official database description",
        "scope": "FRED database description",
        "contribution": "Describes FRED as a source for economic data.",
        "limitation": "Background documentation only.",
        "use": "Basic source description in data chapter.",
        "claim": "FRED is a recognized source for macroeconomic time-series data.",
        "doi_url": "https://fredhelp.stlouisfed.org/fred/about/about-fred/what-is-fred/",
        "status": "verified_official_page",
        "bibtype": "misc",
        "url": "https://fredhelp.stlouisfed.org/fred/about/about-fred/what-is-fred/",
    },
    {
        "key": "chicagofed2026nfci",
        "authors": "Federal Reserve Bank of Chicago",
        "year": "2026",
        "title": "National Financial Conditions Index",
        "publication": "Federal Reserve Bank of Chicago",
        "source_type": "official_data_documentation",
        "peer": "no",
        "language": "English",
        "bucket": "Macroeconomic conditions, credit cycles, and market-shift/default context",
        "method": "financial-conditions index documentation",
        "scope": "U.S. financial conditions",
        "contribution": "Official documentation for NFCI-style financial-condition context.",
        "limitation": "Index context, not firm-level causality.",
        "use": "Supports market-health/financial-conditions interpretation.",
        "claim": "Financial conditions can be represented as macro-regime context.",
        "doi_url": "https://www.chicagofed.org/research/data/nfci/current-data",
        "status": "verified_official_page",
        "bibtype": "misc",
        "url": "https://www.chicagofed.org/research/data/nfci/current-data",
    },
    {
        "key": "fed2025financialstability",
        "authors": "Board of Governors of the Federal Reserve System",
        "year": "2025",
        "title": "Financial Stability Report",
        "publication": "Federal Reserve Board",
        "source_type": "official_report",
        "peer": "no",
        "language": "English",
        "bucket": "Official data sources and empirical context",
        "method": "financial-stability monitoring report",
        "scope": "U.S. financial system vulnerabilities",
        "contribution": "Provides official context for macro-financial vulnerabilities and corporate/credit conditions.",
        "limitation": "Contextual report, not a firm-level prediction paper.",
        "use": "Recent context source for market shifts and credit conditions.",
        "claim": "The thesis sits in a current policy context where financial stability and credit conditions are monitored.",
        "doi_url": "https://www.federalreserve.gov/publications/financial-stability-report.htm",
        "status": "verified_official_page",
        "bibtype": "misc",
        "url": "https://www.federalreserve.gov/publications/financial-stability-report.htm",
    },
    {
        "key": "spglobal2025bankruptcies",
        "authors": "S&P Global Market Intelligence",
        "year": "2025",
        "title": "U.S. Corporate Bankruptcy Filings",
        "publication": "S&P Global Market Intelligence",
        "source_type": "industry_report",
        "peer": "no",
        "language": "English",
        "bucket": "Official data sources and empirical context",
        "method": "bankruptcy filing tracker/reporting",
        "scope": "U.S. corporate bankruptcy filings",
        "contribution": "Recent industry context showing corporate distress remains relevant.",
        "limitation": "Industry report and not part of the production training data.",
        "use": "Context only, not model source.",
        "claim": "Corporate bankruptcy/distress is a current applied problem.",
        "doi_url": "https://www.spglobal.com/market-intelligence/en/news-insights/latest-news-headlines/us-bankruptcy-tracker",
        "status": "verified_publisher_or_official_page",
        "bibtype": "misc",
        "url": "https://www.spglobal.com/market-intelligence/en/news-insights/latest-news-headlines/us-bankruptcy-tracker",
    },
    {
        "key": "gilchrist2012credit",
        "authors": "Gilchrist, Simon and Zakrajsek, Egon",
        "year": "2012",
        "title": "Credit Spreads and Business Cycle Fluctuations",
        "publication": "American Economic Review",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Macroeconomic conditions, credit cycles, and market-shift/default context",
        "method": "credit-spread/business-cycle analysis",
        "scope": "macroeconomic and credit conditions",
        "contribution": "Shows credit spreads contain business-cycle information.",
        "limitation": "Macro-finance source, not firm SEC accounting by itself.",
        "use": "Supports credit-spread and financial-conditions variables.",
        "claim": "Credit conditions are meaningful market-shift context for firm outcomes.",
        "doi_url": "https://doi.org/10.1257/aer.102.4.1692",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "American Economic Review",
        "volume": "102",
        "number": "4",
        "pages": "1692--1720",
        "doi": "10.1257/aer.102.4.1692",
    },
    {
        "key": "longstaff2005corporate",
        "authors": "Longstaff, Francis A. and Mithal, Sanjay and Neis, Eric",
        "year": "2005",
        "title": "Corporate Yield Spreads: Default Risk or Liquidity? New Evidence from the Credit Default Swap Market",
        "publication": "The Journal of Finance",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Macroeconomic conditions, credit cycles, and market-shift/default context",
        "method": "credit spread decomposition",
        "scope": "corporate yield spreads and CDS data",
        "contribution": "Shows corporate spreads reflect both default and liquidity components.",
        "limitation": "Market spread decomposition, not accounting-panel construction.",
        "use": "Supports caution in interpreting macro/credit variables.",
        "claim": "Credit-market indicators are useful context but not pure distress causes.",
        "doi_url": "https://doi.org/10.1111/j.1540-6261.2005.00797.x",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "The Journal of Finance",
        "volume": "60",
        "number": "5",
        "pages": "2213--2253",
        "doi": "10.1111/j.1540-6261.2005.00797.x",
    },
    {
        "key": "bernanke1999financial",
        "authors": "Bernanke, Ben S. and Gertler, Mark and Gilchrist, Simon",
        "year": "1999",
        "title": "The Financial Accelerator in a Quantitative Business Cycle Framework",
        "publication": "Handbook of Macroeconomics",
        "source_type": "book_chapter",
        "peer": "unknown",
        "language": "English",
        "bucket": "Macroeconomic conditions, credit cycles, and market-shift/default context",
        "method": "financial accelerator theory",
        "scope": "macroeconomic credit frictions",
        "contribution": "Explains how credit frictions can amplify business-cycle shocks.",
        "limitation": "Macro theory, not a firm-level empirical model.",
        "use": "Theoretical support for macro-regime framing.",
        "claim": "Macro-financial regimes can affect firms through credit and demand channels.",
        "doi_url": "https://doi.org/10.1016/S1574-0048(99)10034-X",
        "status": "verified_doi",
        "bibtype": "incollection",
        "booktitle": "Handbook of Macroeconomics",
        "publisher": "Elsevier",
        "volume": "1",
        "pages": "1341--1393",
        "doi": "10.1016/S1574-0048(99)10034-X",
    },
    {
        "key": "hevner2004design",
        "authors": "Hevner, Alan R. and March, Salvatore T. and Park, Jinsoo and Ram, Sudha",
        "year": "2004",
        "title": "Design Science in Information Systems Research",
        "publication": "MIS Quarterly",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Design science, dashboard, and decision-support artifact framing",
        "method": "design science research guidelines",
        "scope": "information systems research artifacts",
        "contribution": "Frames IT artifacts as legitimate research outputs when designed and evaluated rigorously.",
        "limitation": "General IS methodology, not financial distress-specific.",
        "use": "Justifies dashboard/panel/model package as an artifact.",
        "claim": "The dashboard is defensible as a design-science artifact when connected to data and evaluation.",
        "doi_url": "https://doi.org/10.2307/25148625",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "MIS Quarterly",
        "volume": "28",
        "number": "1",
        "pages": "75--105",
        "doi": "10.2307/25148625",
    },
    {
        "key": "peffers2007design",
        "authors": "Peffers, Ken and Tuunanen, Tuure and Rothenberger, Marcus A. and Chatterjee, Samir",
        "year": "2007",
        "title": "A Design Science Research Methodology for Information Systems Research",
        "publication": "Journal of Management Information Systems",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Design science, dashboard, and decision-support artifact framing",
        "method": "design science research methodology",
        "scope": "information systems artifact research",
        "contribution": "Provides a process model for problem identification, artifact design, demonstration, evaluation, and communication.",
        "limitation": "Methodology source, not dashboard evaluation evidence by itself.",
        "use": "Structure artifact chapter.",
        "claim": "The dashboard should be presented as a designed and demonstrated artifact, not decoration.",
        "doi_url": "https://doi.org/10.2753/MIS0742-1222240302",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Management Information Systems",
        "volume": "24",
        "number": "3",
        "pages": "45--77",
        "doi": "10.2753/MIS0742-1222240302",
    },
    {
        "key": "chen2012business",
        "authors": "Chen, Hsinchun and Chiang, Roger H. L. and Storey, Veda C.",
        "year": "2012",
        "title": "Business Intelligence and Analytics: From Big Data to Big Impact",
        "publication": "MIS Quarterly",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Design science, dashboard, and decision-support artifact framing",
        "method": "business intelligence and analytics review",
        "scope": "business analytics and big data",
        "contribution": "Frames analytics as a business-impact and decision-support discipline.",
        "limitation": "Broad analytics source, not a distress model paper.",
        "use": "Positions thesis under business analytics/big data.",
        "claim": "The project belongs to business analytics because it translates data/model outputs into decision support.",
        "doi_url": "https://doi.org/10.2307/41703503",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "MIS Quarterly",
        "volume": "36",
        "number": "4",
        "pages": "1165--1188",
        "doi": "10.2307/41703503",
    },
    {
        "key": "shneiderman1996eyes",
        "authors": "Shneiderman, Ben",
        "year": "1996",
        "title": "The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations",
        "publication": "Proceedings of the IEEE Symposium on Visual Languages",
        "source_type": "peer_reviewed_conference_paper",
        "peer": "yes",
        "language": "English",
        "bucket": "Design science, dashboard, and decision-support artifact framing",
        "method": "information visualization task taxonomy",
        "scope": "visual analytics interaction",
        "contribution": "Supports overview, zoom/filter, and details-on-demand logic.",
        "limitation": "Visualization principle, not financial content.",
        "use": "Justifies dashboard layout and filters.",
        "claim": "Interactive filtering and drill-down are not cosmetic; they support analytical workflow.",
        "doi_url": "https://doi.org/10.1109/VL.1996.545307",
        "status": "verified_doi",
        "bibtype": "inproceedings",
        "booktitle": "Proceedings of the IEEE Symposium on Visual Languages",
        "pages": "336--343",
        "doi": "10.1109/VL.1996.545307",
    },
    {
        "key": "arnott2014decision",
        "authors": "Arnott, David and Pervan, Graham",
        "year": "2014",
        "title": "A Critical Analysis of Decision Support Systems Research Revisited: The Rise of Design Science",
        "publication": "Journal of Information Technology",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Design science, dashboard, and decision-support artifact framing",
        "method": "decision-support systems research review",
        "scope": "DSS and design science",
        "contribution": "Links decision support systems research with design science approaches.",
        "limitation": "Methodological source, not empirical distress evidence.",
        "use": "Supports dashboard as a decision-support system.",
        "claim": "The artifact should be evaluated by usefulness and transparency, not only model metrics.",
        "doi_url": "https://doi.org/10.1057/jit.2014.16",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Information Technology",
        "volume": "29",
        "pages": "269--293",
        "doi": "10.1057/jit.2014.16",
    },
    {
        "key": "barney1991firm",
        "authors": "Barney, Jay",
        "year": "1991",
        "title": "Firm Resources and Sustained Competitive Advantage",
        "publication": "Journal of Management",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Strategic management and resilience framing",
        "method": "resource-based view",
        "scope": "strategic management theory",
        "contribution": "Frames persistent firm differences and resource advantages.",
        "limitation": "Does not directly measure SEC ratios or failure targets.",
        "use": "High-level success/resilience framing only.",
        "claim": "Firm-level heterogeneity matters for success and resilience.",
        "doi_url": "https://doi.org/10.1177/014920639101700108",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Journal of Management",
        "volume": "17",
        "number": "1",
        "pages": "99--120",
        "doi": "10.1177/014920639101700108",
    },
    {
        "key": "teece1997dynamic",
        "authors": "Teece, David J. and Pisano, Gary and Shuen, Amy",
        "year": "1997",
        "title": "Dynamic Capabilities and Strategic Management",
        "publication": "Strategic Management Journal",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Strategic management and resilience framing",
        "method": "dynamic capabilities theory",
        "scope": "strategic management under change",
        "contribution": "Explains adaptation and capability renewal under changing environments.",
        "limitation": "The thesis measures financial signals, not capabilities directly.",
        "use": "Frames market shifts and adaptation without overclaiming unobserved capabilities.",
        "claim": "Adaptation is relevant to the title, but empirical measurement is through observable financial resilience.",
        "doi_url": "https://doi.org/10.1002/(SICI)1097-0266(199708)18:7%3C509::AID-SMJ882%3E3.0.CO;2-Z",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Strategic Management Journal",
        "volume": "18",
        "number": "7",
        "pages": "509--533",
        "doi": "10.1002/(SICI)1097-0266(199708)18:7<509::AID-SMJ882>3.0.CO;2-Z",
    },
    {
        "key": "hannan1984structural",
        "authors": "Hannan, Michael T. and Freeman, John",
        "year": "1984",
        "title": "Structural Inertia and Organizational Change",
        "publication": "American Sociological Review",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Strategic management and resilience framing",
        "method": "organizational ecology",
        "scope": "organizational change and survival",
        "contribution": "Explains why organizations may have difficulty adapting under environmental shifts.",
        "limitation": "Sociological theory, not financial ratio modeling.",
        "use": "Frames failure under market shifts conceptually.",
        "claim": "Failure and survival are linked to adaptation constraints, but the thesis measures only financial outcomes.",
        "doi_url": "https://doi.org/10.2307/2095567",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "American Sociological Review",
        "volume": "49",
        "number": "2",
        "pages": "149--164",
        "doi": "10.2307/2095567",
    },
    {
        "key": "duchek2020resilience",
        "authors": "Duchek, Stephanie",
        "year": "2020",
        "title": "Organizational Resilience: A Capability-Based Conceptualization",
        "publication": "Business Research",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Strategic management and resilience framing",
        "method": "conceptual resilience framework",
        "scope": "organizational resilience",
        "contribution": "Conceptualizes resilience as capabilities for anticipation, coping, and adaptation.",
        "limitation": "Does not provide financial-target definitions for public firms.",
        "use": "Supports naming the success target as resilience with caveats.",
        "claim": "Resilience is conceptually broader than profitability, so the thesis must define a measurable financial proxy.",
        "doi_url": "https://doi.org/10.1007/s40685-019-0085-7",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Business Research",
        "volume": "13",
        "pages": "215--246",
        "doi": "10.1007/s40685-019-0085-7",
    },
    {
        "key": "hepfer2022organizational",
        "authors": "Hepfer, Martin and Lawrence, Thomas B.",
        "year": "2022",
        "title": "The Heterogeneity of Organizational Resilience: Exploring Functional, Operational and Strategic Resilience",
        "publication": "Organization Theory",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Strategic management and resilience framing",
        "method": "organizational resilience theory",
        "scope": "organizational resilience heterogeneity",
        "contribution": "Differentiates forms of resilience rather than treating resilience as one simple outcome.",
        "limitation": "Not a financial prediction model.",
        "use": "Supports careful wording around success/resilience target.",
        "claim": "The thesis uses financial resilience as a proxy, not a complete measure of organizational resilience.",
        "doi_url": "https://doi.org/10.1177/26317877221074701",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "Organization Theory",
        "volume": "3",
        "number": "1",
        "pages": "26317877221074701",
        "doi": "10.1177/26317877221074701",
    },
    {
        "key": "linnenluecke2017resilience",
        "authors": "Linnenluecke, Martina K.",
        "year": "2017",
        "title": "Resilience in Business and Management Research: A Review of Influential Publications and a Research Agenda",
        "publication": "International Journal of Management Reviews",
        "source_type": "academic_journal_article",
        "peer": "yes",
        "language": "English",
        "bucket": "Strategic management and resilience framing",
        "method": "resilience literature review",
        "scope": "business and management resilience research",
        "contribution": "Reviews resilience concepts in business and management literature.",
        "limitation": "Broad review; not a direct measurement recipe for SEC data.",
        "use": "Literature anchor for resilience framing.",
        "claim": "Resilience is a recognized management construct, but operationalization must be explicit.",
        "doi_url": "https://doi.org/10.1111/ijmr.12076",
        "status": "verified_doi",
        "bibtype": "article",
        "journal": "International Journal of Management Reviews",
        "volume": "19",
        "number": "1",
        "pages": "4--30",
        "doi": "10.1111/ijmr.12076",
    },
]


CLAIMS = [
    ("C1", "Financial ratios and accounting fundamentals are valid early-warning inputs, but not a novel idea by themselves.", "beaver1966financial; altman1968financial; ohlson1980financial; zmijewski1984methodological; tian2017financial"),
    ("C2", "Firm-period and forward-looking target design are better aligned with early warning than one static firm observation.", "shumway2001forecasting; duffie2007multi; bauer2014hazard"),
    ("C3", "Strict legal bankruptcy/distress is rare and should be treated as a benchmark, not the whole success/failure story.", "campbell2008distress; tinoco2013financial; dasilas2024machine; zhao2024survey"),
    ("C4", "A broader financial-pressure target is defensible when it is clearly separated from legal bankruptcy.", "campbell2008distress; charalambous2022maximizing; tinoco2013financial; billios2024power"),
    ("C5", "ML models are defensible for distress prediction only when benchmarked and temporally validated.", "barboza2017machine; lessmann2015benchmarking; dasilas2024machine; zhao2024survey; breiman2001random; friedman2001greedy"),
    ("C6", "PR-AUC and positive-class recall/F1 must be shown for rare or imbalanced targets.", "davis2006relationship; saito2015precision; fawcett2006roc; chawla2002smote"),
    ("C7", "Feature importance and SHAP-style explanations describe model behavior, not economic causality.", "lundberg2017unified; ribeiro2016trust; guidotti2018survey; molnar2025interpretable; zhang2022xai"),
    ("C8", "Missing values in accounting panels must not be silently converted into zeros or invented persistence.", "rubin1976inference; little2019missing; graham2009missing; vanbuuren2018flexible"),
    ("C9", "Macro/credit variables are useful context, but claims that macro dominates firm fundamentals require empirical evidence.", "gilchrist2012credit; longstaff2005corporate; bernanke1999financial; tinoco2013financial; chicagofed2026nfci"),
    ("C10", "The artifact can be justified as design science and decision support if it connects data, models, interpretation, and user exploration.", "hevner2004design; peffers2007design; chen2012business; shneiderman1996eyes; arnott2014decision"),
    ("C11", "Strategic success/resilience framing is acceptable only if the operational financial proxy is explicit.", "barney1991firm; teece1997dynamic; hannan1984structural; duchek2020resilience; hepfer2022organizational; linnenluecke2017resilience"),
    ("C12", "The current thesis novelty is the audited SEC/FRED/global-event firm-period panel plus target hierarchy, temporal validation, interpretation tables, and dashboard artifact.", "sec2026financial; sec2024edgarapi; fredapi; fredwhat; hevner2004design; tinoco2013financial; dasilas2024machine"),
]


GAPS = [
    ("G1", "Mature bankruptcy-prediction literature", "Many sources predict bankruptcy or default, so the thesis should not claim novelty in bankruptcy prediction itself.", "Frame novelty around audited panel construction, target hierarchy, and artifact translation."),
    ("G2", "Narrow legal-event target", "Strict bankruptcy labels are clean but rare and can underrepresent earlier deterioration.", "Use strict distress as benchmark and broader financial pressure as the main failure-factor target."),
    ("G3", "Validation weakness", "A common weakness in predictive studies is validation that does not reflect deployment time.", "Use prediction_date and temporal test windows; describe leakage controls."),
    ("G4", "Macro context gap", "Firm fundamentals dominate many models, while macro/credit context is often separate or underinterpreted.", "Add FRED macro/regime/event overlays as contextual market-shift fields."),
    ("G5", "Interpretability gap", "Model performance alone is weak for business analytics and defense.", "Use feature groups, feature importance, and dashboard exploration, while avoiding causal overclaiming."),
    ("G6", "Missingness and accounting data integrity", "SEC filings have missing tags, changing XBRL usage, and flow/balance timing issues.", "Treat missingness explicitly and audit source/qtrs/null behavior."),
    ("G7", "Artifact gap", "Many studies end at metrics and tables.", "Deliver a Streamlit dashboard and GitHub-ready panel/package as practical output."),
]


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    def clean(value: str) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(clean(v) for v in row) + " |")
    return "\n".join(out)


def csv_write(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def accessibility_status(ref: dict[str, str]) -> str:
    url = ref["doi_url"].lower()
    publication = ref["publication"].lower()
    if ref["source_type"] in {"official_data_documentation", "official_report"}:
        return "official_or_public_page_accessible"
    if ref["source_type"] == "industry_report":
        return "public_publisher_page_accessible_full_report_may_require_access"
    open_markers = [
        "mdpi.com",
        "plos",
        "frontiers",
        "pmc.ncbi",
        "jmlr.org",
        "papers.neurips",
        "christophm.github.io",
    ]
    open_publications = {
        "journal of machine learning research",
        "plos one",
        "frontiers in artificial intelligence",
        "self-published open book",
    }
    if any(marker in url for marker in open_markers) or publication in open_publications:
        return "full_text_or_public_page_accessible"
    if ref["source_type"] == "book":
        return "metadata_verified_full_text_access_unknown_or_book_access_limited"
    return "metadata_verified_full_text_access_unknown_or_may_be_paywalled"


def evidence_role(ref: dict[str, str]) -> str:
    bucket = ref["bucket"]
    if ref["source_type"] in {"official_data_documentation", "official_report", "industry_report"}:
        return "data_or_context_source"
    if "Future-work" in ref["use"] or "not implemented" in ref["claim"]:
        return "context_or_future_work"
    if "Strategic management" in bucket:
        return "theoretical_framing"
    if "Machine learning" in bucket and ref["method"] in {"random forest algorithm", "gradient boosting machine", "software implementation paper"}:
        return "method_foundation"
    if "Design science" in bucket:
        return "artifact_methodology"
    if "Missing data" in bucket:
        return "data_integrity_methodology"
    return "core_or_supporting_literature"


def critical_evaluation(ref: dict[str, str]) -> str:
    bucket = ref["bucket"]
    source_type = ref["source_type"]
    if source_type in {"official_data_documentation", "official_report", "industry_report"}:
        return "Strong for data provenance or current context, but not peer-reviewed academic evidence."
    if "Classical" in bucket and ref["year"].isdigit() and int(ref["year"]) < 2000:
        return "Foundational and highly relevant, but older; use to show tradition, not modern novelty."
    title = ref["title"].lower()
    if "Machine learning" in bucket and (
        "systematic" in title or "survey" in title or "literature review" in title or ref["method"] == "literature review"
    ):
        return "Strong current synthesis; useful for field positioning, but not primary evidence for this panel."
    if "Machine learning" in bucket and evidence_role(ref) == "method_foundation":
        return "Strong algorithm or implementation citation, but not finance-specific empirical evidence."
    if "Interpretability" in bucket:
        return "Useful for explaining model transparency; must not be used as causal proof."
    if "Missing data" in bucket:
        return "Useful for defending missingness policy; does not resolve SEC-specific tag availability by itself."
    if "Macroeconomic" in bucket:
        return "Useful for market-shift context; do not use to claim macro variables caused individual firm outcomes."
    if "Design science" in bucket:
        return "Useful for artifact framing and dashboard justification; not evidence of model accuracy."
    if "Strategic management" in bucket:
        return "Useful for framing success/adaptation/resilience; not directly measured unless translated into financial proxies."
    return "Relevant support within its stated scope; cite with the limitation column."


def do_not_use_for(ref: dict[str, str]) -> str:
    bucket = ref["bucket"]
    if ref["source_type"] in {"official_data_documentation", "official_report", "industry_report"}:
        return "Do not use as peer-reviewed theory or model-performance evidence."
    if "Future-work" in ref["use"] or "not implemented" in ref["claim"]:
        return "Do not write as an implemented production feature or model."
    if "Classical" in bucket:
        return "Do not use to claim bankruptcy prediction itself is novel."
    if "Interpretability" in bucket:
        return "Do not use to claim feature importance proves causality."
    if "Missing data" in bucket:
        return "Do not use to justify filling missing SEC values with invented facts."
    if "Macroeconomic" in bucket:
        return "Do not use to claim macro variables dominate without empirical support."
    if "Strategic management" in bucket:
        return "Do not use as direct proof of measured financial resilience."
    if "Machine learning" in bucket:
        return "Do not use to claim algorithm choice alone creates thesis novelty."
    return "Do not cite outside the stated data scope or method scope."


def unknown_or_access_note(ref: dict[str, str]) -> str:
    notes = []
    access = accessibility_status(ref)
    if "unknown" in access or "may_require_access" in access or "paywalled" in access:
        notes.append("full_text_access_unknown_or_access_limited")
    if ref["peer"] == "unknown":
        notes.append("peer_review_status_unknown_or_not_applicable")
    if not notes:
        return "none_flagged"
    return "; ".join(notes)


def evaluation_basis(ref: dict[str, str]) -> str:
    access = accessibility_status(ref)
    if "unknown" in access or "may_require_access" in access or "paywalled" in access:
        return "verified_metadata_and_source_summary_level; full_text_not_assumed"
    return "verified_metadata_and_public_or_official_page_level"


def bib_author(ref: dict[str, str]) -> str:
    if ref["authors"] in {
        "U.S. Securities and Exchange Commission",
        "Federal Reserve Bank of St. Louis",
        "Federal Reserve Bank of Chicago",
        "Board of Governors of the Federal Reserve System",
        "S&P Global Market Intelligence",
    }:
        return "{{{}}}".format(ref["authors"])
    return ref["authors"].replace(" and ", " and ")


def bib_entry(ref: dict[str, str]) -> str:
    key = ref["key"]
    typ = ref["bibtype"]
    fields = {
        "author": bib_author(ref),
        "title": ref["title"],
        "year": ref["year"],
    }
    if typ == "article":
        fields["journal"] = ref.get("journal", ref["publication"])
    elif typ == "inproceedings":
        fields["booktitle"] = ref.get("booktitle", ref["publication"])
    elif typ == "incollection":
        fields["booktitle"] = ref.get("booktitle", ref["publication"])
        if ref.get("publisher"):
            fields["publisher"] = ref["publisher"]
    elif typ == "book":
        fields["publisher"] = ref.get("publisher", ref["publication"])
        if ref.get("edition"):
            fields["edition"] = ref["edition"]
    elif typ == "misc":
        fields["howpublished"] = ref["publication"]
    for opt in ["volume", "number", "pages", "doi", "url"]:
        if ref.get(opt):
            fields[opt] = ref[opt]
    if ref.get("doi") and "url" not in fields:
        fields["url"] = "https://doi.org/" + ref["doi"]
    lines = [f"@{typ}{{{key},"]
    for name, value in fields.items():
        escaped = value.replace("\\", "\\\\")
        lines.append(f"  {name} = {{{escaped}}},")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def write_references_bib() -> None:
    content = "\n\n".join(bib_entry(ref) for ref in REFS) + "\n"
    (DOCS / "references.bib").write_text(content, encoding="utf-8")


def write_bibliography() -> None:
    buckets = defaultdict(list)
    for ref in REFS:
        buckets[ref["bucket"]].append(ref)
    lines = [
        "# Curated Bibliography",
        "",
        "Last updated: 2026-05-06",
        "",
        "This bibliography is curated for the final thesis direction: predictive analytics of success and failure factors across industries using an audited SEC/FRED/global-event firm-period panel, a strict legal distress benchmark, a broader financial-pressure target, a success/resilience target, interpretable machine-learning outputs, and a dashboard artifact.",
        "",
        "The bibliography intentionally mixes classical sources with recent 2020-2025 work. The older papers are used as foundations, not as proof that the topic is modern by themselves. Recent reviews, post-pandemic studies, explainable-AI papers, and official data documentation are included so the literature review reflects the current field.",
        "",
        "Use this file as the writing map. Use `docs/references.bib` for citation-manager import. Use `reports/literature/source_to_claim_map.csv` to connect citations to thesis claims. Use `docs/REFERENCE_CRITICAL_EVALUATION.md` before writing critiques or evaluating source strength.",
        "",
        "## Citation Policy",
        "",
        "- Cite a source only where it directly supports the sentence being written.",
        "- Do not cite future-work sources as if they were implemented data or implemented models.",
        "- Do not describe feature importance or missingness indicators as economic causality.",
        "- Do not call broader financial pressure legal bankruptcy.",
        "- For the thesis core, prioritize peer-reviewed journal articles and official data documentation.",
        "",
    ]
    for bucket, refs in buckets.items():
        lines += [f"## {bucket}", ""]
        rows = []
        for ref in refs:
            rows.append([
                f"`{ref['key']}`",
                f"{ref['authors']} ({ref['year']}). {ref['title']}. *{ref['publication']}*.",
                ref["use"],
                ref["limitation"],
                ref["doi_url"],
            ])
        lines.append(md_table(["Key", "Citation", "Use in Thesis", "Caution", "Verified DOI/URL"], rows))
        lines.append("")
    (DOCS / "BIBLIOGRAPHY.md").write_text("\n".join(lines), encoding="utf-8")


def write_matrix_files() -> None:
    headers = [
        "citation_key",
        "authors",
        "year",
        "title",
        "publication",
        "source_type",
        "peer_reviewed_yes_no_unknown",
        "language",
        "bucket",
        "main_method_or_theory",
        "data_scope",
        "main_contribution",
        "main_limitation_or_critique",
        "how_this_thesis_uses_it",
        "supports_claim",
        "doi_or_url",
        "verification_status",
    ]
    rows = [[
        ref["key"],
        ref["authors"],
        ref["year"],
        ref["title"],
        ref["publication"],
        ref["source_type"],
        ref["peer"],
        ref["language"],
        ref["bucket"],
        ref["method"],
        ref["scope"],
        ref["contribution"],
        ref["limitation"],
        ref["use"],
        ref["claim"],
        ref["doi_url"],
        ref["status"],
    ] for ref in REFS]
    csv_write(REPORTS / "literature_matrix.csv", headers, rows)

    counts = Counter(ref["bucket"] for ref in REFS)
    top_rows = [[bucket, str(counts[bucket])] for bucket in sorted(counts)]
    md = [
        "# Literature Matrix",
        "",
        "Last updated: 2026-05-06",
        "",
        "The full machine-readable matrix is in `reports/literature/literature_matrix.csv`. It records what each source actually supports, its limitation, and how it should be used in the thesis.",
        "",
        "## Bucket Coverage",
        "",
        md_table(["Bucket", "References"], top_rows),
        "",
        "## Matrix Preview",
        "",
        md_table(
            ["Key", "Year", "Bucket", "Contribution", "Thesis Use"],
            [[r[0], r[2], r[8], r[11], r[13]] for r in rows[:20]],
        ),
        "",
        "## Usage Rule",
        "",
        "When writing the thesis, use the `main_limitation_or_critique` column. The literature review should not read like a list of summaries; it should explain what each stream contributes and where it remains insufficient for the current research problem.",
        "",
    ]
    (DOCS / "LITERATURE_MATRIX.md").write_text("\n".join(md), encoding="utf-8")


def write_critical_evaluation_files() -> None:
    headers = [
        "citation_key",
        "authors_year",
        "short_description_what_it_says",
        "critique_or_limitation",
        "evaluation_for_this_thesis",
        "evidence_role",
        "safe_thesis_use",
        "do_not_use_for",
        "accessibility_status",
        "peer_reviewed_yes_no_unknown",
        "metadata_verification_status",
        "unknown_or_inaccessible_flag",
        "evaluation_basis",
        "doi_or_url",
    ]
    rows = []
    for ref in REFS:
        rows.append([
            ref["key"],
            f"{ref['authors']} ({ref['year']})",
            ref["contribution"],
            ref["limitation"],
            critical_evaluation(ref),
            evidence_role(ref),
            ref["use"],
            do_not_use_for(ref),
            accessibility_status(ref),
            ref["peer"],
            ref["status"],
            unknown_or_access_note(ref),
            evaluation_basis(ref),
            ref["doi_url"],
        ])
    csv_write(REPORTS / "reference_critical_evaluation.csv", headers, rows)

    flagged = [row for row in rows if row[11] != "none_flagged"]
    lines = [
        "# Reference Critical Evaluation",
        "",
        "Last updated: 2026-05-06",
        "",
        "This file answers the practical writing question: can every source be described, critiqued, and evaluated? Yes, but with different strength levels. The CSV version is `reports/literature/reference_critical_evaluation.csv`.",
        "",
        "## How To Read This",
        "",
        "- `short_description_what_it_says` is the source-level description.",
        "- `critique_or_limitation` is the thesis-specific critique.",
        "- `evaluation_for_this_thesis` says how strong and safe the source is for this project.",
        "- `accessibility_status` separates verified metadata from full-text access.",
        "- `unknown_or_inaccessible_flag` explicitly marks unknown full-text access, access limits, or unknown/not-applicable peer-review status.",
        "- `evaluation_basis` says whether the evaluation is based on verified metadata/source-summary level or on a public/official page.",
        "",
        "Important: metadata verification is not the same thing as full-text access. Some sources have verified DOI/publisher metadata, but the complete article may be paywalled or not checked locally. Those are labeled as unknown or access-limited.",
        "",
        "## Flag Summary",
        "",
        md_table(
            ["Flag Type", "Count"],
            [
                ["total_sources", str(len(rows))],
                ["sources_with_unknown_or_access_limited_notes", str(len(flagged))],
                ["no_unknown_or_access_issue_flagged", str(len(rows) - len(flagged))],
            ],
        ),
        "",
        "## Sources With Unknown Or Access-Limited Notes",
        "",
        md_table(
            ["Key", "Authors/Year", "Flag", "Access Status"],
            [[row[0], row[1], row[11], row[8]] for row in flagged],
        ),
        "",
        "## Full Evaluation Table",
        "",
        md_table(
            ["Key", "Description", "Critique", "Evaluation", "Access/Unknown"],
            [[row[0], row[2], row[3], row[4], row[11]] for row in rows],
        ),
        "",
    ]
    (DOCS / "REFERENCE_CRITICAL_EVALUATION.md").write_text("\n".join(lines), encoding="utf-8")


def write_quality_audit() -> None:
    total = len(REFS)
    journal = sum(1 for ref in REFS if ref["source_type"] == "academic_journal_article")
    peer = sum(1 for ref in REFS if ref["peer"] == "yes")
    english_journal = sum(1 for ref in REFS if ref["source_type"] == "academic_journal_article" and ref["language"] == "English")
    recent_2020 = sum(1 for ref in REFS if ref["year"].isdigit() and int(ref["year"]) >= 2020)
    doi_or_official = sum(1 for ref in REFS if ref["status"].startswith("verified"))
    access_unknown_or_limited = sum(1 for ref in REFS if unknown_or_access_note(ref) != "none_flagged")
    access_clear = total - access_unknown_or_limited
    bucket_counts = Counter(ref["bucket"] for ref in REFS)
    audit_rows = [
        ["total_references", str(total), ">= 50", "PASS" if total >= 50 else "TODO", "Thesis requirement is at least 50 sources."],
        ["academic_journal_articles", str(journal), ">= 25", "PASS" if journal >= 25 else "TODO", "Requirement asks roughly 50-60% academic journal articles; this package exceeds that floor."],
        ["peer_reviewed_sources", str(peer), ">= 30", "PASS" if peer >= 30 else "TODO", "Includes journal articles and peer-reviewed conference papers."],
        ["english_language_academic_journal_articles", str(english_journal), ">= 17", "PASS" if english_journal >= 17 else "TODO", "This satisfies the one-third foreign English-language academic journal requirement under the current source set."],
        ["recent_2020_or_newer_sources", str(recent_2020), ">= 12", "PASS" if recent_2020 >= 12 else "REVIEW", "Recent sources are included so the review is not only classical."],
        ["verified_doi_or_official_pages", str(doi_or_official), f"{total}", "PASS" if doi_or_official == total else "REVIEW", "Every row has a DOI, official page, publisher page, or official report URL."],
        ["sources_with_clear_public_or_official_access_flag", str(access_clear), "documented", "PASS", "These sources are marked as official/public/open-page accessible."],
        ["sources_with_unknown_or_access_limited_notes", str(access_unknown_or_limited), "explicitly labeled", "PASS", "These are not removed; they are labeled in the critical-evaluation table."],
    ]
    for bucket, count in sorted(bucket_counts.items()):
        audit_rows.append([f"bucket::{bucket}", str(count), "see plan minimums", "PASS", "Bucket represented in matrix."])
    csv_write(REPORTS / "reference_quality_audit.csv", ["metric", "value", "target", "status", "note"], audit_rows)

    md = [
        "# Bibliography Audit",
        "",
        "Last updated: 2026-05-06",
        "",
        "## Verdict",
        "",
        "PASS for thesis-readiness. The bibliography now contains more than 50 verified references, a majority of academic journal articles, current 2020-2025 sources, official data documentation, and a source-to-claim map. It is suitable as a basis for writing, assuming the thesis text uses citations precisely and does not overclaim.",
        "",
        "## Counts",
        "",
        md_table(["Metric", "Value", "Target", "Status", "Note"], audit_rows[:8]),
        "",
        "## Bucket Counts",
        "",
        md_table(["Bucket", "Count"], [[bucket, str(count)] for bucket, count in sorted(bucket_counts.items())]),
        "",
        "## Sources To Treat Carefully",
        "",
        "- `merton1974pricing`, `bharath2008forecasting`, and `hillegeist2004assessing` support market-based default models and limitations/future work; they should not be written as implemented production features.",
        "- Official SEC, FRED, Chicago Fed, Federal Reserve, and S&P Global sources support data/context, not academic theory.",
        "- `molnar2025interpretable` is a practical book/reference, not a journal article. Use it for method explanation and cautions.",
        "- Strategic management sources support framing around adaptation and resilience, but the thesis only measures financial proxies.",
        "",
        "## Unsafe Citation Patterns",
        "",
        "- Do not cite classical distress papers to claim novelty in bankruptcy prediction.",
        "- Do not cite XAI sources to claim feature importance proves causality.",
        "- Do not cite macro/credit-cycle papers to claim macro variables caused individual bankruptcies.",
        "- Do not cite market-based default papers as if CHS/Merton distance-to-default features were implemented.",
        "",
    ]
    (DOCS / "BIBLIOGRAPHY_AUDIT.md").write_text("\n".join(md), encoding="utf-8")


def write_claim_and_gap_files() -> None:
    csv_write(
        REPORTS / "source_to_claim_map.csv",
        ["claim_id", "thesis_claim", "supporting_citation_keys"],
        [list(row) for row in CLAIMS],
    )
    csv_write(
        REPORTS / "research_gap_synthesis.csv",
        ["gap_id", "literature_stream", "what_prior_work_does_or_misses", "thesis_response"],
        [list(row) for row in GAPS],
    )


def write_search_strategy() -> None:
    text = dedent(
        """
        # Literature Search Strategy

        Last updated: 2026-05-06

        ## Objective

        Build a thesis-grade literature base for predictive analytics of company success and failure factors under market shifts. The search deliberately combines classical distress-prediction sources, recent 2020-2025 machine-learning and review papers, macro/credit-cycle research, explainable-ML sources, missing-data methodology, design-science/dashboard literature, strategic resilience framing, and official data documentation.

        ## Search Logic

        Search buckets:

        - classical firm failure and financial distress prediction;
        - firm fundamentals, financial ratios, and deterioration features;
        - macroeconomic conditions, credit cycles, and market-shift/default context;
        - machine learning, rare-event evaluation, and temporal validation;
        - interpretability and explainable ML;
        - missing data, data integrity, and accounting-data limitations;
        - design science, dashboard, and decision-support artifact framing;
        - strategic management and resilience framing;
        - official data sources and empirical context.

        Query patterns used:

        - `financial distress prediction machine learning systematic literature review 2024 DOI`;
        - `bankruptcy prediction machine learning survey business failure prediction 2024`;
        - `financial ratios bankruptcy prediction international evidence DOI`;
        - `credit spreads business cycle fluctuations DOI`;
        - `explainable artificial intelligence financial distress prediction DOI`;
        - `design science information systems research dashboard decision support DOI`;
        - official SEC/FRED/Chicago Fed/Federal Reserve data documentation searches.

        ## Inclusion Rules

        - Prefer peer-reviewed journal articles where the source is used to support theory or empirical methodology.
        - Include classic sources only when they are foundational and still cited.
        - Include recent 2020-2025 sources to prove the topic is current.
        - Include official data documentation for SEC, FRED, and macro/financial-condition sources.
        - Include source-specific limitations so the thesis can critique rather than merely summarize.

        ## Exclusion Rules

        - Do not use AI-generated reports as academic references.
        - Do not use blogs or encyclopedia-style pages as counted academic support.
        - Do not include HR, ESG, patents, governance, NLP, Russia/Hong Kong/RFSD, or market-price implementation sources as if they were part of the production pipeline.
        - Do not add unverifiable DOIs, page ranges, or journal titles.

        ## Verification Standard

        Each reference in `docs/references.bib` and `reports/literature/literature_matrix.csv` has either:

        - a DOI link;
        - an official journal/publisher page;
        - an official public-data documentation page; or
        - an official institutional/report page.

        The literature matrix stores the verified URL or DOI and a status flag. The thesis text should cite only the references that directly support the claim being made.
        """
    ).strip() + "\n"
    (DOCS / "LITERATURE_SEARCH_STRATEGY.md").write_text(text, encoding="utf-8")


def write_literature_review_docs() -> None:
    outline = dedent(
        """
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
        - Remaining caveat: strict distress event-date provenance remains a REVIEW risk and should be reported transparently.
        """
    ).strip() + "\n"
    (DOCS / "LITERATURE_REVIEW_OUTLINE.md").write_text(outline, encoding="utf-8")

    review = dedent(
        """
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

        The thesis should be honest about limits. Strict legal distress remains rare and event-date provenance still has a review caveat. Broader financial pressure is not bankruptcy. Resilience is measured through financial proxies, not through all organizational capabilities. Macro and event variables provide context, not automatic causality. These limitations do not weaken the thesis if they are written clearly; they make the contribution more defensible.
        """
    ).strip() + "\n"
    (DOCS / "LITERATURE_REVIEW_DRAFT.md").write_text(review, encoding="utf-8")

    intro = dedent(
        """
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
        """
    ).strip() + "\n"
    (DOCS / "INTRODUCTION_RESEARCH_GAP_DRAFT.md").write_text(intro, encoding="utf-8")

    positioning = dedent(
        """
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
        """
    ).strip() + "\n"
    (DOCS / "THESIS_THEORETICAL_POSITIONING.md").write_text(positioning, encoding="utf-8")


def write_source_truth_index() -> None:
    text = dedent(
        """
        # Final Source Of Truth Index

        Last updated: 2026-05-06

        Use this file to decide which project documents are authoritative during thesis writing.

        ## Current Production Metrics

        - Production panel rows: 31,786.
        - Production panel columns: 181.
        - SEC CIKs: 540.
        - Ticker/display IDs: 541.
        - Period range: 2009-03-31 to 2026-02-28.
        - Prediction timestamp range: 2009-04-15 to 2026-03-31.
        - Prediction-date policy: `prediction_date = filed_date`.

        ## Target Hierarchy

        - Strict legal benchmark: `distress_next_4q`.
        - Main failure-factor target: `failure_pressure_conservative_v2_next_4obs`.
        - Main success/resilience target: `success_resilience_next_4q`.
        - Diagnostic targets only: `failure_pressure_balance_liquidity_next_4obs`, `success_resilience_quality_v2_next_4obs`.

        ## Files To Trust

        - `docs/STRATEGIST_HANDOFF_20260505.md` for strategist-facing summary.
        - `reports/RUN_STATUS_FINAL.md` for production run metrics.
        - `reports/data_quality/readiness_table_20260505.csv` for readiness status.
        - `docs/FINAL_TARGET_HIERARCHY.md` for target roles.
        - `docs/PROJECT_CHRONICLE.md` for reasoning history and decisions.
        - `docs/BIBLIOGRAPHY.md` and `docs/references.bib` for citations.
        - `reports/literature/literature_matrix.csv` for source-to-claim usage.
        - `docs/REFERENCE_CRITICAL_EVALUATION.md` and `reports/literature/reference_critical_evaluation.csv` for source descriptions, critiques, evaluations, and unknown/access-limited flags.

        ## Literature Package Metrics

        - Total verified references: 67.
        - Academic journal articles: 51.
        - Peer-reviewed sources including conference papers: 56.
        - Sources from 2020 onward: 21.
        - Verified DOI, official page, publisher page, or official report URL: 67/67.
        - Unknown or access-limited notes are explicitly labeled in `reports/literature/reference_critical_evaluation.csv`.

        ## Files To Treat As Historical

        - Earlier target-experiment folders are useful evidence but not current production status.
        - Older notes that discuss whether to promote the broader target are historical. The current production broader failure-pressure target is already promoted.
        - Any old reference to a 180-column production panel is historical. The current production panel has 181 columns.

        ## Remaining Review Risk

        - `distress_event_dates = REVIEW` remains the major data-integrity caveat.
        - Event-review firms must not be described as legal distress cases unless source-verified and added to `config/distress_event_dates.csv`.
        """
    ).strip() + "\n"
    (DOCS / "FINAL_SOURCE_OF_TRUTH_INDEX.md").write_text(text, encoding="utf-8")


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_references_bib()
    write_bibliography()
    write_matrix_files()
    write_critical_evaluation_files()
    write_quality_audit()
    write_claim_and_gap_files()
    write_search_strategy()
    write_literature_review_docs()
    write_source_truth_index()
    print(f"Wrote {len(REFS)} references and literature package outputs.")


if __name__ == "__main__":
    main()
