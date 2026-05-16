# Changelog

All notable changes to WealthLens HQ are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-05-16

### Added
- 10 data pipelines: WID, ONS housing, ONS wealth, HMRC CGT, wealth-by-decile, productivity-pay, GDHI, tax composition, BoE rates, child poverty, generational wealth
- FastAPI backend: health, data listing, metadata, columns, summary stats, CSV download endpoints
- Security headers, GZip compression, rate limiting, error envelope middleware
- Vue 3 frontend: 40+ components and composables (Tooltip, Modal, Toast, Badge, ProgressBar, SkeletonLoader, Accordion, TabGroup, NavBar, ConfirmDialog, etc.)
- Dark mode with system preference detection
- Broadsheet-aesthetic chart page redesign
- WCAG AA accessibility: keyboard navigation, focus management, reduced motion, ARIA labels, skip links
- Privacy-respecting analytics integration
- DatasetDetailView with metadata and data preview
- WealthCalculatorView tool
- About page, methodology section, 404 page
- PWA manifest for installable web app
- chart_to_social.py for social media image generation (4 platform sizes)
- CodeQL security scanning workflow
- 874 tests (156 root + 135 backend + 583 frontend)
- Dependabot for Python, npm, and GitHub Actions

### Fixed
- CI mypy scoped to backend only
- Replaced IOError alias with OSError (ruff UP024)
- Suppressed mypy false positive on DataFrame.where(None)
- Seed CSV alignment for all 10 pipeline integration tests
- TypeScript strict mode errors across all frontend components
- ESLint unused imports and variables

## [0.1.0] - 2026-05-15 (retroactive, no git tag)

### Added
- Initial repository scaffold (tasks, research, strategy, docs)
- Data pipelines: WID wealth shares, ONS housing affordability, ONS wealth, HMRC CGT
- Static HTML chart pages generated from pipeline output
- GitHub Pages deployment workflow
- Weekly data update workflow
