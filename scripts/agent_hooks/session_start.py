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
                        "Read CLAUDE.md, AGENTS.md, "
                        "../hq-private/projects/wealthlens/memories/00_ACTIVE.md "
                        "(private sibling repo; skip if absent), "
                        "and tasks/active-sprint.md. "
                        "ACTION REQUIRED: read tasks/ACTION-REQUIRED.md and surface "
                        "its open items (lead with anything due today/overdue) in "
                        "your first reply and in every summary/status/handoff; only "
                        "clear an item when Chris explicitly says it is done. "
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
