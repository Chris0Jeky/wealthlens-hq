# RFC-006 — Wealth, where you live: honest local pages

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07).
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)
Annex: problem A (sub-national statistics without ecological fallacy) IS
this RFC's design law; read it first.

## Problem and who it serves

"Is it like this where I live?" was the most repeated unmet need across
the audience council's regular people (the Bradford renter, the Welsh
councillor) — and the most dangerous to serve, because household wealth is
not measured below region in the UK. The adjacent-field scan shows why it
matters anyway: every dataset that became UK public infrastructure did it
with stable per-area pages (OpenPrescribing per practice, TheyWorkForYou
per MP, police.uk per neighbourhood) — and none of them touch wealth.

Who it serves: regular people (locality doubles the share-probability of a
first visit, per the council), local councillors (copy-ready cited
sentences for committee papers — the councillor persona converts from
zero to monthly on exactly this), local journalists (a per-area page is a
localised story in minutes), and teachers (local numbers hold a classroom
better than national ones).

## Value hypothesis

- **Evidence (council):** the councillor's return trigger was verbatim
  this feature; the renter's "your area" wish roughly doubles first-visit
  share odds by her own honesty check.
- **Evidence (landscape):** per-area permalinks are the common mechanism
  of every civic-data product that achieved reference status; the wealth
  column of that table is empty.
- **Critic corrections (all incorporated):** LA-level *wealth* figures
  would be ecological fallacy or fabrication — the honest product is
  component-resolution honesty (Annex A granularity ladder); and a generic
  local-deprivation dashboard is mission drift into occupied territory
  (LG Inform, Commons Library, End Child Poverty) — the differentiator
  must stay wealth-composition-adjacent (housing wealth, tenure, the
  measurement gap itself).
- **Hypothesis (marked):** "what nobody measures about your area" is
  itself shareable/citable content. Novel; untested; cheap to test.

## MVP slice (≤1 week) vs full vision

**MVP — one page, not a page-per-area:** "Wealth around you" at a single
URL: pick a local authority (client-side selector over a static JSON),
see the granularity ladder rendered honestly:
- Tier 1 (measured here): housing affordability ratio (existing pipeline),
  median house price + 5-year change (UK HPI), tenure mix — owned
  outright / mortgaged / rented (Census 2021), median pay (ASHE), child
  poverty (existing pipeline).
- Tier 3 (region only): total/pension/financial wealth for the containing
  region with its interval, visually distinct, with the sentence "No
  source measures this for [area] — see why", linking the measurement-gap
  explainer.
- A "copy sentence with citation" button per stat (the councillor's
  actual workflow; descriptive sentence templates only, per the
  mission-guardian critique).

**Full vision:** static per-area permalink pages (`/area/{la-slug}`,
~350 pages generated at build — trivially static), postcode → LA lookup
via postcodes.io (MIT-licensed API; or its open dataset bundled at build
to avoid a runtime dependency), region wealth-composition panels (WAS
ITL1: property vs pension vs financial vs physical — the composition
story IS available regionally and nobody shows it), the measurement-gap
explainer as a standalone citable page, and per-area OG cards.

## Architecture sketch

A new pipeline script per source (HPI by LA, Census tenure by LA, ASHE by
LA) following the existing fetch→validate→static-JSON pattern; one
`areas.json` index; the page is a static Vue view over those files. Per-
area pages, when they come, are build-time generated shells (same
mechanism as RFC-001e OG shells). No backend, no geolocation, no PII —
area selection is explicit, never inferred.

## Data sources

- UK House Price Index by LA (Land Registry): gov.uk/government/
  statistical-data-sets/uk-house-price-index — OGL v3; monthly CSV;
  straightforward.
- Census 2021 tenure by LA (ONS, table TS054 or successor):
  ons.gov.uk/census — OGL v3; one-off static extract (census cadence).
- ASHE median gross pay by LA (ONS): OGL v3; annual XLSX; manageable.
- ONS housing affordability by LA — OGL v3; **already a WealthLens
  pipeline**.
- DWP/HMRC Children in Low Income Families by LA — OGL v3; **already a
  WealthLens pipeline**.
- WAS regional wealth + composition (ONS R8 bulletin tables) — OGL v3;
  same extraction as RFC-003a; carries the mandated accreditation caveat.
- postcodes.io (MIT) for postcode→LA, or its bundled open data at build.
- Honest feasibility notes: England-and-Wales vs GB vs UK coverage varies
  by source (HPI is UK; affordability is E&W; WAS is GB) — every page
  states its coverage per stat; Scotland/NI gaps are labelled, not
  papered over.

## Cost envelope

£0 marginal (static). Pipeline runtime minutes. postcodes.io free (or
zero-dependency bundled data).

## Honesty / misreading / abuse risks and mitigations

All of Annex A, plus:
- **Area stigma** ("poorest town in Britain" league-table journalism):
  no rankings UI; pages present an area's own trajectory + region/national
  comparators, not a sortable league table. (Rankings are the genre most
  likely to travel AND most likely to flatten caveats.)
- **Individual inference**: sentence templates speak of distributions
  ("half of homes..."), never residents.
- **Mission drift into generic local stats**: the page's spine is wealth
  composition and the measurement gap; deprivation/poverty appear as
  context, not as the product. If a stat has a better home elsewhere
  (Commons Library dashboards), link out rather than absorb.

## Open challenges, with candidate solutions

1. **LA boundary churn** (mergers, new unitaries): pin to a named
   boundary vintage (ONS GSS codes + year) in areas.json; regenerate on
   boundary changes; state the vintage on-page.
2. **Coverage patchwork** (E&W/GB/UK per source): per-stat coverage badge,
   same component pattern as the granularity badge — one honesty UI
   element, two jobs.
3. **350 pages of thin content risk** (SEO and dignity): start with the
   single selector page (MVP); generate per-area permalinks only when
   each page has ≥5 real local stats + the gap section — a threshold, not
   a date.

## Definition of shipped (visible artifact)

A visitor picks (or types a postcode resolving to) their local authority
and gets: real local housing/tenure/pay/poverty figures each with source +
coverage badge, the regional wealth figure honestly labelled as regional,
one copy-ready cited sentence per stat, and a link to "why nobody can
measure your town's wealth". A councillor can prep a committee paper from
it in five minutes.

## Seeded tasks (half-day granularity)

- [ ] RFC-006a: pipelines for HPI-by-LA + Census tenure-by-LA (fetch,
  validate, static JSON + sidecars) (@agent)
- [ ] RFC-006b: ASHE-by-LA pipeline + areas.json index with GSS codes +
  boundary vintage (@agent)
- [ ] RFC-006c: "Wealth around you" selector page rendering the
  granularity ladder + coverage badges (@agent)
- [ ] RFC-006d: copy-sentence-with-citation component (descriptive
  templates, 2-lens reviewed) (@agent)
- [ ] RFC-006e: measurement-gap explainer page (from was-caveats.md
  material; pairs with RFC-007) (@agent)
- [ ] RFC-006f: WAS regional composition panel (property/pension/
  financial/physical by ITL1) (@agent)

## Dependencies and what it must NOT break

- Independent of the Analyst path. RFC-003a's WAS extraction is shared.
- Must not break: the data-honesty validation gate (new pipelines adopt
  it), WCAG AA, the non-partisan sentence bar.
- Must not: publish any sub-regional wealth estimate, build a rankings
  table, or infer location without explicit user input.
