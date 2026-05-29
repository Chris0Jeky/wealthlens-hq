# WealthLens Registries

Machine-readable metadata for the WealthLens-Sim microsimulation platform.

Blueprint v5 §13.6 places these under `wealthlens/data_registry/` inside the
package. This repo keeps registries at the monorepo root so they are shared
across the simulator, dashboard, and data pipelines without requiring a package
install. Python loaders in `wealthlens_sim.assumptions` reference these files
via repo-relative paths.

## Files

### `sources.yml`

Catalogue of all data sources used in WealthLens pipelines and models. Each
entry records: id, name, URL, access date, format, licence, update pattern, and
notes. Every dataset cited in a WealthLens output must have a corresponding
entry here.

### `assumptions.yml`

Every modelling assumption with source, range, and transferability score.
Schema follows Blueprint v5 section 7.6. Assumptions are surfaced in dashboard
tooltips and provenance manifests so that users can see which priors drive each
estimate.

### `baselines.yml`

Policy-lever status matrix tagging every modelled policy by its legal status as
of the modelling date: current-law, enacted-future, announced,
consultation-stage, or hypothetical. Schema follows Blueprint v5 section 3.1.

## Principles

- Every derived variable traces to an entry in `sources.yml`.
- Every published number cites the assumption IDs it depends on.
- Every policy scenario carries a baseline version tag.
- Registries are versioned with code in git and queryable via Python loaders
  in `wealthlens_sim.assumptions`.
