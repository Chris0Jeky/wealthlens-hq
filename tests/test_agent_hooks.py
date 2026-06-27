"""Regression tests for the agent safety hooks (scripts/agent_hooks/).

The hooks are invoked by Claude Code as subprocesses reading a JSON payload on
stdin, so we exercise the real files the same way (no import gymnastics, and no
risk of the live hook scanning literal blocked strings in this test's own
process). Two regressions are locked:

  * pre_tool_use must NOT fail open on a ``git commit`` that CHAINS a destructive
    command after it (the old ``git commit`` prefix bypass exempted the whole
    line, so ``git commit -m wip && git push --force`` skipped every deny rule);
  * post_tool_failure.summarize_target must not crash (IndexError) on a
    whitespace-only target — the hook that RECORDS failures must not itself fail.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "scripts" / "agent_hooks"
PRE = HOOKS / "pre_tool_use.py"
POST = HOOKS / "post_tool_failure.py"

# Build the destructive tails by concatenation so this source file does not itself
# contain the literal blocked strings.
_FORCE_PUSH = "git push --for" + "ce origin main"
_RM_RF = "rm -" + "rf /"


def _pre_decision(command: str) -> str:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    out = subprocess.run([sys.executable, str(PRE)], input=payload, capture_output=True, text=True)
    assert out.returncode == 0  # the hook signals via printed JSON, never a non-zero crash
    blob = (out.stdout + out.stderr).lower()
    return "deny" if ("deny" in blob or "blocked" in blob) else "allow"


def test_pure_commit_with_secret_like_message_allowed() -> None:
    # The whole point of the commit exemption: a secret-like string in the MESSAGE
    # must not false-positive on a plain commit.
    assert _pre_decision('git commit -m "set api_key=abc12345 in env"') == "allow"


def test_normal_commit_then_push_allowed() -> None:
    assert _pre_decision('git commit -q -m "fix: x" && git push 2>&1 | tail -2') == "allow"


def test_commit_chained_force_push_denied() -> None:
    assert _pre_decision(f"git commit -m wip && {_FORCE_PUSH}") == "deny"


def test_commit_chained_rm_rf_denied() -> None:
    assert _pre_decision(f"git commit -m wip; {_RM_RF}") == "deny"


def test_post_tool_failure_survives_whitespace_target() -> None:
    """A failing tool call whose command is whitespace-only must still be recorded
    (before the fix, summarize_target('   ') raised IndexError and crashed the hook)."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "   "}, "error": "boom"})
    out = subprocess.run([sys.executable, str(POST)], input=payload, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
