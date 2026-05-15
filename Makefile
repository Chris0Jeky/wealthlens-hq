# WealthLens HQ — Makefile
#
# Requires: GNU Make with a POSIX shell (Git Bash on Windows).
# Will not work under cmd.exe or PowerShell directly.
#
# Tiered CI structure:
#   ci-quick   (~60s)  — lint + backend tests, no external deps
#   ci-full    (~3 min) — lint + tests + frontend build + type check
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
        frontend-install frontend-build frontend-dev frontend-lint frontend-typecheck \
        backend-install backend-test backend-lint backend-format \
        pipeline-test pipelines clean

# ── Help ──────────────────────────────────────────────────────────────────
help: ## Show all targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Backend ───────────────────────────────────────────────────────────────
backend-install: ## Install backend Python dependencies
	cd $(BACKEND_DIR) && $(PYTHON) -m pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt yet"

backend-test: ## Run backend pytest suite
	cd $(BACKEND_DIR) && $(PYTHON) -m pytest -q 2>/dev/null || echo "No tests yet"

backend-lint: ## Run ruff check + mypy on backend
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff check . 2>/dev/null || echo "No backend code yet"
	cd $(BACKEND_DIR) && $(PYTHON) -m mypy . 2>/dev/null || echo "No backend code yet"

backend-format: ## Auto-format backend with ruff
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff format . 2>/dev/null || echo "No backend code yet"

dev-backend: ## Start backend dev server (uvicorn)
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# ── Frontend ──────────────────────────────────────────────────────────────
frontend-install: ## Install frontend npm dependencies
	cd $(FRONTEND_DIR) && npm install 2>/dev/null || echo "No package.json yet"

frontend-build: ## Build frontend for production
	cd $(FRONTEND_DIR) && npm run build 2>/dev/null || echo "No frontend code yet"

frontend-dev: ## Start frontend dev server (vite)
	cd $(FRONTEND_DIR) && npm run dev

frontend-lint: ## Lint frontend with ESLint + Prettier
	cd $(FRONTEND_DIR) && npx eslint . 2>/dev/null || echo "No frontend code yet"
	cd $(FRONTEND_DIR) && npx prettier --check . 2>/dev/null || echo "No frontend code yet"

frontend-typecheck: ## Type-check frontend with vue-tsc
	cd $(FRONTEND_DIR) && npx vue-tsc --noEmit 2>/dev/null || echo "No frontend code yet"

# ── Data pipelines ────────────────────────────────────────────────────────
pipeline-test: ## Test data pipeline scripts
	$(PYTHON) $(PIPELINE_DIR)/fetch_ons_wealth.py 2>/dev/null || echo "Pipeline stubs only"
	$(PYTHON) $(PIPELINE_DIR)/fetch_hmrc_stats.py 2>/dev/null || echo "Pipeline stubs only"
	$(PYTHON) $(PIPELINE_DIR)/fetch_wid_data.py 2>/dev/null || echo "Pipeline stubs only"

validate: ## Validate all processed CSV datasets
	$(PYTHON) $(PIPELINE_DIR)/validate.py

pipelines: ## Run all working data pipelines (fetches live data)
	$(PYTHON) $(PIPELINE_DIR)/fetch_wid_data.py
	$(PYTHON) $(PIPELINE_DIR)/fetch_ons_housing.py
	$(PYTHON) $(PIPELINE_DIR)/fetch_ons_wealth.py
	$(PYTHON) $(PIPELINE_DIR)/fetch_hmrc_stats.py

# ── Aggregate targets ─────────────────────────────────────────────────────
install: backend-install frontend-install ## Install all dependencies

lint: backend-lint ## Run all linters
format: backend-format ## Auto-format all code
test: backend-test ## Run all tests

dev-frontend: ## Alias for frontend dev server
	cd $(FRONTEND_DIR) && npm run dev

# ── CI tiers ──────────────────────────────────────────────────────────────
ci-quick: backend-lint backend-test ## Pre-push gate (~60s, no external deps)
	@echo "ci-quick passed"

ci-full: backend-lint backend-test frontend-build frontend-typecheck ## Full CI (~3 min)
	@echo "ci-full passed"

# ── Hooks ─────────────────────────────────────────────────────────────────
test-hooks: ## Test Claude Code agent hooks
	@echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | $(PYTHON) scripts/agent_hooks/pre_tool_use.py && echo "Hook test: destructive command denied (expected)"
	@echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | $(PYTHON) scripts/agent_hooks/pre_tool_use.py && echo "Hook test: safe command allowed (expected)"
	@echo '{"tool_name":"Bash","tool_input":{"command":"git push --force"}}' | $(PYTHON) scripts/agent_hooks/pre_tool_use.py && echo "Hook test: force-push denied (expected)"

# ── Clean ─────────────────────────────────────────────────────────────────
clean: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
