# Changelog

All notable changes to WealthLens HQ are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- About page with methodology and data source citations
- Dark mode toggle with system preference detection and FOUC prevention
- Structured JSON logging for production backend
- Configurable request timeout middleware (pure ASGI, streaming-safe)
- AccessibleDataTable component for screen-reader-friendly chart data
- Copy-link share button on chart pages
- Cache-Control headers for dataset API responses
- Rate limiting middleware with configurable thresholds
- Standardized error response envelope across all API endpoints
- Request logging middleware
- Loading skeleton component for async content
- SEO meta tags and Open Graph metadata
- 404 page and ErrorBoundary with error ID and retry
- Dataset name path parameter validation
- Health endpoint with version and uptime
- CORS preflight cache max-age optimisation

### Changed
- Extracted useChartData composable from chart components
- Route guards validate chart names before navigation
- Document titles update via route metadata

### Infrastructure
- CI pipelines for both backend (pytest, ruff, mypy, bandit) and frontend (vitest, vue-tsc)
- Docker support with multi-stage builds
- Dependabot configuration for automated dependency updates
- GitHub issue and PR templates
- EditorConfig for consistent formatting
- ESLint and Prettier configuration for frontend
- Makefile targets for all common dev tasks

### Data Pipelines
- ONS Wealth and Assets Survey pipeline with retry and timeout
- WID world inequality data pipeline (API key via env var)
- HMRC Capital Gains Tax concentration pipeline
- BoE interest rates pipeline
- Child poverty statistics pipeline
- Generational wealth gap pipeline
- Tax composition pipeline
- Pipeline runner with per-script timeout
- Structured logging across all pipelines

## [0.1.0] - 2026-05-15

### Added
- Initial repository scaffold with task management, research, and strategy docs
- FastAPI backend serving processed CSV datasets as JSON
- Vue 3 + TypeScript frontend with Vite, Pinia, and TailwindCSS
- Interactive wealth shares chart (WID data, ECharts)
- Housing affordability chart (ONS data)
- Capital gains tax concentration chart (HMRC data)
- Wealth by decile chart
- Tax rate calculator
- Three data pipelines: WID, ONS housing, HMRC CGT
- GitHub Pages deployment of v0.1 prototype
- CONTRIBUTING.md, SECURITY.md, ARCHITECTURE.md
