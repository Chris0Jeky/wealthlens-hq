---
name: wl-question-batch
description: Decide whether a WealthLens HQ task needs user questions or can proceed with explicit assumptions, minimising context-window churn.
user-invocable: true
---

# WealthLens HQ Question Batch

Use when you are unsure whether to ask the user or proceed on assumptions.
Do NOT use when you have zero blockers — just proceed.

## Workflow

1. Read `docs/agentic/QUESTION_PROTOCOL.md` — the decision table, question shape,
   and assumption template live THERE (one home; this skill does not restate them).
2. Classify each uncertainty with the table: "must ask" vs "can assume".
3. Batch every "must ask" into ONE compact message using the required shape.
4. For each "can assume", state the assumption with the template and continue.

## Guardrails

- Never drip-feed single questions across multiple messages.
- Data-source interpretation that could mislead the public is always "must ask".
- Record important assumptions in the final handoff.
