#!/usr/bin/env python3
"""Claude Code SessionStart hook — print workspace context."""

from __future__ import annotations

import json


def main() -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": (
                        "WealthLens HQ workspace. "
                        "Read CLAUDE.md, AGENTS.md, .codex/memories/00_ACTIVE.md, "
                        "and tasks/active-sprint.md. "
                        "Multi-domain: code (Python/FastAPI, Vue 3/TypeScript), "
                        "content, research, strategy, outreach. "
                        "Data must cite sources. Charts must be WCAG AA. "
                        "Volunteers will read this code."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
