# Clever: Sovereign Cognitive Partner
# Level 4 Execution Contract (Conservative Realization)
# Note: This Makefile reflects existing repository artifacts while pruning obsolete implementation.

# --- Configuration ---
HOST ?= 127.0.0.1
PORT ?= 5000
PYTHON = python3
PIP = $(PYTHON) -m pip

# --- PHONY Targets ---
.PHONY: help setup optimize start run test lint format clean

help:
	@echo "Clever Repository Management (Conservative)"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Core Operations:"
	@echo "  setup              Install dependencies from requirements.txt"
	@echo "  optimize           Run hardware and environment optimizations"
	@echo "  start              Launch Clever using the canonical runtime entry point"
	@echo "  run                Execute the main application (app.py)"
	@echo ""
	@echo "Development & Quality (Level 5 Standards):"
	@echo "  test               Execute the test suite using pytest"
	@echo "  lint               Run style checks (flake8, black)"
	@echo "  format             Automatically format code using black"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean              Remove temporary build and cache artifacts"

# --- Core Targets ---

setup:
	$(PIP) install -r requirements.txt
	@echo "Environment initialized."

optimize:
	# Realizes Hardware Optimization using the current root-level implementation.
	$(PYTHON) hardware_optimizer.py

start:
	# Primary runtime launcher.
	./runtime/start_clever.sh

run:
	# Direct application execution.
	$(PYTHON) app.py --host $(HOST) --port $(PORT)

# --- Development Standards (Level 5) ---

test:
	# Executes verified tests only.
	$(PYTHON) -m pytest tests/

lint:
	# Enforces repository standards.
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check .

format:
	# Standardizes implementation style.
	black .

# --- Cleanup ---

clean:
	# Removes artifacts to maintain a clean repository state.
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	@echo "Repository purged of ephemeral artifacts."
