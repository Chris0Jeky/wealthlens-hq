# WealthLens HQ — AGENTS.md

Repository-level operating instructions for coding agents working in `wealthlens-hq/`.

Use [CLAUDE.md](./CLAUDE.md) as the Claude Code session contract.
Use [.codex/README.md](./.codex/README.md) for Codex planning and phase gate orientation.
Use [autodoc/README.md](./autodoc/README.md) as the concise code-grounded synthesis layer (once code exists).

## Scope

- Work inside this repository only.
- Treat `.codex/memories/00_ACTIVE.md` as the workspace status board. Always check it — do not assume what is active.
- Prefer small, reviewable diffs. Avoid rewrite-style changes.
- When implementing a backlog item, do the work on a branch scoped to that item.
- Preserve existing repo conventions unless there is a documented reason to change them.
- This is a multi-domain workspace: code, content, research, strategy, outreach. Read the task context to determine which domain you are in.

## Active orchestration

An end-to-end autonomous workflow may be in progress. **Always check** [`.codex/memories/session_notes/ORCHESTRATION.md`](.codex/memories/session_notes/ORCHESTRATION.md) for branch status, open PRs, review rounds, and recovery instructions before starting new work. That file is the master control document for multi-session continuity.

## First 5 minutes on any task

1. Read `.codex/memories/session_notes/ORCHESTRATION.md` (if it exists).
2. Read `.codex/memories/00_ACTIVE.md`.
3. Read `.codex/memories/program/00_READ_THIS_FIRST.md`.
4. Read `tasks/active-sprint.md` for current priorities.
5. Read `tasks/ACTION-REQUIRED.md` — Chris's outstanding human action items (see "Action-required protocol").
6. Use the matching repo skill (`codex-repo-onramp`, `codex-worktree-issue-worker`, `codex-verification-doc-sync`, or `codex-question-batch`) before broad searching.
7. Identify the smallest change that creates measurable progress.

## Action-required protocol

`tasks/ACTION-REQUIRED.md` is the curated list of outstanding tasks that need **Chris** (a human), each with a how-to guide. Surface its open items in every summary, status update, and handoff — lead with anything `[due: …]` today or overdue under a one-line `⚑ Action required:` banner. Only clear an item when Chris explicitly confirms it is done (then move it to the file's `## Done` with `[completed: YYYY-MM-DD]`); never infer completion. When Chris describes a new task for himself, add it in the file's item format. Keep the list ≤ ~8 open items; the full backlog stays in `tasks/inbox.md`, all dated items in `tasks/deadlines.md`.

## Codex autonomy skills

Repo-local Codex skills live under `.agents/skills/` and supplement this file. Use them only when their trigger matches the task; do not load every skill by default.

- `codex-repo-onramp` — use for broad/ambiguous requests, session setup, or high-autonomy orientation.
- `codex-worktree-issue-worker` — use for one assigned issue/task in an isolated git worktree.
- `codex-verification-doc-sync` — use before handoff to run final checks, update status docs, and seed follow-ups.
- `codex-question-batch` — use to decide whether to ask the user or proceed with assumptions.

## Operational issue handling

- Do not silently ignore tool, environment, dependency, auth, MCP, plugin, skill, test, CI, lint, docs, or filesystem errors just because there is a workaround.
- When an issue appears, pause long enough to classify it as blocker, non-blocking risk, pre-existing noise, or invalid signal. State the classification, why work can or cannot continue, and what evidence supports it.
- Inform the user during the run when the issue changes scope, risk, verification confidence, or future operability.
- For every non-blocking workaround, capture a follow-up path: fix now, seed a follow-up, document accepted risk, or explain why no action is needed.
- The final handoff must include any observed issue that was not fully fixed.
- For long-running or multi-session tasks, keep a task-scoped markdown note under `.codex/memories/session_notes/`.

## Backward compatibility

- Never change default values in `.env.example`, config fields, or shared settings unless the new default is backward-compatible.
- New behavior ships toggleable, default OFF. Existing behavior must not change silently.
- Local overrides go in `.env` (not committed), not in templates or shared config.

## Subagents and worktrees

- Use spawned subagents only when the user explicitly asks for subagents, delegation, or parallel agent work.
- Split by disjoint file/module ownership; keep one coordinator responsible for selection, synthesis, docs, and final verification.
- Do not pass absolute main-checkout paths to workers. Project paths must be derived from the worktree root.

## Hard guardrails

### Secrets and sensitive data

- Never commit secrets such as API keys, DB passwords, JWT secrets, or encryption keys.
- Never add "temporary" keys in docs or code.
- If a secret is discovered in-repo, stop and propose rotation plus purge steps.

### Data integrity

- All data must cite its source with URL and access date.
- Do not fabricate statistics, percentages, or data points.
- Charts must be mobile-responsive and meet WCAG AA minimum.

### Authentication and authorization (when dashboard exists)

- All endpoints that return user or private data must require auth.
- All privileged endpoints must enforce authorization server-side.
- Do not rely on UI-only gating.
- Add tests that prove non-admins receive `403` on admin routes.

### Command safety

- Do not run destructive shell commands unless explicitly asked.
- If a task requires a risky command, ask the user first and propose a safer alternative.
- See `docs/agentic/GIT_WORKFLOW.md` for safe vs. blocked git commands.

## How to help — by domain

### When working on WealthLens code (projects/wealthlens-dashboard/)

- Use Python (FastAPI) for backend, Vue 3 + TypeScript for frontend
- All data must cite its source with URL and access date
- Charts must be mobile-responsive and accessible (WCAG AA minimum)
- Write clear docstrings and comments — volunteers will read this code
- Prefer D3.js or ECharts for interactive visualisations
- All data pipelines should be reproducible (scripts in `automation/data-pipelines/`)

### When working on content (tasks/social-media/, strategy/)

- Voice: confident but not arrogant, data-driven, accessible, personal
- Never partisan — present data, not political opinions
- Connect inequality to personal experience (housing, wages, opportunity)
- Reference the messaging playbook in `strategy/branding-playbook.md`

### When working on tasks and planning

- Check `tasks/active-sprint.md` for current priorities
- New ideas go in `tasks/inbox.md` for later triage
- Completed tasks move to `tasks/done.md` with date
- Always check if a task connects to an existing strategy doc before creating new ones

### When working on outreach

- Check `tasks/outreach/contacts.md` for existing relationships
- Never send an email without checking `tasks/outreach/emails-sent.md` for prior contact
- Tone: professional, specific, offering value (not asking for favours)
- Always include a link to something you've already built

### When organising research

- Raw LLM outputs go in `research/raw/` numbered sequentially
- After processing, key insights go in `research/synthesised/key-insights.md`
- Action items extracted from research go in `tasks/inbox.md`

### When making decisions

- Refer to `vision/north-stars.md` for what success looks like
- Refer to `identity/principles.md` for values-based decision making
- When in doubt, optimise for: (1) shipping something real, (2) making it visible, (3) connecting with the right people — in that order

## Definition of Done

- Change is minimal and localized.
- Tests are added or updated, or verification steps are written explicitly (for code work).
- `make ci-quick` passes locally (when code exists).
- Relevant linters and typechecks pass.
- `.codex/memories/00_ACTIVE.md` is updated if the work changes current status.
- If a meaningful decision was made, capture it in `.codex/memories/decisions/`
  (workspace decisions) or `docs/adr/` (product ADRs that must travel with an
  extractable product subtree, e.g. wealthlens-analyst).
- If a data pipeline was added or changed, re-run it to verify the output and regenerate charts.
- If a new data source was used, add it to `projects/wealthlens-dashboard/docs/data-licences.md`.
- Commits are made incrementally as work progresses, not batched at session end.
- If index.html or any public-facing page references a new file, verify that file exists.

## File conventions

- Markdown for all docs
- Dates in `YYYY-MM-DD` format
- Task format: `- [ ] Task description (@owner if assigned) [due: YYYY-MM-DD]`
- When updating any strategy doc, add a `Last updated: YYYY-MM-DD` line at the top
- Commit subjects: `<area>: <imperative summary>`

## Repo map

### Product

- `projects/wealthlens-dashboard/backend/` — FastAPI application (health, data, metadata, columns, summary, CSV)
- `projects/wealthlens-dashboard/frontend/` — Vue 3 + TypeScript + Pinia + TailwindCSS (40+ components)
- `projects/wealthlens-dashboard/data/` — processed datasets (10 pipeline outputs)
- `projects/wealthlens-dashboard/docs/` — product documentation

### Automation

- `automation/data-pipelines/` — 10 Python fetch/process/chart scripts + run_all.py + validate.py
- `automation/analysis/` — research processing scripts (extract_action_items.py)
- `automation/social-media/` — chart_to_social.py (generates 4 platform sizes)
- `automation/workflows/` — CI/CD workflow references

### Strategy and operations

- `strategy/` — branding, content, growth, outreach, funding, partnership, volunteer, career
- `vision/` — mission, theory of change, horizon, north stars, inspiration
- `identity/` — about Chris, CV, principles, passions, portfolio, skills
- `research/` — raw inputs, synthesised insights, data source registry, reading list
- `tasks/` — `ACTION-REQUIRED.md` (Chris's human action items — surface every summary), active sprint, deadlines, inbox, done, outreach tracking, learning, social media

### Memory and planning

- `.codex/memories/00_ACTIVE.md` — current focus and status board
- `.codex/memories/program/` — cross-cutting program context
- `.codex/memories/decisions/` — captured workspace design decisions
- `docs/adr/` — product ADRs (kept out of `.codex/` so they survive the private-repo split and travel with product extraction)
- `.codex/memories/session_notes/` — running notes for multi-session work
- `.agents/skills/` — repo-scoped Codex workflows

## Canonical commands

```bash
make lint              # ruff check + mypy (backend)
make format            # ruff format (auto-fix)
make test              # pytest -q (backend)
make dev-backend       # uvicorn on 127.0.0.1:8000
make dev-frontend      # vite dev server on :3000
make ci-quick          # lint + tests (~60s, no external deps)
make ci-full           # lint + tests + frontend build + type check
```
