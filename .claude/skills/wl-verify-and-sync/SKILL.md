---
name: wl-verify-and-sync
description: Close a WealthLens HQ task properly — verify the changed seam and sync status artifacts when needed.
user-invocable: true
---

# WealthLens HQ Verify And Sync

Use this after meaningful work or before ending a session.

## Verify first

1. Re-read the requested outcome.
2. Verify the changed seam directly (run tests, check output, validate format).
3. State what was verified and what was not.

## Sync when required

Update these only when the work actually changes their truth:

- `.codex/memories/00_ACTIVE.md` — if focus area status changed
- `tasks/active-sprint.md` — if a sprint task was completed or added
- `tasks/done.md` — if a task should be marked complete
- `.codex/memories/decisions/` — if a meaningful decision was made

## Handoff format

```text
## Changed
- <file>: <what changed>

## Verified
- <what was checked and result>

## Not verified
- <what was skipped and why>

## Failures / workarounds
- <any issues encountered>

## Status sync
- <docs updated or "no status change">

## Next slice
- <suggested follow-up>
```

## Guardrails

- Keep status updates factual and short.
- Do not rewrite large docs just to mirror a small code change.
- Do not claim tests passed unless they actually ran.
