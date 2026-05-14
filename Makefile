PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin
PORT ?= 8501
SEC_FROM ?= 2009q1
SEC_TO ?= latest

.PHONY: setup check dashboard download-fred download-sec build-panel refresh-panel rebuild-models

$(BIN)/python:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

setup: $(BIN)/python

check: $(BIN)/python
	$(BIN)/python scripts/project_audit/github_package_smoke_check.py

dashboard: $(BIN)/python
	$(BIN)/streamlit run app/dashboard.py --server.port $(PORT)

download-fred: $(BIN)/python
	$(BIN)/python scripts/data/download_fred_series.py

download-sec: $(BIN)/python
	$(BIN)/python scripts/data/download_sec_fsd_zips.py --from $(SEC_FROM) --to $(SEC_TO)

build-panel: $(BIN)/python
	$(BIN)/python scripts/sec_fsd/inventory_sec_zips.py
	$(BIN)/python scripts/sec_fsd/index_submissions.py
	$(BIN)/python scripts/sec_fsd/match_distress_candidates.py
	$(BIN)/python scripts/sec_fsd/build_universe_v2.py
	$(BIN)/python scripts/sec_fsd/build_panel_v2.py

refresh-panel: $(BIN)/python
	$(MAKE) download-sec
	$(MAKE) download-fred
	$(MAKE) build-panel

rebuild-models: $(BIN)/python
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target distress_next_4q
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target failure_pressure_conservative_v2_next_4obs
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target success_resilience_next_4q
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target industry_relative_resilience_next_4obs
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target stress_resilience_next_4obs
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target recovery_next_4obs
	$(BIN)/python scripts/modeling/train_panel_v2_models.py --target quality_success_cashflow_next_4obs
	$(BIN)/python scripts/modeling/run_exploratory_target_lab.py
	$(BIN)/python scripts/modeling/promote_validated_secondary_targets.py
	$(BIN)/python scripts/modeling/run_validation_extension_gate.py
	$(BIN)/python scripts/modeling/run_target_feature_tweak_experiments.py
	$(BIN)/python scripts/modeling/run_panel_v2_ablation.py
	$(BIN)/python scripts/modeling/make_panel_v2_analysis_outputs.py
	$(BIN)/python scripts/modeling/feature_contribution_summary.py
