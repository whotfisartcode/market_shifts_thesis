PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: setup check dashboard

$(BIN)/python:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

setup: $(BIN)/python

check: $(BIN)/python
	$(BIN)/python scripts/project_audit/github_package_smoke_check.py

dashboard: $(BIN)/python
	$(BIN)/streamlit run app/dashboard.py
