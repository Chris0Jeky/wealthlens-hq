# Observatory integration

Shared kit and collector: [Pulseboard #15](https://github.com/Chris0Jeky/Pulseboard/pull/15), source commit `8d92fff11f581d600c357e402cd521426665f318`.

The production entry loads a vendored, base-aware script with an empty endpoint. No collection, consent storage or account connection is enabled. It is scoped to the public WealthLens site and does not instrument the FastAPI backend or data pipelines.

Loading (#604): `src/utils/observatory.ts` requests `observatory.js?v=<first 16 hex of the locked SHA-256>`, derived at build time by `frontend/scripts/observatory-version.mjs`, so regenerating the artifact changes the URL and the service worker's cache-first script branch cannot keep serving old bytes. It never injects while the prerender snapshots and never appends a second tag; the prerender fails if a snapshot contains one. `check.mjs` also proves the URL version equals the lock digest prefix.

Run `node observatory/check.mjs` from the repository root. Run the existing frontend build, tests, lint, service-worker checks and deployed-path checks before approval. The shared kit has 58 passing local tests; this host's full build has not been executed here.

Activation requires a deployed collector, reviewed notice/CSP, a regenerated SHA-256-locked script and an explicit consent/withdrawal rehearsal. Keep dashboard secrets out of browser builds. Baseline events are opted-in page views and content-free error occurrences; chart exploration, source opens and shares need separately reviewed semantic hooks. Do not infer individual political views from chart use.
