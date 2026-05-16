# WealthLens UK

**Open-source tools making UK wealth inequality data visible, interactive, and impossible to ignore.**

[![Deploy Charts](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/deploy.yml/badge.svg)](https://github.com/Chris0Jeky/wealthlens-hq/actions/workflows/deploy.yml)

## What is this?

WealthLens UK publishes source-backed, mobile-responsive, accessible interactive charts about wealth inequality in the United Kingdom. Every chart cites its data source, is WCAG AA accessible, and can be freely shared and embedded.

### Live charts (v0.1)

- **UK Wealth Shares (1820–2024)** — Top 1% and top 10% share of net personal wealth (WID.world)
- **Housing Affordability by Region** — House price to earnings ratios across England (ONS)
- **Capital Gains Concentration** — How gains are concentrated among top taxpayers (HMRC)

## Tech stack

| Layer | Technology |
|---|---|
| Data pipelines | Python 3.11+, Pandas, Requests |
| Charts | Plotly (static HTML, no server needed) |
| Backend (planned) | FastAPI, Pydantic, SQLite/PostgreSQL |
| Frontend (planned) | Vue 3, TypeScript, Pinia, TailwindCSS, D3.js |
| Infrastructure | GitHub Pages, GitHub Actions |
| Dev tools | ruff, mypy, pytest, Make |

## Quick start

```bash
# Clone
git clone https://github.com/Chris0Jeky/wealthlens-hq.git
cd wealthlens-hq

# Set up Python environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
pip install -r automation/data-pipelines/requirements.txt

# Run all data pipelines (fetches live data and generates charts)
make pipelines

# Open the charts
open projects/wealthlens-dashboard/charts/index.html
```

## Project structure

```
wealthlens-hq/
├── projects/wealthlens-dashboard/   # Charts, data, backend, frontend
│   ├── charts/                      # Interactive HTML charts (deployed)
│   ├── data/                        # Raw + processed datasets (gitignored)
│   ├── backend/                     # FastAPI app (planned)
│   └── frontend/                    # Vue 3 app (planned)
├── automation/
│   ├── data-pipelines/              # Python fetch/process/chart scripts
│   ├── analysis/                    # Research processing (stubs)
│   └── workflows/                   # CI/CD references
├── research/                        # Raw inputs, synthesised insights, data sources
├── strategy/                        # Branding, content, outreach playbooks
├── tasks/                           # Sprint, inbox, done, outreach tracking
└── .github/workflows/               # GitHub Actions (deploy, data update)
```

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
