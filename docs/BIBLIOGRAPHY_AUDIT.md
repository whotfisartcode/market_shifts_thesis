# Bibliography Audit

Last updated: 2026-05-06

## Verdict

PASS for thesis-readiness. The bibliography now contains more than 50 verified references, a majority of academic journal articles, current 2020-2026 sources, official data documentation, Russia/emerging-market contextual additions, and a source-to-claim map. It is suitable as a basis for writing, assuming the thesis text uses citations precisely and does not overclaim.

## Counts

| Metric | Value | Target | Status | Note |
| --- | --- | --- | --- | --- |
| total_references | 75 | >= 50 | PASS | Thesis requirement is at least 50 sources. |
| academic_journal_articles | 58 | >= 25 | PASS | Requirement asks roughly 50-60% academic journal articles; this package exceeds that floor. |
| peer_reviewed_sources | 62 | >= 30 | PASS | Includes journal articles and peer-reviewed conference papers. |
| english_language_academic_journal_articles | 57 | >= 17 | PASS | This satisfies the one-third foreign English-language academic journal requirement under the current source set. |
| recent_2020_or_newer_sources | 27 | >= 12 | PASS | Recent sources are included so the review is not only classical. |
| verified_doi_or_official_pages | 75 | 75 | PASS | Every row has a DOI, official page, publisher page, or official report URL. |
| sources_with_clear_public_or_official_access_flag | 14 | documented | PASS | These sources are marked as official/public/open-page accessible. |
| sources_with_unknown_or_access_limited_notes | 61 | explicitly labeled | PASS | These are not removed; they are labeled in the critical-evaluation table. |

## Bucket Counts

| Bucket | Count |
| --- | --- |
| Classical firm failure and financial distress prediction | 11 |
| Design science, dashboard, and decision-support artifact framing | 5 |
| Firm fundamentals, financial ratios, and deterioration features | 7 |
| Interpretability and explainable ML | 7 |
| Machine learning, rare-event evaluation, and temporal validation | 15 |
| Macroeconomic conditions, credit cycles, and market-shift/default context | 7 |
| Missing data, data integrity, and accounting-data limitations | 4 |
| Official data sources and empirical context | 8 |
| Strategic management and resilience framing | 6 |
| Emerging-market and Russia-specific distress prediction context | 5 |

## Sources To Treat Carefully

- `merton1974pricing`, `bharath2008forecasting`, and `hillegeist2004assessing` support market-based default models and limitations/future work; they should not be written as implemented production features.
- Official SEC, FRED, Chicago Fed, Federal Reserve, and S&P Global sources support data and context, not academic theory.
- Russia/emerging-market additions support context, limitations, and future extension. They do not change the implemented empirical scope from the U.S. SEC/FRED panel.
- `molnar2025interpretable` is a practical book/reference, not a journal article. Use it for method explanation and cautions.
- Strategic management sources support framing around adaptation and resilience, but the thesis only measures financial proxies.

## Unsafe Citation Patterns

- Do not cite classical distress papers to claim novelty in bankruptcy prediction.
- Do not cite XAI sources to claim feature importance proves causality.
- Do not cite macro/credit-cycle papers to claim macro variables caused individual bankruptcies.
- Do not cite market-based default papers as if CHS/Merton distance-to-default features were implemented.
- Do not cite Russia-specific sources as if the current model estimates Russian firms unless a Russian dataset is later added and audited.
