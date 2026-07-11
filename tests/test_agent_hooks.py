"""Regression tests for the Claude Code agent hooks (.claude/hooks/).

The hooks are invoked by Claude Code as subprocesses reading a JSON payload on
stdin, so we exercise the real files the same way. The deny floor (dispatch.py)
carries its own must-block / must-allow matrix in smoke_test.py — CI runs the
whole matrix here so a floor change can never land silently red. A handful of
this repo's earned regressions are also pinned directly:

  * the floor must NOT fail open on a ``git commit`` that CHAINS or SUBSTITUTES
    a destructive command (the old prefix bypass let
    ``git commit -m wip && git push --force`` through);
  * inert quoted text (commit messages describing dangerous commands) must not
    false-positive;
  * post_tool_failure must not crash on a whitespace-only target — the hook
    that RECORDS failures must not itself fail;
  * session_start must emit valid hook JSON even when repo files are missing
    (orientation is fail-open, never blocking).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / ".claude" / "hooks"
DISPATCH = HOOKS / "dispatch.py"
POST = HOOKS / "post_tool_failure.py"
SESSION = HOOKS / "session_start.py"
SMOKE = HOOKS / "smoke_test.py"

# Build destructive tails by concatenation so this source file does not itself
# contain the literal blocked strings.
_FORCE_PUSH = "git push --for" + "ce origin main"
_RM_RF = "rm -" + "rf /"


def _floor_decision(command: str) -> str:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    out = subprocess.run(
        [sys.executable, str(DISPATCH), "--event", "pre"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0  # the floor signals via printed JSON, never a crash
    if not out.stdout.strip():
        return "allow"
    return str(json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"])


def test_smoke_matrix_green() -> None:
    """The full must-block/must-allow matrix (SPECS §6) is the floor's contract."""
    out = subprocess.run([sys.executable, str(SMOKE)], capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stdout + out.stderr


def test_pure_commit_with_secret_like_message_allowed() -> None:
    assert _floor_decision('git commit -m "set api_key=abc12345 in env"') == "allow"


def test_commit_message_describing_dangerous_command_allowed() -> None:
    assert _floor_decision(f'git commit -am "describe the {_FORCE_PUSH} bug" && git push') == "allow"


def test_commit_chained_force_push_denied() -> None:
    assert _floor_decision(f"git commit -m wip && {_FORCE_PUSH}") == "deny"


def test_commit_chained_rm_rf_denied() -> None:
    assert _floor_decision(f"git commit -m wip; {_RM_RF}") == "deny"


def test_commit_with_command_substitution_outside_message_denied() -> None:
    assert _floor_decision(f"git commit $({_FORCE_PUSH}) -m wip") == "deny"


def test_commit_substitution_inside_double_quoted_message_denied() -> None:
    # Double quotes EXPAND $(...): the inner command executes, so it is scanned.
    assert _floor_decision(f'git commit -m "wip $({_RM_RF})"') == "deny"


def test_commit_substitution_inside_single_quoted_message_allowed() -> None:
    # Single quotes never expand — inert text must not false-positive.
    assert _floor_decision(f"git commit -m 'wip $({_RM_RF})'") == "allow"


def test_post_tool_failure_survives_whitespace_target(tmp_path: Path) -> None:
    """A failing tool call whose command is whitespace-only must still be recorded
    (summarize_target('   ') once raised IndexError and crashed the hook)."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "   "}, "error": "boom"})
    out = subprocess.run(
        [sys.executable, str(POST)],
        input=payload,
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(tmp_path), "SYSTEMROOT": "C:\\Windows", "PATH": ""},
    )
    assert out.returncode == 0, out.stderr


def test_session_start_fails_open_outside_repo(tmp_path: Path) -> None:
    """With no tier.json / ACTION-REQUIRED.md present, the hook must still emit
    valid hook JSON (fallback context) and exit 0."""
    out = subprocess.run(
        [sys.executable, str(SESSION)],
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(tmp_path), "SYSTEMROOT": "C:\\Windows", "PATH": ""},
    )
    assert out.returncode == 0, out.stderr
    blob = json.loads(out.stdout)
    assert blob["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert blob["hookSpecificOutput"]["additionalContext"]


def test_session_start_surfaces_action_required(tmp_path: Path) -> None:
    """Open ACTION-REQUIRED items are printed into the orientation context."""
    (tmp_path / "tasks").mkdir()
    (tmp_path / "tasks" / "ACTION-REQUIRED.md").write_text(
        # The protocol prose MENTIONS `## Done` inline before the open items —
        # the parser must cut at the heading, not the first substring match.
        "Protocol: move finished items to the `## Done` section.\n\n"
        "## Open items\n\n"
        "1. - [ ] **Register the domain** — P2 [due: 2026-07-31]\n\n"
        "## Done\n\n- [x] **Old thing** [completed: 2026-01-01]\n",
        encoding="utf-8",
    )
    out = subprocess.run(
        [sys.executable, str(SESSION)],
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(tmp_path), "SYSTEMROOT": "C:\\Windows", "PATH": ""},
    )
    assert out.returncode == 0, out.stderr
    context = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Register the domain" in context
    assert "[due: 2026-07-31]" in context
    assert "Old thing" not in context
