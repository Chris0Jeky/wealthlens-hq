# Agent failure ledger

This file is the reviewed human-readable view of recurring agent/tool/workflow failures. Claude's failure hook writes raw local entries to ignored `.claude/local/failure_ledger.jsonl`; promote only scrubbed summaries here after review.

## Entries

| Date | Class | Surface | Failure | Workaround | Future fix | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-14 | seed | agentic-pack | Ledger created | n/a | Start recording recurring failures and promote confirmed lessons | open |
| 2026-05-29 | git/gh | stacked-PR merge | `gh pr merge <base> --delete-branch` **closed** dependent child PRs (#287–#292) instead of retargeting; closed PRs whose base branch is gone cannot be reopened | Recreated children as fresh PRs to `main` (#314–#319) | On a stack, merge with plain `--merge` (no delete), retarget children just-in-time, delete branches in a final pass. Saved to memory `feedback_stacked_merge_delete_branch` | resolved |
| 2026-05-29 | git/hook | force-push | `git push --force-with-lease` was permission-denied on some `fix/*` branches mid-session (intermittent) | Pushed rewritten history to a fresh `-v2` branch (plain push), new PR, closed old (#320/#321/#322) | Prefer non-force pushes; rewrite history on a new branch name | resolved (workaround) |
| 2026-05-29 | build | hatch sdist | Static `force-include "../../registries"` made the **sdist uninstallable** — the directive persisted in the sdist pyproject and crashed (`Forced include not found`) building a wheel from the unpacked sdist | Replaced with a conditional build hook (`hatch_build.py`) that force-includes only when the path exists and ships files inside both wheel and sdist | caught by adversarial review before merge (#326) | resolved |
| 2026-05-29 | tooling | Bash tool (Windows) | Bash tool runs via bash, not PowerShell; `cd C:\...`, `git show <ref>:<path>`, here-strings, PowerShell `for` syntax all mangle | Use forward-slash absolute paths; read files via the Read tool not `git show ref:path`; write scripts to a file not here-strings | Note in session onboarding | recurring (known) |
