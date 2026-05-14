#!/usr/bin/env python3
"""Claude Code PreToolUse hook for dangerous shell commands.

Reads hook JSON on stdin and denies commands that are destructive, credential-risky,
or inconsistent with the repo's small-diff workflow.
"""

from __future__ import annotations

import json
import re
import sys

DENY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # ── PowerShell pipeline-to-delete safety ───────────────────────────────
    (
        re.compile(
            r"\|\s*"
            r"(?:(?:%\s*\{|foreach-object\s*\{)[^}]*)?"
            r"\b(?:remove-item|ri|del|erase)\b",
            re.I,
        ),
        "Piping into Remove-Item/del is blocked (risks deleting unintended files). "
        "Remove specific named paths directly.",
    ),
    (
        re.compile(
            r"\b(?:get-childitem|gci|dir)\b[^|]*-include\b",
            re.I,
        ),
        "Get-ChildItem -Include has known filtering bugs in PowerShell that can select "
        "far more files than intended. Use -Filter instead.",
    ),
    (
        re.compile(
            r"\b(?:remove-item|ri)\b[^|;]*(?<![/\\])\*(?!\.\w+\b)",
            re.I,
        ),
        "Remove-Item with bare wildcard (*) is blocked. "
        "Specify exact file extension (e.g. *.pyc) or remove specific paths.",
    ),
    (
        re.compile(
            r"\|\s*(?:xargs|%\s*\{[^}]*)\s*\brm\b",
            re.I,
        ),
        "Piping into rm via xargs/ForEach is blocked. "
        "Remove specific named paths.",
    ),
    # ── Destructive commands ───────────────────────────────────────────────
    (
        re.compile(
            r"\brm\b(?=[^;&|\n]*\s(?:-[A-Za-z]*r[A-Za-z]*|--recursive)\b)"
            r"(?=[^;&|\n]*\s(?:-[A-Za-z]*f[A-Za-z]*|--force)\b)",
            re.I,
        ),
        "Destructive recursive removal requires explicit human approval.",
    ),
    (
        re.compile(r"\bremove-item\b(?=[^;&|\n]*\s-(?:recurse|r)\b)", re.I),
        "PowerShell recursive removal requires explicit human approval.",
    ),
    (
        re.compile(r"\b(?:rmdir|rd)\s+(?:/s\b|.+\s/s\b)", re.I),
        "Windows recursive directory removal requires explicit human approval.",
    ),
    (
        re.compile(r"\bdel\s+(?:/s\b|.+\s/s\b)", re.I),
        "Windows recursive deletion requires explicit human approval.",
    ),
    (
        re.compile(r"\bfind\b.+\s-delete\b", re.I),
        "Find-delete can recursively remove files; ask first.",
    ),
    # ── Git safety ─────────────────────────────────────────────────────────
    (
        re.compile(r"\bgit\s+reset\s+--hard\b", re.I),
        "Hard reset would discard work; inspect state and ask first.",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--(?:soft|mixed)\b", re.I),
        "Soft/mixed reset rewrites commit history. Create new commits instead.",
    ),
    (
        re.compile(r"\bgit\s+rebase\b(?!\s+--(?:abort|continue|skip)\b)", re.I),
        "Rebase is not allowed. It rewrites commit history "
        "and requires force-push. Use 'git merge main' instead.",
    ),
    (
        re.compile(r"\bgit\s+pull\b(?=[^;&|\n]*--rebase\b)", re.I),
        "Pull-with-rebase rewrites local history. Use 'git pull --no-rebase' "
        "or 'git merge' instead.",
    ),
    (
        re.compile(
            r"\bgit\s+clean\b(?=[^;&|\n]*(?:--force\b|-[A-Za-z]*f[A-Za-z]*\b))",
            re.I,
        ),
        "Git clean can delete untracked work; ask first.",
    ),
    (
        re.compile(r"\bgit\s+checkout\s+--\s+\S+", re.I),
        "Path checkout can discard local changes; inspect state and ask first.",
    ),
    (
        re.compile(
            r"\bgit\s+restore\s+(?:\.(?:\s|$)|--(?:worktree|staged)\b)",
            re.I,
        ),
        "Git restore discards uncommitted changes. Ask the user first.",
    ),
    (
        re.compile(
            r"\bgit\s+push\b(?=[^;&|\n]*(?:--force(?:-with-lease)?\b|-[A-Za-z]*f[A-Za-z]*\b))",
            re.I,
        ),
        "Force-push is blocked by project policy.",
    ),
    (
        re.compile(r"\bgit\s+branch\b.*\s-D\b", re.I),
        "Force-deleting branches can discard saved work; ask first.",
    ),
    # ── System safety ──────────────────────────────────────────────────────
    (re.compile(r"\bsudo\b", re.I), "sudo is outside normal repo workflow."),
    (
        re.compile(
            r"\bchmod\b(?=[^;&|\n]*(?:^|\s)(?:-R|--recursive)\b)(?=[^;&|\n]*\b777\b)",
            re.I,
        ),
        "Recursive world-writable permissions are blocked.",
    ),
    (
        re.compile(
            r"\b(?:curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b.+\|\s*"
            r"(?:sh|bash|zsh|pwsh|powershell|iex|invoke-expression)\b",
            re.I,
        ),
        "Piping remote scripts into an interpreter is blocked.",
    ),
    (
        re.compile(r"\bnpm\s+publish\b", re.I),
        "Publishing packages requires explicit release approval.",
    ),
    # ── Database safety ────────────────────────────────────────────────────
    (
        re.compile(
            r"\b(?:drop\s+(?:database|schema|table)|truncate\s+table|delete\s+from)\b",
            re.I,
        ),
        "Destructive database commands require explicit approval.",
    ),
]

ENV_FILE_REF = re.compile(
    r"(?<![\w.-])\.env(?!\.example)(?:$|[\s\"'`>/\\])|"
    r"(?<![\w.-])\.env\.(?!example\b)[A-Za-z0-9_.-]+",
    re.I,
)
SECRET_KEY_VALUE = re.compile(
    r"(?i)(?:\b(?:\w+[_-])?(?:token|secret|password|api[_-]?key|auth(?:orization)?|credential)"
    r"(?:[_-]key)?"
    r"|\b(?:\w+[_-])*(?:encryption|signing|private|ssh|gpg|hmac|jwt|session|csrf|access)[_-]key)"
    r"[\"'\s]*[:=]"
)
WRITE_INTENT = re.compile(
    r"(?:>>?|2>|set-content|add-content|out-file|tee-object|\bsed\s+-i\b|\bperl\s+-pi\b)",
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
    compact = " ".join(command.split())

    for pattern, reason in DENY_PATTERNS:
        if pattern.search(compact):
            deny(reason)
            return 0

    if ENV_FILE_REF.search(compact):
        deny("Command touches a local env file. Use templates or ask for explicit approval.")
        return 0

    if SECRET_KEY_VALUE.search(compact) and WRITE_INTENT.search(compact):
        deny("Command appears to write token, password, authorization, or API key material.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
