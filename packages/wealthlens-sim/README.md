# WealthLens-Sim

Open, uncertainty-aware UK wealth-policy microsimulation platform.

## Status

**Pre-alpha** -- package skeleton only. No functional simulation code yet.

## What this package will do

WealthLens-Sim compares wealth-focused reform packages under a common evidence
standard, with the live UK policy environment as its operational anchor. It is
designed to wrap [PolicyEngine-UK](https://policyengine.org/uk) with:

- **Top-tail reconstruction** of UK wealth distributions (Pareto, GPD, rank
  correction) with uncertainty intervals
- **Seven policy families** (A: annual wealth tax, B: one-off levy, C: CGT
  reform, D: IHT/transfer, E: property tax, F: enforcement, G: devolution)
- **ONS National Balance Sheet reconciliation**
- **Provenance manifests** on every published number
- **Behavioural wrappers** with transferability scoring (Phase 3)

## Relationship to WealthLens HQ

This package lives inside the
[wealthlens-hq](https://github.com/Chris0Jeky/wealthlens-hq) monorepo. The
Vue 3 dashboard and FastAPI backend in `projects/wealthlens-dashboard/` serve
as the public-facing layer; this package provides the simulation engine.

## License

AGPL-3.0-or-later. See [LICENSE](./LICENSE) for the full text.

The AGPL license is chosen for compatibility with PolicyEngine-UK (also
AGPL-3.0) and to prevent private capture of a public-interest simulator.
The dashboard frontend and existing data pipelines remain MIT-licensed.
