"""SQLAlchemy models for budget enforcement and per-query accounting.

Two tables (migrations/versions/0003_budgets.py and 0004_query_log.py):

- budgets: the hard cap per period (monthly GBP). The middleware reads the
  active row; a MISSING row blocks spend rather than allowing it (fail-closed,
  ADR 0002). At most one row may be active (partial unique index), and `active`
  defaults true — so rolling a period over is deactivate-then-insert (H1-27).
- query_log: one row per /ask request — tokens in/out, cost, latency, and the
  decision (answered / refused / over_budget / error). The public metrics page
  (p50/p95 latency, cost per query) is computed from this table alone.

Pending: task H1-27 in tasks/hero1-backlog.md (declarative models + session
factory once the Alembic wiring of H1-05 exists).
"""

from __future__ import annotations

from enum import StrEnum


class QueryDecision(StrEnum):
    """Terminal outcome of one /ask request, recorded in query_log."""

    ANSWERED = "answered"
    REFUSED = "refused"  # abstention gate: cannot answer from corpus
    OVER_BUDGET = "over_budget"  # spend cap exceeded -> 429
    ERROR = "error"


def current_spend_gbp() -> float:
    """Sum of query_log.cost_gbp within the active budget period."""
    raise NotImplementedError("H1-27: budget accounting not yet implemented")
