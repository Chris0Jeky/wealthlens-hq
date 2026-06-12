---
name: wl-safe-slice
description: Implement one small, reviewable slice in WealthLens HQ without drifting across layers or domains.
user-invocable: true
---

# WealthLens HQ Safe Slice

Use this when you are implementing or editing inside this repo.

## Workflow

1. Check the current focus in `../hq-private/projects/wealthlens/memories/00_ACTIVE.md` (private sibling repo; skip if absent).
2. Identify the smallest seam that advances the request.
3. Keep the diff within one coherent seam — do not mix code changes with strategy doc changes.
4. Run the narrowest meaningful verification.
5. If the change affects status, queue the required status-board sync (private memories repo) before closing.

## Preferred checks by domain

- Backend code change → `make test` or targeted `pytest`
- Frontend code change → `npm run build` or `npx vue-tsc --noEmit`
- Data pipeline change → run the specific pipeline script
- Content/strategy change → spell check, date format, source citation check
- Research change → verify source URLs and access dates

## Extra guardrails

- Do not accidentally change product semantics while touching plumbing.
- Do not mix coding work with strategy/outreach work in the same slice.
- Data must always cite its source — no fabricated statistics.
- If you touch user-visible frontend text, ensure accessibility (WCAG AA) in the same slice.
- Volunteers will read this code — clarity and docstrings matter.
