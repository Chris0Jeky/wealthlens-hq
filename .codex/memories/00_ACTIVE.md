# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.
>
> **POST-MERGE CLEANUP COMPLETE** (2026-05-16): All 192 PRs handled, 874 tests passing, CI green, 496 stale branches deleted.
> Merge history: [MERGE_ORCHESTRATION.md](.codex/memories/session_notes/MERGE_ORCHESTRATION.md) | PR creation history: [ORCHESTRATION.md](.codex/memories/session_notes/ORCHESTRATION.md) (archived)

Last updated: 2026-05-30

## Latest Wave 13 status (post #336 merge)

- **Merged to main:** #336 `feat/enforcement-compliance-model` after two
  independent adversarial review rounds, all findings fixed, Gemini thread
  resolved/outdated, CI green, and a newer PR opened above it. Enforcement cost
  is now separate from revenue (`enforcement_cost_bn`,
  `enforcement_net_fiscal_impact_bn`); dashboard schema is `1.2`; 645 sim tests
  pass locally on main after #336.
- **Open/newest:** #337 `feat/synth-generation-provenance` -> `main`, recording
  `synth.seed` and `synth.pareto_alpha` in population provenance. Its Gemini
  comment was addressed and resolved; local verification on the rebased branch is
  646 sim tests + ruff + mypy passing; GitHub checks are green and merge state is
  clean. Do not merge #337 while newest.

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
  generation tags in population provenance. It is the newest open PR and still
  needs the full 2-review adversarial cycle plus a newer PR above it before
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
| **WealthLens-Sim** | Gate 1 + Wave 12 engine/output stack + #336 enforcement compliance MERGED to main | Review/drain #337 synth generation provenance, then open the next Wave 13 PR above it |
| Sim CI | `ci-sim.yml` runs ruff+mypy+pytest (py3.11/3.12) + weekly; 645 sim tests on main after #336 | Maintain; add coverage of new modules |
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
