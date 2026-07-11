# WealthLens HQ — AGENTS.md

Repo-wide operating rules for ALL coding agents. Session contract: [CLAUDE.md](./CLAUDE.md);
seams: [AGENT_MAP.md](./AGENT_MAP.md); authority: `.claude/tier.json` (T3 — push free,
merge gated). One home per policy.

## Scope

- Work inside this repository; prefer small reviewable diffs on task-scoped branches.
  Multi-domain workspace: code, content, research, strategy, outreach — identify the
  domain (and the AGENT_MAP region) before reaching for tools.
- Private sibling repo `../hq-private` holds sensitive material — never copy its
  content here; skip private paths when it is absent (volunteer machines).

## Session start

An autonomous multi-session workflow may be in progress: check the newest RESUME
block of `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md`
and `.../memories/00_ACTIVE.md` before new work. Read `tasks/ACTION-REQUIRED.md` and
surface its open items in every summary/handoff — only Chris clears them.

## Operational issues

Never silently ignore a tool, dependency, test, or CI error because a workaround
exists. Classify it (blocker / non-blocking risk / pre-existing noise / invalid signal),
capture a follow-up path, and include every not-fully-fixed issue in the handoff.

## Subagents and worktrees

Spawn subagents only when the user asks for delegation/parallel work. Split by
disjoint region ownership; one coordinator owns synthesis and final verification.
Workers derive paths from the worktree root — never absolute main-checkout paths.

## Hard guardrails

- **Secrets:** never commit keys/passwords/tokens; no "temporary" keys in docs or
  code; a discovered in-repo secret stops work → propose rotation + purge.
- **Data integrity:** every figure cites source + URL + access date; never fabricate
  statistics; charts are mobile-responsive and WCAG AA minimum.
- **Auth (dashboard):** private-data endpoints require auth enforced server-side;
  tests prove non-admins get 403.
- **Command safety:** the deny floor is `.claude/hooks/dispatch.py` (tier-aware, see
  `tier.json`); git posture in `docs/agentic/GIT_WORKFLOW.md`.
- **Backward compatibility:** never change shared/config defaults unless
  backward-compatible; new behaviour ships toggleable, default OFF; local overrides
  go in `.env`, never in templates.

## Domain guidance

- **Code:** follow the region's `CLAUDE.md` (dashboard, sim, pipelines); volunteers
  read this code — clear docstrings.
- **Content:** voice per `strategy/branding-playbook.md`; non-partisan; no claim
  without a source.
- **Tasks:** priorities in `tasks/active-sprint.md`; new ideas → `tasks/inbox.md`;
  completed → `tasks/done.md` with date.
- **Outreach:** check `../hq-private/projects/wealthlens/outreach/contacts.md` and
  `emails-sent.md` first — never double-contact; offer value; link something built.
- **Research:** raw inputs stay intact in `research/raw/`; insights →
  `research/synthesised/key-insights.md`; extracted actions → `tasks/inbox.md`.
- **Decisions:** shipping real → visible → connected (CLAUDE.md § Decision framework).

## Definition of Done

- Change is minimal and localized; tests or explicit verification steps included.
- `make ci-quick` passes locally; relevant linters/typechecks pass.
- **Merges go through [`docs/agentic/REVIEW_GATE.md`](docs/agentic/REVIEW_GATE.md)**
  (≥2 independent adversarial lenses + per-finding verification; bots are a bonus).
- If a seam moved, update `AGENT_MAP.md` (the map's write path) and the region's
  `CLAUDE.md`; sync `00_ACTIVE.md` (private) if status changed; workspace decisions →
  `../hq-private/.../memories/decisions/`, product ADRs → `docs/adr/`.
- Pipeline changed → re-run it; new data source → `data-licences.md` + the registry.
- Commit incrementally by domain; subjects `<area>: <imperative summary>`.

## File conventions and commands

Markdown docs · dates `YYYY-MM-DD` · tasks `- [ ] description (@owner) [due: YYYY-MM-DD]`
· strategy docs carry `Last updated:` · data source records: name, URL, access date,
format, licence, update pattern. Commands: CLAUDE.md § Essential commands; pre-push
minimum `make ci-quick`.
