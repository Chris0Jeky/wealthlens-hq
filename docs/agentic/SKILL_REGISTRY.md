# Skill Registry

All project-scoped skills with trigger conditions and responsibility notes.

## Claude Code skills (`.claude/skills/`)

| Skill | Trigger | Pairs with |
| --- | --- | --- |
| `wl-repo-onramp` | Session start, broad/ambiguous request, unfamiliar area | `00_ACTIVE.md`, `tasks/active-sprint.md` |
| `wl-safe-slice` | Implementing or editing code/content | `00_ACTIVE.md`, relevant task |
| `wl-verify-and-sync` | After meaningful work, before ending session | `00_ACTIVE.md`, changed files |
| `wl-question-batch` | Uncertain whether to ask user or proceed | `QUESTION_PROTOCOL.md` |

## Codex skills (`.agents/skills/`)

| Skill | Trigger | Pairs with |
| --- | --- | --- |
| `codex-repo-onramp` | Session start, broad request, orientation | `00_ACTIVE.md`, `AGENTS.md` |
| `codex-worktree-issue-worker` | One assigned issue in isolated worktree | Issue seed, relevant task |
| `codex-verification-doc-sync` | Before handoff, final checks | `00_ACTIVE.md`, changed files |
| `codex-question-batch` | Uncertain whether to ask user or proceed | `QUESTION_PROTOCOL.md` |

## Adding a skill

1. Create `SKILL.md` with frontmatter (`name`, `description`, `user-invocable`).
2. For Codex skills, add `agents/openai.yaml` alongside.
3. Register the skill in this file.
4. Update `CLAUDE.md` § Skill routing or `AGENTS.md` § Codex autonomy skills.
5. Update `docs/agentic/TOOL_PARITY.md` if the skill has a cross-runtime equivalent.
