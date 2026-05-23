# WealthLens-Sim: Model Charter

Last updated: 2026-05-23

## Purpose

WealthLens-Sim is an open, uncertainty-aware UK wealth-policy microsimulation platform. It compares wealth-focused reform packages under a common evidence standard, with the live UK policy environment as its operational anchor.

## Core research question

Under imperfect UK wealth data, which wealth-focused policy packages most robustly raise revenue, reduce wealth concentration, protect low-liquidity households, limit avoidance and migration risk, and remain administratively credible?

## What WealthLens-Sim is

- An open simulation engine and public visualiser
- A platform for comparing reform packages (seven policy families A--G)
- Explicitly uncertainty-aware --- intervals by default, no naked point estimates
- Focused on wealth stocks and stock-flow interactions
- Honest about behavioural unknowns
- Built on rules-as-code and reproducible pipelines
- Public-facing and research-grade from the same backend

## What WealthLens-Sim is not

- An advocacy site for one preferred tax
- A claim that one instrument is obviously optimal
- A point-estimate revenue calculator
- A general living-standards model
- A model that pretends elasticities are settled
- A campaign calculator with academic language

## Policy families

The simulator compares seven policy families:

- **Family A**: Annual net wealth taxes
- **Family B**: One-off wealth levy
- **Family C**: Capital gains reform
- **Family D**: Inheritance and lifetime-transfer reform
- **Family E**: Property-tax reform (including HVCTS)
- **Family F**: Enforcement and information reform
- **Family G**: Devolution-asymmetric reform

## Baseline legal-status tags

Every policy lever is tagged by its legal status as of the modelling date:

- **Current law**: In force on the modelling date
- **Enacted future law**: Legislation passed but with future commencement
- **Announced**: Formally announced but not yet enacted
- **Consultation-stage**: Under active public consultation (design parameters still moving)
- **Hypothetical**: Not announced, enacted, or in force; modelled as counterfactual

## Assumption registry

Every assumption is machine-readable and traceable (see `registries/assumptions.yml`). Fields include: assumption_id, domain, value_or_distribution, source, transferability_score, valid_range, applies_to, last_reviewed, notes. Every published number cites the assumption IDs it depends on.

## Data principles

1. **Provenance first** --- every derived variable needs source, imputation method, version, and uncertainty tag
2. **Multiple baselines** --- survey-only, top-tail-corrected, macro-reconciled, and stress-test variants
3. **Observed vs imputed vs synthetic** is always visible
4. **Macro reconciliation** is explicit
5. **No overfitting** to rich lists
6. **Northern Ireland** is explicit (GB-only or UK-imputed, labelled)
7. **NBS figures** are versioned
8. **No named-person wealth inference** in public outputs

## Privacy statement

- WealthLens never publishes inferred wealth estimates for named individuals
- WealthLens never combines public records to create avoidable de-anonymisation
- Privacy review required before linking PSC, Land Registry, rich-list, and admin proxies
- Secure-data constraints kept separate from public synthetic outputs
- Aggregate cells sized to prevent re-identification

## Licensing

- **Simulator core** (`packages/wealthlens-sim/`): AGPL-3.0-or-later
- **Dashboard frontend and data pipelines**: MIT
- **Visualisations and methods notes**: CC-BY-4.0
- **Synthetic public datasets**: CC0

## AI/LLM disclosure

See `docs/AI_LLM_DISCLOSURE.md` for the full disclosure policy. Summary: LLMs are used as development tooling (code review, documentation drafting, schema design). LLMs are never used to generate model outputs, set behavioural priors, or write quoted policy positions.

## Validation gates

The simulator must pass nine validation gates (0--8 plus dashboard safety) before public launch. See `docs/gates/` for individual gate specifications. No gate may be skipped. Each gate has explicit pass/fail criteria.

## Backwards-compatibility commitment

Every published baseline is maintained as runnable for at least three years from release. Deprecated baselines are clearly marked but not deleted.

## The discipline answer

> WealthLens does not think anything about policy. It scores policies under explicit assumptions. Personal views of the team are held separately and not branded WealthLens.
