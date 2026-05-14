# Git Workflow — Shared Repo Rules

> Plain-language command explanations and recovery procedures for agents.

## Rules

- **Never rebase.** Use `git merge main` to update your branch. Rebase rewrites history and requires force-push, which is never allowed.
- **Never force-push.** Not `--force`, not `--force-with-lease`, not on any branch.
- **Never `git commit --amend` after pushing.** Create a new fixup commit instead.
- **Never run `git reset --hard`, `git clean -f`, `git checkout -- .`, or `git restore .`** without explicit user approval. These permanently destroy uncommitted work.
- **Recovery commands are always safe:** `git rebase --abort`, `git merge --abort`, `git stash`.

## Explain-before-acting rule

Before any git command that could discard work or rewrite history, you MUST:

1. Tell the user what you want to do in plain language — assume they may not be a git expert.
2. Explain what data is at risk (uncommitted changes? commit history? remote state?).
3. State whether the action is reversible and how to recover if it goes wrong.
4. Wait for explicit user approval before proceeding.

## When you get tangled

If you end up with diverged branches, unresolvable merge conflicts, or detached HEAD:

1. **Stop.** Do not attempt destructive recovery.
2. Run `git status` and `git log --oneline -10`.
3. Tell the user: what happened, what state you are in, and what your options are (safest first).
4. Let the user choose. Never silently discard work to get unstuck.

Recovery options (safest first):

1. `git merge --abort` / `git rebase --abort` — undo in-progress operation, no data loss.
2. `git stash` — save uncommitted changes before attempting recovery.
3. `git merge origin/<branch>` — reconcile diverged branches with a merge commit.
4. Ask the user to intervene manually.

## Safe vs. blocked commands

| Command | Status | Why |
| --- | --- | --- |
| `git merge main` | Always allowed | Merge commit preserves all history |
| `git pull --no-rebase` | Always allowed | Same as fetch + merge |
| `git stash` / `git stash pop` | Always allowed | Reversible |
| `git merge --abort` | Always allowed | Cancels in-progress merge |
| `git rebase --abort` | Always allowed | Cancels in-progress rebase |
| `git push` (no flags) | Allowed | Normal push, no history rewriting |
| `git rebase` | **Blocked** | Rewrites history, requires force-push |
| `git pull --rebase` | **Blocked** | Rewrites local history |
| `git push --force[-with-lease]` | **Blocked** | Can destroy remote commits |
| `git reset --hard` | **Blocked** | Destroys uncommitted changes |
| `git reset --soft/--mixed` | **Blocked** | Rewrites commit history |
| `git clean -f` | **Blocked** | Deletes untracked files permanently |
| `git checkout -- .` | **Blocked** | Discards all uncommitted changes |
| `git restore .` | **Blocked** | Discards all uncommitted changes |
| `git commit --amend` (after push) | **Blocked by policy** | Requires force-push to sync |
