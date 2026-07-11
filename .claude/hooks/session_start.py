#!/usr/bin/env python3
"""Claude Code SessionStart hook — print live orientation instead of mandating reads.

Prints (derived from files at session start, ~0 standing tokens):
  * tier + authority line from .claude/tier.json (authority is declared, not negotiated)
  * open ACTION-REQUIRED items from tasks/ACTION-REQUIRED.md (surfaced every summary;
    only Chris clears them)
  * a failure-ledger triage nudge when the local ledger exceeds 25 entries
  * next-read pointers (seam map, orchestration resume block)

Fail-open: orientation is not safety — any error degrades to a static fallback line.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

FALLBACK = (
    "WealthLens HQ workspace. Read tasks/ACTION-REQUIRED.md and surface its open items "
    "in every summary; only Chris clears them. Check .claude/tier.json for authority."
)


def tier_line() -> str:
    cfg = json.loads((ROOT / ".claude" / "tier.json").read_text(encoding="utf-8"))
    auth = cfg.get("authority", {})
    return (
        f"Tier: {cfg.get('name', '?')} (T{cfg.get('tier', '?')}) — authority: "
        f"push {auth.get('push', '?')} / merge {auth.get('merge', '?')} (.claude/tier.json)."
    )


def action_required_items() -> list[str]:
    text = (ROOT / "tasks" / "ACTION-REQUIRED.md").read_text(encoding="utf-8")
    # Cut at the "## Done" HEADING only — the protocol paragraph mentions
    # `## Done` inline, and a plain substring split truncated before the
    # open items (found by exercising the hook against the real file).
    done = re.search(r"^## Done\s*$", text, re.M)
    open_section = text[: done.start()] if done else text
    items: list[str] = []
    for m in re.finditer(r"^\s*\d+\.\s*- \[ \] \*\*(.+?)\*\*(.*)$", open_section, re.M):
        due = re.search(r"\[due: [^\]]+\]", m.group(2))
        items.append(m.group(1) + (f" {due.group(0)}" if due else ""))
    return items


def ledger_nudge() -> str:
    ledger = ROOT / ".claude" / "local" / "failure_ledger.jsonl"
    if not ledger.exists():
        return ""
    n = sum(1 for _ in ledger.open(encoding="utf-8", errors="ignore"))
    if n > 25:
        return (
            f"Failure ledger: {n} untriaged local entries — a gardener triage pass is due "
            "(classify, promote reviewed summaries to docs/agentic/FAILURE_LEDGER.md, rotate)."
        )
    return ""


def _safe(fn, default):
    """Each orientation section fails open on its own — a missing tier.json must
    not swallow the ACTION-REQUIRED items, and vice versa."""
    try:
        return fn()
    except Exception:
        return default


def build_context() -> str:
    lines = [
        "WealthLens HQ — multi-domain workspace (code, content, research, strategy, outreach).",
        _safe(tier_line, "Tier: unknown (.claude/tier.json missing/unreadable)."),
        "Rules digest: data cites source + URL + access date; charts WCAG AA; volunteers "
        "read this code; never merge red CI; merges go through docs/agentic/REVIEW_GATE.md.",
    ]
    items = _safe(action_required_items, [])
    if items:
        lines.append(
            f"ACTION REQUIRED — {len(items)} open items (surface in EVERY summary/handoff; "
            "only Chris clears them; guides in tasks/ACTION-REQUIRED.md):"
        )
        lines.extend(f"  {i}. {t}" for i, t in enumerate(items, 1))
    if (ROOT / "AGENT_MAP.md").exists():
        lines.append("Seam map: AGENT_MAP.md — regions, verify commands, do-not-read index.")
    lines.append(
        "On Chris's box: read the newest RESUME block of ../hq-private/projects/wealthlens/"
        "memories/session_notes/ORCHESTRATION.md before starting work (skip if absent)."
    )
    nudge = _safe(ledger_nudge, "")
    if nudge:
        lines.append(nudge)
    return "\n".join(lines)


def main() -> int:
    try:
        context = build_context()
    except Exception:  # fail open — orientation must never block a session
        context = FALLBACK
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
