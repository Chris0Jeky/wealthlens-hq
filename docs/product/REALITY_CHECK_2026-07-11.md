# Product Reality Check — 2026-07-11

Last updated: 2026-07-11

A one-session deep audit of the public dashboard **as a visitor actually
experiences it**: the live GitHub Pages site was driven in a real browser,
the deployed JS bundle was decompiled and compared against source, deep links
and third-party endpoints were probed over HTTP, and every claim below is
traced to a file/line or a live observation. Companion to
`PRODUCT_FRONTIER_2026-07.md` (which scored what to build next); this doc
checks what is actually true today.

## Verdict

**The content layer is strong. The delivery layer defeats it.**

The chart pages are genuinely excellent — broadsheet-style articles with
cited, access-dated, interactive charts, honest caveats, stat strips, and
related-chart trails (`/charts/wealth-shares` is the reference example). The
simulator is honest and well-sourced. "1 pixel = £1,000" (`/tools/wealth-scale`)
is the most shareable artefact the project owns.

But the front door hides all of it. Until PR #498, **no home-page card
linked to any chart** (all 10 said "Chart coming soon"). Every card badges
**"Expired"**. The newsletter form has been discarding every subscriber. The
sharing toolbar is dead buttons. Chart pages return HTTP 404 to crawlers. The
four interactive tools have zero inbound links. The July council verdict
("wire what exists before building anything new") was correct and remains
**unexecuted** — sessions since then went to the Analyst and harness work
(legitimately), but nothing on this list moved.

The "not exciting" feeling is not a content problem. It is a wiring,
landing-page, and sharing problem — and most of it is half-day fixes.

## Findings

Severity reflects user-facing impact on the live site today.

### F1 — CRITICAL (fixed: PR #498). Home "View Chart" links never rendered

Vue casts an absent Boolean prop to `false`, not `undefined`, so
`DatasetCard.vue`'s `hasChart !== undefined` override always won and every
home card rendered "Chart coming soon" — while the stat tile above claimed
"10 Interactive Charts". Confirmed in the deployed bundle
(`HomeView-DVNZS7__.js`) and reproduced in vitest; regression test proven to
fail pre-fix. The home page's primary path into the product was dead in
every environment. Why no test caught it: all "shows chart link" unit tests
passed `hasChart: true` explicitly; view tests mock DatasetCard; e2e only
deep-links (see F12).

### F2 — CRITICAL (Chris decision, ACTION-REQUIRED #11). Newsletter posts into the void

`NewsletterSignup.vue` posts to
`https://buttondown.com/api/emails/embed-subscribe/wealthlens`; no
`VITE_BUTTONDOWN_NEWSLETTER_ID` is set in `deploy.yml`, and
`buttondown.com/wealthlens` returns **404 — the list does not exist**. Every
"Stay informed" submission since launch has failed with "Subscription failed
(HTTP 404). Please try again later." (which is false — later won't help).
Either create the Buttondown list (5 min, needs Chris's email) or hide the
form until then (agent-doable).

### F3 — HIGH. Every dataset badges "Expired" on the landing page

`stores/data.ts` grades freshness on a fixed wall-clock ladder
(fresh/stale/expired), but the underlying sources update annually or
biennially — WID data that is fully current still badges "Expired" after 30
days. With the weekly refresh cron red since June and being disabled
(PR #495), the wall of red "Expired" badges is now **permanent**. The honest
cadence data already exists (`constants/datasetProvenance.ts`,
`registries/sources.yml` `update_pattern`): grade age against each source's
own cadence, or replace the badge with a neutral "Data as of {date}".

### F4 — HIGH. Fabricated freshness claim in the masthead

`AppHeader.vue:34` renders `new Date()` as "LIVE · UPDATED 11 JUL 2026" —
the visitor's clock, not any data event — directly above ten "Expired"
badges. On a project whose first value is data honesty, the masthead
fabricates recency. Replace with the build-time data vintage (max
`last_updated` across datasets) or drop "UPDATED".

### F5 — HIGH. The site is invisible to crawlers and social scrapers (one class, several symptoms)

- Deep links (`/charts/*`, `/simulator`, `/tools/*`) are served via the
  GitHub Pages `404.html` SPA fallback → they render for humans but return
  **HTTP status 404** — search engines treat every chart page as "not found",
  and `sitemap.xml` points crawlers at those 404s.
- The no-JS shell is empty: crawlers, link-preview bots, and LLM scrapers see
  a title and nothing else (verified by plain fetch).
- In the baked `index.html`, `og:image` is a **relative path** (scrapers
  require absolute URLs — landing-page previews are broken everywhere) and
  `og:url` claims `https://wealthlens.uk/` — a domain that is **not yet
  registered** (ACTION-REQUIRED #4; until then the site literally advertises
  a URL someone else could own).
- The 12 per-chart OG images in `public/og/` are applied client-side only
  (`usePageMeta`) — no crawler has ever seen them.

Fix class, one move: **prerender the ~20 routes at build time** (e.g.
vite-ssg/prerender), which yields real HTML files (HTTP 200), per-route meta
in the payload, and content in the no-JS shell. Interim one-liners: absolute
`og:image`, real `og:url`.

### F6 — HIGH. The most engaging features are orphaned

Zero inbound links anywhere (nav, home, footer) to:
`/tools/wealth-scale` ("1 pixel = £1,000"), `/tools/wealth-calculator`,
`/tools/wealth-tax-simulator`, `/tools/tax-calculator`, `/faq`. The
wealth-scale breadcrumb even references a `/tools` index that doesn't exist
as a route (404). Additionally `wage-stagnation` and `inheritance-tax` have
chart pages but no home card, and the footer's "All charts" links to a
single chart — there is no chart index page at all.

### F7 — MEDIUM. Dead sharing toolbar beside working machinery

`ShareBar.vue` renders 8 buttons (Copy link, Embed, PNG, SVG, CSV, Bluesky,
LinkedIn, X) with **no click handlers** on every flagship chart page, while
working capability sits adjacent: `SharePanel` (via the "Share & Embed"
toggle) and `ExportButton`/`useChartExport`. For a mission of "impossible to
ignore", the share buttons doing nothing is the single most on-mission gap.
Wire them to the existing machinery or remove them.

### F8 — MEDIUM. 10 broken CSV links on the home page + a false Methodology claim

`DatasetCard` links every card to `/api/data/{name}/download` — a backend
that doesn't exist on the static deploy (and the URL isn't even under the
site's base path). `MethodologyView.vue:366` tells readers "the API provides
CSV download endpoints". The static data layer that already deploys could
serve real CSVs (RFC-001 territory); until then the links misadvertise.

### F9 — MEDIUM. Every visitor's browser polls localhost

`HealthStatus.vue` polls `${VITE_API_BASE_URL ?? "http://localhost:8000"}/api/version`
on mount and every 60 s. On the live site that means every visitor fires
connection-refused errors at their own machine forever, and the footer shows
a red **"API offline"** badge to the public. Should be disabled (or repointed
at a static build-stamp JSON) when `VITE_STATIC_DATA` is set.

### F10 — LOW. Small false or drifting claims

- Home stat tile: "Weekly — automated pipelines refresh data regularly" —
  not true once the weekly cron is disabled (PR #495).
- Chart page chip "Data: 1 month ago" alongside "UPDATED 14 MAY 2026"
  (~2 months at audit time) — check the age arithmetic/copy.
- Masthead lists "ENGLAND · WALES · SCOTLAND · NI" while several core
  datasets (WAS-based, simulator population) are GB-only.

### F11 — LOW. `Accordion.defaultOpen` is declared but never read

(Reviewer finding from PR #498's round.) Same silent-Boolean-prop family as
F1; no current consumer passes it, but the first one to do so gets a
silently-closed panel. `Accordion.vue:6,11`.

### F12 — LOW. The test pyramid has a hole exactly where F1 lived

View tests mock `DatasetCard`; the single e2e spec deep-links to a chart and
never asserts any home-page affordance. Seed: one e2e smoke — "home page
shows ≥ 1 'View Chart' link and it navigates".

## Process observations (not code)

- **17 open PRs** at audit time: extraction #491, harness stack #492–#497,
  10 Dependabot bumps (2026-07-06/07) — the merge train has been stalled ~5
  days. Nothing here changes the product, but #491 gates the repo's declared
  state ("analyst extracted") from being true on main.
- **Direction check:** the strategy docs' diagnosis (course-correction:
  launch bundle first; frontier council: "wire what exists") is *correct* and
  this audit independently reconfirms it. The drift is execution: since
  2026-07-02, sessions shipped Analyst milestones and repo infrastructure —
  valuable — but zero launch-bundle or wiring items. AR #2 (LinkedIn post),
  #3 (outreach), #4 (domain) remain the highest-leverage unblocks and are
  Chris-only.

## Easy wins (each ≤ half-day, ordered by value)

1. ~~Home "View Chart" links~~ — **PR #498** (done, pending CI + merge).
2. **Wire the orphans**: nav/footer/home links to the 4 tools + FAQ; add the
   2 missing charts to the home grid (or ship a small `/charts` index and a
   `/tools` index page).
3. **OG one-liners**: absolute `og:image`; `og:url` → the real Pages URL
   until the domain exists.
4. **Static-aware HealthStatus**: no localhost polling, no "API offline"
   badge on the public site.
5. **Masthead honesty**: data vintage instead of `new Date()`.
6. **Cadence-aware freshness** (or "Data as of {date}") — kills the Expired
   wall using provenance data that already exists.
7. **CSV links** → the static data layer (or hide until real).
8. **Wire ShareBar** to `useChartExport`/`SharePanel`/share-intent URLs — or
   delete the dead buttons.
9. **E2E home smoke test** (locks F1's class shut).
10. **Buttondown** — create the list or hide the form (AR #11; the create
    half is Chris-only).

Bigger, still high-value (seeded, not "easy"): route prerendering (F5's
class fix); a front-page redesign that leads with the 57 % headline, one
featured chart, and a tools row — the home page is currently an index, not a
story, and that is most of the "excitement" gap. (RFC-001's reuse layer
remains the right first *new* build — nothing in this audit displaces it.)

## What was verified / not verified

- **Verified live:** rendered home, chart, simulator, and wealth-scale pages
  (Playwright, screenshots); HTTP 404 status on deep links; empty no-JS
  shell; `buttondown.com/wealthlens` → 404; localhost poll + console errors;
  deployed `HomeView` chunk exhibits the F1 branch; baked OG tags.
- **Verified in code:** every file/line reference above; F1 root cause
  reproduced and mutation-verified in vitest (PR #498).
- **NOT verified:** mobile rendering (desktop viewport only); WCAG audit
  beyond what earlier sessions covered; the two calculators and
  wealth-tax-simulator tools were not driven end-to-end (only reachability
  was checked); Lighthouse/e2e suites not run locally (CI runs them on
  PR #498).

## Seeds

Task seeds: `tasks/inbox.md` § "2026-07-11 reality-check seeds".
Chris item: `tasks/ACTION-REQUIRED.md` #11 (Buttondown decision).
