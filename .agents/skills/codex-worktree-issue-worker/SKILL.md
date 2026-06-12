---
name: codex-worktree-issue-worker
description: Implement one assigned issue or task in an isolated git worktree. Use when given a specific task to complete.
---

# WealthLens HQ — Codex Worktree Issue Worker

## When to use

- Assigned a specific issue, task, or backlog item
- Working in an isolated git worktree
- Single-issue implementation scope

## Steps

1. Read the issue or task description fully.
2. Read `../hq-private/projects/wealthlens/memories/00_ACTIVE.md` (private sibling repo; skip if absent) for current context.
3. Identify the smallest diff that resolves the issue.
4. Create a branch named for the task: `<area>/<short-description>`.
5. Implement the change — stay within the intended seam.
6. Run verification (tests, lint, build) appropriate to the change type.
7. Commit with `<area>: <imperative summary>`.
8. Before handoff, use `codex-verification-doc-sync` skill.

## Domain-specific verification

- Backend code → `make test` or targeted `pytest`
- Frontend code → `npm run build` or `npx vue-tsc --noEmit`
- Data pipeline → run the specific pipeline script
- Content/docs → check formatting, dates, source citations
- Research → verify source URLs and access dates

## Guardrails

- Do not drift outside the issue scope.
- Do not mix code changes with strategy/outreach changes.
- Data must always cite its source — no fabricated statistics.
- Volunteers will read this code — write clear docstrings.
- Keep running notes in `../hq-private/projects/wealthlens/memories/session_notes/` (private sibling repo) for multi-session work.
