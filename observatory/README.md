# Pulseboard integration

The public WealthLens dashboard loads Pulseboard SDK 3.3.0 ([Pulseboard#105](https://github.com/Chris0Jeky/Pulseboard/issues/105)),
generated from Pulseboard `main` at `1e7c880e315d7908c64d6b9b83508a4f616a0e4d` for project id `wealthlens`
(Pulseboard's Sync sites workflow keeps the copy, the lock and its `source` commit current). The FastAPI
backend, the data pipelines and the simulation package are not instrumented and do not change.

## What is installed

- `projects/wealthlens-dashboard/frontend/public/observatory.js`: the generated SDK. Do not edit or reformat it
  (it stays in the frontend `.prettierignore`); regenerate it from a Pulseboard checkout with
  `cd <Pulseboard>/observatory && node adapters/build-sdk.mjs wealthlens <this repo> projects/wealthlens-dashboard/frontend/public/observatory.js`
  after `git rm` of the old file, then update `observatory.lock.json`.
- `observatory.lock.json` pins its SHA-256 (LF-normalised), the SDK version (`"sdk": "3.3.0"`) and the Pulseboard commit it was built from (`source`).
- `observatory/check.mjs` (`node observatory/check.mjs` from the repository root) proves the hash matches the lock,
  the header names `pulseboard-sdk <lock sdk> for wealthlens` and its body hash is intact, the collector is
  `https://pulseboard-observatory.commit-atlas.workers.dev`, no server constants ship, the URL version equals the
  lock digest prefix, the script defines `window.Pulseboard` without any network call before the DOM is ready,
  and on any other origin it is inert (no request, timer or storage) and releases the reserved bar space.

## How it loads

`src/utils/observatory.ts` (`startObservatory`, called from `src/main.ts`) appends one tag for
`observatory.js?v=<first 16 hex of the locked SHA-256>` only in production builds with `VITE_PULSEBOARD=on`
(default off, as the repo requires of new behaviour; `.github/workflows/deploy.yml` sets it for the published site;
drop that line to turn the SDK off) (#604: the versioned URL keeps the
service worker's cache-first script branch from serving old bytes). It never loads while the prerender snapshots
(no tag is baked; the prerender fails if a snapshot has one), on `/embed/*` routes, or in any frame, so a site that
embeds a chart never shows the Beta bar. `App.vue` reserves the bar space with a static, `v-once`
`<div data-pulseboard-bar style="min-height: 2.5rem">` right after the skip link and before the header, so the skip
link stays the first Tab stop and no re-render patches the bar. The SDK renders its bar into it and releases it when
no bar shows; `src/utils/observatory.ts` releases it wherever the SDK is not loaded or its script fails to load (with
the flag off, the prerender bakes it released).

The SDK only runs on `https://chris0jeky.github.io` and never under automation, so local previews, Lighthouse and
Playwright runs see it inert. There is no Content-Security-Policy on this site today; if one is added,
`connect-src` must include `https://pulseboard-observatory.commit-atlas.workers.dev` (no `unsafe-inline` is needed).

## What is sent

Only the common vocabulary: `page.view` on load, and again on each in-app navigation to a different path
(`router.afterEach` calls `window.Pulseboard?.route('home')`; `home` is the only registered route), plus the SDK's
diagnostics. There are no `track` calls. Product events must never carry amounts, balances, holdings, tickers,
calculator inputs or anything else a visitor enters; any future event needs a registered name and enum-only props.

Consent categories (Pulseboard `observatory/docs/SDK.md`): **Usage counts** (on by default), **Diagnostics** and
**Journeys and product data** (on by default outside the EEA; in the EEA or when the region is unknown, off until
the visitor presses OK on the Beta bar). Global Privacy Control or Do Not Track turns everything off with no bar
and no request. Detailed data is kept 90 days; aggregate counts currently 14 days. The public copy of this notice
is the "Usage Data (Beta)" section of the About page.

Nothing is stored until the collector admits `wealthlens` (`COLLECT_STAT_PROJECTS` / `COLLECT_PRODUCT_PROJECTS` in
Pulseboard); until then requests are refused and the SDK stops after three failures per endpoint.
