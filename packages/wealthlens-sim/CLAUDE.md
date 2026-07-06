# Region: wealthlens-sim

UK wealth-policy microsimulation library (AGPL-3.0, own pyproject + CI lane ci-sim).
Engine + 7 policy families (A–G) + uncertainty propagation are BUILT and merged —
ignore any "pre-alpha skeleton" wording in older docs. Root seam map: `/AGENT_MAP.md`.

## Invariants

- Public entry point is `engine.simulate(...)` — NOT `run_scenario` (that name belongs
  to `rules.run_scenario`).
- Every parameter value traces to a cited source in repo-root `registries/`
  (bundled into wheel+sdist by `hatch_build.py`); provenance manifests on every output.
- The behavioural response layer stays standalone and default-OFF until cited
  base-share data exists (decision D-B) — never apply a sub-population elasticity to
  total family revenue.
- The synthetic population is illustrative (~£26tn vs ~£15–16tn real UK wealth) and
  must stay labelled as such; calibrate to cited WAS marginals before publishing figures.
- `outputs.to_dashboard_json` is a versioned public contract (golden files pin it).

## Verify

`cd packages/wealthlens-sim && python -m pytest -q` (~853 tests). CI: ci-sim on
3.11 + 3.12 with a 90% coverage gate. Full `vitest`-style watch modes don't exist here;
ruff + mypy run via the root config.
