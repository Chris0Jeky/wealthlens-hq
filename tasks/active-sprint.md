# Active Sprint

Last updated: 2026-07-06

> Head budget ≤150 lines: only live truth here. The full session-by-session history
> (sessions 1-17, waves, merge trains) rotated to
> [`docs/archive/active-sprint-2026-H1.md`](../docs/archive/active-sprint-2026-H1.md)
> on 2026-07-06 — append new detail there, keep this head current.

> **⚑ PRODUCT FRONTIER (2026-07-02):** deep product review + extension portfolio in
> `docs/product/PRODUCT_FRONTIER_2026-07.md` (surface verdicts, RFC-001..008,
> anti-portfolio, hard-problems annex). Docs only; changes NO priority: launch
> bundle first. Seeds: `tasks/inbox.md` § "2026-07-02 product frontier seeds".

> **⚑ STRATEGY REVIEW (2026-07-02):** `strategy/state-of-the-project-2026-07.md` +
> `strategy/course-correction-2026-07.md`. Visibility ≈ zero since launch; priority
> rule reinstated — **launch bundle before new sweeps**.

> **2026-07-06 — ANALYST EXTRACTED + T3 HARNESS MIGRATION.**
> **Extraction:** Hero #1 moved to its own public repo
> <https://github.com/Chris0Jeky/wealthlens-analyst> (PR #491) — plan, backlog,
> ADRs, CI and its CLAUDE.md travelled with it; only
> `projects/wealthlens-analyst/POINTER.md` remains here. All H1-* work continues
> THERE (M4 abstention completed here first: #478/#479/#480, sessions 18).
> **Harness:** estate-blueprint T3 migration landed — `.claude/tier.json` (push
> free / merge gated, relaxed-git declared), argv-aware deny floor + smoke matrix
> (#492), 1,602-entry failure-ledger triage (#493, 0 blockers), weekly-data-update
> cron disabled under the red-lane law (#495, tracking #494), root `AGENT_MAP.md`
> + region CLAUDE.mds (#496), CLAUDE.md/AGENTS.md diet + single-runtime cleanup
> (this PR). Memory graduation done; estate registry updated.

## Current sprint (course-correction order)

1. - [ ] Launch bundle: draft the LinkedIn post + 4 outreach emails (agent-draftable;
       the sends are Chris's — ACTION-REQUIRED #2/#3)
2. - [ ] Chris hour: golden answers (AR #5), Hetzner account (AR #6), OpenAI key
       rotation (AR #9), domain (AR #4)
3. - [ ] README + repo-metadata refresh (public face of the repo; includes the stale
       "pre-alpha" wording in `packages/wealthlens-sim/README.md`)
4. - [ ] Analyst URL path (H1-23 → H1-27 → H1-30) — continues in
       `Chris0Jeky/wealthlens-analyst`, not here
5. - [ ] First post-launch-bundle product slice: RFC-001a-d reuse layer

Done from the 2026-07-02 proposal: H1-19/20 (#477/#478), H1-21/22 (#479/#480),
post-gemini review gate (`docs/agentic/REVIEW_GATE.md`, was due 2026-07-16).

> **⚑ See [`ACTION-REQUIRED.md`](ACTION-REQUIRED.md)** for Chris's outstanding
> human items — surfaced in every summary; only Chris clears them.
