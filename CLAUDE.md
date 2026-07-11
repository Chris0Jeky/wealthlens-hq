# CLAUDE.md — WealthLens HQ

Tier: workshop (T3) — authority: push free / merge gated (`.claude/tier.json`)

Compact Claude Code session contract. Repo-wide operating rules live in
[AGENTS.md](./AGENTS.md); code seams in [AGENT_MAP.md](./AGENT_MAP.md). One home per
policy — this file links, it does not restate.

## Session start

The SessionStart hook prints the live orientation: tier/authority, the open
ACTION-REQUIRED items, and a ledger-triage nudge. Beyond that:

1. On Chris's box, read the newest RESUME block of
   `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md`
   (master control for multi-session work; skip if `../hq-private` is absent —
   volunteer machines).
2. Read `AGENT_MAP.md`, pick the region the task names, and follow that region's
   own `CLAUDE.md` when you touch it.
3. For current focus, read the head of
   `../hq-private/projects/wealthlens/memories/00_ACTIVE.md` (private repo).

Do not bulk-read strategy, vision, identity, or research archives unless the task
requires them — the map's Do-Not-Read index is the default.

## Action required (Chris's reminders — do not skip)

`tasks/ACTION-REQUIRED.md` lists tasks only **Chris** can do. Surface its open items
in **every** summary, status update, and handoff — lead with anything due or overdue
under a `⚑ Action required:` banner. Only Chris clears an item; never infer
completion. When he describes a new task for himself, add it in the file's item
format. Full protocol: the file's own header.

## Private HQ repo (sensitive material)

Personal/sensitive material (identity, applications, outreach contacts + logs,
session memories incl. ORCHESTRATION.md, journal, funding) lives in the private repo
`Chris0Jeky/hq-private`, cloned as a sibling at `../hq-private` (moved 2026-06-13,
decision C — public history before that date was not rewritten). **Never copy
hq-private content back into this public repo.** If `../hq-private` does not exist,
skip private-path steps — they are Chris-only.

## Who is Chris

Chris is a London-based software engineer and the founder of WealthLens UK: BSc
Computer Science (First Class, Middlesex, 2025), published lead author (Springer
SGAI-AI 2025), GE Digital DevSecOps internship, builder of Taskdeck (4,000-commit
local-first dev tool), Widening Participation outreach at Middlesex. Primary stack:
C#/.NET 8, Python, TypeScript; FastAPI, Vue 3, Docker, AWS. Fuller context:
`../hq-private/identity/` (private repo).

## Mission and values

Build open-source tools that make UK wealth inequality data accessible, interactive,
and impossible to ignore, with organisations like Tax Justice UK, Patriotic
Millionaires UK, and the Equality Trust. Values: data first, opinion second · open
source always · accessible by default · independent and non-partisan.

## Repository role

WealthLens HQ is the command-centre repo: strategy, research, tasks, outreach,
automation, and the products in `AGENT_MAP.md` (dashboard, sim, data pipelines).
Multi-domain — agents work on code, content, research, or outreach depending on the
task. Hero #1 (the WealthLens Analyst RAG service) was **extracted 2026-07-06** to
<https://github.com/Chris0Jeky/wealthlens-analyst> — work on it there; only
`projects/wealthlens-analyst/POINTER.md` remains here.

## Architecture quick reference

- **Dashboard:** FastAPI + Pydantic backend; Vue 3 + TypeScript, Pinia, TailwindCSS,
  D3.js/ECharts frontend (GitHub Pages).
- **Sim:** `packages/wealthlens-sim` — cited-registry microsimulation (own CI lane).
- **Pipelines:** `automation/data-pipelines` — reproducible fetch/process/chart.
- **Dev tools:** uv/pip (Python), npm (Node), ruff, mypy, vitest.

## Essential commands

```bash
make lint              # ruff check + mypy (backend)
make format            # ruff format (auto-fix)
make test              # pytest -q (backend + frontend)
make dev-backend       # dashboard uvicorn on 127.0.0.1:8000
make dev-frontend      # vite dev server on :3000
make ci-quick          # lint + tests (~60s, no external deps) — pre-push minimum
make ci-full           # lint + tests + frontend build + type check
make test-hooks        # deny-floor smoke matrix (after ANY hook change)
```

## Skill routing

- `wl-repo-onramp`: broad/ambiguous work, session start, unfamiliar area.
- `wl-safe-slice`: implement a small reviewable change.
- `wl-verify-and-sync`: final verification and status sync.
- `wl-question-batch`: decide whether to ask, assume, or proceed.

## Important paths

- `tasks/ACTION-REQUIRED.md` — Chris's human action items (surface every summary)
- `tasks/active-sprint.md` — current priorities · `tasks/deadlines.md` — date table
- `tasks/inbox.md` — untriaged backlog · `tasks/done.md` — completed work
- `research/data-sources/data-source-registry.md` — data source catalogue
- `strategy/branding-playbook.md` — public voice (the home for content-voice rules)
- `strategy/course-correction-2026-07.md` — priority rule: launch bundle first
- `docs/product/PRODUCT_FRONTIER_2026-07.md` — scored extension portfolio + anti-portfolio
- `../hq-private/projects/wealthlens/memories/00_ACTIVE.md` — status board (private)

## Protocols (links, not restatements)

- **Questions:** batch true blockers into one message, else proceed on a named
  assumption — `docs/agentic/QUESTION_PROTOCOL.md`.
- **Failures:** hooks capture to the local ledger; unresolved issues go in the
  handoff; reviewed summaries → `docs/agentic/FAILURE_LEDGER.md`.
- **Merges/reviews:** agents merge ONLY through `docs/agentic/REVIEW_GATE.md`
  (≥2 independent adversarial lenses + per-finding verify + green CI + aging).
  Never touch repo protections, secrets, or production credentials.
- **Verification:** verify the exact changed seam; never claim tests passed unless
  they ran; close with the handoff shape in `AGENT_MAP.md`.
- **Git posture:** relaxed, declared in `.claude/tier.json`, floor-enforced —
  `docs/agentic/GIT_WORKFLOW.md`.

## Work style

Narrow diffs over rewrites · new behaviour toggleable, default OFF · classify every
failure (blocker / non-blocking risk / pre-existing noise / invalid signal) · commit
incrementally by domain (>~3 changed files without a commit is a smell; subjects
`<area>: <imperative summary>`) · volunteers read this code — clear docstrings.
Hard guardrails (secrets, data integrity, auth): AGENTS.md § Hard guardrails.

## Decision framework

Optimise for (1) shipping something real, (2) making it visible, (3) connecting with
the right people — in that order. Prefer a few source-backed, shareable chart pages
over a large generic dashboard.

## Windows notes

Primary dev platform is Windows 10 Pro. PowerShell does not chain with `&&` — use
`;` and check `$LASTEXITCODE`. Machine-level quirks: `~/.claude/MACHINE.md`.
Local overrides go in `.claude/settings.local.json` only.
