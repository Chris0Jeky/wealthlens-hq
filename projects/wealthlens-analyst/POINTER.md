# WealthLens Analyst — moved

Extracted 2026-07-06 to **<https://github.com/Chris0Jeky/wealthlens-analyst>**
(clean import; the import commit there records `wealthlens-hq@32b4867`).

Everything analyst-related moved with it: the code (this subtree), the locked
plan (`docs/plan/HERO1_PLAN.md`), the backlog (`tasks/hero1-backlog.md`,
`tasks/hero1-corpus-candidates.md`), the writeups plan, ADRs 0001-0003, the
`ci-analyst.yml` workflow, the `analyst-db` compose service, the Makefile
targets, and the Dependabot entry.

Two residual couplings, tracked in the analyst's backlog (H1-33/H1-34):

- the analyst carries a trimmed copy of the 8 `analyst_corpus: true` entries;
  this repo's `registries/sources.yml` remains authoritative for the
  dashboard/pipelines only;
- the tabular corpus CSVs are still produced by this repo's data pipelines
  (copied into the analyst's `data/processed/`) until its self-contained
  fetch lands.
