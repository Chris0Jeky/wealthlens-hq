# Contributing to WealthLens Dashboard

This project is early-stage and welcomes contributors. The most useful contributions are small, source-backed, and easy to review.

## Principles

- Cite every data source with URL and access date.
- Keep charts mobile-responsive and WCAG AA accessible.
- Prefer plain language over jargon.
- Keep data pipelines reproducible.
- Write clear docstrings and comments — volunteers will read this code.

## Local Setup

### Prerequisites

- Python 3.11+ ([python.org](https://www.python.org/downloads/))
- Node.js 22+ ([nodejs.org](https://nodejs.org/)) — for frontend work
- Git

### Clone and install

```bash
git clone https://github.com/Chris0Jeky/wealthlens-hq.git
cd wealthlens-hq
```

### Python (backend + pipelines)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev,pipelines]"
```

### Run data pipelines

Each pipeline fetches live data, processes it, and generates a chart:

```bash
python automation/data-pipelines/fetch_wid_data.py
python automation/data-pipelines/fetch_ons_housing.py
python automation/data-pipelines/fetch_ons_wealth.py
python automation/data-pipelines/fetch_hmrc_stats.py
```

Or run all at once:

```bash
python automation/data-pipelines/run_all.py
```

### Run tests

```bash
python -m pytest tests/ -v
```

### Run linter

```bash
python -m ruff check automation/ tests/
python -m ruff format --check automation/ tests/
```

### Start backend dev server

```bash
cd projects/wealthlens-dashboard/backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Validate processed data

```bash
python automation/data-pipelines/validate.py
```

## Project Structure

```
automation/data-pipelines/   — Python scripts that fetch, process, and chart data
projects/wealthlens-dashboard/
  backend/                   — FastAPI API serving processed datasets as JSON
  frontend/                  — Vue 3 + TypeScript + Pinia + TailwindCSS
  charts/                    — Generated interactive HTML charts
  data/raw/                  — Downloaded source files
  data/processed/            — Cleaned CSV outputs
tests/                       — pytest test suite
```

## Good First Contributions

- Add a new data pipeline for a UK dataset (see `tasks/inbox.md` for ideas).
- Add tests for an untested module.
- Improve accessibility of an existing chart or page.
- Add or verify a data source record in `docs/data-licences.md`.
- Improve a methodology note.
- Build a small chart prototype from a cited dataset.

## Submitting Changes

1. Fork the repository and create a feature branch.
2. Make small, focused commits with descriptive messages.
3. Ensure `python -m pytest tests/ -v` passes.
4. Ensure `python -m ruff check automation/ tests/` is clean.
5. Open a pull request with a clear description of what changed and why.

## Code of Conduct

Be kind, be patient, be constructive. This is a volunteer project built in the open.
