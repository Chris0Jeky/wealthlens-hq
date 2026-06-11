# Hero #1 backlog — WealthLens v2 analyst

Last updated: 2026-06-11 (post-session-6: #403 + #404 merged; M0 done bar Chris's gates)

> Seeded by the kickoff session. Ordered; each task ≤ half a day. Work top-down:
> a task is startable when its `deps` are done. Plan: `docs/plan/HERO1_PLAN.md`.
> Session opener: "Read projects/wealthlens-analyst/CLAUDE.md and this backlog,
> pick up the next unblocked task, confirm approach in two lines, implement."
> Format: `- [ ] H1-NN (M*) Task — done-when. [deps: …]`

## ▶ NEXT SESSION (seeded 2026-06-11)

1. **H1-01** — corpus-slice tagging. The report shortlist is researched and
   decision-ready in `tasks/hero1-corpus-candidates.md` (verified URLs +
   paste-ready `sources.yml` YAML). Proceed with its recommended set unless
   Chris objects; record access dates fresh at fetch time.
2. **H1-12** — pure RRF fusion (`retrieval/fuse_rrf.py`), no deps, fully
   unit-testable offline. Good warm-up or parallel PR.
3. **H1-06/07** — document fetch + tabular chunking (after H1-01).
4. Waiting on Chris (see `tasks/ACTION-REQUIRED.md` items 6-7): H1-02 golden
   questions review; ADR 0003 **D3 hosting**.

Local env: `docker compose up -d analyst-db` (port **15432**); use
`make PYTHON=python <target>` on this box. PR gate per repo convention:
2 independent adversarial reviews + bot threads resolved + green CI, then merge.

## M0 — kickoff residue (startable immediately)

- [ ] H1-01 (M0) Tag the corpus slice in `registries/sources.yml`: add `analyst_corpus: true` to `ons-was-wealth`, `hmrc-cgt-statistics`, `hmrc-tax-receipts`; add 3-5 new entries for the chosen IFS/RF reports (id, name, url, access_date, format: report, licence, update_pattern, pipeline: null, notes) — done when `sources.yml` validates as YAML and lists 6-8 slice sources. [deps: none]
- [ ] H1-02 (M0) Chris reviews the 20 DRAFT golden questions in `evals/golden/golden_set.jsonl`, rewrites freely, writes `expected_answer` + `required_citations` for the in-corpus 15 (@Chris) — done when no `status: DRAFT` remains in the first 20. [deps: none]
- [ ] H1-03 (M0) Chris rules on ADR 0003 — REMAINING: **D3 hosting only** (needs his account/payment); D1/D2/D4 adopted by delegation 2026-06-11 per the memo's recommendations (@Chris) — done when D3 is recorded and ADR 0003 flips to Accepted. [deps: none]

## M1 — corpus ingested

- [x] H1-04 (M1) Add a `postgres` service (pgvector image) to `docker-compose.yml` + `DATABASE_URL` plumbing in the analyst config — done when `docker compose up postgres` serves a DB with `CREATE EXTENSION vector` available. [deps: none] [completed: 2026-06-11 — `analyst-db` service, host port 15432 (5432/5433 are Windows-excluded on the dev box)]
- [x] H1-05 (M1) Wire Alembic: `alembic.ini` + `migrations/env.py` against the analyst SQLAlchemy metadata; promote the four draft migrations (chunks, embeddings, budgets, query_log) to real revisions — done when `alembic upgrade head` succeeds on an empty DB and `alembic downgrade base` reverses it. [deps: H1-04] [completed: 2026-06-11 — verified live: upgrade/downgrade/re-upgrade + FTS/vector/constraint smoke tests]
- [ ] H1-06 (M1) Implement `ingest/fetch_documents.py`: download the 3-5 IFS/RF report PDFs from their registry URLs into `data/corpus/` (gitignored), verifying checksum + recording access date — done when all slice PDFs fetch reproducibly and a missing/changed URL fails loudly. [deps: H1-01]
- [ ] H1-07 (M1) Implement tabular-source rendering in `ingest/slice_corpus.py`: turn the existing pipelines' processed WAS/HMRC outputs into citable text chunks (one chunk per table section/band with year + units) — done when chunks carry full provenance (source_id, document_id, section, page=null, span) and a unit test locks the format. [deps: H1-05]
- [ ] H1-08 (M1) Implement PDF extraction + chunking for the report documents (page-aware, ~500-token chunks, heading-anchored sections) — done when every chunk row has non-null page + span and a sampled chunk visually matches the source PDF page. [deps: H1-05, H1-06]
- [ ] H1-09 (M1) Ingestion integrity gate: reject any chunk with null provenance; `make ingest-slice` runs fetch→chunk→write end-to-end — done when a deliberately provenance-stripped fixture chunk fails ingestion in a test. [deps: H1-07, H1-08]
- [ ] H1-10 (M1) Build the FTS path: `tsvector` column + GIN index migration + `retrieval/fts.py` query — done when a fixture query returns ranked chunks and the index is used (EXPLAIN). [deps: H1-09]
- [ ] H1-11 (M1) Embed the corpus: `retrieval/dense.py` + batch embedding script through the `llm/client.py` seam (model per ADR 0003), writing pgvector rows + index — done when every chunk has an embedding and cosine query returns sane neighbours on 3 spot checks. [deps: H1-09]

## M2 — hybrid retrieval behind /ask

- [ ] H1-12 (M2) Implement `retrieval/fuse_rrf.py` (k=60) over FTS + dense rank lists, deterministic, pure-Python — done when unit tests pin RRF math incl. tie + disjoint-list cases (no DB, no model). [deps: none — pure function; integration needs H1-10, H1-11]
- [ ] H1-13 (M2) Implement `/ask?debug=retrieval`: fused top-N with per-chunk provenance + both component ranks, Pydantic response model — done when the route returns schema-valid JSON against the live local DB. [deps: H1-10, H1-11, H1-12]
- [ ] H1-14 (M2) Retrieval sanity-recall run on the Chris-reviewed golden subset; record results in `evals/reports/` — done when the report states top-10 recall per question with misses listed, not tuned away. [deps: H1-02, H1-13]
- [ ] H1-15 (M2) `query_log` write path: every /ask logs tokens (0 in debug mode), latency_ms, decision — done when rows appear for debug queries and a test asserts the row shape. [deps: H1-13]

## M3 — reranker + citations

- [ ] H1-16 (M3) Implement `retrieval/rerank.py` (ADR 0003 D1: Cohere Rerank 4 Fast) behind `RERANK_ENABLED` (default OFF) — done when flag-off is byte-identical to M2 behaviour and flag-on reorders a fixture case. [deps: H1-13]
- [ ] H1-17 (M3) A/B recall: re-run H1-14 with rerank on; record both columns in the same report — done when the report shows flag-on vs flag-off side by side. [deps: H1-14, H1-16]
- [ ] H1-18 (M3) Implement `answer/compose.py`: generation through the client seam, prompt forces claims to cite retrieved chunk ids — done when a live local query returns an answer whose citations are all in the retrieved set. [deps: H1-13]
- [ ] H1-19 (M3) Implement `answer/citations.py`: resolve cited chunk_ids to {source, document, section/page} from the DB; strip/flag unresolvable citations — done when a fabricated chunk_id in a fixture answer is caught and the response carries resolved citations only. [deps: H1-18]
- [ ] H1-20 (M3) Publish the /ask response JSON schema (answer | refusal | over-budget variants) + schema-validity deterministic check — done when `evals/checks/deterministic.py` validates live responses against it. [deps: H1-18, H1-19]

## M4 — abstention

- [ ] H1-21 (M4) Implement `answer/abstain.py`: the confidence gate (ADR 0003 D4: fused-RRF threshold + min-hits), returning the structured refusal — done when weak-evidence fixture queries refuse and strong ones don't, under unit test. [deps: H1-13]
- [ ] H1-22 (M4) Wire the gate into /ask ahead of generation; refusal logged as decision=refused with zero generation cost — done when the 5 out-of-corpus golden questions all refuse against the live local corpus. [deps: H1-20, H1-21]
- [ ] H1-23 (M4) Flesh out `evals/checks/deterministic.py`: citation presence + resolvability, schema validity, correct refusal set, latency/cost bound stubs — done when `make eval-deterministic` passes locally and in the ci-analyst job. [deps: H1-20, H1-22]

## M5 — evals, observability, spend cap

- [ ] H1-24 (M5) Grow the golden set toward 100 (batch of ~30 drafted from corpus topics for Chris review; 10+ refusal cases) — done when ≥50 reviewed pairs exist (@Chris reviews). [deps: H1-02]
- [ ] H1-25 (M5) Wire RAGAS in `evals/run_ragas.py` (LLM + embeddings injected via the seam) — done when `make eval-ragas` produces metric scores on the reviewed set. [deps: H1-22, H1-24]
- [ ] H1-26 (M5) `make eval-report`: one committed markdown report combining deterministic + RAGAS + latency/cost percentiles — done when the report is generated from a single command and committed under `evals/reports/`. [deps: H1-23, H1-25]
- [ ] H1-27 (M5) Budget enforcement: `budget/models.py` + `budget/middleware.py` live — cap from `BUDGET_MONTHLY_CAP_GBP`, fail-closed on missing budget row, 429 + structured refusal when exceeded — done when a test exhausts a seeded budget and asserts the 429 body. [deps: H1-15]
- [ ] H1-28 (M5) Self-hosted Langfuse (docker-compose) + OTel tracing on /ask spans (retrieve, rerank, compose) — done when a local query produces a complete trace in Langfuse. [deps: H1-13]
- [ ] H1-29 (M5) Metrics endpoint: p50/p95 latency + cost/query computed from `query_log` — done when the endpoint serves correct percentiles over seeded fixture rows (unit-tested math). [deps: H1-15, H1-27]

## M6 — ship

- [ ] H1-30 (M6) Provision hosting per ADR 0003 (app + Postgres+pgvector + Langfuse or hosted alternative), deploy, run Alembic + ingest — done when /healthz is green on the public URL. [deps: H1-03, H1-22, H1-27]
- [ ] H1-31 (M6) Public metrics page wired to the deployed metrics endpoint; final eval report generated FROM the deployed config and committed — done when the URL shows live p50/p95 + cost/query and the report is on main. [deps: H1-26, H1-29, H1-30]
- [ ] H1-32 (M6) README failure-modes section + writeup #1 drafted from `docs/plan/WRITEUPS.md` outline; demo sent to the 10 named people (checking `tasks/outreach/` logs first) (@Chris sends) — done when writeup #1 is published and 10 sends are logged in `tasks/outreach/emails-sent.md`. [deps: H1-30, H1-31]
