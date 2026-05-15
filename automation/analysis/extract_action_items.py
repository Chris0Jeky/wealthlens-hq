"""Extract action items from research files.

Action items should be reviewed before being appended to tasks/inbox.md.

Scans all .md files under research/raw/ recursively and extracts:
- Unchecked checkbox items: ``- [ ] ...``
- Lines starting with "Action:" or "TODO:" (case-insensitive)
- Lines starting with bold-action patterns like "- **Action**:"

Results are grouped by source file, deduplicated, and printed to stdout
(or written to a file with --output). Nothing is auto-appended anywhere;
the user reviews the output first.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Repository root: automation/analysis/ -> two parents up
REPO_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = REPO_ROOT / "research" / "raw"

# Patterns that indicate an action item
_CHECKBOX_RE = re.compile(r"^\s*-\s*\[\s*\]\s+.+", re.MULTILINE)
_ACTION_TODO_RE = re.compile(
    r"^\s*(?:action|todo)\s*:\s*.+", re.IGNORECASE | re.MULTILINE
)
_BOLD_ACTION_RE = re.compile(
    r"^\s*-\s*\*\*(?:action|todo)\*\*\s*:\s*.+", re.IGNORECASE | re.MULTILINE
)


def _normalise(item: str) -> str:
    """Strip whitespace for deduplication comparison."""
    return item.strip()


def _to_checkbox(item: str) -> str:
    """Ensure the item is formatted as a Markdown checkbox line.

    Items that already start with ``- [ ]`` are kept as-is (after stripping).
    Other items (e.g. ``Action: do X``) are wrapped in checkbox syntax.
    """
    stripped = item.strip()
    if stripped.startswith("- [ ]"):
        return stripped
    # Strip leading list marker / bold wrapper if present
    # e.g. "- **Action**: do X" -> "do X"
    cleaned = re.sub(
        r"^[-*]\s*(?:\*\*(?:action|todo)\*\*\s*:\s*)?",
        "",
        stripped,
        flags=re.IGNORECASE,
    ).strip()
    # Also strip bare "Action:" / "TODO:" prefix
    cleaned = re.sub(
        r"^(?:action|todo)\s*:\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    if not cleaned:
        return stripped  # fallback: return original
    return f"- [ ] {cleaned}"


def scan_file(path: Path) -> list[str]:
    """Return deduplicated action items found in *path*."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return []

    hits: list[str] = []
    for pattern in (_CHECKBOX_RE, _ACTION_TODO_RE, _BOLD_ACTION_RE):
        hits.extend(pattern.findall(text))

    # Deduplicate while preserving first-seen order
    seen: set[str] = set()
    unique: list[str] = []
    for raw in hits:
        key = _normalise(raw)
        if key and key not in seen:
            seen.add(key)
            unique.append(_to_checkbox(raw))
    return unique


def scan_directory(directory: Path) -> dict[Path, list[str]]:
    """Recursively scan *directory* for .md files and extract action items.

    Returns a mapping of ``{file_path: [action_items]}`` with only non-empty
    entries.
    """
    results: dict[Path, list[str]] = {}
    for md_file in sorted(directory.rglob("*.md")):
        items = scan_file(md_file)
        if items:
            results[md_file] = items
    return results


def format_report(
    results: dict[Path, list[str]],
    repo_root: Path,
) -> str:
    """Build a human-readable Markdown report from scan results."""
    lines: list[str] = []
    lines.append("## Action items extracted from research/raw/")
    lines.append("")

    total_items = 0
    for file_path, items in results.items():
        rel = file_path.relative_to(repo_root)
        # Use forward slashes for consistent Markdown output
        lines.append(f"### {rel.as_posix()}")
        for item in items:
            lines.append(item)
        lines.append("")
        total_items += len(items)

    lines.append("---")
    file_count = len(results)
    lines.append(f"Total: {total_items} action items from {file_count} files")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract action items from research/raw/ Markdown files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be found without side effects (default behaviour).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="FILE",
        help="Write results to FILE instead of stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for action item extraction."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    args = parse_args(argv)

    if not RESEARCH_DIR.is_dir():
        logger.warning(
            "Directory %s does not exist — nothing to scan.", RESEARCH_DIR
        )
        return

    logger.info("Scanning %s for action items …", RESEARCH_DIR)
    results = scan_directory(RESEARCH_DIR)

    if not results:
        logger.info("No action items found.")
        return

    report = format_report(results, REPO_ROOT)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(report + "\n", encoding="utf-8")
        logger.info("Report written to %s", out_path)
    else:
        # Reconfigure stdout for UTF-8 on Windows where the default
        # console encoding (e.g. cp1252) cannot represent all characters
        # found in research Markdown files.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.write(report + "\n")

    logger.info("Done. Review items before appending to tasks/inbox.md.")


if __name__ == "__main__":
    main()
