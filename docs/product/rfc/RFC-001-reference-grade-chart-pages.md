# RFC-001 — Reference-grade chart pages (the reuse layer)

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07). Not scheduled; competes
for post-launch-bundle capacity per `strategy/course-correction-2026-07.md`.
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)

## Problem and who it serves

The 12 chart pages are read-only dead ends. Verified 2026-07-02: no CSV or
data download exists on any chart page (the one advertised CSV link 404s on
the static deploy); the ShareBar rendered on all 7 flagship pages is a
documented non-functional placeholder; the "embed" iframes the entire
article page including site chrome; social-link previews always show the
generic landing card because per-chart OG tags are set client-side and
crawlers never execute them (the 12 bespoke OG images exist, unseen);
time-range buttons toggle but do nothing; the freshness badge marks
perfectly-current annual data red past 30 days; there is no "cite this"
affordance despite every ingredient (chart ID, source, licence, access
date) being on screen; two chart pages and all four /tools pages are
orphaned from every navigation surface; there is no charts index.

Who it serves: journalists (embed/download/cite on deadline), researchers
and think-tankers (extractable series), teachers and students (citable
images + tables), campaigners (working share plumbing), and — indirectly —
every regular person whose pasted link currently unfurls as a grey card.

## Value hypothesis

- **Evidence (audience council, 2026-07-02, 12 personas + 3 adversarial
  critics):** every persona's realistic behaviour is harvest-and-leave —
  extract one artefact (screenshot, PNG, sentence, citation) and go. All 12
  hit at least one dead control; the sceptical personas' trust visibly
  dropped at the same four defects (dead buttons, 404 CSV, fake embed,
  false stale badge). The critics' unanimous survivor: "fix or remove every
  dead control" and "surface the data layer" are the only interventions
  immune to attention-economics attack because they require zero behaviour
  change from anyone.
- **Evidence (landscape):** OWID's default-citation status is mechanically
  produced by exactly this layer (chart URL also serves .csv/.metadata
  /.png; copy-paste citation; one-line licence). UK incumbents lack it and
  their artefacts rot (IFS: no embeds, 403s scripts; RF: dashboard loads a
  2019 CSV that 404s; WTC: expired TLS cert).
- **Hypothesis (marked):** fixing OG previews increases second-hop
  click-through on shares. High-confidence direction, unmeasurable until
  analytics exist (ACTION-REQUIRED #4).

## MVP slice (≤1 week) vs full vision

**MVP (one week of half-days):**
1. "Download data" on every chart page: link the existing static
   `/data/{slug}.json` + a build-time CSV mirror. Zero new data plumbing.
2. "Cite this" popover: short + long citation strings generated from
   `chartArticles.ts` + `datasetProvenance.ts` (chart ID, source, licence,
   access date), crediting BOTH WealthLens and the upstream source (OWID
   pattern).
3. Kill-or-ship pass: remove the placeholder ShareBar and the inert
   time-range buttons (removal is shipping); fix the freshness badge to be
   cadence-aware ("current for an annual series") using
   `datasetProvenance.ts` update patterns.
4. De-orphan: nav + homepage + footer links to /tools/*; a /charts index
   page listing all 12; add wage-stagnation + inheritance-tax to sitemap,
   homepage grid, and related-charts graph.
5. OG activation: build-time script writes 12 static HTML shells with
   correct meta tags pointing at the existing `public/og/{slug}.png`.

**Full vision:** chart-only embed route (no site chrome) with a no-cookies
pledge in the snippet; dated permalinks for citers (see RFC-002 and Annex
problem C); plain-English one-liner atop every chart; the 5 bare pages
promoted to full broadsheet pages (pure content work — the config layout is
already built); per-chart "reuse rights" line, including an explicit
CC BY-NC-ND warning on generational-wealth; levels-£/shares-% toggle where
applicable (Fed DFA pattern).

## Architecture sketch (respects current stack)

Everything is build-time static; no backend, no runtime cost.

- CSV mirrors: extend `scripts/generate_static_api.py` to also emit
  `{slug}.csv` next to the JSON it already writes.
- OG shells: a deploy step (Node or Python) that writes
  `dist/charts/{slug}/index.html` containing the correct
  og:title/og:image/og:url meta + a JS bootstrap of the SPA. Must coexist
  with the SPA 404 fallback — verify GH Pages serves directory index.html
  before the 404 fallback (it does; document the check).
- Cite-this: pure frontend component consuming existing config; no new
  source of truth (guardrail: do NOT add a 7th provenance copy — read from
  `datasetProvenance.ts`).
- Embed route: `/embed/{slug}` rendering only the chart + source line +
  backlink, `robots noindex`, no analytics, sandbox-friendly. Alternative
  zero-code interim: repurpose the 10 already-deployed standalone Plotly
  pages under `/charts/*.html` as embed targets (they are self-contained
  and dependency-free) — but reconcile their numbers with the SPA charts
  first (two renderers = drift risk).

## Data sources

No new data. The existing 12 registry-reconciled datasets
(`registries/sources.yml`, `frontend/src/constants/datasetProvenance.ts`).
All OGL v3 / CC-BY except: generational-wealth (Resolution Foundation,
CC BY-NC-ND 4.0 — output-licence decision pending, ACTION-REQUIRED #10;
until decided, its download/embed affordances must carry the ND notice and
the cite string must state the source licence).

## Cost envelope

£0 marginal hosting (static). No LLM spend. Build time +seconds.

## Honesty / misreading / abuse risks and mitigations

- **tax-composition is an illustrative composite** (disclosed only in a
  collapsed accordion today). If it becomes downloadable/embeddable, the
  caveat must travel IN the artefact: a `data_type` column in the CSV, a
  caveat line in the embed footer. Same for every `illustrative_fallback`
  dataset.
- **NC-ND source** (above): the reuse layer must not invite licence
  violations on that one chart; per-chart reuse-rights line is the
  mitigation, not a global "free to reuse" claim.
- **Cite-this laundering:** professionals will still cite ONS/HMRC — by
  design. The cite string names WealthLens as processor and the upstream as
  source, which serves the mission (data visibility) either way.
- **Embed abuse** (framing charts in misleading contexts): the embed
  carries its own title, source line, and backlink; that is the practical
  ceiling of control and matches OWID's posture.

## Open challenges, with candidate solutions

1. **SPA prerender vs GH Pages routing.** Candidate: directory-index shells
   (above). Fallback: switch chart routes to hash-free paths already used;
   worst case, per-chart static "share pages" at `/s/{slug}` used only as
   the og:url target. Half-day spike task seeded below.
2. **Canonical identity split** (index.html claims wealthlens.uk; app
   generates github.io URLs; watermark prints wealthlens.uk). Until the
   domain exists (ACTION-REQUIRED #4), standardise everything on the
   github.io URL — a wrong-but-consistent canonical beats three identities.
   One config constant; seeded.
3. **Two renderers drift** (SPA ECharts vs standalone Plotly HTML). If the
   Plotly pages become embed targets, add a drift-lock test comparing both
   against the same `/data/{slug}.json`; else retire them from the deploy.

## Definition of shipped (visible artifact)

On any chart page a visitor can: download the plotted data (CSV/JSON), copy
a two-line citation, copy a chart-only embed snippet that renders without
site chrome, and paste the page URL into WhatsApp/LinkedIn and see the
chart image unfurl. Plus: a /charts index exists, every page is reachable
by navigation, and no control on any page does nothing.

## Seeded tasks (half-day granularity)

- [ ] RFC-001a: emit `{slug}.csv` from `generate_static_api.py` + "Download
  data" buttons on ChartView (both layouts) (@agent)
- [ ] RFC-001b: Cite-this component (short/long strings from existing
  config; credits upstream + WealthLens) on all 12 pages (@agent)
- [ ] RFC-001c: remove placeholder ShareBar + inert time-range buttons;
  cadence-aware freshness badge from datasetProvenance (@agent)
- [ ] RFC-001d: /charts index page + nav/homepage/footer links to /tools/*
  + sitemap/homepage/related-charts for the 2 orphaned charts (@agent)
- [ ] RFC-001e: spike + implement OG static shells at deploy (verify GH
  Pages directory-index precedence; then wire the 12 shells) (@agent)
- [ ] RFC-001f: chart-only /embed/{slug} route with no-cookies pledge +
  per-chart reuse-rights line (NC-ND handled) (@agent)
- [ ] RFC-001g: plain-English one-liners (12) + promote the 5 bare pages to
  broadsheet layout (content; 2-lens factual review) (@agent)
- [ ] RFC-001h: canonical-URL consolidation to one identity until the
  domain decision (@agent)

## Dependencies and what it must NOT break

- Depends on: nothing external. Domain (AR #4) improves canonical story but
  is not a blocker. Analytics (AR #4) needed to measure, not to ship.
- Must not break: existing chart URLs (they are the citable asset), WCAG AA
  and the AccessibleDataTable fallbacks, the deploy pipeline's data
  regeneration, the Lighthouse CI gates. Must not add tracking anywhere,
  especially not in embeds. Must not create a new provenance copy — read
  from the existing single sources of truth.
