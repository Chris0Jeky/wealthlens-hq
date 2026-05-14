---
name: codex-question-batch
description: Decide whether a task needs user questions or can proceed with explicit assumptions. Reduces back-and-forth while blocking unsafe work.
---

# WealthLens HQ — Codex Question Batch

## When to use

- Uncertain whether to ask the user or proceed
- Multiple potential blockers in a single task
- Want to minimise context-window churn

## Steps

1. List all uncertainties for the current task.
2. Classify each as "must ask" or "can assume" using the decision table in `docs/agentic/QUESTION_PROTOCOL.md`.
3. For "must ask" items: batch all questions into one compact message.
4. For "can assume" items: state each assumption explicitly.

## Must-ask triggers

- Irreversible product choice
- Destructive action (file deletion, force-push, DB drop)
- Missing credential or private token
- Security/auth boundary ambiguity
- Data source interpretation that could mislead the public

## Can-assume triggers

- Reversible UI layout or copy choice
- Missing local dependency
- Broad task scope (propose small first slice)
- Test selection (run narrowest check)
- Content voice/tone (follow branding playbook)

## Assumption template

```text
Assumption: <specific assumption>. Reason: <source or convention>. Reversible by changing <file/setting>.
```

## Guardrails

- Never drip-feed single questions across multiple messages.
- If you have zero blockers, proceed without asking.
- Record important assumptions in the handoff.
