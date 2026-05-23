# Architecture

Last updated: 2026-05-16

This document describes the WealthLens HQ system architecture for new contributors.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Pages                              │
│                  (Static frontend + JSON data)                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │ serves
┌────────────────────────────────▼────────────────────────────────┐
│                     Vue 3 Frontend (SPA)                         │
│         TypeScript / Pinia / TailwindCSS / ECharts               │
└────────────────────────────────┬────────────────────────────────┘
                                 │ fetches /api/* (dev) or /data/*.json (prod)
┌────────────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend (dev only)                     │
│              Python 3.11+ / Pydantic / pandas                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ reads
┌────────────────────────────────▼────────────────────────────────┐
│                  Processed CSV datasets                          │
│        automation/data-pipelines/ output → data/processed/       │
└────────────────────────────────┬────────────────────────────────┘
                                 │ fetched by
┌────────────────────────────────▼────────────────────────────────┐
│                    Data Pipelines                                │
│       Python scripts fetching from ONS, HMRC, WID, BoE          │
└─────────────────────────────────────────────────────────────────┘
```

In production, the frontend is a static SPA deployed to GitHub Pages. It reads
pre-generated JSON files from `/data/`. In development, Vite proxies `/api/*`
requests to the local FastAPI server which reads CSVs on-the-fly.

## Directory Structure

```
wealthlens-hq/
├── projects/wealthlens-dashboard/
│   ├── backend/                   # FastAPI API server
│   │   ├── app/
│   │   │   ├── main.py           # App factory, middleware, routes
│   │   │   ├── routers/data.py   # Dataset endpoints
│   │   │   ├── middleware.py     # Security headers
│   │   │   ├── rate_limit.py     # Per-IP rate limiting
│   │   │   └── error_handlers.py # Structured error responses
│   │   └── tests/                 # pytest suite
│   ├── data/processed/            # Processed CSV files (shared by backend + pipelines)
│   └── frontend/                  # Vue 3 SPA
│       ├── src/
│       │   ├── components/        # Reusable UI + chart components
│       │   ├── views/             # Route-level page components
│       │   ├── composables/       # Shared reactive logic (useChartData, useDarkMode, etc.)
│       │   ├── stores/            # Pinia stores
│       │   ├── router/            # Vue Router config
│       │   ├── constants/         # Static config (chart names, dataset metadata)
│       │   └── utils/             # Pure helpers (fetchWithRetry, wealthPosition, format)
│       ├── public/data/           # Static JSON fallbacks for production
│       └── vite.config.ts         # Build config (base: /wealthlens-hq/)
├── automation/
│   └── data-pipelines/            # Python scripts to fetch & process datasets
│       ├── fetch_*.py             # One script per data source
│       ├── run_all.py             # Execute all pipelines
│       └── validate.py            # Validate processed CSVs
├── research/                      # Source research and analysis
├── strategy/                      # Brand, outreach, planning
├── tasks/                         # Sprint boards and inbox
└── Makefile                       # Dev commands (lint, test, dev servers)
```

## Data Flow

1. **Fetch**: Pipeline scripts (`automation/data-pipelines/fetch_*.py`) pull raw data from ONS, HMRC, WID, Bank of England via HTTP.
2. **Process**: Scripts clean, normalize, and output CSV to `data/processed/`.
3. **Serve (dev)**: FastAPI reads CSVs, returns paginated JSON via `/api/data/{dataset}`.
4. **Serve (prod)**: Static JSON in `frontend/public/data/` (generated during build or pipeline run).
5. **Display**: Vue components fetch data → Pinia store → ECharts renders interactive charts.

## Technology Choices

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend framework | Vue 3 + TypeScript | Composition API, strong typing, approachable for volunteers |
| State management | Pinia | Official Vue store, simple API, devtools support |
| Charts | ECharts (via vue-echarts) | Rich chart types, responsive, tree-shakeable |
| Styling | TailwindCSS v4 | Utility-first, consistent design, fast iteration |
| Backend | FastAPI + Pydantic | Auto-docs (OpenAPI), validation, async support, Python ecosystem |
| Data processing | pandas | Industry standard for tabular data, volunteers likely know it |
| Build tool | Vite | Fast HMR, native ESM, zero-config Vue support |
| Testing | vitest (frontend), pytest (backend) | Fast, native ESM support, good DX |
| Deployment | GitHub Pages | Free, simple, fits static SPA model |

## Development Setup

```bash
# Prerequisites: Python 3.11+, Node 22+, Git

# Clone
git clone https://github.com/Chris0Jeky/wealthlens-hq.git
cd wealthlens-hq

# Backend
cd projects/wealthlens-dashboard/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd projects/wealthlens-dashboard/frontend
npm install
npm run dev   # Opens http://localhost:3000

# Run tests
make ci-quick   # Backend lint + backend tests
```

The Vite dev server proxies `/api/*` to `localhost:8000` automatically.

## How to Add a New Dataset

1. **Write a pipeline script**: Create `automation/data-pipelines/fetch_<name>.py` that fetches, cleans, and outputs a CSV to `projects/wealthlens-dashboard/data/processed/<name>.csv`.
2. **Register in backend**: Add the dataset slug/CSV filename to `DATASETS` and matching source metadata to `DATASET_META` in `app/routers/data.py`.
3. **Generate static JSON**: Run the pipeline and copy output to `frontend/public/data/<name>.json`.
4. **Register the chart name**: Add the dataset slug to `frontend/src/constants/charts.ts` (`VALID_CHART_NAMES`).
5. **Create a chart component**: See below.

## How to Add a New Chart Component

1. Create `frontend/src/components/<Name>Chart.vue`:
   - Import `vue-echarts` and only the ECharts modules you need (tree-shaking).
   - Fetch data with `fetchWithRetry()`.
   - Handle loading, error, and empty states.
2. Register the chart name in `frontend/src/constants/charts.ts` (add to `VALID_CHART_NAMES`).
3. Add the component to `ChartView.vue` using `defineAsyncComponent` and map it in the chart component lookup.
4. Add a test file at `frontend/src/components/__tests__/<Name>Chart.test.ts`.
5. Verify with `npx vitest run` and `npx vue-tsc --noEmit`.

## Key Conventions

- **Base path**: All frontend URLs are prefixed with `/wealthlens-hq/` (set in `vite.config.ts`).
- **WCAG AA**: All charts must have sufficient color contrast, ARIA labels, and keyboard accessibility.
- **Source citations**: Every dataset must cite its source with URL and access date.
- **Static fallbacks**: Every dataset served by the API must also have a static JSON in `public/data/` for the GitHub Pages deploy.
- **Design tokens**: CSS custom properties (`--wl-*`) defined in the global stylesheet for consistent theming.
