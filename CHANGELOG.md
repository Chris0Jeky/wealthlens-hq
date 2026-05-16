# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- FastAPI backend with data API serving UK wealth inequality datasets as paginated JSON
- Dataset metadata endpoint with source citations for every dataset
- Health check endpoint with `/health/data` CSV availability check
- Pydantic response models for all data API endpoints
- CORS configuration with `CORS_ORIGINS` environment variable override
- Vue 3 + TypeScript + Pinia + TailwindCSS frontend scaffold
- Interactive ECharts chart components: WealthSharesChart, HousingAffordabilityChart, CgtConcentrationChart, WealthByDecileChart
- Chart routing with HomeView navigation and NotFoundView (404 catch-all)
- ErrorBoundary component wrapping router view with retry limit and focus management
- WCAG AA accessibility improvements: skip link, ARIA labels, keyboard navigation, high-contrast colours
- Data pipelines for ONS wealth, ONS housing, WID wealth shares, and HMRC CGT statistics
- Shared accessible chart HTML wrapper for pipeline-generated charts
- CSV validation module with `make validate` target
- Cross-platform Python pipeline runner (`run_all.py`)
- Social media image export tool (`chart_to_social.py`) with 4-platform output
- Research scanner (`extract_action_items.py`) for extracting action items from research docs
- GitHub Actions CI for backend (pytest, ruff, mypy)
- GitHub Actions CI for frontend (eslint, vue-tsc, vitest, build)
- GitHub Pages deploy workflow
- Weekly data update workflow with scheduled pipeline runs
- Backend test suite for API endpoints, metadata, pagination, and health/data
- Frontend test suite with vitest, vue-test-utils, and jsdom (DatasetCard and store tests)
- Pipeline tests for ONS housing, ONS wealth, WID, HMRC, chart HTML, and CSV validation
- Unit tests for `extract_action_items.py`
- ESLint and Prettier configuration for frontend
- `.env.example` documenting expected environment variables
- WID API key moved to environment variable with public default
- `CONTRIBUTING.md` with setup instructions
- MIT `LICENSE`
- Data licences documentation
- `.prettierignore` added with `package-lock.json`
- Vite manual chunk splitting for ECharts and Vue vendor bundles

### Fixed

- ONS WAS pipeline URL and improved fallback handling
- ONS XLSX parser handling of trailing NaN columns
- Corrupt XLSX graceful handling and partial decile data rejection
- Backend CSV error handling widened to `OSError` with improved error messages
- Path leakage, TOCTOU race, and registration pattern in health endpoint
- `UnicodeDecodeError` handling in automation scripts
- Frontend `fetchDataset()` throw contract preserved with improved error messages
- Pinia store error handling in `fetchDataset()`
- Frontend `v-if` chain corrected to `v-else-if`
- CORS empty-string filtering and edge-case handling
- CGT chart `nan%` bug
- Ruff lint errors: `IOError` replaced with `OSError` (UP024), unused imports, E402 import ordering

### Changed

- Pipeline scripts migrated from `print()` to `logging` module
- Vue router extracted to `src/router/index.ts`
- `vue-echarts` included in ECharts manual chunk
- Pipeline timeout extracted to module-level constant
- `.gitignore` updated and tracked cache files removed

[Unreleased]: https://github.com/Chris0Jeky/wealthlens-hq/commits/main
