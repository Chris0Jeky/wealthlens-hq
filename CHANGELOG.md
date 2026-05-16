# Changelog

All notable changes to WealthLens HQ are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- ONS Wealth and Assets Survey data pipeline (`fetch_ons_wealth.py`)
- ONS Total Wealth fetch/process/chart script
- Backend CI workflow (pytest, ruff, mypy)
- Frontend CI workflow (vue-tsc, build)
- ESLint and Prettier configuration for frontend
- CONTRIBUTING.md for the dashboard project
- Makefile targets for lint, format, test, and CI

### Fixed
- CI mypy scoped to backend only
- Replaced IOError alias with OSError (ruff UP024)
- Suppressed mypy false positive on DataFrame.where(None)

_Note: 120+ feature PRs are open and under review but not yet merged.
See the open pull requests for upcoming features including dark mode,
structured logging, request timeout middleware, and more._

## [0.1.0] - 2026-05-15 (retroactive)

### Added
- Initial repository scaffold with task management, research, and strategy docs
- FastAPI backend serving processed CSV datasets as JSON
- Vue 3 + TypeScript frontend with Vite, Pinia, and TailwindCSS
- Interactive wealth shares chart (WID data, ECharts)
- Housing affordability chart (ONS data)
- Capital gains tax concentration chart (HMRC data)
- Wealth by decile chart
- 404 page and ErrorBoundary component
- Data pipelines: WID, ONS housing, HMRC CGT
- Pipeline runner (`run_all.py`) and validation script
- GitHub Pages deployment of v0.1 prototype
- Weekly data update workflow
