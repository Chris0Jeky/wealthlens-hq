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
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -e ".[dev,pipelines]"
make ci-quick
```

## Good first contributions

- Add a new data pipeline for a UK public dataset.
- Add or improve tests for an existing module.
- Improve the accessibility of an existing chart.
- Build a small chart prototype from a cited dataset.

## Branch naming

```
<type>/<short-description>
```

Types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`

Examples: `feat/wealth-calculator`, `fix/chart-contrast`, `docs/api-endpoints`

## Commit messages

Use imperative mood in the format `<area>: <summary>`:

- `frontend: add wealth calculator comparison mode`
- `backend: fix rate limiting for /api/data endpoints`
- `pipeline: update ONS housing data fetch script`

## Pull request guidelines

1. Fork the repo and create a feature branch from `main`.
2. Make small, focused commits (one logical change per commit).
3. Ensure tests and linting pass: `make ci-quick`
4. Open a PR with a clear description of what changed and why.

## Code style

| Language | Formatter | Linter | Types |
|----------|-----------|--------|-------|
| Python | `ruff format` | `ruff check` | `mypy` |
| TypeScript | Prettier | ESLint + vue plugin | `vue-tsc --noEmit` |

## Testing

- **Backend**: pytest (`projects/wealthlens-dashboard/backend/tests/`)
- **Frontend**: vitest (`src/components/__tests__/`)
- **E2E**: Playwright (planned — not yet configured)
- **Full CI**: `make ci-full` (lint + tests + build + type check)

## Accessibility requirements

All UI changes must meet WCAG AA:
- 4.5:1 minimum contrast ratio for text
- Interactive elements keyboard-accessible
- ARIA labels on non-text content
- No information conveyed by colour alone

## AI/LLM usage

This project uses LLMs (Claude Code, Codex) as development assistants. All LLM-assisted output is reviewed by a human before merge. See [`docs/AI_LLM_DISCLOSURE.md`](docs/AI_LLM_DISCLOSURE.md) for the full disclosure policy, including what is declared, what is prohibited, and how LLM use is audited.

## Code of conduct

Be kind, be patient, be constructive. This is a volunteer project built in the open.
