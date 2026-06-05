# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.
>
> **POST-MERGE CLEANUP COMPLETE** (2026-05-16): All 192 PRs handled, 874 tests passing, CI green, 496 stale branches deleted.
> Merge history: [MERGE_ORCHESTRATION.md](.codex/memories/session_notes/MERGE_ORCHESTRATION.md) | PR creation history: [ORCHESTRATION.md](.codex/memories/session_notes/ORCHESTRATION.md) (archived)

Last updated: 2026-06-05

## Latest status (2026-06-05 endless-cycle)

> Full live detail in `.codex/memories/session_notes/ORCHESTRATION.md` (master
> control). This board is the short version.

**Session 3 (loop resumed):** ran a 5-agent understanding sweep (bug-sweep = 4
false positives; sim core solid). Merged **#358** (gate mypy on automation/ + fix
26 errors), **#359** (new `uncertainty/sobol.py` — Sobol sensitivity indices,
Saltelli/Jansen, no SALib, 801 sim tests), and **#360** (gate mypy on root tests/ +
fix 14 errors). **#361** open/aging (data-integrity: reject blank/NaN numeric cells
in the GDHI + tax-composition pipelines). Each PR: 2 independent adversarial reviews
+ all bot threads resolved + CI green. automation/ AND tests/ are now mypy-gated.
The #361 review surfaced the same NaN-leak class in `fetch_ons_wealth`/`fetch_ons_housing`
+ a `validate.py` gap — seeded as the next PRs (see ORCHESTRATION "Next tasks").

- **Merged to main (2026-06-04 cycle):** #338–#348 (11 PRs) — uncertainty
  sampling (#338) + propagation (#345) + engine MC wiring (#346), the
  ConfidenceFanChart (#347), the `/api/simulator` bridge (#348), the #339
  data-integrity revert, and 5 Dependabot bumps (#340–#344).
- **Merged to main (2026-06-05 session 2):**
  - **#349** (`8c17153`) — live `/simulator` scenario page. Review caught two real
    `useFetch` stale-write races (post-`json()` boundary + cleared-URL
    invalidation); both fixed with regression tests.
  - **#350** (`5e3d7c3`) — CI hardening. `make ci-quick` no longer swallows
    failures (runs real ruff+mypy+201 pytest); `requirements-dev.txt` pins
    ruff/mypy/httpx/pandas-stubs for a clean install; Dependabot auto-merge
    workflow + job timeouts.
- **Open PRs (1):** **#351** `feat/simulator-static-publish` — publishes the
  simulator JSON + `scenarios.json` statically and un-gates `/simulator` + nav
  link (in the real `AppHeader`, not the dead `NavBar`). 2 gemini + 3 codex
  findings all addressed; CI green. Aging, then merge first next cycle.
- **ci-quick swallow: FIXED** in #350 (was the long-standing verification caveat).
  Remaining reliability follow-up: the `automation/data-pipelines` suite is not in
  CI and `test_validate` fails with 12 validation errors (dtype/dupes/range) — see
  `tasks/inbox.md`.

## Current phase: Wave 13 calibration and extension

**2026-05-30 cycle:** Built the full Wave 12 PR3 engine as a 5-PR stack + a Wave 13
example, each with 2 independent adversarial reviews + all bot comments addressed:
- `engine.simulate(population, scenario, *, registries, devolution, enforcement)
  -> EngineResult` — wires synth→rules→provenance; equal-weight per-decile
  attribution; Family G devolution scope; Family F enforcement uplift; real
  interval propagation from the top-tail Pareto alpha range with a complete
  provenance manifest; `outputs.to_dashboard_json` (+ golden files) emitting the
  dashboard contract with root-level `provenance_complete` + a `caveats[]` array;
  `examples.headline_revenue` runnable demo.
- **Merged to main:** #329 (engine-core), #330 (devolution), #331 (enforcement),
  #332 (intervals), #333 (dashboard JSON outputs), #334 (headline example),
  #335 (synth ONS/WAS calibration and provenance), and #336 (enforcement
  compliance model). **645 sim tests pass locally on main after #336.**
- **Open:** #337 `feat/synth-generation-provenance` -> main records synth
  generation-input tags in population provenance. It is the newest open PR and
  still needs the full 2-review adversarial cycle plus a newer PR above it before
  merge.
- Reviews caught real issues (decile non-conservation for tiny weights, provenance
  overclaiming, enforcement-overstatement + unsourced-state surfacing in the
  dashboard contract, headline honest-labelling). 33 stale branches pruned.
- Backlog (tasks/inbox.md Wave 13): review/drain #337 once aged;
  Monte-Carlo/Sobol uncertainty; wire the dashboard JSON into a Vue scenario
  page.

## Prior phase: Gate-1 Simulator merged → Wave 12 (engine/synth)

**2026-05-29 MERGE+ADVANCE cycle:** All 38 open PRs resolved. The entire Gate-1
`packages/wealthlens-sim` simulator (skeleton, schema, registry loaders, top-tail
Pareto reconstruction, provenance, all 7 policy families A–G) is now MERGED to
`main` via PRs #284–#323. 523 sim tests pass locally. All adversarial-review
findings addressed (int-truncation, ci-validation, faithful schedule preservation);
CI gap (sim untested) closed by ci-sim.yml (#323). Dependabot cleared.
Backlog seeded: IHT v0.1 limitations + registry packaging (LOW). See
[ORCHESTRATION.md](session_notes/ORCHESTRATION.md) for the full merge-train log.
Next: Wave 12 — static engine + synthetic household generator.

## Prior phase: Ready to Ship — Feature Complete v0.1 (dashboard)

All dashboard code is on main. Site live. Codebase includes:
- 10 data pipelines (WID, ONS housing, CGT, wealth-by-decile, productivity-pay, GDHI, tax composition, BoE rates, child poverty, generational wealth)
- Vue 3 frontend: 40+ components/composables, dark mode, broadsheet chart redesign, WCAG AA, analytics
- FastAPI backend: health, data, metadata, columns, summary stats, CSV download, security headers, GZip, rate limiting
- Latest frontend coverage in cleanup verification: 1125 tests passing; backend targeted/API checks green.
- CI/CD: ruff, mypy, bandit, pytest, ESLint, vue-tsc, vitest coverage, vite build, Playwright E2E, Lighthouse, CodeQL, and Deploy all green on latest main.
- Deployment: GitHub Pages auto-deploy on push to main

### Active focus areas

| Area | Status | Next step |
| --- | --- | --- |
| **WealthLens-Sim** | Gate 1 + Wave 12 engine + #337 provenance MERGED; #338 uncertainty-sampling + #339 IHT review fixes open | Drain #339 and #338 once aged; wire sampling into engine or dashboard JSON into Vue |
| Sim CI | `ci-sim.yml` runs ruff+mypy+pytest (py3.11/3.12) + weekly; 651 sim tests on main | Maintain; add coverage of new modules |
| Sim packaging | registries bundled into wheel+sdist (hatch hook); pip-installable | — |
| Data pipelines | 8+ pipelines on main | Maintain; add new pipelines as needed |
| Charts (v0.1) | Live (4 charts + broadsheet redesign) | Build more chart components in Vue |
| Backend API | Full-featured (health, data, metadata, columns, CSV, summary stats) | Deploy to staging |
| Frontend | Vue 3 + TS + Pinia + TailwindCSS with dark mode, a11y, analytics | Wire up remaining chart components |
| Deployment | Live at chris0jeky.github.io/wealthlens-hq/ | Automatic on push to main |
| Testing | Latest frontend coverage: 1125 tests passing; backend targeted/API checks green in cleanup | Maintain coverage |
| CI/CD | Latest relevant main workflows green - Backend on `09c4ea5`, Frontend/CodeQL/E2E/Lighthouse/Deploy on `1f5318e` | Monitor for failures |
| Social assets | chart_to_social.py generates 4 platform sizes | Generate assets for first LinkedIn post |
| Social accounts | Twitter/X + Bluesky created | Update LinkedIn profile, write first post |
| Outreach | Emails sent to mySociety + Democracy Club | Follow up |
| GitHub Issues | Previously created (good first issue + help wanted) | Share in first LinkedIn post |
| Reading | *The Trading Game* started | Continue; start Piketty when it arrives |
| Newsletters | 5 subscribed | Ongoing — read and note insights |

### Recent activity

- 2026-05-29: **MERGE CYCLE + GATE-1 SIM + WAVE 12 START.** Cleared all 38 open PRs (0 remain). Merged the entire Gate-1 simulator to main (skeleton, schema, loaders, top-tail Pareto reconstruction, provenance, Families A–G; PRs #284–#326). Fixed all adversarial-review findings as their own reviewed PRs: top-tail int-truncation/ci-validation (#321), provenance faithful-schedule (#322), **CI gap** — added `ci-sim.yml`, the simulator was never run in CI (#323), IHT charitable/RNRB data-integrity (#324), **security** — patched tmp/uuid → 0 Dependabot alerts (#325), registry wheel+sdist packaging (#326). Wrote Wave 12 design doc + merged PR1 `synth/` (#327) and PR2 `rules/run_scenario` (#328). Every PR had 2 independent adversarial reviews; the gate caught a real sdist-uninstallable bug and a dispatch/contract drift. 564 sim tests; 0 alerts. Next: Wave 12 engine PR (task #17).
- 2026-05-17: **PR CLEANUP RESUME COMPLETE** - reviewed, repaired, and merged PRs through `#272`; latest relevant main workflows are green (`#271` CI Backend after backend changes; `#272` Frontend, CodeQL, E2E, Lighthouse, and Deploy); zero open PRs remain.
- 2026-05-17: Fixed final merge train issues: OG coverage for wage-stagnation, Bandit-safe version metadata without subprocess, chart registry merge conflicts, Playwright assertions, i18n test plugins, and package metadata conflicts.

- 2026-05-16: **REPO CLEANUP** — deleted 496 stale branches (292 local + 204 remote), updated all docs
- 2026-05-16: Post-merge health check — all CI green, 874 tests passing
- 2026-05-16: Merge session complete — 192 PRs handled (155 merged, 21 closed, 10 Dependabot, 6 deferred)
- 2026-05-16: Deployed Vue frontend to GitHub Pages as master site
- 2026-05-15: Scaffolded FastAPI backend + Vue 3 frontend; deployed v0.1 with 4 charts

### Guardrails snapshot

- No production deployment yet — all changes are local/greenfield.
- Data integrity: every dataset cites source, URL, and access date.
- Open source: all code will be public. Never commit secrets.
- Volunteers will read this code — clarity over cleverness.

### Best next actions

1. Update LinkedIn profile (headline, about, featured) — link to live site
2. Write and publish first LinkedIn post — "Why I'm building WealthLens UK"
3. Wire up first Vue chart component using the data store + API
4. Make first open-source PR to mySociety, Democracy Club, or TJN repos
5. Send outreach emails now unblocked by v0.1 deployment (TJN, Equality Trust, Gary Stevenson)
6. Handle deferred major dependency upgrades (pandas 3, TypeScript 6, Vite 8) when ready
7. Deploy backend to staging environment
