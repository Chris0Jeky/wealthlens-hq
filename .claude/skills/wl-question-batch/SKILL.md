---
name: wl-question-batch
description: Decide whether a WealthLens HQ task needs user questions or can proceed with explicit assumptions, minimising context-window churn.
user-invocable: true
---

# WealthLens HQ Question Batch

Use this when you are unsure whether to ask the user or proceed with assumptions.

## Decision process

1. Read `docs/agentic/QUESTION_PROTOCOL.md` for the full decision table.
2. Classify each uncertainty as "must ask" or "can assume."
3. For "must ask" items, batch all questions into one compact message.
4. For "can assume" items, state the assumption using the template.

## Quick reference — must ask

- Irreversible product choice (e.g., which charting library to use permanently)
- Destructive action (e.g., deleting research files, force-pushing)
- Missing credential or private token
- Security/auth boundary ambiguity
- Data source interpretation that could mislead the public

## Quick reference — can assume

- Reversible UI layout or copy choice
- Missing local dependency (report gap, run what you can)
- Broad task scope (propose small first slice)
- Test selection (run narrowest check, state coverage gap)
- Content voice/tone (follow `strategy/branding-playbook.md`)
- Research consolidation approach (follow existing conventions)

## Assumption template

```text
Assumption: <specific assumption>. Reason: <source or convention>. Reversible by changing <file/setting>.
```

## Guardrails

- Never drip-feed single questions across multiple messages.
- If you have zero blockers, do not ask — just proceed.
- Record important assumptions in the handoff.
