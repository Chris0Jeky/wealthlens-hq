# Agent question protocol

Purpose: reduce unnecessary back-and-forth while still blocking unsafe or irreversible work.

## Decision table

| Uncertainty type | Ask user? | Default action |
| --- | --- | --- |
| Irreversible product choice | Yes | Batch into one concise question. |
| Destructive filesystem/git action | Yes | Stop until explicit approval. |
| Missing credential or private token | Yes | Ask for the credential or alternate verification path; do not invent. |
| Security/auth boundary ambiguity | Yes | Ask or choose the safer/restrictive behavior and report assumption. |
| Public API/schema contract ambiguity | Usually yes | Check code/docs first; ask only if conflicting. |
| Data source interpretation | Usually yes | Cite the source and state your reading; ask if ambiguous. |
| Reversible UI copy/layout preference | No | Choose existing design convention and mark assumption. |
| Missing local dependency | No, unless blocking | Report environment gap, run narrower/static check if possible. |
| Broad task scope | No initial ask | Propose a small first slice and proceed unless user requested planning only. |
| Test selection ambiguity | No | Run narrowest relevant check, then state coverage gap. |
| Content voice/tone choice | No | Follow `strategy/branding-playbook.md` and mark assumption. |
| Research consolidation approach | No | Follow existing conventions in `research/` and mark assumption. |

## Required question shape

When a question is needed, ask all blockers at once:

```text
I can proceed after these blockers are resolved:
1. <blocker> — affects <risk/decision>. My default would be <default>.
2. <blocker> — affects <risk/decision>. My default would be <default>.
```

Avoid single-question drip feeds. Each extra message in a long session increases context pressure.

## Assumption template

When proceeding without asking:

```text
Assumption: <specific assumption>. Reason: <source or convention>. Reversible by changing <file/setting>.
```

Record important assumptions in the final handoff or active session note.
