---
name: codex-verification-doc-sync
description: Final verification and status sync before handoff. Use before ending a session or completing a task.
---

# WealthLens HQ — Codex Verification Doc Sync

## When to use

- Before handing off completed work
- Before ending a session
- After meaningful changes to code, content, or docs

## Steps

1. Re-read the requested outcome.
2. Verify the changed seam directly (run tests, check output, validate format).
3. State what was verified and what was not.
4. Update `.codex/memories/00_ACTIVE.md` if focus area status changed.
5. Update `tasks/active-sprint.md` or `tasks/done.md` if tasks completed.
6. Capture decisions in `.codex/memories/decisions/` if meaningful tradeoffs were made.
7. Produce handoff summary using the format below.

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
- Do not claim tests passed unless they actually ran.
- Include any unresolved failures or workarounds in the handoff.
