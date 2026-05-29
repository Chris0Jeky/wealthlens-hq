# WealthLens UK

**Open-source tools making UK wealth inequality data visible, interactive, and impossible to ignore.**

[![Deploy Charts](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/deploy.yml/badge.svg)](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/deploy.yml)
[![CI Backend](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/ci-backend.yml)
[![CI Frontend](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/ci-frontend.yml/badge.svg)](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/ci-frontend.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Node 22+](https://img.shields.io/badge/Node-22%2B-green.svg)](https://nodejs.org/)

## What is this?

WealthLens UK publishes source-backed, mobile-responsive, accessible interactive charts about wealth inequality in the United Kingdom. Every chart cites its data source, is WCAG AA accessible, and can be freely shared and embedded.

### Live site

**[chris0jeky.github.io/wealthlens-hq](https://chris0jeky.github.io/wealthlens-hq/)**

Interactive charts with broadsheet aesthetic, dark mode, keyboard navigation, and WCAG AA compliance:

- **UK Wealth Shares (1820–2024)** — Top 1% and top 10% share of net personal wealth (WID.world)
- **Housing Affordability by Region** — House price to earnings ratios across England (ONS)
- **Capital Gains Concentration** — How gains are concentrated among top taxpayers (HMRC)
- **Wealth by Decile** — Distribution of wealth across population deciles (ONS WAS)

Plus 10 backend datasets covering productivity-pay gap, GDHI by region, tax composition, BoE rates, child poverty, and generational wealth.

## Tech stack

| Layer | Technology |
|---|---|
| Data pipelines | Python 3.11+, Pandas, Requests (10 pipelines) |
| Backend API | FastAPI, Pydantic, SQLite (dev) / PostgreSQL (prod) |
| Frontend | Vue 3, TypeScript, Pinia, TailwindCSS, D3.js, Vite |
| Infrastructure | GitHub Pages, GitHub Actions (CI + deploy) |
| Dev tools | ruff, mypy, bandit, pytest, ESLint, vue-tsc, vitest |
| Tests | 874 passing (156 root + 135 backend + 583 frontend) |

## Quick start

```bash
# Clone
git clone https://github.com/Chris0Jeky/wealthlens-hq.git
cd wealthlens-hq

# Backend
cd projects/wealthlens-dashboard/backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload          # API at http://localhost:8000

# Frontend (separate terminal)
cd projects/wealthlens-dashboard/frontend
npm install
npm run dev                            # Vite dev server at http://localhost:3000

# Data pipelines
cd automation/data-pipelines
pip install -r requirements.txt
python run_all.py                      # Fetches live data, generates CSVs
```

## Project structure

```
wealthlens-hq/
├── projects/wealthlens-dashboard/
│   ├── charts/                      # Static Plotly HTML charts (deployed)
│   ├── data/processed/              # Pipeline output CSVs (10 datasets)
│   ├── backend/                     # FastAPI app (health, data, metadata, CSV, stats)
│   └── frontend/                    # Vue 3 + TypeScript + Pinia + TailwindCSS
├── automation/
│   ├── data-pipelines/              # 10 Python fetch/process scripts
│   └── social-media/               # chart_to_social.py (4 platform sizes)
├── research/                        # Raw inputs, synthesised insights, data sources
├── strategy/                        # Branding, content, outreach playbooks
├── tasks/                           # Sprint, inbox, done, outreach tracking
└── .github/workflows/               # CI: backend, frontend, CodeQL, deploy, weekly-update
```

## API Documentation

The backend API provides interactive documentation powered by FastAPI:

| Interface | URL | Description |
|-----------|-----|-------------|
| Swagger UI | `http://localhost:8000/docs` | Interactive API explorer with try-it-out |
| ReDoc | `http://localhost:8000/redoc` | Clean, readable API reference |

Start the backend with `make dev-backend` or `uvicorn app.main:app --reload` from the backend directory, then open either URL in your browser.

### Available endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/data/` | List available datasets |
| GET | `/api/data/metadata` | Metadata for all datasets (with source citations) |
| GET | `/api/data/{name}/metadata` | Metadata for a single dataset |
| GET | `/api/data/{name}` | Paginated dataset rows (`?page=` and `?limit=`) |
| GET | `/api/data/{name}/columns` | Per-column metadata (dtype, null/unique counts) |
| GET | `/api/data/{name}/summary` | Descriptive statistics for numeric columns |
| GET | `/api/data/{name}/download` | Download dataset as streaming CSV |

## How to contribute

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good first contributions:**
- Add or verify a data source record in the registry
- Improve a chart's accessibility or methodology note
- Build a new chart prototype from a cited dataset
- Fix a bug in a data pipeline

## Data principles

- Every dataset cites its source with URL and access date
- No fabricated statistics — all numbers are traceable
- Charts are mobile-responsive and WCAG AA accessible
- All data pipelines are reproducible

## Values

- **Data first, opinion second** — present facts, not party politics
- **Open source always** — code, data, and methodology are public
- **Accessible by default** — built for everyone, not just specialists
- **Independent and non-partisan** — no affiliation with any party or campaign

## Licence

Code: [MIT](LICENSE) — Data visualisations: [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

Built by [Chris](https://github.com/Chris0Jeky) in London.
