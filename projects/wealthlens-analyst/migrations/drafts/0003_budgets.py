"""DRAFT migration 0003 — budgets table (promoted to a real revision in H1-05).

The hard spend cap (ADR 0002). The middleware reads the single active row;
a missing row BLOCKS spend (fail-closed) — that behaviour lives in code, but
the schema supports it by making "no budget" representable and distinct from
"budget of zero".

DDL sketch::

    CREATE TABLE budgets (
        budget_id     SERIAL PRIMARY KEY,
        period_start  DATE NOT NULL,          -- monthly periods
        period_end    DATE NOT NULL,
        cap_gbp       NUMERIC(8, 2) NOT NULL CHECK (cap_gbp >= 0),
        active        BOOLEAN NOT NULL DEFAULT TRUE,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    -- at most one active budget at a time
    CREATE UNIQUE INDEX budgets_one_active ON budgets (active) WHERE active;
"""
