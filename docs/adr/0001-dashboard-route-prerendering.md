# ADR 0001 — Dashboard route prerendering via post-build browser snapshot

Date: 2026-07-11
Status: ACCEPTED
Region: dashboard-frontend
Driver: `docs/product/REALITY_CHECK_2026-07-11.md` finding F5 — deep links
return HTTP 404 via the GitHub Pages SPA fallback, the no-JS shell is empty,
and per-route OG meta (including the 12 per-chart OG images) is applied
client-side only, so no crawler or link-preview scraper has ever seen it.

## Decision

Prerender every enumerable route at build time by **snapshotting the real
production bundle in a headless browser** (Playwright chromium driving the
Vite preview server), writing one static HTML file per route into `dist/`.
Do **not** adopt vite-ssg or any SSR-based generator.

Mechanics (implemented in `frontend/scripts/prerender.ts`):

1. `vite build` runs unchanged (VITE_STATIC_DATA=true, as on deploy).
2. The prerender script starts Vite's preview server programmatically,
   loads each route in headless chromium (service workers blocked, light
   colour scheme, reduced motion), waits for network idle plus the
   `usePageMeta` marker (`meta[data-wl-meta][property="og:url"]`), then
   serialises the full document.
3. Output is a **flat `.html` file per route** (`/faq` →
   `dist/faq.html`, `/charts/wealth-shares` →
   `dist/charts/wealth-shares.html`). GitHub Pages serves `/faq` from
   `faq.html` with **HTTP 200 and no redirect**, so every existing
   non-trailing-slash URL — the citable asset — keeps its exact form.
   `/` overwrites `dist/index.html`.
4. A probe of an unknown path is snapshotted to `dist/404.html`, so the
   Pages fallback for genuinely unknown routes is the real
   Page-not-found page (noindex, 404 status) instead of a copy of the
   home shell. The deploy step `cp dist/index.html dist/404.html` is
   retired.
5. `dist/sitemap.xml` is generated in the same run from the same route
   manifest, so the sitemap lists exactly the prerendered set by
   construction. The stale committed `public/sitemap.xml` and the
   drifted `scripts/generate_sitemap.py` (repo root) are retired.

### Single source of meta: `usePageMeta`

The baked meta is whatever `usePageMeta` set at snapshot time — the
composable **is** the prerender's source, so baked and hydrated meta
cannot drift by construction. To make that true:

- Every element `usePageMeta` creates carries a `data-wl-meta` marker
  (it also now manages `<link rel="canonical">`, `og:locale`,
  `og:image:width/height`, a default OG image, and an optional
  `robots` directive).
- The static per-page tags in `index.html` (description, og:*,
  twitter:*, canonical — several of them false: relative `og:image`,
  `og:url`/canonical pointing at the unregistered `wealthlens.uk`) are
  removed; only route-invariant tags stay.
- `main.ts` strips all `[data-wl-meta]` elements **before** mounting,
  and the mounting view recreates them — so a hydrated page has exactly
  one copy of each tag, and mid-run SPA-fallback serving during the
  prerender loop is self-correcting.
- The canonical site identity is `https://chris0jeky.github.io/wealthlens-hq`
  (one constant, `src/constants/site.ts`) until the domain decision
  (ACTION-REQUIRED #4) — RFC-001h's "wrong-but-consistent beats three
  identities".

### Hydration model

`app.mount()` clears the container and renders fresh (snapshot-and-remount,
not true SSR hydration). Crawlers and no-JS readers get the full baked
content; JS users see the baked page until the bundle loads, then an
identical re-render. Accepted trade-off: a brief re-render (and, on chart
pages, a short loading state while static JSON refetches). True hydration
would require `createSSRApp` + markup that matches the *initial* client
render (loading skeletons), which is exactly what we don't want to bake.

## Alternatives considered

- **vite-ssg / SSR-based prerender** — rejected. The stack is Vite 8
  (rolldown) + Vue 3.5; vite-ssg's supported Vite range lags majors, and
  SSR would require making every browser-API touchpoint SSR-safe
  (echarts/vue-echarts canvas rendering, service-worker registration,
  localStorage theme bootstrap, D3 interop), a large risky diff across
  the whole codebase for the same output. The snapshot approach renders
  the exact production bundle a visitor runs.
- **Static OG shells only (RFC-001e)** — meta without content; leaves
  the empty no-JS shell and per-route 404s for non-chart routes.
- **Directory-style output (`route/index.html`)** — works, but GH Pages
  301-redirects `/foo` → `/foo/`, changing every already-shared URL's
  served form. Flat `.html` files keep the exact URLs 200-direct.

## Consequences

- Deploy, e2e, and Lighthouse workflows install chromium and run
  `npm run prerender` after `npm run build`; e2e and Lighthouse now
  audit the prerendered artifact (deploy parity). `ci-frontend` keeps
  the plain build (no browser install) — prerender correctness is
  gated by the e2e job.
- The service-worker cache name is bumped (`wl-v1` → `wl-v2`) so
  previously cached SPA-fallback documents are purged; HTML stays
  network-first, so online users always get the prerendered pages.
- Trailing-slash variants of deep links fall through to `404.html`
  (as all deep links did before) and still render via the SPA router —
  no regression, but the canonical form is the non-slash URL.
- `/datasets/:name` pages are prerendered from the deployed
  `data/datasets.json`, so the route set follows the data layer;
  routes that can't be enumerated at build time can't exist.
- Prerendering adds ~1–2 s per route (~35 routes) plus a chromium
  install to the affected CI jobs.
