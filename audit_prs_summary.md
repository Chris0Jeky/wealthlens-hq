# CC 2.1.154–2.1.158 Tool-Channel Corruption Audit — WealthLens HQ

Audit date: 2026-05-31
Auditor: Claude Code (Opus 4.6, CC 2.1.153)
Repo: wealthlens-hq (main branch, commit 41d5270)

## Audit script bug

The `audit_prs.sh` script has a jq bug: inside
`map(select(["FAILURE",...] | index(.)))`, the pipe `|` rebinds `.` to the
array literal, so `index(.)` becomes `index(the_whole_array)` which always
finds itself at position 0 (truthy). Every PR is falsely classified as FAILED
regardless of actual CI status. All 44 FAILED results are false positives.

## Current main health (raw exit codes)

| Suite | Result | Exit code |
|-------|--------|-----------|
| Simulator pytest | 648 passed in 8.12s | 0 |
| Simulator ruff | All checks passed | 0 |
| Simulator mypy | 0 issues in 44 source files | 0 |
| Dashboard backend pytest | 190 passed in 3.60s | 0 |
| Frontend vitest | 1138 passed (108 test files) in 19.41s | 0 |

## Summary table

| PR | Title | CI | diff_lines | diff-matches-claim | tests-pass-now | verdict |
|----|-------|----|-----------|-------------------|----------------|---------|
| 284 | docs: add Model Charter | PASS | 110 | yes | yes | CLEAN |
| 285 | docs: add AI/LLM disclosure policy | PASS | 99 | yes | yes | CLEAN |
| 286 | feat: sim package skeleton + registries | PASS | 477 | yes | yes | CLEAN |
| 291 | chore: batch Dependabot updates | PASS | 839 | yes | yes | CLEAN |
| 295 | feat(sim): top-tail Pareto reconstruction | PASS | 946 | yes | yes | CLEAN |
| 296 | feat(sim): provenance manifest + collector | PASS | 531 | yes | yes | CLEAN |
| 297 | feat(sim): Family A wealth tax | PASS | 742 | yes | yes | CLEAN |
| 298 | feat(reforms): Family B one-off levy | PASS | 1382 | yes | yes | CLEAN |
| 299 | feat(reforms): Family E HVCTS | PASS | 671 | yes | yes | CLEAN |
| 300 | feat(reforms): Family C CGT baseline | PASS | 688 | yes | yes | CLEAN |
| 301 | feat(reforms): Family D IHT baseline | PASS | 1148 | yes | yes | CLEAN |
| 302 | feat(reforms): Family F enforcement | PASS | 756 | yes | yes | CLEAN |
| 303 | feat(reforms): Family G devolution | PASS | 481 | yes | yes | CLEAN |
| 305 | fix(registry): document api_url field | PASS | 13 | yes (verified) | yes | CLEAN |
| 306 | fix(registry): YAML scientific notation note | PASS | 13 | yes | yes | CLEAN |
| 307 | fix(schema): constituent-nation validator | PASS | 55 | yes | yes | CLEAN |
| 308 | fix(loaders): robust path discovery | PASS | 231 | yes | yes | CLEAN |
| 311 | chore(deps): fastapi bump | PASS | 9 | yes (verified) | yes | CLEAN |
| 312 | chore(deps): uvicorn bump | PASS | 9 | yes | yes | CLEAN |
| 313 | chore(deps): js-cookie bump | PASS | 23 | yes | yes | CLEAN |
| 314 | chore: AGPL-3.0 license split | PASS | 309 | yes | yes | CLEAN |
| 315 | feat: populate sources.yml | PASS | 157 | yes | yes | CLEAN |
| 316 | feat: populate assumptions registry | PASS | 359 | yes | yes | CLEAN |
| 317 | feat: populate baselines.yml | PASS | 208 | yes | yes | CLEAN |
| 318 | feat(sim): Pydantic schema module | PASS | 556 | yes | yes | CLEAN |
| 319 | feat(sim): assumption + baselines loaders | PASS | 846 | yes | yes | CLEAN |
| 320 | docs(registry): clarify effective_date | PASS | 30 | yes | yes | CLEAN |
| 321 | fix(top-tail): safety guards + coercion | PASS | 193 | yes | yes | CLEAN |
| 322 | fix(provenance): strict typing + schedule | PASS | 202 | yes | yes | CLEAN |
| 323 | ci(sim): add CI workflow for sim | PASS | 107 | yes | yes | CLEAN |
| 324 | fix(iht): charitable gifts + RNRB cap | PASS | 190 | yes | yes | CLEAN |
| 325 | fix(security): patch tmp/uuid alerts | PASS | 159 | yes | yes | CLEAN |
| 326 | feat(sim): registries in wheel + resolver | PASS | 200 | yes | yes | CLEAN |
| 327 | feat(synth): synthetic-population generator | PASS | 414 | yes | yes | CLEAN |
| 328 | feat(rules): Scenario + run_scenario | PASS | 398 | yes | yes | CLEAN |
| 329 | feat(engine): engine.simulate (core) | PASS | 780 | yes | yes | CLEAN |
| 330 | feat(engine): devolution scope | PASS | 235 | yes | yes | CLEAN |
| 331 | feat(engine): enforcement uplift | NO_CHECKS* | 321 | yes (verified) | yes | CLEAN |
| 332 | feat(engine): interval propagation | NO_CHECKS* | 550 | yes (verified) | yes | CLEAN |
| 333 | feat(outputs): to_dashboard_json + goldens | PASS | 748 | yes | yes | CLEAN |
| 334 | feat(examples): headline-revenue demo | PASS | 195 | yes | yes | CLEAN |
| 335 | feat(synth): calibrate to ONS marginals | PASS | 572 | yes | yes | CLEAN |
| 336 | feat(enforcement): compliance baseline | PASS | 1082 | yes | yes | CLEAN |
| 337 | feat(synth): generation provenance | PASS | 245 | yes | yes | CLEAN |

*NO_CHECKS: #331 and #332 were stacked PRs based on feature branches (not
main). CI workflows trigger only on PRs to main, so no checks ran on these
branches. This is documented in ORCHESTRATION.md and is expected behavior.
Their code is now on main where all tests pass (648 sim tests, exit code 0).

## Verdict

**0 SUSPECT. 0 NO-OP. 44/44 CLEAN.**

No evidence of CC 2.1.154–2.1.158 tool-channel corruption affecting this repo.
All PRs contain substantive diffs matching their titles, CI passes where
configured, and the full test suite (648 sim + 190 backend + 1138 frontend =
1976 total tests) passes on current main with exit code 0.
