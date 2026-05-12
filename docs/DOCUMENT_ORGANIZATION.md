# Document Organization

Last updated: 2026-05-12

## Current Source Of Truth

Use these first for current production facts, thesis writing, and strategist review:

- `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md`
- `docs/FINAL_ACCEPTANCE_REPORT_20260512.md`
- `docs/FINAL_CONSISTENCY_REVIEW_20260512.md`
- `docs/FACTUAL_FREEZE_20260509.md`
- `docs/CURRENT_STATUS.md`
- `reports/RUN_STATUS_FINAL.md`
- `docs/FINAL_TARGET_HIERARCHY.md`
- `docs/MASTER_DATA_MODEL_TARGET_EXPLAINER.md`
- `docs/THESIS_CLAIMS_SAFE_UNSAFE_FINAL.md`
- `docs/FINAL_SCOPE_LOCK_NOTE.md`
- `docs/PROJECT_GLOSSARY_AND_FIELD_GUIDE.md`
- `docs/TECHNICAL_QA_RESOLUTION_20260509.md`

The current production panel facts are controlled by `docs/FINAL_SOURCE_OF_TRUTH_INDEX.md` and `docs/FACTUAL_FREEZE_20260509.md`. As of the current freeze, the production panel has 31,702 rows, 190 columns, 540 SEC CIKs, 540 ticker/display IDs, and `prediction_date = filed_date`.

## Decision History

- `docs/PROJECT_CHRONICLE.md` is the full decision and build log. It intentionally contains old intermediate counts, older model numbers, failed ideas, and superseded decisions. Use it for history, not as the current factual authority.
- `docs/STRATEGIST_HANDOFF_20260505.md` is now a historical handoff. It contains stale counts from an earlier rebuild and should not be used as a current source-of-truth document.

## Extension Layer

The extension layer is thesis-relevant. Four target-lab labels have been promoted through a documented audit gate into the production panel as validated secondary target columns; diagnostic and robustness-extension labels remain outside the production panel.

- `docs/CONTROLLED_EXTENSION_DECISION_REPORT.md`
- `docs/EXPLORATORY_TARGET_LAB.md`
- `docs/CALIBRATION_AND_RANKING_NOTE.md`
- `docs/FINANCIAL_QUALITY_FEATURES_NOTE.md`
- `docs/MARKET_HEALTH_INDEX_V2_NOTE.md`
- `reports/target_lab/exploratory_target_lab_summary.md`
- `reports/target_lab/validation_extension_gate_summary.md`
- `reports/target_lab/validated_secondary_target_promotion_audit_summary.md`

Current extension status: four former exploratory targets are now validated secondary production outcomes, `deterioration_next_4obs` remains diagnostic, and two creative targets are robustness-extension outcomes. `persistent_resilience_next_6obs` is strong enough for long-horizon sensitivity analysis; `sector_relative_improvement_next_4obs` is useful but weaker and should stay exploratory robustness. Calibration, ranking diagnostics, feature-level importance, direction-of-effect, and reason-code reports now exist.

## Thesis Writing Package

- `docs/THESIS_REQUIREMENTS_CHECKLIST.md`
- `docs/INTRODUCTION_RESEARCH_GAP_DRAFT.md`
- `docs/LITERATURE_REVIEW_DRAFT.md`
- `docs/LITERATURE_REVIEW_OUTLINE.md`
- `docs/THESIS_THEORETICAL_POSITIONING.md`
- `docs/BIBLIOGRAPHY.md`
- `docs/references.bib`
- `docs/LITERATURE_MATRIX.md`
- `docs/REFERENCE_CRITICAL_EVALUATION.md`
- `docs/RUSSIA_EMERGING_MARKET_LITERATURE_ADDITIONS.md`
- `docs/LEGAL_FULL_TEXT_ACCESS_AND_READING_NOTES.md`

## Methodology And Artifact Notes

- `docs/PANEL_DATA_ARCHITECTURE_AND_EXPANSION.md`
- `docs/FACTOR_ANALYSIS_AND_DATA_INTEGRITY.md`
- `docs/MISSINGNESS_INDICATOR_POLICY.md`
- `docs/TARGET_DEFINITIONS_FINAL_REVIEW.md`
- `docs/DISTRESS_EVENT_DATE_PROVENANCE.md`
- `docs/MARKET_HEALTH_INDEX_NOTE.md`
- `docs/MARKET_HEALTH_INDEX_V2_NOTE.md`
- `docs/CALIBRATION_AND_RANKING_NOTE.md`
- `docs/MODEL_TUNING_AND_AUTOGLUON_NOTE.md`
- `reports/model_tuning_advanced/ADVANCED_BOOSTING_PROTOCOL.md`
- `docs/GLOBAL_EVENTS_AND_DASHBOARD_STRATEGY.md`
- `docs/TOPIC_RELEVANCE_AND_SCOPE_NOTE.md`

## Supporting Literature QA

- `docs/LITERATURE_SEARCH_STRATEGY.md`
- `docs/BIBLIOGRAPHY_AUDIT.md`

## Historical / Redundant Archive

Superseded notes are kept under:

```text
docs/_redundant/
```

The archive has its own manifest:

```text
docs/_redundant/README.md
```

Do not use archived files as current project status unless explicitly writing about the reasoning history.

## Superseded Root Documents

Some historical documents remain in the root `docs/` folder because other files reference them. They should not be cited for current panel dimensions, current target counts, or current model metrics:

- `docs/STRATEGIST_HANDOFF_20260505.md`
- `docs/DATA_INTEGRITY_CAVEAT_AUDIT_20260507.md`
- `docs/REPRODUCIBILITY_FREEZE_20260507.md`

Use the May 9 source-of-truth/freeze docs and the current run status instead.

## External Uploaded Inputs

Original PDFs, external review JSON files, and uploaded strategist plans are organized outside the clean workspace at:

```text
/Users/whotfisart/codex/Thesis work/_external_inputs/
```

These are input/source files, not current project-status documents.
