# Changelog

All notable changes to WealthLens HQ are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- FastAPI backend serving processed CSV datasets as JSON
- Vue 3 + TypeScript frontend with Vite, Pinia, and TailwindCSS
- Interactive wealth shares chart (WID data, ECharts)
- Housing affordability chart (ONS data)
- Capital gains tax concentration chart (HMRC data)
- Wealth by decile chart (ONS WAS)
- 404 page and ErrorBoundary component
- Pipeline runner (`run_all.py`) and validation script (`validate.py`)
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

## [0.1.0] - 2026-05-15 (retroactive, no git tag)

### Added
- Initial repository scaffold (tasks, research, strategy, docs)
- Data pipelines: WID wealth shares, ONS housing affordability, ONS wealth, HMRC CGT
- Static HTML chart pages generated from pipeline output
- GitHub Pages deployment workflow
- Weekly data update workflow
