# Agent Index — WealthLens HQ

> Fast agent orientation. Last reviewed: 2026-06-27.

## Do-not-read list

These paths are large, generated, or low-signal for most tasks. Skip unless the task explicitly requires them:

- `research/raw/Claude_Resources/` — raw LLM outputs, large
- `research/raw/Codex_Resources/` — raw LLM outputs, large
- `research/raw/Combined/` — merged research, large
- `.idea/` — IDE settings
- `node_modules/`, `.venv/` — dependencies (when they exist)

## Product seams

| Domain | Key paths | Status |
| --- | --- | --- |
| Dashboard backend | `projects/wealthlens-dashboard/backend/` | Built — FastAPI (health/data/metadata/columns/summary/CSV) + tests |
| Dashboard frontend | `projects/wealthlens-dashboard/frontend/` | Built — Vue 3 + TS + Pinia + TailwindCSS (80+ `.vue` files) + vitest/Playwright |
| Data pipelines | `automation/data-pipelines/` | Built — 11 `fetch_*` scripts + `run_all.py` + `validate.py` + tests |
| Research analysis | `automation/analysis/` | Built — `extract_action_items.py`, `summarise_research.py` |
| Social media gen | `automation/social-media/` | Built — `chart_to_social.py` (4 platform sizes) |
| Hero #1 RAG analyst | `projects/wealthlens-analyst/` | Active build — ingest + FTS retrieval + evals + Alembic migrations (locked plan) |
| Microsimulator | `packages/wealthlens-sim/` | Built — engine + 7 policy families (A–G) + uncertainty layer |
| CI/CD workflows | `.github/workflows/` | Active — ci-backend/frontend/analyst/sim/pipelines, CodeQL, deploy, e2e, lighthouse |

## Operational seams

| Domain | Key paths | Notes |
| --- | --- | --- |
| Task tracking | `tasks/active-sprint.md`, `tasks/inbox.md` | Markdown-based, manual |
| Strategy | `strategy/*.md` | 8 playbooks, fully written |
| Vision | `vision/*.md` | 5 docs, fully written |
| Research | `research/synthesised/key-insights.md` | Distilled from 10+ raw inputs |
| Outreach | `../hq-private/projects/wealthlens/outreach/` | Contacts, emails sent, follow-ups (private sibling repo) |
| Data sources | `research/data-sources/data-source-registry.md` | Template with TODOs |

## Current agent-readiness

- Claude Code harness: fully configured (settings, hooks, skills, protocols)
- Codex skills: basic set (onramp, worker, verification, question batch)
- Control plane: `../hq-private/projects/wealthlens/memories/00_ACTIVE.md` as status board (private sibling repo)
- Product code is BUILT and live: dashboard backend (FastAPI) + frontend (Vue 3, deployed to GitHub Pages), 11 data pipelines, the `wealthlens-sim` microsimulator, and the Hero #1 `wealthlens-analyst` RAG service (active build). See AGENTS.md "Repo map" for the authoritative inventory.
- Strategy and research documentation is comprehensive and coherent

## Minimum handoff format

```text
## Changed
- <file>: <what changed>

## Verified
- <what was checked and result>

## Not verified
- <what was skipped and why>

## Failures / workarounds
- <any issues encountered>

## Status sync
- <docs updated or "no status change">

## Next slice
- <suggested follow-up>
```
