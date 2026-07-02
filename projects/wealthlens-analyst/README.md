# WealthLens Analyst

Evidence-backed research analyst over official UK wealth statistics
(ONS Wealth and Assets Survey, HMRC distributional statistics, selected
IFS/Resolution Foundation reports). Citation-first hybrid RAG with honest
abstention, a committed eval harness, and a hard spend cap.

**Status:** M2 — hybrid retrieval is live behind `POST /ask?debug=retrieval`
(Postgres FTS + pgvector dense, RRF-fused, full chunk provenance + component
ranks). M1 ingest (tabular slice → chunks → FTS → embeddings) is done; PDF
sources (H1-08) and generation/abstention (M3-M4) are pending and raise
`NotImplementedError` or return 501. Plan: `docs/plan/HERO1_PLAN.md`
(repo root) · backlog: `tasks/hero1-backlog.md` · decisions: `docs/adr/0001-0003`.

## Layout

- `src/wealthlens_analyst/` — the service (retrieval, answer, llm seam,
  budget, api, ingest). See `CLAUDE.md` for the subtree map and locked rules.
- `migrations/` — Alembic; hand-written revisions in `migrations/versions/`
  (see `migrations/README.md` for usage).
- `evals/` — golden set (human-reviewed; DRAFT questions await review),
  deterministic checks, RAGAS runner, committed reports.
- `tests/` — pytest (mypy strict, monorepo ruff rules).

## Quick start

```bash
pip install -e "projects/wealthlens-analyst[dev,evals]"
docker compose up -d analyst-db   # Postgres+pgvector on :15432 (repo root)
make ingest-slice     # chunk + write + embed the frozen corpus slice
make dev              # uvicorn on 127.0.0.1:8100
curl -X POST "http://127.0.0.1:8100/ask?debug=retrieval" \
  -H "Content-Type: application/json" -d '{"question": "who holds the most wealth?"}'
make eval-golden-validate
```

Configuration: copy `.env.example` to `.env`. Never commit secrets.

## Failure modes

_To be written at M6 (see HERO1_PLAN). This section will document what the
system refuses to answer and why, known weak spots, and honest limitations._
