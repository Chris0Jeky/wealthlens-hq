# Active Sprint

Last updated: 2026-06-27

> **SESSION 11 (2026-06-26) — CHECKPOINT: 4 PRs merged, 0 open, main green.**
> H1-08/H1-09 stayed infra-blocked (Docker daemon down, no report PDFs), so the
> session shipped the seeded CGT enrichment then ran a 4-area offline-defect sweep
> and fixed every confirmed finding. **Merged:** **#446** H1-07 CGT band-range +
> cumulative-concentration chunks (serves golden G-007/G-008; data-honesty clamp,
> 2-lens review caught + fixed a real "gains account for taxpayers" category error);
> **#447** `validate.py` now covers all 11 datasets (+ a drift guard) and tolerates
> BoE honest-missing NaN without admitting a wholesale-blank column; **#448** the
> analyst spend-cap parser rejects nan/inf/non-positive (fail-closed, ADR-0002 —
> nan would have let the cap never trip); **#449** `/api/data/metadata` degrades
> per-dataset instead of 503-ing the whole citations catalog, plus a REQUEST_TIMEOUT
> positive/finite floor and a rate-limit health-path trailing-slash exemption. Each:
> 2 independent adversarial-review lenses + every gemini bot comment addressed +
> green CI. **Mid-session Chris started Docker → H1-09 is now UNBLOCKED** (analyst-db
> container verified up on :15432, migrations at head). **NEXT SESSION:** **H1-09**
> (wire CGT/WAS/HMRC chunks → DB → FTS → embed; embed gated on `OPENAI_API_KEY`) is
> the top task; then the **prettierrc** full-adoption PR (scoped + Chris-authorised,
> plan in `inbox.md`); then another offline-defect sweep if both stall. Full state:
> `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md`.

> **SESSION 10 (2026-06-26) — WRAPPED.** Found main CI was actually **RED**
> (two scheduled jobs drifted after the 06-19 push): fixed the `CI Simulator`
> mypy/numpy PEP695 break (**#441**, `python_version=3.12`); diagnosed + seeded
> the `Weekly Data Update` failure (upstream ONS drift — validate.py correctly
> blocked bad data; network/decision-blocked). **Drained 12 of 14 Dependabot PRs**
> one-at-a-time after a 14-agent changelog/usage/CI review (#439/#434/#437/#391/
> #390/#440/#396/#435/#438/#433/#394/#436); **main green + deployed**. Shipped
> **H1-02** golden-question reword + source_id mapping, zero answers (**#442**).
> Chris then decided the last two: **#402 vue-router 4→5 APPROVED** → landed via
> **#444** (re-created clean after #402 went stale + dependabot wouldn't rebase);
> **#397 mypy** → **adopted mypy 2.x repo-wide** via **#443** (cap `<2`→`<3` in
> root/backend/analyst + added a `<3` ceiling to sim; fixes the CI-vs-local drift;
> verified green on every package CI). **All 14 Dependabot PRs now drained; 0 open
> PRs; main green across every workflow + deployed.** Also shipped **H1-07**
> (#445): tabular-source rendering in the analyst's `slice_corpus.py` — citable
> chunks from WAS/HMRC processed data, fail-closed data-honesty allowlist, full
> provenance, 12-test lock, 2-lens adversarial review (all findings fixed). Full state:
> `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md`.

> **SESSION 9 WRAPPED (2026-06-19).** main green; **only the 8 held Dependabot PRs are
> open** (everything built this session is merged). **Shipped this session (16 PRs):**
> cycle 2 — #415/#405/#417/#416/#418; **Chart accessibility (9/9 charts)** —
> #419/#420/#421/#422/#423/#424/#425/#426/#427 each ship an `AccessibleDataTable`
> fallback (WCAG 1.1.1), built via parallel worktree fan-outs + 2-lens adversarial
> reviews; **systemic null→0 data-integrity fix** — #428 shared `toNumberOrNaN`
> (utils/chart.ts) guarding every parser (missing cell → "—", never a fabricated 0) +
> #430 consolidated the last 5 charts onto it + fixed the stacked-total/series-alignment
> consequences; **#431** corrected the discredited wealth figures in the redesign mockups
> (+ marked superseded); **#432** killed the compiled-`.js`-shadow footgun (`vue-tsc -b
> --noEmit` + `clean:shadows` prebuild/pretest hooks). Reviews caught real bugs
> throughout (false "net negative wealth" aria-label, wrong HBAI source citation, many
> null→0 fabrications, a CI-breaking validate-on-gitignored-CSVs PR that was correctly
> CLOSED). **Held for Chris (8):** #390 fetch-metadata3 & #402 vue-router5 (majors);
> #391 plotly, #396 uvicorn, #399 vue, #393 vue-i18n (prod); #394 pandas-stubs, #397
> mypy<3 (dev-major). **Open questions put to Chris at wrap-up** (Dependabot triage,
> H1-02, docs data-array re-sync, prettier reconcile, gdhi granularity, cron fate).
> Full state: `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md`.

> **PRIOR (2026-06-13 — session 8 autonomous build loop):** 5 PRs merged to main,
> each with a planning workflow + 2 independent adversarial-review lenses + green CI:
> **#406** H1-01 (tag Hero #1 corpus slice: 8 sources in `registries/sources.yml`),
> **#407** H1-12 (pure RRF fusion `retrieval/fuse_rrf.py` + 15 tests),
> **#408** PR-8 (rate-limit overflow characterisation test, mutation-verified),
> **#409** WL-001 (**fixed a 100× unit bug** on the WID wealth-shares chart — shares
> were plotted as fractions on a % axis, showing ~0.5% vs the true 57% — and wired the
> unused `AccessibleDataTable`, WCAG 1.1.1), **#410** PR-5 (productivity-pay
> "illustrative data" caveat, 4-layer data-honesty fix). Dependabot #392 closed (mypy
> conflict). New data-integrity item flagged for Chris (`ACTION-REQUIRED` #9: the
> wealth-shares stat cards "28%"/"1980=50%" don't match the now-correct WID series).
> Wave 4 in flight: WL-003/007 (inheritance-tax metadata + chart-contract test).
> Full state: `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md` (session 8).

> **Prior (2026-06-11 — Hero #1 launched):** PRs #403 (kickoff: plan/backlog/ADRs/
> scaffolding/evals) + #404 (Postgres+pgvector + Alembic, live-verified) MERGED. Next
> unblocked: H1-01 (tag corpus slice), H1-02 (@Chris: review 20 golden questions),
> H1-12 (RRF). See `tasks/hero1-backlog.md` + `docs/plan/HERO1_PLAN.md` (LOCKED).
>
> **Prior (2026-06-05 — session 3 loop wrapped):** 11 PRs merged (#358-#368), main
> `c3712e3`, **0 open PRs, 1025 tests green**, repo spotless. Highlights: mypy gated on
> `automation/` + root `tests/`; new `uncertainty/sobol.py`; the full blank-cell→NaN
> data-integrity arc across every pipeline + a `validate.py` NONFINITE backstop + shared
> `_cells.to_finite_float`; and the **flagship behavioural layer groundwork** —
> `behavioural/response.py` (cited reduced-form revenue-response factor) + `registry.py`
> (cited-channel loader), standalone/default-OFF. Each PR: 2 adversarial reviews + all bot
> threads + green CI.
>
> **Behavioural engine-apply is BLOCKED on cited base-share data** (deferred to Chris — see
> ORCHESTRATION "❓ DEFERRED QUESTIONS"). Recommended next when the loop resumes: **B1 —
> assumption-source citation URLs**. Re-run `/loop keep going` to resume.

> **⚑ See [`ACTION-REQUIRED.md`](ACTION-REQUIRED.md)** for Chris's outstanding
> human action items (job application due today, LinkedIn launch, outreach emails,
> domain, and a ci-quick fix decision). The agent surfaces these every summary.

This week's focus. Keep this list to 5-7 tasks.

> **NEXT SESSION START HERE:** Wave 13 is active. Read
> `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md` (private sibling repo; top "🟢 HANDOFF" section) first —
> it has the full state, where to start (#337 synth generation provenance review/aging), the engine
> architecture, the backlog, and the ops gotchas. Quick status below.

## Sprint: 2026-05-30 to 2026-06-06 (Wave 13 — calibrate, surface, extend)

**Status:** Full Wave 12 engine is on `main` through **#335**, and Wave 13 #336
`feat/enforcement-compliance-model` is merged. **#337**
`feat/synth-generation-provenance` is open as the newest Wave 13 PR. Do not merge
#337 while it is newest; run the full two-review gate, fix every finding/comment,
and open another PR above it first.

1. - [x] **Drain PR #333** (`outputs.to_dashboard_json` + golden files + the
   provenance-label/caveat bot fixes) → main (@Chris) [completed: 2026-05-30]
2. - [x] **Calibrate the synth generator to CITED public WAS/ONS marginals** — PR
   #335 merged after two adversarial reviews, bot-thread cleanup, green CI, and
   a newer PR above it. (@Chris) [completed: 2026-05-30]
3. - [x] **Drain PR #334** (headline-revenue example) after a new PR lands above it (@Chris) [completed: 2026-05-30]
4. - [x] **Review/drain #336 proper enforcement compliance model** — merged to
   main after two independent adversarial review rounds; fixed enforcement cost
   vs revenue, NAO year/source, interval invariants, and enforcement provenance.
   (@Chris) [completed: 2026-05-30]
5. - [x] Wave 13: review/drain #337 synth generation provenance — merged to main
   at `94446e3` after two independent adversarial reviews, all bot threads
   resolved, green CI, and a newer PR (#338) opened above it. (@Chris) [completed: 2026-05-31]
6. - [x] Wave 13: drain #338 `feat/uncertainty-sampling` — **merged** to main
   (`3b31de2`) after 7 codex P2 rounds + 4 adversarial reviews. (@Chris) [completed: 2026-06-04]
7. - [~] Wave 13: build the uncertainty **propagation** layer (#345) + wire it into
   the engine as an optional Monte-Carlo revenue band, default OFF (#346, stacked
   on #345). #345 merge-ready; #346 under review. Then: more sampled parameters
   (assumption RangeValues), Sobol sensitivity, and a Vue ConfidenceFanChart that
   renders the dashboard JSON band + caveats. See `tasks/inbox.md`. (@Chris)

## Completed sprint: 2026-05-29 to 2026-06-05 (Wave 12 engine)

**Context:** The entire Gate-1 simulator (skeleton, schema, loaders, top-tail
reconstruction, provenance, all 7 policy families A–G) is MERGED to `main` (PRs
#284–#326). Wave 12 (the engine driving them) is underway: `synth/` (#327) and
`rules/run_scenario` (#328) merged. 564 sim tests pass; ci-sim green; 0 open PRs.

1. - [x] CI gap: add `packages/wealthlens-sim` to CI — ci-sim.yml + types-PyYAML + scipy mypy override (PR #323) (@Chris) [completed: 2026-05-29]
2. - [x] IHT v0.1: deduct charitable bequest from estate; cap RNRB at residence value (PR #324) (@Chris) [completed: 2026-05-29]
3. - [x] Security: patch tmp/uuid Dependabot alerts via npm overrides (PR #325) (@Chris) [completed: 2026-05-29]
4. - [x] Package registries into wheel+sdist via hatch build hook + resolver fallback (PR #326) (@Chris) [completed: 2026-05-29]
5. - [x] Wave 12 PR1 `synth/`: deterministic synthetic-population generator (PR #327) (@Chris) [completed: 2026-05-29]
6. - [x] Wave 12 PR2 `rules/`: Scenario + run_scenario over the population (PR #328) (@Chris) [completed: 2026-05-29]
7. - [x] **Wave 12 PR3 `engine/`** (built as a 5-PR stack): `engine.simulate(population, scenario, *, registries, devolution, enforcement) -> EngineResult` — synth→rules→provenance, real interval propagation, equal-weight per-decile attribution, F/G composition, `outputs.to_dashboard_json` + golden + a runnable example (@Chris) [engine merged: 2026-05-30; #333/#334/#335 merged]
   - 3a `feat/engine-core` **#329 merged** · 3b devolution **#330 merged** · 3c enforcement **#331 merged** · 3d intervals **#332 merged** · 3e outputs **#333 merged** · Wave-13 example **#334 merged**. Each: 2 adversarial reviews + all bot comments addressed.

## Why These

- **Merge cycle (1–4):** cleared all 38 open PRs with rigour; closed the CI gap (simulator was untested in CI), the IHT data-integrity simplifications, the security alerts, and the pip-install packaging gap — each its own reviewed PR.
- **Wave 12 (5–7):** the policy families existed but nothing drove them. `synth/` supplies a population, `rules/` runs a scenario over it; the **engine PR (7)** ties synth→rules→provenance into a single `EngineResult` — the first end-to-end headline-revenue number. Then `outputs/` formats it for the dashboard.
- **Follow-ups (backlog, not this sprint):** review/drain #337 synth generation provenance; Monte-Carlo uncertainty (Wave 13); real WAS/FRS microdata behind the Protocol seam.

## Completed This Sprint

- [x] Extract all research insights, action items, contacts, and data sources into structured files (@Chris) [completed: 2026-05-14]
- [x] Create initial WealthLens HQ scaffold (@Codex) [completed: 2026-05-14]
- [x] Order *The Trading Game* by Gary Stevenson and *A Brief History of Equality* by Piketty; begin reading (@Chris) [completed: 2026-05-14]
- [x] Create Twitter/X account and Bluesky account (@Chris) [completed: 2026-05-14]
- [x] Build 3 data pipelines + interactive Plotly charts: WID wealth shares, ONS housing affordability, HMRC CGT concentration (@Chris) [completed: 2026-05-14]
- [x] Send volunteer emails to mySociety and Democracy Club (@Chris) [completed: 2026-05-14]
- [x] Subscribe to 5 key newsletters: Resolution Foundation, Tax Policy Associates, Milanovic, Tooze, IFS (@Chris) [completed: 2026-05-14]
- [x] Scaffold FastAPI backend with health, data, metadata endpoints (@Chris) [completed: 2026-05-15]
- [x] Scaffold Vue 3 + TypeScript + Pinia + TailwindCSS frontend (@Chris) [completed: 2026-05-15]
- [x] Deploy Vue frontend to GitHub Pages as master site (@Chris) [completed: 2026-05-16]
- [x] Merge all ~192 PRs (10 waves of reviewed, stacked PRs) — zero open PRs remain (@Chris) [completed: 2026-05-16]
- [x] Resume interrupted PR cleanup and merge remaining reviewed PRs through #272; final main CI green and zero open PRs remain (@Codex) [completed: 2026-05-17]
- [x] Post-merge health check — fix lint, types, tests; 874 tests passing, all CI green (@Chris) [completed: 2026-05-16]
- [x] Clean up 292 local + 204 remote stale branches (@Chris) [completed: 2026-05-16]
