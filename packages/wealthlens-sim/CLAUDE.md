# Region: wealthlens-sim

UK wealth-policy microsimulation library (AGPL-3.0, own pyproject + CI lane ci-sim).
Engine + 7 policy families (A–G) + uncertainty propagation are BUILT and merged —
ignore any "pre-alpha skeleton" wording in older docs. Root seam map: `/AGENT_MAP.md`.

## Invariants

- Public entry point is `engine.simulate(...)` — the `engine/` package, NOT
  `run_scenario` (that name belongs to `rules.run_scenario`).
- Every parameter value traces to a cited source in repo-root `registries/`
  (bundled into wheel+sdist by `hatch_build.py`); provenance manifests on every output.
- The behavioural response layer stays standalone and default-OFF until cited
  base-share data exists (decision D-B, in `../hq-private/.../decisions/`) — never
  apply a sub-population elasticity to total family revenue.
- The synthetic population is illustrative but **already calibrated** to the cited ONS
  WAS GB total (`ONS_WAS_TOTAL_WEALTH_GBP = £13.568tn`, WAS Apr 2020–Mar 2022;
  `test_synth::test_defaults_match_public_ons_wealth_marginals` pins total/median/top-decile).
  Do not "re-calibrate" the defaults — they are anchored. GB-only (NI excluded).
- `outputs.to_dashboard_json` is a versioned public contract (golden files pin it).

## Verify

`cd packages/wealthlens-sim && python -m pytest -q` (~853 tests). CI: ci-sim on
3.11 + 3.12 with a 90% coverage gate. ruff + mypy use this package's OWN
`pyproject.toml` config (`[tool.ruff]`/`[tool.mypy]`), not the repo root's.
