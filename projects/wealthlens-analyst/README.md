# WealthLens Analyst

Evidence-backed research analyst over official UK wealth statistics
(ONS Wealth and Assets Survey, HMRC distributional statistics, selected
IFS/Resolution Foundation reports). Citation-first hybrid RAG with honest
abstention, a committed eval harness, and a hard spend cap.

**Status:** scaffolding (M0). Stubs import cleanly and raise
`NotImplementedError` where logic is pending. Plan: `docs/plan/HERO1_PLAN.md`
(repo root) · backlog: `tasks/hero1-backlog.md` · decisions: `docs/adr/0001-0003`.

## Layout

- `src/wealthlens_analyst/` — the service (retrieval, answer, llm seam,
  budget, api, ingest). See `CLAUDE.md` for the subtree map and locked rules.
- `migrations/` — Alembic; schema drafts live in `migrations/drafts/` until
  task H1-05 promotes them.
- `evals/` — golden set (human-reviewed; DRAFT questions await review),
  deterministic checks, RAGAS runner, committed reports.
- `tests/` — pytest (mypy strict, monorepo ruff rules).

## Quick start (once M1 lands)

```bash
pip install -e "projects/wealthlens-analyst[dev,evals]"
make dev              # uvicorn on 127.0.0.1:8100
make ingest-slice     # fetch + chunk + embed the frozen corpus slice
make eval-golden-validate
```

Configuration: copy `.env.example` to `.env`. Never commit secrets.

## Failure modes

_To be written at M6 (see HERO1_PLAN). This section will document what the
system refuses to answer and why, known weak spots, and honest limitations._
