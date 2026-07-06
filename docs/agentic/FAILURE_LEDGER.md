# Agent failure ledger

This file is the reviewed human-readable view of recurring agent/tool/workflow failures. Claude's failure hook writes raw local entries to ignored `.claude/local/failure_ledger.jsonl`; promote only scrubbed summaries here after review. The SessionStart hook nudges a triage pass when the local ledger exceeds 25 entries.

## Triage 2026-07-06 — full backlog classified (1,602 entries, 2026-05-14 → 2026-07-06)

Gardener-style pass over the entire untriaged local ledger (4 parallel classifier
agents + synthesis; every entry counted). **Blockers: 0.** Class totals:
pre-existing-noise 640 · non-blocking-risk 633 · invalid-signal 329.
The raw JSONL was rotated to `.claude/local/archive/failure_ledger-2026-07-06.jsonl`
(local, untracked); the live ledger restarts empty.

| Cluster | ~n | Class | Resolution |
| --- | --- | --- | --- |
| PowerShell syntax fed to Git Bash (cmdlets, `$null` redirect, PS blocks) | 527 | pre-existing-noise | Documented in `~/.claude/MACHINE.md`; no repo action |
| Relative `./` paths in Read/Write after cwd resets / in worktrees | 222 | non-blocking-risk | **Promoted** → MACHINE.md: absolute forward-slash paths always |
| git worktree/branch lifecycle collisions during wave orchestration | 162 | non-blocking-risk | Covered by global law 7 (`--detach origin/main`; check `git worktree list` before branch ops) |
| Windows backslash paths mangled in bash (`cd C:Usersjekyt...`) | 113 | pre-existing-noise | MACHINE.md; forward slashes always |
| Subagent StructuredOutput schema-validation retries | 84 | non-blocking-risk | **Promoted** → MACHINE.md: embed the exact JSONSchema (verbatim property names) in orchestrator prompts |
| Fresh worktrees missing `node_modules`/`.venv` (vitest/vue-tsc/ruff unresolved) | 62 | non-blocking-risk | **Fixed structurally**: `worktree.symlinkDirectories` in `.claude/settings.json` — add any new dependency dir to that list |
| Inline `python -c`/`node -e` probe quoting breakage | 25 | non-blocking-risk | Write probes as scratchpad `.py` files (already in MACHINE.md Bash-tool note) |
| Merge conflicts / non-fast-forward during the May 192-PR consolidation | 25 | non-blocking-risk | Historical (one-time consolidation); wave protocol since |
| `gh` CLI field/flag misuse (`gh pr checks` has `state`/`bucket`, not `conclusion`) | 7 | non-blocking-risk | Folded here as the lesson; no further action |
| `git add` of gitignored generated `frontend/public/data` | 6 | non-blocking-risk | Generated output: regenerate via the static-API script, never `git add` |
| Expected red-green dev-loop exits, existence probes, transient network, hook self-tests | 329 | invalid-signal | By design; no action |

## Entries

| Date | Class | Surface | Failure | Workaround | Future fix | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-14 | seed | agentic-pack | Ledger created | n/a | Start recording recurring failures and promote confirmed lessons | open |
| 2026-05-29 | git/gh | stacked-PR merge | `gh pr merge <base> --delete-branch` **closed** dependent child PRs (#287–#292) instead of retargeting; closed PRs whose base branch is gone cannot be reopened | Recreated children as fresh PRs to `main` (#314–#319) | On a stack, merge with plain `--merge` (no delete), retarget children just-in-time, delete branches in a final pass. Saved to memory `feedback_stacked_merge_delete_branch` | resolved |
| 2026-05-29 | git/hook | force-push | `git push --force-with-lease` was permission-denied on some `fix/*` branches mid-session (intermittent) | Pushed rewritten history to a fresh `-v2` branch (plain push), new PR, closed old (#320/#321/#322) | Prefer non-force pushes; rewrite history on a new branch name | resolved (workaround) |
| 2026-05-29 | build | hatch sdist | Static `force-include "../../registries"` made the **sdist uninstallable** — the directive persisted in the sdist pyproject and crashed (`Forced include not found`) building a wheel from the unpacked sdist | Replaced with a conditional build hook (`hatch_build.py`) that force-includes only when the path exists and ships files inside both wheel and sdist | caught by adversarial review before merge (#326) | resolved |
| 2026-05-29 | tooling | Bash tool (Windows) | Bash tool runs via bash, not PowerShell; `cd C:\...`, `git show <ref>:<path>`, here-strings, PowerShell `for` syntax all mangle | Use forward-slash absolute paths; read files via the Read tool not `git show ref:path`; write scripts to a file not here-strings | Note in session onboarding | recurring (known) |
