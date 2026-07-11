# Active Sprint

Last updated: 2026-07-11

> Head budget ≤150 lines: only live truth here. The full session-by-session history
> (sessions 1-17, waves, merge trains) rotated to
> [`docs/archive/active-sprint-2026-H1.md`](../docs/archive/active-sprint-2026-H1.md)
> on 2026-07-06 — append new detail there, keep this head current.

> **⚑ DELIVERY-LAYER STACK (2026-07-11, session 20): 4 PRs open, UNMERGED —
> needs a review session, oldest-first.** The hard remainder of the reality
> check, built as a linear stack (each PR bases on the previous; merge #514
> first, the rest retarget automatically): **#514** route prerendering — all
> ~45 routes baked to real HTML with meta (fixes F5: crawler 404s, empty
> no-JS shell, unseen OG images; + F9 HealthStatus; ADR 0001 in `docs/adr/`);
> **#515** editorial front page — 57% WID-cited hero, featured chart, tools
> row, 12-chart pillar index, build-time data vintage in the masthead
> (F4/F6/F10, the "excitement gap"); **#516** reuse layer — chrome-free
> /embed/:chart with iframe auto-resize, ShareBar fully wired, static CSV
> mirrors (F7/F8; RFC-001 a/f/h; generational-wealth CSV held on AR #10);
> **#517** cadence-aware freshness — the permanent "Expired" wall replaced
> by the grammar in `docs/product/freshness-grammar.md` (F3, + F10 age
> copy). Reviews were EXPLICITLY deferred by Chris to a dedicated session
> (2026-07-11 delegation) — do not merge without the REVIEW_GATE pass.
> ci-frontend/lighthouse only trigger on main-based PRs, so the stack's
> upper PRs show e2e (green) until #514 merges and they retarget.

> **⚑ REALITY CHECK (2026-07-11):** live-site + code audit of the public
> dashboard written up in `docs/product/REALITY_CHECK_2026-07-11.md`.
> Verdict: content layer strong, delivery layer defeats it. Headlines: the
> home page's "View Chart" links had NEVER rendered (Vue Boolean-prop cast;
> **fixed + merged, PR #498**); the newsletter form posts to a nonexistent
> Buttondown list — every subscriber since launch lost (**ACTION-REQUIRED
> #11**); all 10 cards badge "Expired" (fixed-30-day ladder vs annual
> sources, permanent now #495 disabled the cron); masthead fabricates
> "UPDATED {today}" via `new Date()`; chart deep links serve HTTP 404 to
> crawlers + og:image is relative → invisible to search/social; 4 tools +
> FAQ have zero inbound links; ShareBar is 8 dead buttons. Seeds (most ≤
> half-day): `tasks/inbox.md` § "2026-07-11 reality-check seeds".
> Independently reconfirms course-correction: launch bundle + wiring first.
> The stalled 2026-07-06 PR backlog was drained by this session's merge train.

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
