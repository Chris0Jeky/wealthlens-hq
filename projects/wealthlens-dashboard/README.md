# WealthLens Dashboard

Source-backed, mobile-first, accessible chart pages that make UK wealth inequality data easier to inspect, share, download, and embed.

## Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic
- **Frontend:** Vue 3, TypeScript, Pinia, TailwindCSS
- **Visualisation:** D3.js (broadsheet newspaper aesthetic)
- **Data:** Reproducible pipelines in `automation/data-pipelines/`
- **CI:** GitHub Actions — backend lint/mypy/bandit/pytest, frontend lint/typecheck/vitest/build

## Chart datasets (12)

| Slug | Source | CSV |
|------|--------|-----|
| wealth-shares | WID (World Inequality Database) | `wid_wealth_shares_gb.csv` |
| housing-affordability | ONS Housing Affordability | `ons_housing_affordability_by_region.csv` |
| wealth-by-decile | ONS Wealth & Assets Survey | `ons_wealth_by_decile.csv` |
| cgt-concentration | HMRC CGT Statistics | `hmrc_cgt_concentration.csv` |
| wage-stagnation | ONS Annual Survey of Hours and Earnings (ASHE) | `wage_stagnation.csv` |
| inheritance-tax | HMRC Inheritance Tax Statistics | `inheritance-tax.csv` |
| productivity-pay | ONS Productivity & Pay | `productivity_pay_gap.csv` |
| gdhi-by-region | ONS GDHI | `ons_gdhi_by_region.csv` |
| tax-composition | HMRC Tax Receipts | `tax_composition.csv` |
| boe-rates | Bank of England | `boe_rates.csv` |
| child-poverty | DWP / HBAI | `child_poverty_by_region.csv` |
| generational-wealth | ONS WAS | `generational_wealth_gap.csv` |

## API Endpoints

The API serves its currently listed datasets; its endpoints are prefixed with `/api/data/`:

- `GET /` — list available datasets
- `GET /metadata` — metadata for all datasets
- `GET /{dataset}/metadata` — metadata for one dataset
- `GET /{dataset}/columns` — per-column metadata
- `GET /{dataset}/summary` — descriptive statistics
- `GET /{dataset}/download` — download as CSV
- `GET /{dataset}` — paginated rows (query: `page`, `limit`)
- `GET /health` — health check

The full 12-chart provenance list also includes two static chart data sources; `GET /` is the authoritative list of datasets served by the API.

## Charts

Twelve interactive chart pages with broadsheet newspaper styling:

- **Top 1% Wealth Share Since 1820** (`WealthSharesChart`)
- **Housing Affordability by Region** (`HousingAffordabilityChart`)
- **Wealth Distribution by Decile** (`WealthByDecileChart`)
- **Capital Gains Concentration** (`CgtConcentrationChart`)
- **Real Wage Stagnation** (`WageStagChart`)
- **Who Pays Inheritance Tax?** (`InheritanceTaxChart`)
- **The Productivity-Pay Gap** (`ProductivityPayChart`)
- **Regional Disposable Income** (`GdhiByRegionChart`)
- **What Britain Taxes** (`TaxCompositionChart`)
- **Bank Rate and Inflation** (`BoeRatesChart`)
- **Child Poverty by Region** (`ChildPovertyChart`)
- **The Generational Wealth Gap** (`GenerationalWealthChart`)

Each chart includes source citation and methodology note; downloadable CSVs are provided where licensing permits.

## Development

```bash
# Backend
make dev-backend       # uvicorn on 127.0.0.1:8000

# Frontend
cd projects/wealthlens-dashboard/frontend
npm install
npm run dev            # Vite dev server on :3000

# Tests
make test              # pytest (backend + root)
npm run test           # vitest (frontend)

# Lint & type check
make lint              # ruff + mypy
npm run lint           # eslint
npm run typecheck      # vue-tsc
```

## Each Chart Page Includes

- Headline and short interpretation
- Source URL and access date
- Methodology note
- Downloadable CSV where provided
- Mobile-responsive and WCAG AA accessible implementation
