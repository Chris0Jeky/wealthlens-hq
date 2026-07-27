# WealthLens HQ — AGENTS.md

Repo-wide operating rules for ALL coding agents. Session contract + proving checks +
pitfalls: [CLAUDE.md](./CLAUDE.md); seams: [AGENT_MAP.md](./AGENT_MAP.md); authority:
`.agent-harness/tier.json` (T3 — push free, merge free on the T3 gate). Merge, review,
worktree and question doctrine lives in the global laws (`~/.claude/CLAUDE.md`) — one home
per policy, never restated here.

## Scope

Work inside this repository; small reviewable diffs on task-scoped branches. This is a
multi-domain workspace (code, content, research, strategy, outreach) — name the domain and the
AGENT_MAP region before reaching for tools. The private sibling `../hq-private` holds sensitive
material: never copy its content here, and skip private paths when it is absent (volunteer
machines).

## Hard guardrails

- **Secrets:** never commit keys/passwords/tokens; no "temporary" keys in docs or code; a
  discovered in-repo secret stops work → propose rotation + purge.
- **Data integrity:** every figure cites source + URL + access date; never fabricate statistics;
  charts are mobile-responsive and WCAG AA minimum.
- **Auth (dashboard):** private-data endpoints enforce auth server-side; tests prove non-admins
  get 403.
- **Backward compatibility:** never change shared/config defaults incompatibly; new behaviour
  ships toggleable, default OFF; local overrides go in `.env`, never in templates.
- **Command safety:** the vendored deny floor is `.claude/hooks/dispatch.py` (v1.6.20,
  tier-aware); after ANY hook change run `python .claude/hooks/smoke_test.py` (~5m30s). Git
  posture: `docs/agentic/GIT_WORKFLOW.md`.

## Operational issues

Never silently ignore a tool, dependency, test or CI error because a workaround exists.
Classify it — blocker / non-blocking risk / pre-existing noise / invalid signal — capture a
follow-up path, and include every not-fully-fixed issue in the handoff. Hooks capture failures
to the local ledger; reviewed summaries graduate to `docs/agentic/FAILURE_LEDGER.md`.

## Worktrees here

`.claude/settings.json` symlinks `node_modules` and `.venv` into Claude-managed worktrees. A
hand-made `git worktree add` needs `-c core.longpaths=true` (see CLAUDE.md pitfalls) and gets no
symlinks — install deps or run frontend checks in the main checkout. Workers derive paths from
their own worktree root, never absolute main-checkout paths.

## Domain guidance

- **Code:** follow the region's `CLAUDE.md` (dashboard, sim, pipelines); volunteers read this
  code — clear docstrings.
- **Content:** voice per `strategy/branding-playbook.md`; non-partisan; no claim without a source.
- **Tasks:** priorities in `tasks/active-sprint.md`; new ideas → `tasks/inbox.md`; completed →
  `tasks/done.md` with date; Chris-only items → `tasks/ACTION-REQUIRED.md` (surface every summary).
- **Outreach:** check `../hq-private/projects/wealthlens/outreach/contacts.md` and
  `emails-sent.md` first — never double-contact; offer value; link something built.
- **Research:** raw inputs stay intact in `research/raw/`; insights →
  `research/synthesised/key-insights.md`; extracted actions → `tasks/inbox.md`.

## Definition of Done

- Change is minimal and localized; the seam's proving check from CLAUDE.md ran green (state
  which one). Pre-push minimum: `make PYTHON=python ci-quick`.
- Seam moved → update `AGENT_MAP.md` and the region's `CLAUDE.md`; status changed → sync
  `00_ACTIVE.md` (private); workspace decisions → `../hq-private/.../memories/decisions/`,
  product ADRs → `docs/adr/`.
- Pipeline changed → re-run it; new data source → `data-licences.md` + the registry.
- Commit incrementally by domain; subjects `<area>: <imperative summary>`.

## File conventions

Markdown docs · dates `YYYY-MM-DD` · tasks `- [ ] description (@owner) [due: YYYY-MM-DD]` ·
strategy docs carry `Last updated:` · data source records: name, URL, access date, format,
licence, update pattern.
