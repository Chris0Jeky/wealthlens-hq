# .agents/skills/ — Codex Skill Index

Repo-local Codex skills for WealthLens HQ. These supplement `AGENTS.md` and are loaded by trigger, not by default.

## Skill index

| Skill | Trigger | Description |
| --- | --- | --- |
| `codex-repo-onramp` | Session start, broad/ambiguous request | Orient to the workspace before editing |
| `codex-worktree-issue-worker` | One assigned issue in isolated worktree | Implement a single task in isolation |
| `codex-verification-doc-sync` | Before handoff, final checks | Verify changes and sync status docs |
| `codex-question-batch` | Uncertain whether to ask or proceed | Decide ask vs. assume with templates |

## Usage pattern

```text
1. Read AGENTS.md
2. Read ../hq-private/projects/wealthlens/memories/00_ACTIVE.md (private sibling repo; skip if absent)
3. Check if a skill matches the task type
4. If yes, follow the skill's workflow
5. If no, follow AGENTS.md general guidance
```

## Adding a skill

1. Create a directory under `.agents/skills/<skill-name>/`.
2. Add `SKILL.md` with frontmatter and instructions.
3. Add `agents/openai.yaml` for Codex agent dispatch.
4. Register in this README and in `docs/agentic/SKILL_REGISTRY.md`.
5. Update `AGENTS.md` § Codex autonomy skills.
