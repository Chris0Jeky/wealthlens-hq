# RFC-004 — The scenario library: wealthlens-sim as the public reference for wealth-tax arithmetic

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07). Explicitly deferred past
the July launch bundle ("the simulator gets nothing new this month",
`strategy/course-correction-2026-07.md` S3); this RFC is the plan for when
that freeze lifts. Twelve-month-bet candidate #1.
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)
Annex: problem B (uncertainty grammar) is the output contract.

## Problem and who it serves

The public debate question — "what would a wealth tax actually raise?" —
has no maintained, honest, public answer surface in the UK. The Wealth Tax
Commission's 2020 simulator is dead (TLS cert expired, 2020 data, verified
2026-07-02); PolicyEngine simulates income-tax-and-benefit flows, not the
wealth stock, with a structurally weak top tail; IFS/RF publish PDFs.
Meanwhile WealthLens sits on a 853-test open microsimulation engine with
seven policy families, interval arithmetic, Monte-Carlo sampling already
wired into `simulate()`, Sobol sensitivity, and a provenance manifest on
every number — surfaced to the public as a two-item dropdown that cannot
answer the canonical scenario (1% above £2m). Six of twelve council
personas — spanning a pensioner, a sixth-former, a journalist, an
economist, a think-tanker, and a campaigner — independently named that
identical missing scenario: the strongest single-feature signal in the
council. The engine's own README still claims "pre-alpha skeleton" against
853 passing tests.

Who it serves: journalists and researchers (sanity-check arithmetic with
visible uncertainty), campaigners AND sceptics (the same neutral tool
stress-tests inflated claims and dismissive ones), teachers and students,
and any regular reader who wants "so what would it raise?" answered with a
band instead of a headline.

## Value hypothesis

- **Evidence (council):** six-persona convergence on one concrete gap;
  the think-tanker would use it "2-3 times a quarter for pre-meeting
  sanity checks"; the economist would benchmark it against WTC 2020 and
  set it as a problem-set exercise.
- **Evidence (landscape):** the WTC simulator proved public appetite and
  then died of unmaintenance — even a modest maintained version wins by
  default; the field is empty and both natural incumbents have declared
  their scope elsewhere.
- **Deflations to hold (critics):** nobody will cite it as *a costing* —
  correct, and the tool must keep saying so itself; the campaigner will
  quote WTC's own headline in public and use this privately — fine, use is
  use; institutional citation follows standing, which this earns slowly or
  never. The bet's 12-month value is being *the* reference arithmetic when
  the Autumn Budget 2026 debate spikes, not week-one traffic.
- **Hypothesis (marked):** a validation panel (our number vs published
  estimates, same assumptions where possible) converts expert scepticism
  into adoption. Grounded in the PolicyEngine precedent (they publish
  divergence-from-official-forecast tables and won HMT's trust), unproven
  for this project.

## MVP slice (≤1 week) vs full vision

**MVP (the week the freeze lifts):**
1. **Publish the canonical grid, statically.** Extend the existing
   generator (`automation/data-pipelines/generate_simulator_dashboards.py`)
   from 2 scenarios to a precomputed grid: thresholds {£500k, £1m, £2m,
   £5m, £10m} × rates {0.5%, 1%, 2%} for family A, plus the WTC comparator
   (1% over £2m) called out by name. ~15-20 JSON fixtures; the fixture
   pipeline and dashboard contract v1.3 already carry intervals, caveats,
   and provenance. Scenario expansion is "a dict entry and a regenerate"
   (verified in the surface review).
2. **Permalink + download + cite** on /simulator: scenario selection into
   the URL, a "download this scenario (JSON)" link (the files are already
   publicly fetchable — link them), and the RFC-001 cite component.
3. **Fix the engine README** (one line: it is not a pre-alpha skeleton).
4. **Retire-or-wire decision for the orphaned /tools/wealth-tax-simulator**
   (recommended: wire — below). Interim if wiring slips: retire from the
   build; two contradictory models must not both be reachable.

**Full vision:**
- **Monte-Carlo bands**: flip the generator to pass a `SamplingConfig` —
  the engine argument already exists; the JSON already carries
  `interval_method` to label the band honestly (Annex B vocabulary:
  "simulation band", not "sensitivity range").
- **"What drives this number"**: one Sobol-derived sentence per scenario
  ("most of this range comes from the top-tail assumption") — the lay
  legibility of the most research-grade thing the engine does; no UK tool
  has it.
- **Wire the slider UI to the grid**: the orphaned 738-line interactive
  tool becomes the front-end for the precomputed grid — sliders snap to
  the nearest gridpoint, every displayed number is an engine number with a
  band. Interactivity married to honesty; the two-models-disagree risk
  dies.
- **Validation panel**: a table row per published estimate (WTC 2020
  central estimates; subsequent IFS commentary) against the WealthLens
  band under matched assumptions, differences explained, sources cited.
  Comparison, never calibration-by-eye.
- **Behavioural attenuation as a second labelled band** ("mechanical" vs
  "after estimated responses") — ONLY when the cited base-share data
  arrives (the behavioural module is complete but engine-apply is blocked
  on exactly that; a standing Chris question since session 3). Until then
  the absence stays explicit: "upper bound; behavioural responses not
  modelled".
- **Other families**: one-off levy (family B, instalments) next — it is
  the WTC's other headline design; CGT/property scenarios timed to their
  news moments; IHT stays withheld until Tier B calibration per
  `docs/IHT_CALIBRATION.md` (the refusal is itself trust collateral).
- **"State of the debate" page** for Budget season: the grid, the
  validation table, and the honest caveats on one URL (pairs with the
  moments strategy in the frontier index).

## Architecture sketch

All compute stays offline/build-time; the site stays static.

- Generator loop over a SCENARIOS grid → `data/simulator/*.json` →
  existing static mirror. Grid of ~20-60 fixtures at a few KB each:
  trivial hosting.
- Monte-Carlo cost is paid in CI, not runtime. Open question below on
  population size; generation can move to the weekly workflow (regenerate
  on engine or assumption change, not every deploy) if deploy time
  suffers.
- /simulator gains URL state + a grid-navigator (two selects or the wired
  sliders); ConfidenceFanChart, RevenueBreakdown, ProvenancePanel are
  reused unchanged — they already render bands, caveats, and citations
  exemplarily (session-13 audit finding).

## Data sources

- The engine's own cited assumptions registry
  (`packages/wealthlens-sim/registries/assumptions.yml` + provenance
  manifest system) — every published number already carries source URL +
  access date.
- Wealth Tax Commission final report + evidence papers (wealthandpolicy.com,
  free) — anchors and the validation comparators. Advani, Chamberlain,
  Summers (2020) for the canonical 1%/£2m estimates.
- ONS WAS (OGL v3) via the existing synthetic-population calibration.
- Honest feasibility notes: the synthetic population is GB-only (no NI) and
  2,000 households at seed 20 in published payloads — small for tail-driven
  estimates; both facts are disclosed in-payload today and must remain so.

## Cost envelope

£0 marginal hosting (static JSON). CI minutes for grid regeneration
(bounded; free tier absorbs it at this scale). No LLM spend.

## Honesty / misreading / abuse risks and mitigations

- **"Not a costing" must survive virality.** The label lives in the
  payload caveats and the fan chart; under Annex B it must also live in
  every exported/shared artefact (range + label baked into the image).
- **Rebuttal-factory drift** (mission-guardian critique): the tool's copy
  frames it as scenario arithmetic for anyone — a sceptic stress-testing
  an inflated claim is as much the audience as a campaigner rebutting
  "it would raise nothing". No campaign framing in product copy, ever.
- **Spending equivalences**: if kept, multiple neutral yardsticks (per the
  critics), not a single emotive one.
- **Grid granularity invites over-reading** ("exactly £X bn at 1.25%"):
  gridpoints only, ranges always, interpolation between gridpoints refused
  in the UI (sliders snap).
- **Behavioural absence** is the biggest expert objection; it stays an
  explicit label until it can be a cited band — never an invented
  elasticity (no-fabrication guardrail; the critics killed any "central
  estimate she can say on air" shortcut).

## Open challenges, with candidate solutions

1. **Tail noise at 2,000 households** for £5m/£10m thresholds: candidate —
   raise build-time population (e.g. 20k households) for grid generation
   and/or average over seeds; profile CI cost first; disclose population
   size in-payload either way. If £10m-threshold estimates stay
   seed-unstable, publish that threshold as "indicative only" or drop it —
   instability disclosed beats stability faked.
2. **Monte-Carlo band width communication**: Annex B grammar; the
   `interval_method` badge distinguishes it from today's alpha-sweep
   sensitivity range so the two never masquerade as each other.
3. **Slider-to-grid UX** (users expect continuity): snap with visible
   gridpoint ticks; show neighbouring gridpoints' bands so movement feels
   informative, not broken.
4. **Validation-panel assumption matching**: WTC's estimates embed
   different valuation/coverage assumptions; candidate — a per-row "what
   differs" footnote written once, reviewed by the 2-lens gate; where
   assumptions can't be matched, say "not directly comparable" rather than
   forcing a row.

## Definition of shipped (visible artifact)

The WTC-comparator scenario (1% over £2m) is live on /simulator with a
Monte-Carlo band, a permalink, a JSON download, a citation string, and a
validation row against the WTC's published estimate — and either the
slider tool drives the grid or it no longer exists. A journalist can link
"what would 1% over £2m raise" and get an honest band with receipts.

## Seeded tasks (half-day granularity)

- [ ] RFC-004a: grid the generator (family A thresholds × rates + WTC
  comparator); regenerate fixtures; scenario URL state on /simulator (@agent)
- [ ] RFC-004b: download-JSON + cite affordances on /simulator; engine
  README truth fix (@agent)
- [ ] RFC-004c: SamplingConfig flip → Monte-Carlo bands + interval_method
  badge copy (Annex B vocabulary) (@agent)
- [ ] RFC-004d: profile + raise build-time population for grid generation;
  seed-stability check on top thresholds; disclose in payloads (@agent)
- [ ] RFC-004e: wire /tools/wealth-tax-simulator sliders to the grid
  (snap-to-gridpoint) OR retire it; kill the second model either way (@agent)
- [ ] RFC-004f: validation panel v1 (WTC rows, "what differs" footnotes,
  2-lens review) (@agent)
- [ ] RFC-004g: Sobol "what drives this number" sentence per scenario (@agent)
- [ ] RFC-004h: one-off-levy (family B) scenario set with instalment
  framing (@agent)

## Dependencies and what it must NOT break

- Blocked until the July course-correction's simulator freeze lifts
  (Analyst URL + launch bundle first). Behavioural band blocked on cited
  base-share data (standing Chris question).
- Must not break: dashboard contract v1.3 consumers, the IHT withholding
  (stays withheld pending Tier B calibration), golden fixtures discipline,
  the "illustrative synthetic population" disclosure, engine test suite.
- Must not: publish interpolated non-gridpoint numbers, invent behavioural
  elasticities, or let the interactive tool show any number the engine did
  not produce.
