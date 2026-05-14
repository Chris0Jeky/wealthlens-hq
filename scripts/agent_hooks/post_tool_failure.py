#!/usr/bin/env python3
"""Record sanitized Claude Code tool failures for later review.

Records enough to prevent recurring silent failures while minimizing
secret/context leakage.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
LEDGER = ROOT / ".claude" / "local" / "failure_ledger.jsonl"
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b((?:\w+[_-])?(?:token|secret|password|api[_-]?key|auth(?:orization)?|credential)"
    r"(?:[_-]key)?"
    r"|(?:\w+[_-])*(?:encryption|signing|private|ssh|gpg|hmac|jwt|session|csrf|access)[_-]key)"
    r"[\"'\s]*[:=][\"'\s]*"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s,;}\]]+)"
)
AUTHORIZATION_RE = re.compile(
    r"(?i)\bauthorization\b\s*[:=]\s*(?:bearer\s+)?[A-Za-z0-9._~+/=-]+"
)
BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
CONN_STRING_RE = re.compile(
    r"(?i)\b\w+://[^/:]+:([^@]+)@[^\s,;\"']+"
)


def scrub(text: object, limit: int = 240) -> str:
    s = str(text or "")
    s = AUTHORIZATION_RE.sub("authorization=<redacted>", s)
    s = BEARER_RE.sub("Bearer <redacted>", s)
    s = CONN_STRING_RE.sub(lambda m: m.group(0).replace(m.group(1), "<redacted>"), s)
    s = SECRET_ASSIGNMENT_RE.sub(lambda m: f"{m.group(1)}=<redacted>", s)
    s = s.replace(str(ROOT), ".")
    if len(s) > limit:
        s = s[:limit] + "... <truncated>"
    return s


def summarize_target(value: object) -> str:
    s = str(value or "")
    if not s:
        return ""
    scrubbed = scrub(s, 500)
    first = scrubbed.split(maxsplit=1)[0]
    digest = hashlib.sha256(scrubbed.encode("utf-8", "ignore")).hexdigest()[:12]
    return f"{scrub(first, 60)} sha256:{digest}"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name", "unknown")
    tool_input = payload.get("tool_input", {}) or {}
    entry = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "class": "unclassified",
        "surface": scrub(tool_name, 80),
        "command_or_target": summarize_target(
            tool_input.get("command") or tool_input.get("file_path") or ""
        ),
        "failure": scrub(
            payload.get("error") or payload.get("stderr") or payload.get("message") or "",
            240,
        ),
        "workaround": "",
        "future_fix": "classify and promote if recurring",
        "status": "open",
    }

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUseFailure",
                    "additionalContext": (
                        "Tool failure recorded in ignored "
                        ".claude/local/failure_ledger.jsonl. Classify unresolved "
                        "failures in the handoff."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
