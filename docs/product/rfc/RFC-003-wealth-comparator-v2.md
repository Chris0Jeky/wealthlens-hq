# RFC-003 — "Where do you fit?" v2: the UK wealth comparator

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07).
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)
Annex: problem B (uncertainty grammar) governs the output design.

## Problem and who it serves

Nobody in the UK can find out where they sit in the wealth distribution.
The IFS "Where do you fit in?" covers income only; the ONS "How do you
compare?" calculator has been frozen since March 2022 on 2018-20 data
(verified 2026-07-02); no incumbent offers wealth. WealthLens has already
built the missing tool — cited, tested, accessible — and then hidden it:
all four /tools/* routes are orphaned (zero links from nav, homepage, or
footer, verified), it runs on WAS Round 7 (2018-2020) boundaries although
Round 8 (2020-22, published 2025-01-24) exists, it demands one pre-summed
"total household wealth" number most people cannot produce (nobody knows
their pension's capital value), percentile output caps at "top 1%", and
there is no shareable result (no URL state, no result image, no OG card).

Who it serves: regular people first — the renter, the nurse, the graduate,
the pensioner in the audience council all named personal legibility as
their hook ("it converts the site's data into a fact about ME"). Secondary:
teachers (a projector set-piece), and academics (one council economist
would use it in an undergraduate lecture — ONS's own comparator being
frozen was his stated reason).

## Value hypothesis

- **Evidence (council):** cross-class demand from four regular-person
  personas plus two experts, each independently. The strongest single
  quote: "the two assets built closest to her language are the two things
  no navigation reaches."
- **Evidence (landscape):** the personal-anchor pattern is proven (OECD
  Compare Your Income, IFS income tool surviving since the 2000s, WID's
  income comparator; the registry itself benchmarks against OECD and notes
  the gap).
- **Deflations to hold (critics, all three):** usage shape is **once plus
  one share**, not retention — design and measure accordingly. Quiz
  virality claims are survivorship bias (ONS ran a comparator for years
  with no viral loop); the cold-start problem is real (~5 views/fortnight
  today); wealth-result valence cuts both ways (people don't post "I'm in
  the bottom 30%" and posting "top 20%" is boasting) — so the shareable
  artefact should support *findings about the distribution* ("the median
  is lower than you think") as well as *findings about me*.
- **Hypothesis (marked):** a result card that leads with a distribution
  fact rather than a personal rank shares better and dodges the valence
  trap. Cheap to A/B once analytics exist.

## MVP slice (≤1 week) vs full vision

**MVP:**
1. De-orphan (ships with RFC-001d; listed here as the dependency).
2. **Round 8 refresh** with an explicit what-changed note (pension
   methodology break, accreditation suspension) — the repo already holds
   drafted Round 8 caveat text (`research/methodology/was-caveats.md`) and
   candidate thresholds (`research/raw/Combined/...Combined_Research_
   Report.md`); re-verify every boundary against the ONS R8 tables at
   implementation (data-integrity guardrail).
3. **Forgiving inputs**: keep the single-number expert path, add a guided
   path — own or rent? rough property value + mortgage left? savings band?
   pension: "I know my pot" / "I have a workplace/DB pension" / "no idea".
4. **Honest output = a range, not a point** (Annex B): "roughly the
   60th-70th percentile" with the vintage stamped ("based on 2020-22
   survey data — the latest that exists"). Integer-point precision on
   4-year-old data is false precision; ranges are both more honest and
   more defensible.
5. **URL state** so a result can be linked at all.

**Full vision:**
- **The pension problem, solved by twin positions, not valuation:** never
  capitalise a DB pension (the critics killed the "rough multiplier" —
  2-3x swings by scheme and age make it a fact-check waiting to happen).
  Instead show two positions from published WAS tables: "including pension
  wealth" and "excluding pension wealth". The user with an unvaluable
  pension sees an honest bracket; the tool teaches the single most
  misunderstood fact about UK wealth (pensions are ~40% of it) as a side
  effect.
- **Shareable result card**: client-side canvas → portrait PNG, carrying
  the range, the vintage, and the source line baked into the pixels (the
  artefact-carries-honesty law). No server, no PII — inputs never leave
  the browser (already true; keep saying so).
- **Age-band and region context** at published-table granularity only:
  "median for your age band" (GB, WAS age tables), "your region's median
  vs GB" (ITL1) — context lines, never a recomputed personal percentile
  ("for a 30-year-old in the North East" as a *comparison*, not a rank —
  WAS cannot support joint age×region×percentile honestly).
- Top-tail resolution ("top 0.5%/0.1%") only from published threshold
  sources with their own caveat (the WAS top-tail undercount note is
  already enforced site-wide); otherwise the cap stays at "top 1%".

## Architecture sketch

Pure client-side on the static site, as today: `utils/wealthPosition.ts`
holds the boundaries (single source of truth already consumed by the
scroller with a consistency test — refresh both together). New: a
`assets/decile-tables/` JSON emitted by a small pipeline script from the
ONS R8 workbook, so future rounds are a data refresh, not a code edit.
Result card via canvas/offscreen render of a dedicated component. URL
state via query params (no router changes needed).

## Data sources

- ONS Wealth and Assets Survey Round 8 (Apr 2020-Mar 2022), total wealth
  decile boundaries incl./excl. pension wealth, age-band and region medians:
  ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/
  incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022
  — OGL v3. Feasibility: tables ship as XLSX attached to the bulletin;
  one-off manual extraction with a recorded access date is fine (this is
  how R7 was done); caveats mandated by `research/methodology/was-caveats.md`
  (accreditation suspension, DB-pension series break, top-tail undercount).
- No other sources required for MVP. (Rich-List top-tail anchors stay in
  the scroller where they already live with their own sourcing.)

## Cost envelope

£0 marginal. No LLM. One-off data-extraction labour.

## Honesty / misreading / abuse risks and mitigations

- **False precision on stale data** → ranges + vintage on every output and
  baked into the share card. The card must be *unable to travel naked*.
- **DB pension valuation** → structurally avoided (twin positions).
- **Valence/shame dynamics** → neutral copy; the card template leads with
  a distribution fact; never grievance framing ("you have less than X" is
  shown plainly, never editorialised).
- **Household vs individual confusion** → the tool is household-based
  (WAS's unit); say so at input and on the card (the wealth-tax tool's
  per-taxpayer units were a real past bug — PR #461 — keep the lesson).
- **Classroom use exposes pupil disparities** (teacher persona's caution)
  → a "demo mode" with three preset example households, so a teacher never
  has to ask real students for real numbers.

## Open challenges, with candidate solutions

1. **R8 threshold verification**: the repo's R8 numbers are research notes,
   not pipeline outputs. Candidate: a tiny `fetch_was_deciles.py` in the
   pipelines dir emitting the JSON + metadata sidecar, so the numbers gain
   the same provenance discipline as every chart. (Half-day.)
2. **Percentile maths between deciles**: current linear interpolation is
   fine for mid-distribution; at the tails, switch output to bounded
   statements ("above the 90th percentile threshold of £X") instead of
   interpolated points — bounded claims are exactly what the tables
   license.
3. **Share-card rendering consistency across devices**: canvas text
   rendering varies; candidate: fixed-size offscreen render at 2x,
   downscale, test on the three big mobile browsers. Fallback: server-free
   SVG→PNG via existing satori dependency at build time for the STATIC
   preset cards, with only the numbers overlaid client-side.

## Definition of shipped (visible artifact)

The calculator is linked from the site nav; a person who knows only "own a
£250k house with £150k mortgage, some savings, a pension I can't value"
gets an honest percentile RANGE on 2020-22 data with the caveat visible;
the result has a URL; and a result card can be saved/shared carrying
range + vintage + source in the image. (Round 8 note published alongside.)

## Seeded tasks (half-day granularity)

- [ ] RFC-003a: fetch_was_deciles.py → R8 decile/age/region JSON + sidecar,
  verified against the ONS bulletin tables (@agent)
- [ ] RFC-003b: swap wealthPosition.ts to R8 via generated JSON; update
  scroller constants + drift-lock; what-changed note (@agent)
- [ ] RFC-003c: guided-input mode (own/rent, bands, pension three-way) →
  range output + vintage stamp (@agent)
- [ ] RFC-003d: twin positions incl./excl. pension wealth from R8 tables
  (@agent)
- [ ] RFC-003e: URL state + usePageMeta for the tools (@agent)
- [ ] RFC-003f: share-card component (canvas PNG, portrait, caveat baked
  in); demo mode presets for classrooms (@agent)

## Dependencies and what it must NOT break

- Depends on RFC-001d (de-orphan) shipping first or together.
- Must not break: the WealthScaleScroller consistency test, existing
  calculator unit tests (extend, don't rewrite), the no-data-leaves-the-
  browser property, WCAG AA.
- Must not: capitalise DB pensions, output integer percentiles as points,
  or ship any result artefact without vintage + source.
