# WealthLens: AI and LLM Disclosure Policy

Last updated: 2026-05-23

## Why this policy exists

LLMs are pervasive in 2026 academic and policy workflows. Pretending otherwise is the new HARKing (Hypothesising After the Results are Known). This protocol is the disclosure standard WealthLens commits to.

WealthLens's credibility depends on the chain of reasoning being inspectable. LLMs are inspectable when used as tools (the human reviewer can check the output); they are not inspectable when used as oracles (the LLM's reasoning is opaque). This policy separates these two uses.

A project that uses LLMs heavily and does not say so will eventually have that fact discovered and used against it. Pre-disclosure is the only sustainable position.

## What is declared

| Category | Disclosure requirement |
|---|---|
| Code generation | Lines or modules drafted with LLM assistance are tagged in commit messages; significant LLM-drafted sections noted in CONTRIBUTING.md |
| Literature search | LLM-assisted literature discovery declared in paper acknowledgements |
| Data labelling / classification | LLM-assisted labels disclosed in methods section; sample validated by human reviewer |
| Imputation | Any LLM use for imputation requires explicit methods-section description and sensitivity analysis without the LLM-imputed values |
| Documentation / report drafting | Disclosed in paper acknowledgements; reviewed by human author before publication |
| Naming, schema design | Disclosed in repository, not in research outputs |

## What is prohibited

- LLMs setting behavioural priors or policy parameters
- LLMs writing quoted policy positions or interpretations attributable to WealthLens
- LLMs generating model outputs (revenue figures, distributional estimates) directly
- LLMs settling methodological disputes between the team and external reviewers
- LLMs drafting peer-review responses without explicit author review and disclosure

## What is encouraged

- LLMs as coding assistants under standard code review
- LLMs as documentation drafters under standard editorial review
- LLMs as schema-design and naming aids
- LLMs as initial literature-search filters before human verification
- LLM-generated test cases that humans curate

## Pre-registration and replication infrastructure

To make the disclosure credible:
- Methodology pre-registration on OSF before first public outputs
- Pre-specified hypotheses and analysis plan
- Replication packages on Zenodo with DOIs
- Public commit history (no interactive rebase to hide LLM-assisted commits)
- Annual audit of LLM use, published with the year's release notes

## Current LLM usage in this project

WealthLens HQ uses Claude Code (Anthropic) and Codex (OpenAI) as development assistants for:
- Code scaffolding and implementation
- Documentation drafting
- Test generation
- Research synthesis and literature discovery
- CI/CD configuration

All LLM-assisted output is reviewed by the project maintainer before merge. LLM-assisted commits are identifiable in the git history through commit metadata and agent configuration files (`.claude/`, `.codex/`, `AGENTS.md`).

## Annual audit commitment

Each calendar year, WealthLens will publish a brief summary of:
- Which LLMs were used and for what categories of work
- What proportion of code was LLM-assisted (estimated)
- Any incidents where LLM output was found to be incorrect after merge
- Changes to this disclosure policy
