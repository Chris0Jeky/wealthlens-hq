# Contributing to WealthLens UK

Last updated: 2026-05-16

WealthLens UK is an open-source project making UK wealth inequality data visible, interactive, and impossible to ignore. Contributions of all sizes are welcome.

## Project values

- Cite every data source with URL and access date.
- Charts must be mobile-responsive and meet WCAG AA accessibility standards.
- Data pipelines must be reproducible from source to output.
- Write clear comments and docstrings -- volunteers will read this code.

## Repository structure

This is a monorepo. Key directories:

| Path | Purpose |
|---|---|
| `projects/wealthlens-dashboard/` | Main product: backend (FastAPI), frontend (Vue 3), charts, data |
| `automation/data-pipelines/` | Python scripts that fetch, process, and chart public datasets |
| `research/` | Raw inputs, synthesised insights, data source registry |
| `tasks/` | Sprint tracking, inbox, and outreach |
| `strategy/` | Branding, content, and outreach playbooks |

## Detailed setup

For full prerequisites, environment setup, backend/frontend commands, and pipeline usage, see [projects/wealthlens-dashboard/CONTRIBUTING.md](projects/wealthlens-dashboard/CONTRIBUTING.md).

## Quick start

```bash
git clone https://github.com/Chris0Jeky/wealthlens-hq.git
cd wealthlens-hq
pip install -e ".[dev,pipelines]"
python -m pytest tests/ -v
```

## Good first contributions

- Add a new data pipeline for a UK public dataset.
- Add or improve tests for an existing module.
- Improve the accessibility of an existing chart.
- Build a small chart prototype from a cited dataset.

## Pull request guidelines

1. Fork the repo and create a feature branch.
2. Make small, focused commits with descriptive messages.
3. Ensure tests pass: `python -m pytest tests/ -v`
4. Ensure linting is clean: `python -m ruff check automation/ tests/`
5. Open a PR with a clear description of what changed and why.

## Code of conduct

Be kind, be patient, be constructive. This is a volunteer project built in the open.
