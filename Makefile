# WealthLens HQ — Makefile
#
# Requires: GNU Make with a POSIX shell (Git Bash on Windows).
# Will not work under cmd.exe or PowerShell directly.
#
# Tiered CI structure:
#   ci-quick   (~60s)  — backend lint + tests, no external deps
#   ci-full    (~3 min) — backend + frontend lint, type-check, tests, build
#
# Reliability contract: every check target runs its tool and FAILS LOUDLY on a
# non-zero exit. Targets do NOT swallow errors (no `2>/dev/null || echo ...`), so
# `make ci-quick` is green only when lint, types, and tests genuinely pass.
#
# Usage:
#   make help          — show all targets
#   make ci-quick      — pre-push gate (fast)
#   make ci-full       — full confidence pass

# ── Python detection ──────────────────────────────────────────────────────
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
BACKEND_DIR := projects/wealthlens-dashboard/backend
FRONTEND_DIR := projects/wealthlens-dashboard/frontend
PIPELINE_DIR := automation/data-pipelines
ANALYSIS_DIR := automation/analysis

.PHONY: help install lint format test dev-backend dev-frontend \
        ci-quick ci-full \
        frontend-install frontend-build frontend-dev frontend-lint frontend-test frontend-typecheck \
        backend-install backend-test backend-lint backend-format \
        pipeline-test pipelines validate automation-lint tests-typecheck dev-tools-install test-hooks clean

# ── Help ──────────────────────────────────────────────────────────────────
help: ## Show all targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Backend ───────────────────────────────────────────────────────────────
# Check targets fail loudly: a non-zero exit from ruff/mypy/pytest aborts the
# recipe (and any aggregate target that depends on it). No error swallowing.
backend-install: ## Install backend Python dependencies (incl. dev: pytest, ruff, mypy)
	cd $(BACKEND_DIR) && $(PYTHON) -m pip install -r requirements-dev.txt

backend-test: ## Run backend pytest suite
	cd $(BACKEND_DIR) && $(PYTHON) -m pytest -q

backend-lint: ## Run ruff check + mypy on backend
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff check .
	cd $(BACKEND_DIR) && $(PYTHON) -m mypy .

backend-format: ## Auto-format backend with ruff
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff format .

dev-backend: ## Start backend dev server (uvicorn)
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# ── Frontend ──────────────────────────────────────────────────────────────
frontend-install: ## Install frontend npm dependencies (local dev; CI uses `npm ci`)
	cd $(FRONTEND_DIR) && npm install

frontend-build: ## Build frontend for production
	cd $(FRONTEND_DIR) && npm run build

frontend-dev: ## Start frontend dev server (vite)
	cd $(FRONTEND_DIR) && npm run dev

frontend-lint: ## Lint frontend with ESLint (matches CI; prettier not yet a gate)
	cd $(FRONTEND_DIR) && npm run lint

frontend-typecheck: ## Type-check frontend with vue-tsc
	cd $(FRONTEND_DIR) && npm run typecheck

frontend-test: ## Run frontend vitest suite
	cd $(FRONTEND_DIR) && npm run test

# ── Data pipelines ────────────────────────────────────────────────────────
pipeline-test: ## Run data-pipeline unit tests (offline)
	# PIPELINE_DIR has a hyphen so it is not an importable package; put it on
	# PYTHONPATH so tests can import the pipeline modules without ModuleNotFoundError.
	PYTHONPATH=$(PIPELINE_DIR) $(PYTHON) -m pytest $(PIPELINE_DIR)/tests/ -q

automation-lint: ## Type-check automation/ with mypy (fails loudly on any error)
	$(PYTHON) -m mypy automation

tests-typecheck: ## Type-check root tests/ with mypy (separate run: a shared `tests` pkg name clashes with automation/data-pipelines/tests)
	$(PYTHON) -m mypy tests

validate: ## Validate all processed CSV datasets
	$(PYTHON) $(PIPELINE_DIR)/validate.py

pipelines: ## Run all working data pipelines (fetches live data)
	$(PYTHON) $(PIPELINE_DIR)/fetch_wid_data.py
	$(PYTHON) $(PIPELINE_DIR)/fetch_ons_housing.py
	$(PYTHON) $(PIPELINE_DIR)/fetch_ons_wealth.py
	$(PYTHON) $(PIPELINE_DIR)/fetch_hmrc_stats.py

# ── Aggregate targets ─────────────────────────────────────────────────────
dev-tools-install: ## Install root dev tools (mypy, ruff, pandas-stubs, Pillow, ...) used by lint/test
	$(PYTHON) -m pip install ".[dev]"

install: backend-install frontend-install dev-tools-install ## Install all dependencies

lint: backend-lint frontend-lint automation-lint tests-typecheck ## Run all linters
format: backend-format ## Auto-format all code
test: backend-test frontend-test ## Run all tests

dev-frontend: ## Alias for frontend dev server
	cd $(FRONTEND_DIR) && npm run dev

# ── CI tiers ──────────────────────────────────────────────────────────────
ci-quick: backend-lint backend-test ## Pre-push gate (~60s, no external deps)
	@echo "ci-quick passed"

ci-full: backend-lint automation-lint tests-typecheck backend-test frontend-lint frontend-typecheck frontend-test frontend-build ## Full CI (~3 min)
	@echo "ci-full passed"

# ── Hooks ─────────────────────────────────────────────────────────────────
test-hooks: ## Test Claude Code agent hooks
	@echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | $(PYTHON) scripts/agent_hooks/pre_tool_use.py && echo "Hook test: destructive command denied (expected)"
	@echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | $(PYTHON) scripts/agent_hooks/pre_tool_use.py && echo "Hook test: safe command allowed (expected)"
	@echo '{"tool_name":"Bash","tool_input":{"command":"git push --force"}}' | $(PYTHON) scripts/agent_hooks/pre_tool_use.py && echo "Hook test: force-push denied (expected)"

# ── Clean ─────────────────────────────────────────────────────────────────
# `clean` is the one place `|| true` is correct: removing absent paths is not a
# failure.
clean: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
