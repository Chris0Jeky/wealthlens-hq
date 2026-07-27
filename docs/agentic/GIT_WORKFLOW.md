# Git Workflow — Repo Posture

Solo-developer repo with a **declared relaxed-git posture**: `.claude/tier.json` sets
`relaxed_work_loss_guards: true`, and the deny floor (`.claude/hooks/dispatch.py`,
matrix in `smoke_test.py`) enforces the only hard limits — force-push in all
spellings, catastrophic deletes, pipe-to-shell, secret-file mutation. Everything
else (amend, rebase, reset, stash, clean, merge, `--force-with-lease`) is allowed.

## Explain-before-acting

For commands that discard uncommitted work (`git reset --hard`, `git clean -f`,
`git checkout -- .`): state briefly what will be lost, then proceed — unless you
know of unsaved work (yours or another agent's), in which case stash first.
Under `wave_mode` these commands are floor-denied — another agent's work is in
the blast radius.

## When you get tangled

Diverged branches, unresolvable conflicts, detached HEAD:

1. `git status` + `git log --oneline -10`.
2. Tell the user what happened, what state you are in, and the options (safest
   first). Never silently discard significant work.

## Merging

Merge doctrine has one home and it is not this repo: the global twelve laws
(`~/.claude/CLAUDE.md`; tier table in agent-harness `BLUEPRINT.md` §1), which also
carry the stacked-PR and never-squash rules. This repo is the **T3** row — push free,
merge free once one bounded independent review at the current head and green CI hold.
