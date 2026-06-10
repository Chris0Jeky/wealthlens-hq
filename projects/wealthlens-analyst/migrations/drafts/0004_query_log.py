"""DRAFT migration 0004 — query_log (promoted to a real revision in H1-05).

One row per /ask request. This single table feeds BOTH the spend-cap
accounting (sum of cost_gbp in the active period, ADR 0002) and the public
metrics page (p50/p95 latency, cost per query) — no separate metering system.

`decision` matches budget.models.QueryDecision:
answered | refused | over_budget | error.

DDL sketch::

    CREATE TABLE query_log (
        query_id     BIGSERIAL PRIMARY KEY,
        asked_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
        question_sha TEXT NOT NULL,           -- hash, not raw text (privacy)
        decision     TEXT NOT NULL CHECK
                     (decision IN ('answered','refused','over_budget','error')),
        gate_signal  DOUBLE PRECISION,        -- abstention-gate signal (audit)
        tokens_in    INTEGER NOT NULL DEFAULT 0,
        tokens_out   INTEGER NOT NULL DEFAULT 0,
        cost_gbp     NUMERIC(10, 6) NOT NULL DEFAULT 0,
        latency_ms   INTEGER NOT NULL,
        rerank_used  BOOLEAN NOT NULL DEFAULT FALSE
    );
    CREATE INDEX query_log_asked_at ON query_log (asked_at);
"""
