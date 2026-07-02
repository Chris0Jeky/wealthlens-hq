# Course Correction — July 2026

Last updated: 2026-07-02

> The critical half of the July 2026 whole-project review. Companion doc:
> [`state-of-the-project-2026-07.md`](state-of-the-project-2026-07.md) covers
> what is working and the build path. This doc covers what is NOT working, why,
> and the operating changes to fix it. Seeded tasks live in `tasks/inbox.md`
> under "2026-07-02 strategy review seeds".
>
> Method: every claim cites a repo file or a command output gathered on
> 2026-07-02. No private-repo (`hq-private`) content appears here.

## TL;DR

WealthLens has become excellent at the part of the mission that requires no
one's permission (building) and has done almost none of the part that was the
point (being seen). The mission is "visible, interactive, and impossible to
ignore"; the decision framework says ship real things, make them visible,
connect with the right people, in that order (`CLAUDE.md`). Leg 1 is
overwhelmingly won. Legs 2 and 3 are at approximately zero, and have been
since the site went live on 2026-05-16. This is not a motivation problem; it
is a structural one. Every distribution action is gated on a human hour that
never gets scheduled, while agent capacity flows into the ungated lane
(audits, sweeps, dependency drains) which is now past diminishing returns.
The fix is not to build less well. It is to give distribution the same
operating machinery that made building unstoppable: prepared drafts, batched
human hours, explicit done-definitions, and measurement.

## The evidence

Numbers gathered 2026-07-02 unless noted.

| North star | Status | Evidence |
|---|---|---|
| 1. Ship something real | **Won, repeatedly** | Live site, 12 cited charts, simulator, Analyst answering with citations (see companion doc) |
| 2. Make it visible | **~Zero** | 0 stars, 0 forks, 0 watchers; GitHub 14-day traffic: **5 views, 1 unique visitor** (`gh api .../traffic/views`); repo has no description, homepage URL, or topics set (`gh repo view`) |
| 3. Connect with the right people | **Stalled since mid-May** | Last outreach sends were the two volunteer emails of 2026-05-14 (`tasks/done.md`); the four unblocked partner emails have waited since v0.1 went live (~2026-05-16) and blew through their own 2026-06-21 deadline (`tasks/deadlines.md`, `tasks/ACTION-REQUIRED.md` #3) |

Supporting detail:

- **Zero published content, ever.** `tasks/social-media/posts-published.md` is
  an empty table; `posts-drafted.md` says "No drafts yet."
  `strategy/content-strategy.md` specifies a five-day-per-week cadence. The
  accounts exist (created 2026-05-14, `tasks/done.md`) and have sat silent for
  seven weeks. The LinkedIn launch post has been "the single highest-visibility
  action available" in `tasks/ACTION-REQUIRED.md` (#2) since May.
- **The volunteer funnel was consumed by the build system.** All 10 GitHub
  issues (created 2026-05-16 as good-first-issue/help-wanted bait) are CLOSED
  (`gh issue list --state all`), done by the agent loop. Zero open entry
  points remain. `git shortlog` shows no human contributor besides Chris.
  `strategy/volunteer-strategy.md` names "good first issues" as a needed
  asset; the strategy was executed in reverse.
- **The project cannot measure its own visibility.** The Plausible composable
  exists and is tested (`frontend/src/composables/useAnalytics.ts`) but is
  dormant: it activates only when `VITE_PLAUSIBLE_DOMAIN` is set, which is
  commented out in `.env.example` and blocked on the unregistered domain
  (ACTION-REQUIRED #4, open since May). Even north-star metrics like
  "newsletter signups" (`vision/north-stars.md`) have no collection mechanism.
- **Strategy is shelf-ware.** All five vision docs and 5 of 7 strategy docs
  have not been substantively touched since 2026-05-14 (git log; the two
  June-13 touches were private-repo path repoints). The strategy corpus is
  good; it is simply not driving decisions. Meanwhile
  `research/synthesised/gaps-and-contradictions.md` §5 prescribed the exact
  priority chain: "charts -> deploy -> first post -> first outreach emails ->
  everything else." Execution stopped at "deploy" on 2026-05-16 and has been
  building sideways since.
- **The public front door undersells the work.** `README.md` still says 4
  charts and 874 tests; reality is 12 chart pages and roughly 2,500+ tests
  (session notes, `tasks/active-sprint.md`). The GitHub repo description is
  empty. For a project whose thesis is "visibility is an engineering problem"
  (`research/synthesised/key-insights.md` #1), the shop window is stale.
- **Time-sensitive items are silently expiring.** `tasks/deadlines.md` has not
  been updated since 2026-05-14. The UCL IIPP Forum (June 16-17) passed
  unremarked; the outreach-email date passed; the July HMRC CGT release
  ("engage same-day") is imminent with no prepared plan; the JRRT outline
  (2026-08-24) is seven weeks out. The file's own instruction ("check this
  weekly") is not happening.
- **Diminishing returns on the ungated lane.** The audit arc through mid-June
  found real, serious public errors and was worth every hour (see companion
  doc). But by sessions 14-15 the sweeps were coming back CLEAN (simulator
  sweep 2: zero findings; analyst core sweep: zero findings,
  `tasks/active-sprint.md`), and effort continued to flow there because it is
  the lane that needs no human hour. Motion is being measured (PRs merged)
  where progress should be (people reached, per
  `vision/north-stars.md` visibility metrics).
- **Sequencing debt inside Hero #1.** The eval golden set has been DRAFT since
  2026-06-11 (H1-02/H1-14, ACTION-REQUIRED #5) while M3 built on top; the
  frozen corpus slice is still missing its 3-5 IFS/RF reports because PDF
  fetch is network-blocked for the agent (H1-06) and nobody downloaded them by
  hand, so the Analyst currently answers from 23 chunks drawn from 2 tabular
  sources. Both blockers are under an hour of human time, combined.

## Root cause

One asymmetry explains nearly all of this: **work the agent can complete alone
advances at extraordinary speed; work requiring roughly one human hour stalls
indefinitely.** The operating loop (autonomous sessions, adversarial review,
sweep-when-blocked) is optimised for throughput in the permissionless lane.
When the build chain blocked, the loop correctly found more building to do,
because that is what it can do. Nothing in the system schedules, batches, or
prepares the human-gated actions, so they accumulate in
`tasks/ACTION-REQUIRED.md` (three of its items date to mid-May) while their
value decays. The result is a project that by its own decision framework
(`CLAUDE.md`: ship, then visibility, then connection) keeps re-winning leg 1
because legs 2 and 3 are structurally unreachable by the machinery it built.

Two secondary causes:

- **"Done" is defined as merged, not seen.** Only `docs/plan/HERO1_PLAN.md`
  gets this right: "live URL + eval report + writeup published + demo sent to
  10 named people. Nothing else counts." No other workstream has a
  visibility-inclusive definition of done.
- **No measurement, no pressure.** With analytics dormant and north-star
  metrics uncollected, zero-visibility produces zero discomfort. None of the
  numbers in the table above are tracked anywhere in the repo.

## What must change: strategy

**S1. Reinstate the priority chain as the operating rule.** The chain from
`gaps-and-contradictions.md` §5 (charts -> deploy -> **first post -> first
outreach** -> everything else) becomes the standing tie-breaker: when choosing
the next task, an undone earlier link outranks any later-link work, however
attractive. The first post and first outreach emails are seven weeks overdue
under this rule.

**S2. Adopt the Hero #1 definition of shipped project-wide.** A workstream is
done when something public points at it: a post, a writeup, an embed, a sent
email, a published eval report. Merged-to-main is an internal milestone, not
an outcome. Apply retroactively: the dashboard (live 2026-05-16) is *built*
but will not be *shipped* until the launch post exists.

**S3. One sharp spear for July: the Analyst to a public URL, plus the launch
bundle.** `research/synthesised/key-insights.md` #48 already warned that the
biggest risk is doing everything at once. July's spear is: finish the Analyst
path (companion doc, steps 1-7), and ship the launch bundle (LinkedIn post +
four outreach emails + README/repo-metadata refresh) alongside it. The
dashboard gets maintenance and the July CGT release moment only. The
simulator gets nothing new this month.

**S4. Give the north stars numbers and dates.** `vision/north-stars.md` lists
metrics with no targets, so zero is never a miss. Agent proposes, Chris sets:
e.g. by 2026-08-31: first LinkedIn post published; 4 outreach emails sent and
logged; Analyst live URL public; writeup #1 published; analytics collecting;
plus modest reach targets Chris considers honest (stars, profile views,
replies). The point is not the specific numbers; it is that misses become
visible.

**S5. Rebuild the volunteer funnel deliberately.** Policy: the agent leaves a
standing set of 3-5 genuinely valuable, labelled, scoped good-first-issues
OPEN and does not do them. Volunteer-strategy assets (CONTRIBUTING.md, issue
list) only work if the issues survive contact with the autonomous loop.

## What must change: execution

**E1. The weekly Chris hour.** One recurring 60-90 minute block. The agent
prepares the agenda the day before: every ACTION-REQUIRED item batched with
its materials ready (drafted post to approve, drafted emails to send, golden-answer
pack to fill in, account signups queued with exact steps). Chris executes;
nothing else is scheduled into that hour. This single mechanism unblocks
items 2, 3, 4, 5, 6, 9 of `tasks/ACTION-REQUIRED.md` within two to three
weeks. (Proposed here; goes into ACTION-REQUIRED only when Chris adopts it.)

**E2. Sweep moratorium.** No new audit sweeps of already-swept surfaces until
the Analyst URL is live. The review gate on NEW code stays. When the build
chain blocks, the fallback order becomes: launch-bundle assets, then
discoverability hygiene, then seeded inbox follow-ups; sweeps last.

**E3. Distribution as code.** Treat posts and emails like PRs: agent drafts
into `tasks/social-media/posts-drafted.md` (per `strategy/content-strategy.md`
formats and `strategy/branding-playbook.md` voice), two-lens review for
factual claims (every figure cited, same bar as charts), Chris approves and
publishes, result logged in `posts-published.md` with performance notes.
`automation/social-media/chart_to_social.py` already generates platform
assets and has never been used in anger.

**E4. Fix the shop window this week (agent-doable).** Refresh README numbers
and sections; set the GitHub repo description, homepage URL, and topics (on
Chris's nod, since it is outward-facing); verify OG images render on link
shares. These are hours of work that multiply every future visibility action.

**E5. Turn measurement on.** Register `wealthlens.uk` (ACTION-REQUIRED #4,
~£10/yr), set `VITE_PLAUSIBLE_DOMAIN`, and stand up Plausible (hosted tier or
self-hosted on the same Hetzner box as the Analyst, ADR 0003). From then on,
the weekly hour starts with the numbers.

**E6. Clear the standing risks.** (a) Rotate the chat-exposed OpenAI key
(ACTION-REQUIRED #9). (b) Document the post-gemini review gate before the
2026-07-17 bot sunset: two-lens internal adversarial review + codex remains
the standard, so the gate does not silently weaken. (c) Decide the RF-derived
chart's output licence (ACTION-REQUIRED #10). (d) Hand-download the 3-5
IFS/RF PDFs to complete the frozen corpus (10 minutes) or grant the agent
fetch access for H1-06.

**E7. Doc hygiene so state stays legible.** Prune `tasks/deadlines.md` of
passed items and restore the weekly check; reconcile stale checkboxes (e.g.
H1-01 is complete per PR #406 but unticked in `tasks/hero1-backlog.md`);
refresh or explicitly retire each stale strategy doc (a one-line "still
current as of YYYY-MM-DD" stamp is enough) so staleness is a signal again.

## The next 14 days, concretely

| When | What | Owner |
|---|---|---|
| Days 1-2 | H1-19 + H1-20 (Analyst citation resolution + schema); README refresh; repo description/homepage/topics prepared for Chris's nod | agent |
| Days 1-2 | Draft LinkedIn launch post + carousel; draft 4 outreach emails; prepare golden-answers pack | agent |
| Chris hour 1 | Publish post + update profile (AR #2); send 4 emails (AR #3); register domain (AR #4); rotate key (AR #9); download IFS/RF PDFs | Chris, ~90 min |
| Days 3-7 | H1-21/22/23 (abstention + deterministic evals); H1-08 PDF chunking once PDFs exist; wire Plausible once domain exists; post-gemini review-gate doc; reopen 3-5 good-first-issues | agent |
| Chris hour 2 | Golden answers (AR #5, ~1h) -> unblocks H1-14 recall report; Hetzner account (AR #6, ~30 min) | Chris |
| Days 8-14 | H1-14 recall report; H1-24-29 (evals, budget middleware, tracing, metrics); H1-30/31 deploy to public URL; writeup #1 draft; CGT-release same-day content if the stats drop | agent |
| Chris hour 3 | Edit + publish writeup #1; send demo to 10 named people (AR-listed private logs checked first); confirm north-star targets (S4) | Chris |

End state if this holds: by mid-July the Analyst is public with an eval
report, the launch post and outreach emails are out, analytics is measuring,
the volunteer funnel has real openings, and every currently-open
ACTION-REQUIRED item except BGV prep is closed.

## What we are NOT changing

- The locked Hero #1 plan and its NEVER-DO list stay locked.
- The two-lens adversarial review gate on product code stays.
- The data-honesty bar (cite everything, fabricate nothing, caveat weakness)
  stays; it extends to social posts and the writeup, not the reverse.
- Non-partisan voice per `strategy/branding-playbook.md` stays.

## Seeded tasks

Mirrored in `tasks/inbox.md` § "2026-07-02 strategy review seeds"; human-gated
items already tracked in `tasks/ACTION-REQUIRED.md` are referenced, not
duplicated.

- [ ] Adopt the weekly Chris hour (E1): Chris confirms a recurring slot; agent
  prepares the agenda pack before each (@Chris decision, then @agent standing)
- [ ] Sweep moratorium + fallback order (E2): record in the orchestration
  workflow notes once Chris confirms (@Chris decision)
- [ ] README refresh to current reality (@agent; also in companion doc)
- [ ] Repo description + homepage + topics via `gh repo edit` (@agent, on
  Chris's nod)
- [ ] Verify OG/social-share previews on the live site's key pages (@agent)
- [ ] Post-gemini review-gate doc before 2026-07-17 (@agent)
- [ ] Reopen 3-5 scoped good-first-issues and add the reserve policy note to
  CONTRIBUTING.md (@agent)
- [ ] Wire Plausible once the domain exists: set `VITE_PLAUSIBLE_DOMAIN`,
  decide hosted vs self-hosted alongside the Analyst box (@agent after AR #4)
- [ ] Prune + restore `tasks/deadlines.md` weekly check; add JRRT outline
  go/no-go decision point (due 2026-08-24) (@agent)
- [ ] Propose numeric 90-day north-star targets for Chris to set (S4) (@agent
  draft, @Chris decide)
- [ ] Strategy-doc freshness pass: stamp, refresh, or retire each of the 7
  strategy docs (@agent draft, @Chris approve)
- [x] Tick H1-01 in `tasks/hero1-backlog.md` (complete per PR #406,
  2026-06-13; `registries/sources.yml` carries 8 `analyst_corpus: true`
  sources) (@agent) [completed: 2026-07-02, during this review]
