# State of the Project — July 2026

Last updated: 2026-07-02

> A whole-project assessment: what WealthLens is genuinely doing well, where it
> is headed, and the concrete path there. Companion doc:
> [`course-correction-2026-07.md`](course-correction-2026-07.md) covers what is
> NOT working and what must change. Seeded tasks for both live in
> `tasks/inbox.md` under "2026-07-02 strategy review seeds".
>
> Method: every claim below cites a repo file or a command output gathered on
> 2026-07-02. No private-repo (`hq-private`) content appears here.

## TL;DR

In seven weeks WealthLens went from scaffold to: a live, cited, WCAG-AA
dashboard with 12 chart pages; a policy simulator package with 850+ tests; and
a RAG analyst that now answers questions about UK wealth statistics with
citations provably drawn from its corpus, at ~£0.002 per answer. The
engineering system producing this (small reviewed PRs, adversarial review
gates, data-honesty audits) is the project's strongest asset and has repeatedly
caught real public-facing errors before readers could. The trajectory, if the
current plan is simply finished, is a shippable, differentiated product (the
Analyst) sitting on top of an unusually trustworthy data layer. The main risk
to that trajectory is not technical and is covered in the course-correction
doc: almost nobody has seen any of it yet.

## What is genuinely working

### 1. Something real is shipped, and it is unusually honest

- Live site since 2026-05-16 (`tasks/active-sprint.md`, completed list) at
  chris0jeky.github.io/wealthlens-hq, serving 12 cited chart pages, three
  interactive calculators, and a scenario simulator page
  (`tasks/active-sprint.md`, sessions 12-13 notes; PR #463 made all 12 charts
  visible on the Data Sources page).
- Every dataset carries source, URL, access date, licence, and update pattern
  (`registries/sources.yml`, `research/data-sources/data-source-registry.md`),
  and the licence/frequency claims shown to the public were reconciled against
  the registry with a shared source-of-truth module and a drift-lock test so
  the transparency pages cannot silently diverge again
  (`frontend/src/constants/datasetProvenance.ts`, PR #464).
- The WAS accreditation-loss caveat mandated by
  `research/methodology/was-caveats.md` is enforced on every WAS-sourced
  chart. This is exactly the "treat disagreement and weakness in the data as a
  feature" posture the research called for
  (`research/synthesised/gaps-and-contradictions.md` §2).

### 2. Data honesty is a working system, not a slogan

The June audit arc (PRs #456, #460, #461, #462, #464 per
`tasks/active-sprint.md` session 13) found and fixed real public
misrepresentations before any journalist could: a CGT stat card overstating
concentration ~2x, an impossible "bottom-50% median" understating by ~6.6x, a
scroller whose percentile markers mathematically contradicted the calculator on
the same site, and a 100x unit bug on the flagship WID chart (#409). Each fix
shipped with a regression or drift-lock test. For a project whose entire brand
is "we let the numbers speak", this audit culture is the moat: it is the reason
the site can be put in front of researchers and journalists without fear.

### 3. The delivery system compounds

- ~1,475 commits since 2026-05-01 (git log, 2026-07-02); roughly 65 PRs merged
  in June alone across sessions 9-15, each gated by two independent adversarial
  review lenses plus bot review plus green CI (`tasks/active-sprint.md`).
- Test base has grown to roughly 2,500+ across packages: ~1,335 frontend vitest
  (session 13), 235 backend (session 12), 853 simulator (session 14), 137
  analyst (session 15). Eleven CI workflows including CodeQL, Lighthouse, E2E,
  and weekly drift schedules (`.github/workflows/`).
- The review gate demonstrably earns its keep: it caught a latent
  simulator-crashing bug in a schema-valid input (#471), a fail-open safety
  hook (#454), and mutation-tested coverage gaps in the analyst's accounting
  suite (#475). This is not process theatre.

### 4. Hero #1 (the Analyst) is past the hard part

Against the locked plan (`docs/plan/HERO1_PLAN.md`) and backlog
(`tasks/hero1-backlog.md`):

- Everything agent-buildable in M0-M2 is done. What remains there is
  human-gated or environment-blocked: H1-02/H1-14 (Chris's golden answers and
  the recall report they unlock, ACTION-REQUIRED #5), H1-03's checkbox
  (hosting decided 2026-06-13; awaiting the Hetzner account, ACTION-REQUIRED
  #6), and H1-06/H1-08 (the IFS/RF report PDFs, network-blocked for the
  agent). M3's core landed 2026-07-02: the Analyst answers real questions
  with citations provably contained in the retrieved set, figures verbatim
  against the database, at ~£0.002 per answer with every model call metered
  and budget-capped (PRs #474, #475, #476; re-runnable proof committed at
  `projects/wealthlens-analyst/evals/checks/check_compose_live.py`).
- The remaining backlog to a public URL is enumerable and small: H1-19/20
  (citation resolution + response schema), H1-21/22/23 (abstention gate +
  deterministic evals), H1-24-29 (eval growth, budget middleware, tracing,
  metrics), H1-30/31 (provision + deploy), H1-32 (writeup + demo sends). Most
  are agent-doable half-day tasks; the human-gated ones are already listed in
  `tasks/ACTION-REQUIRED.md` (items 5 and 6).
- The plan's definition of shipped is exemplary and worth quoting: "live URL +
  eval report committed + writeup #1 published + demo link sent to 10 named
  people. Nothing else counts."

### 5. Decision hygiene keeps momentum durable

Locked plan + ADRs (`docs/adr/0001-0003`) + an ordered backlog of half-day
tasks means any future session (human or agent) can pick up the next unblocked
task without re-planning. Deferred decisions are recorded with rationale
rather than silently dropped (H1-16 rerank deferral note in the backlog;
ACTION-REQUIRED #10 licence question). The simulator's honest framing
("illustrative synthetic population") shows the same discipline applied to
modelling.

## Where this is headed

If the current plan is simply finished, the natural end-state of this phase is:

1. **The Analyst live at a public URL** answering questions about UK wealth
   statistics with resolvable citations, a published eval report, a public
   cost/latency metrics page, and a written-up build story
   (`docs/plan/WRITEUPS.md` outline exists). That is a genuinely
   differentiated artefact: few public tools answer distributional questions
   with provable, cited grounding, and fewer publish their eval numbers.
2. **The dashboard as the credibility surface** it was designed to be: a small
   library of permanent, source-backed, embeddable chart pages exactly as
   `vision/theory-of-change.md` prescribes ("prioritise permanent chart pages,
   downloads, embeds, and methodology notes over a large all-purpose
   dashboard").
3. **The simulator as depth in reserve**: 850+ tests of policy-family
   modelling with provenance manifests, ready to power "what would this reform
   raise" content when the visibility engine exists to carry it.

That combination directly serves the mission (`vision/mission.md`): the data
exists, the honesty machinery exists, and the interactive layer exists. What
converts it from a well-built artefact into "impossible to ignore" is
distribution, which is the course-correction doc's subject.

## The path there (how)

Ordered, with owners. Human-gated items reference their
`tasks/ACTION-REQUIRED.md` entry rather than duplicating it.

| # | Step | Owner | Size | Reference |
|---|------|-------|------|-----------|
| 1 | H1-19 citation resolution, then H1-20 /ask response schema | agent | 2 half-days | `tasks/hero1-backlog.md` |
| 2 | Golden answers working session: agent prepares per-question corpus excerpts (no drafted answers, per the no-fabrication rule), Chris writes answers in one ~1h sitting, unblocking H1-14 recall measurement | Chris + agent | ~1h Chris | ACTION-REQUIRED #5 |
| 3 | H1-21/22/23 abstention gate + deterministic evals in CI | agent | 2-3 half-days | backlog M4 |
| 4 | Corpus completion: fetch the 3-5 IFS/RF report PDFs (H1-06; currently network-blocked for the agent, ~10 min for Chris to download) so the frozen slice is actually whole before the public URL | Chris (or grant fetch access) | ~10 min | backlog M1 |
| 5 | H1-24-29 eval growth, budget middleware, Langfuse tracing, metrics endpoint | agent | ~5 half-days | backlog M5 |
| 6 | Hetzner CAX21 account, then H1-30/31 provision + deploy + public metrics | Chris then agent | ~30 min Chris | ACTION-REQUIRED #6 |
| 7 | H1-32: writeup #1 drafted from `docs/plan/WRITEUPS.md`, demo sent to 10 named people | agent drafts, Chris edits + sends | 1 half-day + Chris hour | backlog M6 |
| 8 | In parallel: the July HMRC CGT statistics release gets a same-day chart/content moment (`tasks/deadlines.md` July row; confirm the exact date on the gov.uk release calendar) | agent preps, Chris posts | 1 half-day | deadlines.md |

Realistic elapsed time given demonstrated velocity: **2-3 working sessions of
agent time plus roughly three focused hours from Chris**, spread over 2-3
weeks. Nothing on this path requires new architecture, new corpus decisions,
or new spend beyond the ~£7/month hosting already decided in ADR 0003.

## What to protect while course-correcting

The course-correction doc argues for redirecting effort toward visibility.
These strengths should NOT be traded away in that shift:

- **The review gate on new code.** It has caught real bugs in nearly every PR
  round. Keep two-lens adversarial review for product code.
- **The no-fabrication lines.** Golden answers stay Chris-written; charts stay
  source-cited; the corpus slice stays frozen until the URL is live
  (`projects/wealthlens-analyst/CLAUDE.md` NEVER-DO list).
- **Spend discipline.** Fail-closed budget accounting is a product feature
  ("cheap, reliable, provably valuable"), not overhead.
- **Honest framing of synthetic/illustrative data.** It is the difference
  between a credible tool and a debunkable one.

## Seeded tasks

Mirrored in `tasks/inbox.md` § "2026-07-02 strategy review seeds". Items that
already exist in `tasks/hero1-backlog.md` or `tasks/ACTION-REQUIRED.md` are
referenced there rather than duplicated.

- [ ] Prepare the H1-14 golden-answers working pack: per-question corpus
  excerpts + candidate citation ids, no drafted answers (@agent)
- [ ] Draft LinkedIn launch post + one chart carousel into
  `tasks/social-media/posts-drafted.md` for Chris to publish (@agent)
- [ ] Draft the four unblocked outreach emails (value-offering, per
  `strategy/outreach-strategy.md`) for Chris to review and send (@agent)
- [ ] Refresh `README.md` to current reality: 12 chart pages, current test
  counts, the Analyst and simulator sections (@agent)
- [ ] Watch the gov.uk release calendar for the HMRC CGT statistics date;
  prepare the same-day chart/content plan (@agent)
- [ ] Add an embed path for one flagship chart (iframe snippet + short docs
  page), per theory-of-change step 3 (@agent)
- [ ] Draft writeup #1 skeleton from `docs/plan/WRITEUPS.md` once H1-30
  deploys (@agent)
