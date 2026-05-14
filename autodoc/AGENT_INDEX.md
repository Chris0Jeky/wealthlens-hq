# Agent Index — WealthLens HQ

> Fast agent orientation. Last reviewed: 2026-05-14.

## Do-not-read list

These paths are large, generated, or low-signal for most tasks. Skip unless the task explicitly requires them:

- `research/raw/Claude_Resources/` — raw LLM outputs, large
- `research/raw/Codex_Resources/` — raw LLM outputs, large
- `research/raw/Combined/` — merged research, large
- `identity/cv.pdf` — binary file
- `.idea/` — IDE settings
- `node_modules/`, `.venv/` — dependencies (when they exist)

## Product seams

| Domain | Key paths | Status |
| --- | --- | --- |
| Dashboard backend | `projects/wealthlens-dashboard/backend/` | Stub (`.gitkeep`) |
| Dashboard frontend | `projects/wealthlens-dashboard/frontend/` | Stub (`.gitkeep`) |
| Data pipelines | `automation/data-pipelines/` | Stubs (`NotImplementedError`) |
| Research analysis | `automation/analysis/` | Stubs (`NotImplementedError`) |
| Social media gen | `automation/social-media/` | Stub (`NotImplementedError`) |
| CI/CD workflows | `automation/workflows/` | Placeholder YAML |

## Operational seams

| Domain | Key paths | Notes |
| --- | --- | --- |
| Task tracking | `tasks/active-sprint.md`, `tasks/inbox.md` | Markdown-based, manual |
| Strategy | `strategy/*.md` | 8 playbooks, fully written |
| Vision | `vision/*.md` | 5 docs, fully written |
| Research | `research/synthesised/key-insights.md` | Distilled from 10+ raw inputs |
| Outreach | `tasks/outreach/` | Contacts, emails sent, follow-ups |
| Data sources | `research/data-sources/data-source-registry.md` | Template with TODOs |

## Current agent-readiness

- Claude Code harness: fully configured (settings, hooks, skills, protocols)
- Codex skills: basic set (onramp, worker, verification, question batch)
- Control plane: `.codex/memories/00_ACTIVE.md` as status board
- No production code — all product directories are stubs
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
