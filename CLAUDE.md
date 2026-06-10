# CLAUDE.md — WealthLens HQ

Compact session contract for Claude Code in `wealthlens-hq/`. Move detailed procedures into `.claude/skills/*/SKILL.md`, `docs/agentic/*`, or `autodoc/*`.

## Authority order

1. User prompt for the current turn.
2. `AGENTS.md` for repo-wide operating rules.
3. `.codex/memories/00_ACTIVE.md` for current focus areas and status.
4. `.codex/memories/program/00_READ_THIS_FIRST.md` for program context.
5. `autodoc/AGENT_INDEX.md` for code-grounded orientation (once code exists).
6. Relevant skill under `.claude/skills/*/SKILL.md`.
7. Strategy, vision, and identity docs for non-coding work.
8. Research docs for data and analysis work.

When sources conflict, use the higher source and report the conflict.

## First 5 minutes

1. Read `.codex/memories/session_notes/ORCHESTRATION.md` — **master control document** for the active multi-session workflow (branch status, open PRs, review rounds, recovery instructions). If it exists, follow its recovery checklist before doing anything else.
2. Read `AGENTS.md`.
3. Read `.codex/memories/00_ACTIVE.md`.
4. Read `.codex/memories/program/00_READ_THIS_FIRST.md`.
5. Read `tasks/active-sprint.md`.
6. Read `tasks/ACTION-REQUIRED.md` — Chris's outstanding human action items; you must surface these (see "Action-required protocol" below).
7. Select one primary skill and, at most, one support skill.
7. Identify the smallest safe, reviewable change.
8. State blockers, assumptions, verification target, and docs-sync target before editing.

Do not bulk-read strategy docs, vision docs, identity docs, or research archives unless the task explicitly requires them.

## Action-required protocol (Chris's reminders — do not skip)

`tasks/ACTION-REQUIRED.md` is the curated list of outstanding tasks that need
**Chris** (a human), each with a how-to guide. It is the mechanism that stops
high-leverage actions getting lost. Treat it as a standing instruction:

- **Read it at session start** (it is in "First 5 minutes").
- **Surface the open items in every summary, status update, handoff, and
  end-of-turn wrap-up** — not only when asked. Lead with anything time-sensitive
  (a `[due: …]` that is today or overdue) under a one-line `⚑ Action required:`
  banner, then a short numbered list of open titles with due flags, then point to
  the file for the guides. Keep it brief; do not dump the guides every time.
- **Only clear an item when Chris explicitly says it is done.** Never infer
  completion. When he confirms: tick the box, move it to the file's `## Done`
  section with `[completed: YYYY-MM-DD]`, and bump the file's `Last updated`.
- **When Chris describes a new task for himself**, add it to the file in the
  documented item format (title, priority, why, how, done-when).
- The full idea backlog stays in `tasks/inbox.md`; all dated items in
  `tasks/deadlines.md`. Promote into ACTION-REQUIRED only what is currently
  actionable and important (keep it ≤ ~8 open items).

## Who is Chris

Chris is a London-based software engineer and the founder of WealthLens UK, an open-source project making UK wealth inequality data visible to the public.

### Background

- BSc Computer Science, First Class Honours, Middlesex University (2025)
- Published lead author: "Navigating the N-Person Prisoners' Dilemma" - Springer, SGAI-AI 2025
- 15-month software engineering internship at GE Digital (DevSecOps, AWS, Jenkins, CI/CD)
- Near-co-founder of a quant/options trading platform startup
- Built Taskdeck: a 4,000-commit local-first developer tool (.NET 8, Vue 3, LLM integration)
- Works at Middlesex University in Widening Participation outreach
- See `identity/` for fuller context

### Technical skills

- Primary: C#/.NET 8, Python, TypeScript, JavaScript
- Backend: FastAPI, Node.js/Express, .NET, REST APIs
- Frontend: Vue 3, Pinia, TailwindCSS, D3.js
- Data: Pandas, scikit-learn, SQLite, PostgreSQL, MongoDB
- Infrastructure: Docker, AWS, Jenkins, CI/CD, Git, Linux
- AI/LLM: OpenAI API, Gemini API, multi-provider abstraction, intent classification

## Mission

Build open-source tools that make UK wealth inequality data accessible, interactive, and impossible to ignore. Collaborate with organisations like Tax Justice UK, Patriotic Millionaires UK, and the Equality Trust.

## Values

- Data first, opinion second
- Open source always
- Accessible by default
- Independent and non-partisan

## Repository role

WealthLens HQ is the command-centre repo for strategy, research, tasks, outreach, community, automation, and planned software projects. This is a multi-domain workspace — agents work on code, content, research, and outreach depending on the task.

The main planned product is `projects/wealthlens-dashboard/`, with:

- Python and FastAPI for backend/API work
- Vue 3, TypeScript, Pinia, TailwindCSS, D3.js or ECharts for frontend and visualisation
- Reproducible data pipelines in `automation/data-pipelines/`
- Source citations for every dataset, including URL and access date
- Mobile-responsive charts that meet WCAG AA minimum
- Clear docstrings and comments because volunteers will read the code

## Hero #1: WealthLens Analyst (active build)

`projects/wealthlens-analyst/` — evidence-backed RAG analyst over official UK
wealth statistics. **The plan is locked** (`docs/plan/HERO1_PLAN.md`); the
ordered backlog is `tasks/hero1-backlog.md`; decisions are `docs/adr/0001-0003`.
The subtree has its own `CLAUDE.md` with the locked decisions and a NEVER-DO
list (no re-planning, no new corpus sources before the live URL, no fabricated
golden answers, every model call through `llm/client.py`, hard spend cap).
Session opener: read that CLAUDE.md + the backlog, pick the next unblocked
task, confirm approach in two lines, implement.

## Architecture quick reference

- **Dashboard backend:** Python 3.11+, FastAPI, Pydantic, SQLite (dev) / PostgreSQL (prod)
- **Dashboard frontend:** Vue 3 + TypeScript, Pinia, TailwindCSS, D3.js or ECharts, Vite
- **Data pipelines:** Python, Pandas, reproducible scripts in `automation/data-pipelines/`
- **Infrastructure:** Docker, GitHub Actions, AWS
- **Dev tools:** uv (Python), npm (Node), ruff (lint/format), mypy (types), vitest (frontend tests)

## Essential commands

```bash
make lint              # ruff check + mypy (backend)
make format            # ruff format (auto-fix)
make test              # pytest -q (backend)
make dev-backend       # uvicorn on 127.0.0.1:8000
make dev-frontend      # vite dev server on :3000
make ci-quick          # lint + tests (~60s, no external deps)
make ci-full           # lint + tests + frontend build + type check
```

Pre-push: `make ci-quick` at minimum.

## Skill routing

Use these Claude skills when relevant:

- `wl-repo-onramp`: broad or ambiguous work, session start, unfamiliar area.
- `wl-safe-slice`: implement a small reviewable change.
- `wl-verify-and-sync`: final verification and status sync.
- `wl-question-batch`: decide whether to ask, assume, or proceed.

## Important paths

- `.codex/memories/session_notes/ORCHESTRATION.md` — **master control for multi-session workflow** (read first!)
- `tasks/ACTION-REQUIRED.md` — **Chris's outstanding human action items** (surface these every summary; see "Action-required protocol")
- `tasks/active-sprint.md` — current priorities
- `tasks/deadlines.md` — all time-sensitive items in one date table
- `tasks/inbox.md` — new ideas and untriaged work
- `tasks/done.md` — completed work with dates
- `research/raw/` — raw and consolidated research inputs
- `research/synthesised/key-insights.md` — distilled research conclusions
- `research/data-sources/data-source-registry.md` — data source catalogue
- `strategy/branding-playbook.md` — tone, platform, and public voice guidance
- `vision/north-stars.md` — success metrics and milestones
- `identity/principles.md` — values-based decision guidance
- `projects/wealthlens-dashboard/` — main product (backend, frontend, data, docs)
- `projects/wealthlens-analyst/` — Hero #1 RAG analyst (locked plan: `docs/plan/HERO1_PLAN.md`; backlog: `tasks/hero1-backlog.md`)
- `automation/data-pipelines/` — reproducible data fetching scripts
- `.codex/memories/00_ACTIVE.md` — current focus and status board

## Domain-specific guidance

### Research handling

Raw source documents from Claude, Codex, and other assistants may remain in provider-specific folders under `research/raw/`. When research is consolidated by topic, keep the original raw files intact and add the merged output as a clearly named Markdown file in `research/raw/` or a distilled note in `research/synthesised/`.

Action items extracted from research should go into `tasks/inbox.md`. Key insights should go into `research/synthesised/key-insights.md`.

### Content voice

- Confident but not arrogant
- Data-driven and accessible
- Personal where useful, especially around housing, wages, opportunity, and widening participation
- Non-partisan: present data, not party-political opinions
- Avoid making claims that are not backed by sources

### Outreach rules

- Check `tasks/outreach/contacts.md` before contacting anyone
- Check `tasks/outreach/emails-sent.md` for prior contact history
- Tone should be professional, specific, and value-offering
- Include a link to something already built whenever possible

### File conventions

- Markdown for docs
- Dates in `YYYY-MM-DD`
- Task format: `- [ ] Task description (@owner if assigned) [due: YYYY-MM-DD]`
- Strategy docs must include `Last updated: YYYY-MM-DD` near the top
- Keep data source records explicit: source name, URL, access date, format, licence, update pattern, and notes

## Default work style

- Prefer narrow diffs over rewrites.
- Preserve backward compatibility. New behavior toggleable, default OFF.
- Do not silently ignore failures. Classify as blocker, non-blocking risk, pre-existing noise, or invalid signal.
- Record workarounds and future fix paths.
- Keep generated summaries short and factual.
- Do not merge PRs, change repo protections, alter secrets, or edit production credentials.
- Volunteers will read this code — write clear docstrings and comments where they help.

## Hard guardrails

### Secrets
- Never commit API keys, DB passwords, JWT secrets, or encryption keys.
- Never add "temporary" keys in docs or code.
- If a secret is discovered in-repo, stop and propose rotation + purge.

### Data integrity
- All data must cite its source with URL and access date.
- Do not fabricate statistics, percentages, or data points.
- Charts must be mobile-responsive and meet WCAG AA minimum.

### Auth (when dashboard exists)
- All endpoints returning user or private data must require auth.
- All privileged endpoints must enforce authorization server-side.
- Add tests proving non-admins get `403` on admin routes.

### Config defaults
- New features default OFF.
- Never change defaults unless backward-compatible.

## Question protocol

Ask only when the uncertainty is a true blocker: irreversible product decision, missing credential, destructive action, security boundary. Otherwise proceed with a stated assumption. Batch questions into one compact message. See `docs/agentic/QUESTION_PROTOCOL.md`.

## Failure protocol

Every failed command, missing dependency, tool denial, or workaround must appear in the final handoff if unresolved. Claude hooks append raw entries to ignored `.claude/local/failure_ledger.jsonl`; promote only reviewed summaries to `docs/agentic/FAILURE_LEDGER.md`.

## Verification protocol

Before final response: (1) re-read the requested outcome, (2) verify the exact changed seam, (3) state commands run and results, (4) state what was not verified and why, (5) update status docs only if their truth changed. Do not claim tests passed unless they actually ran.

## Decision framework

When prioritising, optimise for:

1. Shipping something real
2. Making it visible
3. Connecting with the right people

In practice, prefer a small number of source-backed, shareable chart pages over a large generic dashboard.

## Git and repo structure

Single repo at `wealthlens-hq/`. Commit subjects: `<area>: <imperative summary>`. Use `gh` CLI for GitHub operations.

### Incremental commits

Commit early and often as you work. Do not batch all changes into one commit at the end of a session. Group commits by domain:

- One commit for a pipeline fix, another for the chart it affects.
- One commit for infrastructure (pyproject.toml, Makefile), another for docs.
- One commit per new feature or file group.

Each commit should be independently reviewable. If a session produces more than ~3 files of changes without a commit, something is wrong.

## Windows notes

- Primary dev platform is Windows 10 Pro.
- Use PowerShell syntax (backtick for line continuation, `$null` not `/dev/null`).
- Do not chain commands with `&&` in PowerShell; use `;` and check `$LASTEXITCODE`.

## Local settings

Use committed `.claude/settings.json` for Claude Code guardrails. Codex uses `AGENTS.md` and `.agents/skills/*`. Use `.claude/settings.local.json` for personal machine overrides only.
