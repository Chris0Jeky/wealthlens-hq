# Git Workflow — Repo Rules

> Solo-developer repo. Rules are relaxed but still prevent catastrophic data loss.

## Rules

- **Never `git push --force`** (bare force). Use `--force-with-lease` if you must rewrite remote history.
- **Never run `rm -rf /` or `rm -rf ~`** — catastrophic filesystem deletion.
- All standard git commands are allowed: commit, amend, rebase, reset, stash, clean, etc.
- Prefer new commits over amending when sharing context with the user, but amending is fine if asked.

## Explain-before-acting rule

For commands that discard uncommitted work (`git reset --hard`, `git clean -f`, `git checkout -- .`):

1. Briefly state what will be lost.
2. Proceed unless the user has unsaved work you know about.

## When you get tangled

If you end up with diverged branches, unresolvable conflicts, or detached HEAD:

1. Run `git status` and `git log --oneline -10`.
2. Tell the user: what happened, what state you are in, and options (safest first).
3. Let the user choose. Never silently discard significant work.

## Safe vs. caution commands

| Command | Status | Notes |
| --- | --- | --- |
| `git commit`, `git commit --amend` | Allowed | Normal workflow |
| `git rebase`, `git rebase -i` | Allowed | Fine for local branches |
| `git reset --soft/--mixed/--hard` | Allowed | Mention if uncommitted work at risk |
| `git stash`, `git stash pop` | Allowed | Reversible |
| `git clean -f` | Allowed | Mention what will be deleted |
| `git push` | Allowed | Normal push |
| `git push --force-with-lease` | Allowed | Safer force-push |
| `git push --force` | **Blocked** | Use --force-with-lease instead |
| `git merge`, `git pull` | Allowed | Any strategy is fine |
