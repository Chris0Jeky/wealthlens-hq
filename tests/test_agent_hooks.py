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
  * post_tool_failure must keep secrets out of the failure ledger (the PR #572
    review counterexamples) with bounded work on any payload size (#573);
  * session_start must emit valid hook JSON even when repo files are missing
    (orientation is fail-open, never blocking).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOKS = REPO / ".claude" / "hooks"
DISPATCH = HOOKS / "dispatch.py"
POST = HOOKS / "post_tool_failure.py"
SESSION = HOOKS / "session_start.py"
SMOKE = HOOKS / "smoke_test.py"

# Build destructive tails by concatenation so this source file does not itself
# contain the literal blocked strings.
_FORCE_PUSH = "git push --for" + "ce origin main"
_RM_RF = "rm -" + "rf /"


def _floor_decision(command: str) -> str:
    # CLAUDE_PROJECT_DIR is load-bearing: since floor v1.6.20 the dispatcher fails
    # CLOSED (ValueError -> deny) when a Bash payload carries neither a `cwd` nor
    # the env var, because it cannot resolve which tier.json governs the command.
    # Claude Code always supplies one; a bare subprocess does not, so every
    # must-ALLOW expectation here silently inverted until this was passed.
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    out = subprocess.run(
        [sys.executable, str(DISPATCH), "--event", "pre"],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(REPO)},
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


def test_session_start_reads_canonical_authority_path(tmp_path: Path) -> None:
    """Authority moved to .agent-harness/tier.json (2026-07-27); the legacy .claude/
    path must still resolve, and the canonical one must win when both exist."""
    for authority_dir, tier_name in ((".claude", "legacy"), (".agent-harness", "workshop")):
        (tmp_path / authority_dir).mkdir()
        (tmp_path / authority_dir / "tier.json").write_text(
            json.dumps({"tier": 3, "name": tier_name, "authority": {"push": "free", "merge": "free"}}),
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
        assert f"Tier: {tier_name} (T3)" in context
        assert f"{authority_dir}/tier.json" in context


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


# --- failure-ledger secret masking (#573, CodeQL alert #5) -------------------
# Every case records a real failure through the hook and inspects the ledger it
# wrote: the property that matters is what reaches failure_ledger.jsonl.

_SECRET = "DO_NOT_LOG_ME"


def _record_failure(tmp_path: Path, error: str, command: str = "", timeout: float = 30) -> str:
    """Run post_tool_failure.py on one failure and return the raw ledger text."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "error": error})
    out = subprocess.run(
        [sys.executable, str(POST)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={"CLAUDE_PROJECT_DIR": str(tmp_path), "SYSTEMROOT": "C:\\Windows", "PATH": "", "PYTHONUTF8": "1"},
        timeout=timeout,
    )
    assert out.returncode == 0, out.stderr
    return (tmp_path / ".claude" / "local" / "failure_ledger.jsonl").read_text(encoding="utf-8")


def _load_post_module() -> object:
    import importlib.util

    spec = importlib.util.spec_from_file_location("post_tool_failure_under_test", POST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The six counterexamples from PR #572's review rounds, each of which leaked the
# secret into the ledger on that PR's heads.
_PR572_COUNTEREXAMPLES = {
    "prefix-longer-than-64": "a" * 65 + "token=" + _SECRET,
    "unicode-prefix": "\u00fcn\u00efc\u00f8d\u00e9_\u043a\u043b\u044e\u0447_token=" + _SECRET,
    "multiline-quoted-value": 'api_key=",first\n' + _SECRET + '"',
    "newline-between-key-and-value": 'api_key:\n  "' + _SECRET + '"',
    "escaped-quote-in-value": 'api_key="abc\\"' + _SECRET + '"',
    "assignment-inside-consumed-value": 'password=",token=abc ' + _SECRET + '"',
}


def test_ledger_masks_pr572_counterexamples(tmp_path: Path) -> None:
    for name, error in _PR572_COUNTEREXAMPLES.items():
        case_dir = tmp_path / name
        case_dir.mkdir()
        ledger = _record_failure(case_dir, error)
        assert _SECRET not in ledger, (name, ledger)
        assert "<redacted>" in ledger, (name, ledger)


def test_ledger_masks_quoting_edge_cases(tmp_path: Path) -> None:
    cases = {
        # An escaped backslash closes the quote; the adjacent text is still value.
        "escaped-backslash-then-text": 'api_key="abc\\\\"' + _SECRET + '"',
        "unterminated-quote": 'password="never closed ' + _SECRET,
        "single-quoted-multiline": "secret_key: '\n" + _SECRET + "\n'",
        "json-quoted-key": '{"client_secret": "' + _SECRET + '", "user": "bob"}',
        "escaped-json-in-text": '{\\"token\\": \\"' + _SECRET + '\\"}',
        "nested-object-value": '{"credentials": {"client_id": "' + _SECRET + '"}}',
        "fat-arrow": "password => '" + _SECRET + "'",
        "camel-case-keyed": "accessKey=" + _SECRET,
    }
    for name, error in cases.items():
        case_dir = tmp_path / name
        case_dir.mkdir()
        ledger = _record_failure(case_dir, error)
        assert _SECRET not in ledger, (name, ledger)


def test_ledger_preserves_authorization_bearer_and_connection_masking(tmp_path: Path) -> None:
    cases = {
        "authorization-bearer": ("Authorization: Bearer " + _SECRET, "authorization=<redacted>"),
        "authorization-basic-in-curl": ('curl -H "Authorization: Basic ' + _SECRET + '"', "authorization=<redacted>"),
        "standalone-bearer": ("-H 'X-Api: bearer " + _SECRET + "'", "Bearer <redacted>"),
        "connection-string": ("postgres://admin:" + _SECRET + "@db.internal:5432/app", "admin:<redacted>@db.internal"),
        "connection-password-with-at": ("redis://u:p@" + _SECRET + "@cache.local", "u:<redacted>@cache.local"),
    }
    for name, (error, expected) in cases.items():
        case_dir = tmp_path / name
        case_dir.mkdir()
        ledger = _record_failure(case_dir, error)
        assert _SECRET not in ledger, (name, ledger)
        assert expected in ledger, (name, ledger)


def test_ledger_keeps_harmless_context(tmp_path: Path) -> None:
    """Masking must not swallow ordinary failure text."""
    error = "GET http://localhost:8080/api failed: token expired; max_tokens=4096 user=bob"
    ledger = _record_failure(tmp_path, error)
    assert "http://localhost:8080/api failed: token expired; max_tokens=4096 user=bob" in ledger


def test_ledger_masks_secret_in_command_target(tmp_path: Path) -> None:
    ledger = _record_failure(tmp_path, "boom", command="API_KEY=" + _SECRET + " ./deploy.sh")
    assert _SECRET not in ledger


def test_ledger_scrub_work_is_bounded_on_huge_payloads(tmp_path: Path) -> None:
    """A multi-megabyte adversarial failure is recorded quickly, and a secret
    inside the persisted window is still masked."""
    import time

    error = 'password="' + _SECRET + '" ' + ("a_" * 20 + "token:" + " x://y:" * 5) * 60_000
    assert len(error) > 4_000_000
    started = time.perf_counter()
    ledger = _record_failure(tmp_path, error, command=error)
    elapsed = time.perf_counter() - started
    assert _SECRET not in ledger
    assert elapsed < 20, elapsed  # subprocess start + 5 MB JSON parse dominate


def test_scrub_is_linear_on_pathological_inputs() -> None:
    """Scanner-level timing: every adversarial shape at the full scan cap
    finishes far below anything a backtracking regex needs."""
    import time

    module = _load_post_module()
    cap = module.SCAN_CAP  # type: ignore[attr-defined]
    shapes = [
        "a_" * 5000 + "token=x",
        "token=" + "a://b:" * 1400 + "@x",
        "token=a://b:c@" * 600,
        "x://" + "y:" * 4500,
        "token :" * 1300,
        "bearer " * 1300,
        "Bearer token=" * 700,
        "'" * 9000,
        "a_key=" + "{" * 9000,
        "api_key=x/api_key=" * 500,
        "api_key: '' " * 800,
        "a://b:@" * 1300,
        "token=a://b:c " * 700 + "@d",
        'password="' + "\\" * 9000,
    ]
    for shape in shapes:
        text = shape[:cap]
        started = time.perf_counter()
        for truncated in (False, True):
            module._Masker(text, truncated).run()  # type: ignore[attr-defined]
        assert time.perf_counter() - started < 0.5, shape[:40]
        # And through the public entry point with a far larger payload.
        started = time.perf_counter()
        module.scrub(shape * 200)  # type: ignore[attr-defined]
        assert time.perf_counter() - started < 0.5, shape[:40]
