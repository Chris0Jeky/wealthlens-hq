# Inbox

Last updated: 2026-06-04

> Latest: 11 PRs merged 2026-06-04 (#338-#348). The simulator dashboard pipeline
> is live end-to-end: `/api/simulator` bridge (#348) + the `/simulator` scenario
> page (#349, open/newest, fully reviewed, aging). See ORCHESTRATION.md.

Every concrete action item extracted from research. Triage into active-sprint, backlog, or done.

## Simulator dashboard follow-ups (from #348/#349 reviews — data integrity)

- [x] **Publish simulator JSON statically** so `/simulator` works on the deployed
  (static) GitHub Pages build, un-gate the route + nav link. [completed: 2026-06-05, PR #351]
- [x] **Surface the synthetic-population caveat in `to_dashboard_json` itself** (not
  only the generator), so every consumer of the contract gets it. [completed: 2026-06-05, PR #354]
- [x] **Make the synthetic caveat key off ground-truth `is_synthetic`, not the
  `population_version` string.** [completed: 2026-06-05, PR #354] Threaded
  `population_is_synthetic` through `EngineResult` (fail-closed default `True`,
  from `getattr(population, "is_synthetic", True)`); `_caveats` now gates on it, so a
  synthetic population can't fail open by being mistagged. Tested via a `model_copy`
  flip to `is_synthetic=False`. (A genuine real-microdata provider is still the
  separate WAS/FRS task below.)
- [x] **Add URL + access date to population provenance sources (B2).**
  [completed: 2026-06-05, PR #355] `to_dashboard_json` now emits a
  `population_provenance` block resolving `population_provenance_ids` against
  `registries/sources.yml` to {id,name,url,access_date,licence} (real URLs);
  `synth.*` params id-only.
- [ ] **B1: URLs for assumption `source` citation strings** (e.g. "Vermeulen 2018")
  — these have no `registries/sources.yml` entry. Add verified citations to
  `registries/assumptions.yml` (do NOT fabricate); then surface them in the
  `assumptions_consumed` provenance. Upstream `wealthlens-sim`.
- [~] **Calibrate synthetic IHT** before serving any IHT scenario. **Tier A DONE**
  (merged PR #356, see `docs/IHT_CALIBRATION.md`): an ONS-sourced annual mortality scalar
  now converts the at-death STOCK to an annual FLOW (£1,009bn → £21.3bn), fixing the
  ~40x stock-vs-flow error. **Remaining (Tier B):** ~£21bn is still ~3x the ~£7-8bn
  real because the synth over-states top wealth; needs age-specific mortality (ONS
  life tables q_x) + age-wealth correlation in the synth. **IHT stays EXCLUDED**
  until then. Tier B should also wire `model.iht.annual_mortality_rate.v1` into the
  engine's `assumptions_consumed` (currently documented in the registry but not in
  any served scenario's provenance) so a served IHT caveat carries the source. Also:
  Gate-3 charitable 10% reduced-rate uses gross estate not the post-relief baseline
  amount (refine with Tier B).
- [x] **Clean up the compiled `.js` shadows** emitted by `vue-tsc -b` — **DONE in
  PR #432** (2026-06-19). Root cause: `build` ran `vue-tsc -b` (composite BUILD mode
  = emits) with no `noEmit`/`outDir`, writing a `.js` next to every `.ts`; Vite/vitest
  resolve `.js` before `.ts` so the committed config shadows + gitignored `src/**/*.js`
  shadows silently won and went stale. Fix: `build` → `vue-tsc -b --noEmit` (typecheck
  still catches errors, emits nothing); deleted the 4 tracked shadows (vite.config.js,
  vitest.config.js, scripts/*.js); gitignored them; added a `clean:shadows`
  (`git clean -fX …`) `prebuild`/`pretest` hook so a dev's pre-existing stale shadows
  are wiped before build/test. 2-lens reviewed (typecheck-still-catches-errors proven
  by injection) + codex P2 (existing dev shadows) addressed.
- [~] **Sync the `docs/redesign/pages/` static prototypes to the corrected
  wealth-shares figures** (surfaced by PR #416 review). **PROSE + STAT CARDS done in
  PR #431** (Top 1% 28→21, Postwar low 1980/50→~1990/52, removed "1910 levels",
  "since 1980"→"~1990", fixed a 1990 bottom-90 slip the review caught) + each file
  now carries a "DESIGN MOCKUP — NOT DEPLOYED" banner pointing to chartArticles.ts.
  **REMAINING:** the embedded chart DATA arrays that draw the SVG line — `const DATA`
  in `chart.html` (~lines 651-674) and `WEALTH_SHARES` in `landing.jsx` (~369-392) —
  still plot the OLD series (top 1% = 28, the ~1980/50% low) and the era-band shading
  is hardcoded at 1980. #431 explicitly flags this as stale in the banners but does
  NOT re-sync it, because the 5-column arrays carry middle-40/bottom-50 columns that
  the 2-series WID data in `wealth-shares.json` can't supply. To finish: source the
  full historical WID decomposition (incl. p50p90 / p0p50) and rebuild the arrays +
  move the era band to ~1990. Low severity (not deployed).

---

## Reliability follow-ups

- [~] Fix `make ci-quick` false-positive and dashboard backend failures observed
  2026-05-30. A valid POSIX-shell run reports 11 pytest failures + 2 errors but
  still exits 0 because backend commands are guarded with `|| echo ...`.
  Failures seen: missing `plotly` for productivity-pay pipeline tests,
  `cgt-concentration` emits non-finite JSON, and invalid dataset names return
  404 where tests expect 422.
  **Update 2026-06-05:** the Makefile error-swallowing is fixed in **PR #350**
  (`ci-quick` now runs real ruff + mypy + pytest and fails loudly; backend shows
  201 passed; `requirements-dev.txt` pins ruff/mypy/httpx/pandas-stubs for a clean
  install). The *backend* suite is green. The pipeline-side failures below remain.
- [x] **Get the `automation/data-pipelines` (and root) test suites into CI** —
  **RESOLVED / already covered** (re-verified 2026-06-19). (1) The unit suites DO run
  in CI now: `ci-pipelines.yml` (from #352) executes root `tests/`, dashboard `tests/`,
  and `automation/data-pipelines/tests/` + mypy on `automation`/`tests`. (2) The "12
  validation errors" are gone: `make pipeline-test` = 52 passed and `make validate` =
  "All 9 datasets validated OK". (3) **Do NOT add `validate.py` to CI** — tried it in
  PR #429 and the 2-lens review caught that `projects/wealthlens-dashboard/data/processed/`
  is **gitignored** (only `wage_stagnation.csv` tracked), so validate.py MISSING→exit(1)s
  on a clean checkout; #429's own CI failed and it was closed. The processed CSVs are
  intermediate build artifacts (regenerated by the pipeline; re-run weekly by
  `weekly-data-update.yml`); the data the SPA actually ships — `frontend/public/data/*.json`
  — is already validated in CI by vitest (`static-data-validation.test.ts` +
  `freshnessContract.test.ts`). LESSON: `make validate` passes locally only because the
  dev tree has the gitignored CSVs; always check git-tracked vs gitignored before wiring
  a script into CI.
- [ ] **`Weekly Data Update` (`weekly-data-update.yml`) is RED on main — upstream
  ONS source drift, not a code regression** (diagnosed 2026-06-26, session 10).
  The scheduled job re-fetches live data and `validate.py` correctly REJECTED it,
  so nothing bad was committed (the committed CSVs + deployed SPA are fine — this is
  the data-integrity backstop working). Two distinct upstream breakages:
  1. **`ons_wealth_by_decile.csv` collapsed to 2 rows (expected ≥10) with negative
     values.** `fetch_ons_wealth.py` parses ONS Total Wealth "Table 2.2"; the live
     workbook layout/sheet changed so the parser now extracts almost nothing. Needs
     the LIVE XLSX to re-derive the row/column offsets (a blind edit risks shipping
     bad wealth-by-decile data). Source: `ons-was-wealth` in `registries/sources.yml`.
  2. **`ons_gdhi_by_region.csv` has 233 duplicate `region` rows.**
     `fetch_ons_gdhi._filter_to_leaf_itl_level()` bails to "return as-is" when ITL
     code detection drifts (`tl_mask.sum() < 5`), leaving aggregate+leaf rows that
     duplicate region names. This is the SAME dataset as the open geography-decision
     item below ("GdhiByRegionChart: the dataset labels mixed geographies as 'UK
     regions'") — fixing it needs Chris's call on which ITL level to show (ITL1
     nations/regions vs ITL3 sub-regions) AND a parser hardening that fails-loud (or
     drops dupes) instead of silently keeping aggregates.
  **Do NOT loosen `validate.py` to make the job green** — the validation is correct;
  the fetchers need repair against the live sources. Both require network access to
  the live ONS files. Defensive add when fixing: a post-parse dedup/row-count guard
  in each fetcher so a future layout drift triggers the cited-fallback path rather
  than emitting malformed data.

---

## Hero #1 (Analyst) ingest follow-ups

- [ ] **CGT tabular chunks: explicit band RANGES + a cumulative-concentration line**
  (seeded 2026-06-26, from the H1-07 review). `ingest/slice_corpus.py` renders one
  chunk per HMRC CGT size-of-gain band with that band's PER-BAND figures, labelled
  "... in this band" so HMRC's "£X+" band name is not misread as an "above £X"
  cumulative share. Two additive refinements would sharpen the concentration story
  (golden G-007): (a) render each band as an explicit range (`band_lower[i]` to
  `band_lower[i+1]`; last band "and above") instead of the bare "£X+"; (b) add a
  clean cumulative line from `cumul_gains_from_top_pct` / `cumul_taxpayers_from_top_pct`
  (handling the >100% rounding artefact on the low bands) so a citation can state
  top-tail concentration directly. Small, additive; do after the live URL exists.

---

## Wave 13 candidates (seeded 2026-05-30, after the Wave 12 engine stack)

The Wave 12 engine (synth→rules→engine→outputs) is built and merged through
#335, and Wave 13 #336 enforcement compliance is merged. Follow-ups surfaced by
the build + its adversarial reviews:

- [x] **Proper enforcement compliance model** — PR #336 merged after the full
  two-review gate. It replaces the Family-F overstatement placeholder with a
  baseline-vs-theoretical compliance model anchored to HMRC/NAO tax-gap evidence;
  enforcement cost is separate from revenue and enforcement assumptions are in
  dashboard provenance. [completed: 2026-05-30]
- [x] **Monte-Carlo sampling layer (`uncertainty/sampling.py`)** — PR #338 merged
  (`3b31de2`) after 7 codex rounds + 4 adversarial reviews: deterministic
  independent + Latin-hypercube draws over uniform/triangular marginals
  (`ParameterSpec`/`SamplingConfig`/`ParameterSamples`/`sample_parameters`) with a
  fully injective, exact-float, reproducible provenance trail. [completed: 2026-06-04]
- [~] **Monte-Carlo propagation layer (`uncertainty/propagation.py`)** — open as PR
  #345 `feat/uncertainty-propagation` (2 reviews, all findings fixed):
  `propagate(samples, evaluate, *, lower/upper_quantile, central) -> PropagationResult`
  runs a scalar `evaluate` once per joint draw and summarises a cited Interval
  (quantile band + median-or-point-estimate central) + per-draw outputs (for Sobol)
  + reproducible provenance. Engine-free.
- [ ] **Wire propagation into the engine (default OFF)** — add optional
  `uncertainty: SamplingConfig | None = None` to `engine.simulate`; when set, sample
  the top-tail alpha from its registry range and `propagate` each revenue figure
  (total/by-nation/by-decile) into Monte-Carlo quantile bands with `central` = the
  point estimate at central alpha. Default None = today's single alpha band. Then
  add more sampled parameters (assumption RangeValues) + Sobol sensitivity.
- [x] **Calibrate the synth generator to cited public WAS/ONS marginals** — PR #335
  merged; default synth calibration is Great Britain scoped, cites ONS/WAS sources,
  and threads source IDs through population provenance. [completed: 2026-05-30]
- [ ] **Real WAS/FRS microdata provider behind the `PopulationSource` Protocol** —
  needs a UKDS licence; the seam already accepts any `households`+`provenance_ids` source.
- [ ] **Wire the dashboard JSON into a Vue scenario page** — `to_dashboard_json` emits the
  contract (totals/by-nation/by-decile intervals + provenance + caveats); build the
  ConfidenceFanChart + ProvenanceTooltip + a caveats banner that renders `caveats[]`.
- [x] **Record synth generation inputs in provenance** — PR #337 merged to main
  at `94446e3`. Threads all generation-affecting `SynthConfig` inputs through
  `population.provenance_ids` / dashboard JSON with canonical sorted mapping
  order. Full gate satisfied: two independent adversarial reviews, all bot
  threads resolved, CI green, newer PR (#338) above it. [completed: 2026-05-31]

---

## Build: WealthLens-Sim Microsimulator (Blueprint v5)

> **Status (2026-05-30):** Gate 1 (schema + registries + loaders), the top-tail
> Pareto reconstruction, provenance, all seven policy families (A–G), and the
> Wave 12/Wave 13 engine-output stack is MERGED to `main` through #336. 645 sim
> tests pass locally on main after #336. See `docs/WAVE12_SIMULATION_ENGINE_DESIGN.md`.

### Gate 1: Schema + Registry Layer — DONE
- [x] Pydantic schema module — households, policies, results (PR #292/#318) [completed: 2026-05-23]
- [x] Assumption + baselines registry loaders with validation (PR #293/#319) [completed: 2026-05-29]
- [x] Sources registry populated; registries packaged into wheel+sdist (#326) [completed: 2026-05-29]

### Gate 2: Data Foundation — partial
- [x] Top-tail Pareto reconstruction module (Blueprint §5.1-5.3) — 5 baseline variants (PR #295) [completed: 2026-05-29]
- [x] Synthetic household generator (Wave 12 PR1 #327) — lognormal+Pareto, deterministic [completed: 2026-05-29]
- [x] Calibrate synth generator to cited public WAS/ONS marginals (PR #335) [completed: 2026-05-30]
- [ ] FRS-WAS real-microdata linker (Blueprint §7.1-7.2) — needs UKDS licence; behind the population-source Protocol seam
- [ ] ONS NBS macro reconciliation (`reconcile/`, Gate 2) + reconstruction orchestration (`reconstruction/`)

### Gate 3: Policy Family Calculators — DONE (all 7 merged)
- [x] Family A annual wealth tax / B one-off levy / C CGT / D IHT / E HVCTS / F enforcement / G devolution (PRs #297–#303) [completed: 2026-05-29]
- [ ] IHT v0.1 modelling refinement: 10% reduced-rate test uses gross estate not the post-relief "baseline amount" (documented simplification)

### Gate 4: Behavioural + Uncertainty
- [x] Interval propagation in the engine (top-tail alpha interval + assumption RangeValues) — Wave 12 engine PR (#332) [completed: 2026-05-30]
- [~] Monte Carlo / Sobol uncertainty engine (`uncertainty/`, Blueprint §10) — Wave 13;
  sampling-layer groundwork open as PR #338 (`uncertainty/sampling.py`), engine wiring next
- [ ] Migration elasticity, avoidance/lock-in, liquidity-constraint behavioural models (Blueprint §6)

### Gate 5: Output + Integration
- [x] Provenance manifest system (Blueprint §13.4) — collector + manifest (PR #296) [completed: 2026-05-29]
- [x] Nation-level disaggregation — `revenue_by_nation` from every family + merged in `run_scenario` (#328) [completed: 2026-05-29]
- [x] **Wave 12 engine PR (task #17):** `engine.simulate(population, scenario, *, registries, devolution, enforcement) -> EngineResult` wiring synth→rules→provenance; interval propagation; per-decile attribution; population-source `Protocol` seam; families F (enforcement uplift) + G (devolution scope) composition (#329-#332) [completed: 2026-05-30]
- [x] `outputs.to_dashboard_json` (Gate 9 dashboard contract) + golden-file test (#333) [completed: 2026-05-30]
- [ ] PolicyEngine-UK integration / validation (`engine/` bridge, Blueprint §12)
- [ ] Dashboard API bridge + assumptions sensitivity dashboard component

## Accessibility: chart data-table fallbacks (WCAG 1.1.1)

Seeded 2026-06-19 (session 9). Audit: only 3 of 12 data charts ship an
`AccessibleDataTable` fallback (CgtConcentration, InheritanceTax, WealthShares).
Per "Charts must meet WCAG AA" + "accessible by default", every data chart should
offer a verbatim data-table alternative to its `role="img"` canvas. Pattern is
established (see `WealthSharesChart.vue` / `CgtConcentrationChart.vue`): import
`AccessibleDataTable`, map the chart's already-loaded rows to `columns` + `rows`,
mark numeric columns, add a sourced `caption`. Additive, default-visible table
below the chart; no data changes. One small reviewable PR per chart (or tight
group). Each: real per-row cell-mapping test + 2 adversarial reviews.

- [ ] BoeRatesChart — accessible data table (boe-rates.json)
- [ ] ChildPovertyChart — accessible data table (child-poverty.json)
- [ ] GdhiByRegionChart — accessible data table (gdhi-by-region.json)
- [ ] GenerationalWealthChart — accessible data table (generational-wealth.json)
- [ ] HousingAffordabilityChart — accessible data table (housing-affordability.json)
- [ ] ProductivityPayChart — accessible data table (productivity-pay.json)
- [ ] TaxCompositionChart — accessible data table (tax-composition.json)
- [ ] WageStagChart — accessible data table (wage-stagnation.json)
- [ ] WealthByDecileChart — accessible data table (wealth-by-decile.json)

### Data-quality follow-ups surfaced during the a11y audit (2026-06-19)

- [~] **Systemic null→0 fabrication in chart parsers — shared `toNumberOrNaN`
  sweep.** DONE in **PR #428** (aging): added a robust shared `toNumberOrNaN` to
  `frontend/src/utils/chart.ts` (strict types + non-finite rejection, unit-tested)
  and routed every chart's parse step through it (the 4 that were still on bare
  `Number()` — Gdhi/TaxComposition/WealthByDecile/WealthShares — plus ProductivityPay
  + ChildPoverty, which a review caught as partially-guarded). Also fixed two
  consequences the guard exposed: TaxComposition (stacked total) now drops a year
  missing any plotted component (no £NaN total), and WealthShares aligns its two
  series on a shared year union (no index-shift when a year is dropped). The a11y
  thread had already fixed CGT #417 / child-poverty #421 / generational #423 /
  boe+housing+wage (batch-2) inline. **Remaining:** consolidate those inline guards
  onto the shared helper (DRY, optional).

- [ ] **GdhiByRegionChart: the dataset labels mixed geographies as "UK regions".**
  `gdhi-by-region.json` mixes true ITL1 regions (South East, Scotland) with
  sub-regions that double-count (Wales + East Wales + West Wales and The Valleys)
  and local authorities (Westminster, Camden, Blackpool). The chart title/aria
  ("by Region") and the new table caption all call these "regions", overstating
  comparability. Fix: either filter to standard ITL1 regions, or relabel as
  "areas" and split the view. Own reviewed PR + cite the ONS source granularity.
  (Surfaced by review on #420; the a11y table itself faithfully mirrors the chart.)
- [x] **WealthByDecileChart: aria-label/docstring falsely claimed the poorest decile
  has "net negative wealth" / is "highlighted in red"** while the committed ONS
  data is +£13.9bn (positive) — fixed in #422 (gated the claim on a
  `poorestIsNegative` computed; tooltip + bar colour were already conditional).
- [ ] **Frontend `.prettierrc` is stale / unenforced — reconcile it with the code.**
  Surfaced 2026-06-19 (#430 review). `frontend/.prettierrc` declares
  `semi: false, singleQuote: true`, but the entire committed codebase uses
  **semicolons + double-quotes**, and `format:check` (`prettier --check`) runs
  **nowhere in CI** — so prettier is effectively dead and the config lies about the
  house style. Decide the canonical style (almost certainly semi + double-quote to
  match the ~120 existing files), update `.prettierrc` to match, run `prettier
  --write` once, and add `npm run format:check` to `ci-frontend.yml` so it stays
  enforced. One reviewed PR (the `prettier --write` will be a large no-op-ish diff —
  do it on a clean branch). Until then, hand-match each file's existing style.

## Build: Charts and Visualisations

- [ ] Build "Where Do You Fit in UK Wealth?" personal comparator calculator
- [ ] Build "Top 1% wealth share over time" chart with definition toggle (ONS WAS / WID / RF corrected)
- [ ] Build "Regional house-price-to-earnings scrollytelling" chart
- [ ] Build "House for the price of a house: what £200k buys across the UK" photo carousel
- [ ] Build "Animated UK wealth concentration: 1980-2025" GIF/MP4
- [ ] Build "Inheritance Britain: who inherits what, and when?" Sankey diagram
- [ ] Build "The Two Englands: London vs the rest, in 10 charts" small-multiples
- [ ] Build "Marmot postcode life-expectancy gap" lookup tool
- [ ] Build "Compare your effective tax rate to a billionaire" calculator
- [ ] Build "CEO-vs-worker pay clock" — UK FTSE-100 version (for "High Pay Day" in January)
- [ ] Build "Lifetime tax burden by income percentile" calculator
- [ ] Build "1 pixel = £1,000: UK wealth to scale" horizontal scroller (a la Korostoff)
- [ ] Build "If the UK were 100 people" pictogram / Instagram Reel
- [x] Build UK tax revenue composition chart ("tax on work vs tax on wealth") [completed: 2026-05-16]
- [x] Build capital gains concentration chart (top 5,000 receive >50% of gains) [completed: 2026-05-15]
- [ ] Build inheritance tax chart (only 4-5% of estates pay IHT)
- [ ] Build real wage stagnation + counterfactual chart
- [x] Build regional GDP per head map [completed: 2026-05-16 — GDHI pipeline built]
- [x] Build child poverty by region map [completed: 2026-05-16 — pipeline built]
- [x] Build productivity-pay gap (scissor chart) [completed: 2026-05-16 — pipeline built]
- [x] Build generational wealth gap by birth cohort chart [completed: 2026-05-16 — pipeline built]
- [ ] Build ownership by age and tenure chart (owner-occupied / private rent / social rent)
- [ ] Build "Share of adults with almost no financial buffer" chart (FCA Financial Lives)
- [ ] Build wealth-to-income ratio chart
- [ ] Build UK billionaire wealth tracker (Forbes-driven, weekly refresh)
- [ ] Build wealth tax revenue simulator with rate/threshold/exemption/behavioural-response sliders
- [ ] Build "The capital-gains toggle" — top 1% share with and without capital gains
- [ ] Build effective tax rate by wealth percentile chart (with CenTax permission)
- [ ] Build 50 richest families vs bottom half chart (needs careful methodology)
- [ ] Build FTSE 100 CEO pay ratio chart
- [ ] Build Trussell foodbank use chart (2.89m parcels, ~50x 2010/11)
- [ ] Build university access by household income decile visualisation (UCAS data)
- [ ] Build WP Sankey: access at 18 -> wealth distribution at 60
- [ ] Build postcode-driven local house-price-to-earnings lookup
- [ ] Build "UK Spirit Level 2.0" — regional scatterplots
- [ ] Build "The wealth detective — find the UK billionaire near you" postcode lookup
- [ ] Build "Methodology honesty card" — source toggle UI beside every wealth chart

## Build: Infrastructure and Platform

- [ ] Register `wealthlens.uk` domain
- [ ] Set up Astro 5 + Vue 3 islands + Observable Plot scaffold
- [ ] Configure Cloudflare Pages deploy from GitHub
- [ ] Set up Cloudflare R2 bucket for raw data snapshots
- [x] Set up GitHub Actions cron skeleton with Python ETL using OWID five-stage model [completed: 2026-05-16 — weekly-update.yml]
- [ ] Write OG-image build task with `satori` + `resvg-js`
- [ ] Set up `@newswire/frames` for responsive iframe embeds
- [ ] Implement `/oembed?url=...&format=json` endpoint on a Cloudflare Worker
- [x] Set up public GitHub repository with MIT/Apache-2.0 licence on code, CC-BY 4.0 on charts [completed: 2026-05-14]
- [ ] Build a "data status" badge for every chart
- [x] Run WCAG 2.2 AA accessibility pass: keyboard navigation, role="img", alt text, contrast [completed: 2026-05-16]
- [ ] Create 3-4 Canva templates for sharing charts as social images
- [ ] Set up donation page: Open Collective or Ko-fi
- [ ] Set up email list: Buttondown (free <100 subs) or Substack
- [ ] Set up project board via GitHub Projects
- [x] Set up analytics: Plausible (£7/month) or Umami (self-hosted, free) [completed: 2026-05-16 — privacy-respecting analytics integrated]
- [ ] Set up project email (hello@wealthlens.uk)
- [ ] Apply for GitHub Sponsors
- [ ] Create media kit: one-pager PDF about the project
- [ ] Create "Data Sources & Licences" page for the website
- [ ] Create contributors page on website
- [x] Build simple landing page (GitHub Pages, Astro, or Hugo) [completed: 2026-05-15 — Vue frontend deployed to GitHub Pages]
- [x] Write README with mission, screenshot, "How to contribute", tech stack, licence [completed: 2026-05-16]
- [x] Write CONTRIBUTING.md with setup instructions and task list [completed: 2026-05-15]
- [x] Create GitHub Issues for first 10 tasks (labelled "good first issue", "help wanted") [completed: 2026-05-15]

## Build: Data Pipelines

- [x] Build `fetch_ons_wealth.py` data pipeline [completed: 2026-05-15]
- [x] Build `fetch_hmrc_stats.py` data pipeline [completed: 2026-05-14]
- [x] Build `fetch_wid_data.py` data pipeline [completed: 2026-05-14]
- [ ] Build reliable spreadsheet parsers for high-value XLSX/ODS wealth releases
- [ ] Set up DWP Stat-Xplore API access (free registration + key)
- [ ] Set up Companies House API key (free, 600 req/5min)
- [x] Ingest Bank of England IADB series via parameterised CSV URLs [completed: 2026-05-16 — fetch_boe_rates.py]
- [ ] Ingest ONS Beta API datasets (JSON, rate limit 120 req/10s)
- [ ] Ingest HMRC tax receipts and NICs annual bulletin CSV
- [x] Ingest ONS housing affordability XLSX [completed: 2026-05-14 — fetch_ons_housing.py]
- [ ] Ingest Land Registry Price Paid Data CSV (~5GB)
- [x] Set up Nomis API for GDHI data (no auth required) [completed: 2026-05-16 — fetch_ons_gdhi.py]
- [ ] Build pdfplumber parser for HMRC Personal Wealth Statistics PDF tables
- [ ] Ingest High Pay Centre CEO pay data from PDF (manual data entry)
- [x] Build `chart_to_social.py` — auto-generate platform-sized images from chart data [completed: 2026-05-15]
- [x] Set up GitHub Action: `weekly-data-update.yml` [completed: 2026-05-16]
- [x] Set up GitHub Action: `deploy.yml` (auto-deploy on push) [completed: 2026-05-15]
- [ ] Build research automation: `summarise_research.py` (Claude API)
- [x] Build research automation: `extract_action_items.py` [completed: 2026-05-15]

## Build: WP Pathway Explorer

- [ ] Build weekend prototype: "Postcode -> Pathway Snapshot" Vue 3 + FastAPI app
- [ ] Create three FastAPI endpoints: `/lookup/{postcode}`, `/providers`, `/programmes`
- [ ] Hand-curate JSON for 19 London providers' contextual-offer policies
- [ ] Create static JSON for bursary data
- [ ] Deploy prototype on Fly.io or Railway
- [ ] Demo prototype to WP team
- [ ] Write one-page brief mapping tool to OfS EORR Risks 1, 2, 4, 7, 12
- [ ] Write costed three-month plan with named deliverables
- [ ] File DPIA with Information Governance team
- [ ] Request named WP team sponsor
- [ ] Propose WP postcode-to-university data tool to Middlesex University WP team

## WealthLens Schools Initiative (seeded 2026-05-31)

Bring WealthLens data literacy workshops into schools via Middlesex
University's widening participation programme. Chris is starting this
initiative and needs approvals, partnerships, and curriculum design.

### Internal approvals and alignment

- [ ] Get buy-in from direct WP team manager for WealthLens workshops
- [ ] Get approval from the Marketing department head (Chris's department)
- [ ] Identify any formal approval process for external workshop content at Middlesex
- [ ] Draft a one-page proposal: what the workshops cover, target age group (Y10+), learning outcomes, how it ties to WP objectives and OfS metrics

### Find academic partners at Middlesex

- [ ] Research economics faculty at Middlesex: who teaches inequality, public policy, or political economy? Look for people whose research aligns
- [ ] Research business school faculty: anyone working on wealth, taxation, or economic data literacy?
- [ ] Check if any PhD students at Middlesex are researching wealth inequality, economic education, or data literacy for young people
- [ ] Look into the Education department: anyone doing work on financial literacy, economic citizenship, or critical data literacy in schools?
- [ ] Draft a short pitch email for academics: "I run WP workshops and I'm building an open-source data tool for UK wealth inequality. Would you be interested in collaborating on school workshops?"

### External partnerships and models

- [ ] Research existing data literacy / economic education programmes for schools in the UK (e.g., CORE Econ, Economy, Young Money, RSA)
- [ ] Check if any other universities run inequality-focused WP workshops
- [ ] Explore whether the "From the Boys" podcast initiative at William Ellis School could be a pilot site for WealthLens workshops
- [ ] Identify 2-3 schools (beyond William Ellis) that might be interested in piloting

### Workshop design

- [ ] Design a 60-minute workshop outline: "Reading the Data: What Does Wealth Inequality Look Like?"
- [ ] Identify which WealthLens charts / data are most accessible for Y10 students
- [ ] Create a simple student handout with 3-4 chart exercises
- [ ] Plan how to tie workshops to the National Curriculum (citizenship, maths/statistics, PSHE)

## Build: Tools

- [ ] Build openpoverty-uk Python API wrapping DWP HBAI, ONS FRS, IMD, JRF data
- [ ] Scrape and publish a UK Companies House dataset with a story on GitHub
- [ ] Scrape and publish a Hansard dataset with a story on GitHub
- [ ] Build one D3/Observable interactive visualisation

## Outreach: Emails to Send

- [ ] Email Tax Justice UK (info@taxjustice.uk) with prototype link [UNBLOCKED — v0.1 is live]
- [ ] Contact Patriotic Millionaires UK via website contact form [UNBLOCKED — v0.1 is live]
- [ ] Email The Equality Trust (info@equalitytrust.org.uk) [UNBLOCKED — v0.1 is live]
- [ ] DM Gary Stevenson (@garyseconomics) on X with prototype link [UNBLOCKED — v0.1 is live]
- [x] Email mySociety (whofundsthem@mysociety.org) to join volunteer cohort [completed: 2026-05-14]
- [x] Email Democracy Club (hello@democracyclub.org.uk) [completed: 2026-05-14]
- [ ] Email Common Wealth (info@common-wealth.org) with proposal [after building CH/LR tool]
- [ ] Email Arun Advani at CenTax (a.advani.1@warwick.ac.uk) [after publishing original analysis]
- [ ] Email Max Lawson at Oxfam (max.lawson@oxfam.org) [after building widget]
- [ ] Soft-launch email to John Burn-Murdoch (FT) with chart URLs [after v0.1]
- [ ] Email Charles Arthur (The Overspill) with first post
- [ ] Pitch Data Elixir (Lon Riesberg) with technical post
- [ ] Pitch Python Weekly (Rahul Chaudhary) with technical post + repo
- [ ] Email info@theodi.org for guest blog interest
- [ ] Email Myf Nixon at mySociety about practitioner blog post

## Outreach: Volunteering

- [ ] Sign up to Democracy Club volunteer alerts
- [ ] Sign up to Full Fact's volunteer mailing list
- [ ] Make first PR to mySociety FixMyStreet/Alaveteli (issues tagged "Suitable for Volunteers")
- [ ] Open a PR on TJN's `swift_codes_scraper` repo (modern Python rewrite)
- [ ] Engage one issue on Democracy Club's `UK-Polling-Stations`
- [ ] Open a PR on mySociety's `local-intelligence-hub`
- [ ] Contribute to one Bellingcat Volunteer Community investigation
- [ ] Contribute to OpenSAFELY / Bennett Institute open-source project
- [ ] Contribute to Alan Turing Way book sprints
- [ ] Subscribe to DataKind UK newsletter (for when volunteer apps reopen)

## Outreach: Events and Speaking

- [ ] Attend LSE III Inequalities Seminar Series (Tuesdays during term)
- [ ] Attend UCL IIPP Forum 16-17 June 2026
- [ ] Show up at Newspeak House civic-tech sessions in London
- [ ] Attend Resolution Foundation events at 2 Queen Anne's Gate
- [ ] Investigate attending The Conduit events in London
- [ ] Attend Campaign Lab bi-weekly hack nights
- [ ] Attend Journalism Technology London Meetup
- [ ] Submit MozFest 2026 CFP under digital rights / economic power tracks
- [ ] Submit AIES 2026 abstract (deadline 14 May) for Global Inequalities track
- [ ] Pitch PyData London CFP
- [ ] Submit Hacks/Hackers London talk (DM @HacksHackersLDN on X)
- [ ] Pitch ODI Friday Lecture for autumn slot
- [ ] Pitch Papers We Love London for SGAI paper read-through
- [ ] Apply to TEDxLondon (tedxlondon.com/speaker-applications)
- [ ] Pitch The Conduit: "How engineers can turn inequality data into public action"
- [ ] Submit RightsCon 2027 CFP (opens 1 August 2026)
- [ ] Get UKGovCamp ticket when registration opens (~October 2026)
- [ ] Register for NICAR 2027 (opens ~October 2026)

## Outreach: Podcast Pitches

- [ ] Pitch Tech Won't Save Us (Paris Marx on Bluesky @parismarx)
- [ ] Pitch The Bunker (podmasters.co.uk; 200-word pitch)
- [ ] Pitch ODI podcast (info@theodi.org)
- [ ] Pitch Trashfuture (DM @raaleh or @inthesedeserts on social)
- [ ] Pitch Intelligence Squared (podcasts@intelligencesquared.com)
- [ ] Pitch Novara's Downstream (DM @AaronBastani)
- [ ] Pitch 80,000 Hours (podcast@80000hours.org; 150-word hook + 3 topics)

## Outreach: Grants and Funding

- [ ] Apply to JRRT Larger Grants — September 2026 round (outline by 24 August)
- [ ] Apply to SSI Fellowship — apps open August 2026, close ~6 October 2026
- [ ] Apply to Mozilla Foundation Fellowship — next cycle opens early 2027
- [ ] Apply to Bellingcat Tech Fellowship (tech@bellingcat.com)
- [ ] Apply for Bethnal Green Ventures Autumn 2026 cohort (~May 2026 window)
- [ ] Apply for UnLtd Starting Up Award (500-8,000, rolling)
- [ ] Submit EOI to Esmee Fairbairn, Friends Provident, Barrow Cadbury, Trust for London
- [ ] Apply for internal HEIF + APP investment line + innovation/seedcorn fund (Middlesex)
- [ ] Apply to Comic Relief Tech for Good (with charity partner)
- [ ] Apply to Paul Hamlyn Ideas and Pioneers Fund (via partner org)
- [ ] Contact Trust for London — book a call with grants manager before EOI
- [ ] Track Alan Turing Institute Open Source AI Fellowship 2027 cycle

## FOI Requests to File

- [ ] HMRC top 0.01% effective tax rates by income decile
- [ ] Non-dom counts and tax paid by gross income band
- [ ] Trust ownership of UK property at LA level
- [ ] ATED dwellings by region
- [ ] SDLT by buyer category (corporate / foreign individual / trust)
- [ ] HMRC High Net Worth Unit caseload aggregates
- [ ] Subnational income percentiles by region and London borough

## Content: Social Media and Writing

- [x] Create Twitter/X account with bio and pinned manifesto thread (5-7 tweets) [completed: 2026-05-14]
- [x] Create Bluesky account [completed: 2026-05-14]
- [ ] Update LinkedIn headline and About section per rebranding playbook
- [ ] Add WealthLens to LinkedIn experience
- [ ] Update LinkedIn Featured section (WealthLens, Springer pub, WP post, Taskdeck)
- [ ] Add skills to LinkedIn: Data Visualisation, Open Data, Economic Research, Widening Participation
- [ ] Update Instagram bio gradually
- [ ] Build a private X List of 30-50 accounts (10 big, 20 mid, 20 peers)
- [ ] Join ukgovernmentdigital.slack.com
- [ ] Request access to Bureau Local Slack via TBIJ
- [ ] Write first blog post: "Why I'm building WealthLens UK" (LinkedIn article + Dev.to)
- [ ] Write blog post: "What my experience building trading systems taught me about wealth inequality"
- [ ] Write technical blog post on WealthLens methodology
- [ ] Post LinkedIn announcement using founding document copy
- [ ] Post Instagram launch post
- [ ] Post call for volunteers with specific roles listed

## Content: Writing for the Curriculum

- [ ] Write 500-word summary of r > g argument and the Acemoglu-Robinson critique [Week 1]
- [ ] Produce one-page UK inequality fact-sheet [Week 2]
- [ ] List Atkinson's 15 proposals and assess each [Week 3-4]
- [ ] Write 500-word piece on whether UK exhibits homoploutia [Week 4]
- [ ] Write balanced 1,000-word essay on Wilkinson-Pickett causal claims [Week 6]
- [ ] Write 1,500-word "Best Case Against a UK Wealth Tax" essay + rebuttal [Week 9]
- [ ] Produce timeline of UK wealth-related tax reforms 1965-2026 [Week 8]
- [ ] Write 3,000-word synthesis: "How the UK became as unequal as it is" [Week 12]
- [ ] Write 2,000-word piece: "Why top 1% income share is contested" [Week 17]
- [ ] Write 1,500-word piece: "Will AI reduce or amplify UK wealth inequality?" [Week 23]
- [ ] Produce comparative table of Swiss, Norwegian, Spanish, French, and proposed UK wealth-tax regimes [Week 24]

## Content: Data Analysis

- [ ] Replicate a UK Lorenz curve from FRS or WAS data in Python/R [Week 13]
- [ ] Pull UK top 1% income share time series from WID [Week 16]
- [ ] Produce UK top 1% income share chart 1918-2024 [Week 16]
- [ ] Derive WTC 260bn and 80bn revenue figures from model assumptions [Week 8]

## Career: Job Applications and Education

- [x] Apply to mySociety SocietyWorks Developer role by 31 May 2026 [submitted: 2026-05-31; rejected 2026-06-11]. Tracking file: `../hq-private/career/applications/mysociety-societyworks-2026.md` (private repo)
- [ ] Apply to GDS Senior Developer and HMRC/DWP/MoJ DDaT roles via Civil Service Jobs
- [ ] Apply to NHS England Band 7 digital roles
- [ ] Apply to UCL ARC RSE (autumn round, September-November)
- [ ] Apply to Alan Turing REG
- [ ] Apply to Monzo / Wise / GoCardless / Cleo
- [ ] Apply to Mozilla UK remote roles
- [ ] Apply to Wellcome Trust engineering roles
- [ ] Begin LeetCode and system-design preparation for FAANG/fintech
- [ ] Consider Georgia Tech OMSCS Spring 2027 (applications August-September 2026)
- [ ] Consider AFSEE fellowship for LSE Inequalities (January 2027 deadline)
- [ ] Submit Chevening 2027/28 application by 7 October 2026
- [ ] Submit one freelance data-journalism pitch per month to openDemocracy / The Ferret / Tortoise
- [ ] File FOI requests via WhatDoTheyKnow and document methodology publicly

## Legal and Governance

- [ ] Research domain availability: wealthlens.uk, wealthlensuk.org
- [ ] Choose licence: MIT or AGPL-3.0 (for dashboard code)
- [ ] Incorporate WealthLens UK as CIC Limited by Shares at month 3-4 (~£130)
- [ ] Create data-licences.md documenting licence for each data source
- [ ] Create privacy policy for website
- [ ] Conduct full page-by-page licence audit for every think-tank dataset

## Finance

- [ ] Open a Cash ISA; start saving surplus monthly
- [ ] Build £5,000 emergency fund within 3-4 months of new role

## Community and People

- [x] Create contributors/onboarding/roles/thank-yous people files [completed: created, then moved to `../hq-private/projects/wealthlens/people/` with the private-repo split 2026-06-13]
- [ ] Create Discord server (delay until prototype exists): #general, #engineering, #data-research, #design, #content, #introductions
- [x] Write "About" page copy for future website [completed: 2026-05-16 — AboutView.vue on frontend]

## Personal Brand

- [ ] Create/update Linktree with all links
- [ ] Repurpose personal Instagram to promote inequality/data mission (gradual transition)
- [ ] Verify Bluesky handle via personal domain
- [ ] Set up Ghost blog on personal domain (or Substack mirror)
- [ ] Apply for FRSA via thersa.org
- [ ] Add openpoverty-uk to Civic Tech Field Guide directory [after building]
