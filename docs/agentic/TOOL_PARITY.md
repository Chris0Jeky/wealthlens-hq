# Tool Parity — Claude Code vs Codex

Which runtime capabilities each agent has and where shared baselines live.

## Native tools

| Capability | Claude Code | Codex |
| --- | --- | --- |
| File read/write/edit | Read, Edit, Write, Glob, Grep | Built-in file tools, `rg`, shell |
| Shell execution | Bash tool (guarded by hooks) | Direct shell (guarded by AGENTS.md policy) |
| Web search/fetch | WebSearch, WebFetch | Shell `curl`/`wget` or MCP |
| Task tracking | TaskCreate/TaskUpdate | Task API or `.codex/` planning files |
| Sub-agents | Agent tool (worktree isolation) | Spawned workers (real git worktrees) |
| MCP servers | `.mcp.json` + cloud MCP | `.mcp.json` (shared) |

## Guardrails

| Layer | Claude Code | Codex |
| --- | --- | --- |
| Dangerous-command deny | `scripts/agent_hooks/pre_tool_use.py` hook | AGENTS.md § Command safety (manual adherence) |
| Failure logging | `scripts/agent_hooks/post_tool_failure.py` hook | `codex-verification-doc-sync` skill (manual) |
| Session context | `scripts/agent_hooks/session_start.py` hook | AGENTS.md § First 5 Minutes |
| Static deny list | `.claude/settings.json` deny patterns | N/A (no equivalent static config) |
| Secret redaction | Hook-level scrubbing in failure ledger | AGENTS.md § Secrets policy |

## Shared config

- `.mcp.json` — MCP server definitions, used by both runtimes
- `docs/agentic/` — shared protocols (question, failure, git workflow, skill registry)
- `autodoc/AGENT_INDEX.md` — code-grounded orientation for both agents

## Skills parity

| Domain | Claude skill | Codex skill |
| --- | --- | --- |
| Onramp | `wl-repo-onramp` | `codex-repo-onramp` |
| Implementation | `wl-safe-slice` | `codex-worktree-issue-worker` |
| Verification | `wl-verify-and-sync` | `codex-verification-doc-sync` |
| Question batch | `wl-question-batch` | `codex-question-batch` |

## Maintenance

Update this file when adding MCP servers, hooks, skills, or guardrail layers to either runtime.
