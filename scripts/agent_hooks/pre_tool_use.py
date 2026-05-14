#!/usr/bin/env python3
"""Claude Code PreToolUse hook — lightweight safety net.

Solo-developer repo: only block truly destructive commands that could
cause irreversible data loss. Everything else is allowed.
"""

from __future__ import annotations

import json
import re
import sys

DENY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # ── Only block catastrophic irreversible actions ──────────────────────
    (
        re.compile(r"\brm\s+-rf\s+[/~](?:\s|$)", re.I),
        "Recursive force-delete at root/home is blocked.",
    ),
    (
        re.compile(r"\bgit\s+push\b.*--force\b(?!-with-lease)", re.I),
        "Force-push (without --force-with-lease) is blocked. Use --force-with-lease if needed.",
    ),
    (
        re.compile(
            r"\b(?:curl|wget|iwr|irm)\b.+\|\s*"
            r"(?:sh|bash|zsh|pwsh|powershell|iex|invoke-expression)\b",
            re.I,
        ),
        "Piping remote scripts into an interpreter is blocked.",
    ),
    (
        re.compile(r"\bsudo\b", re.I),
        "sudo is outside normal repo workflow.",
    ),
    (
        re.compile(r"\bnpm\s+publish\b", re.I),
        "Publishing packages requires explicit approval.",
    ),
]

SECRET_KEY_VALUE = re.compile(
    r"(?i)(?:\b(?:\w+[_-])?(?:token|secret|password|api[_-]?key|credential)"
    r"[\"'\s]*[:=]\s*[\"'][^\"']{8,})"
)
WRITE_INTENT = re.compile(
    r"(?:>>?|set-content|add-content|out-file)",
    re.I,
)


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name")
    if tool_name not in {"Bash", "PowerShell"}:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    command = str(tool_input.get("command") or tool_input.get("code") or "")

    # For git commit commands, only scan the git verb, not the message body
    if re.match(r"\s*git\s+commit\b", command):
        return 0

    compact = " ".join(command.split())

    for pattern, reason in DENY_PATTERNS:
        if pattern.search(compact):
            deny(reason)
            return 0

    if SECRET_KEY_VALUE.search(compact) and WRITE_INTENT.search(compact):
        deny("Command appears to write secret/credential material to a file.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
