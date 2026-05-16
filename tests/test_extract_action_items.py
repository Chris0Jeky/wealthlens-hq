"""Tests for automation/analysis/extract_action_items.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from extract_action_items import format_report, main, scan_directory, scan_file
import extract_action_items as module


# ---------------------------------------------------------------------------
# scan_file
# ---------------------------------------------------------------------------


def test_scan_file_checkbox_items(tmp_path: Path) -> None:
    """Only unchecked checkbox items are returned."""
    md = tmp_path / "tasks.md"
    md.write_text("- [ ] Task one\n- [ ] Task two\n- [x] Done task\n", encoding="utf-8")

    items = scan_file(md)

    assert len(items) == 2
    assert "- [ ] Task one" in items
    assert "- [ ] Task two" in items


def test_scan_file_action_todo_patterns(tmp_path: Path) -> None:
    """Action: and TODO: lines are extracted and wrapped in checkbox syntax."""
    md = tmp_path / "notes.md"
    md.write_text(
        "Action: Do something\nTODO: Fix this\nNotes: Not an action\n",
        encoding="utf-8",
    )

    items = scan_file(md)

    assert len(items) == 2
    # Both should be wrapped in checkbox format
    assert all(item.startswith("- [ ]") for item in items)
    assert any("Do something" in item for item in items)
    assert any("Fix this" in item for item in items)


def test_scan_file_bold_action(tmp_path: Path) -> None:
    """Bold-action pattern like '- **Action**: Bold item' is extracted."""
    md = tmp_path / "bold.md"
    md.write_text("- **Action**: Bold item\n", encoding="utf-8")

    items = scan_file(md)

    assert len(items) == 1
    assert "Bold item" in items[0]
    assert items[0].startswith("- [ ]")


def test_scan_file_deduplication(tmp_path: Path) -> None:
    """Duplicate action items are returned only once."""
    md = tmp_path / "dupes.md"
    md.write_text("- [ ] Same task\n- [ ] Same task\n- [ ] Same task\n", encoding="utf-8")

    items = scan_file(md)

    assert len(items) == 1
    assert "- [ ] Same task" in items


def test_scan_file_missing_file() -> None:
    """Scanning a nonexistent file returns an empty list (no exception)."""
    items = scan_file(Path("/nonexistent/path/file.md"))

    assert items == []


def test_scan_file_unreadable_file(tmp_path: Path) -> None:
    """A file with invalid UTF-8 bytes returns an empty list."""
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff\xfe" + b"- [ ] task\n" + b"\x80\x81\x82")

    items = scan_file(bad)

    assert items == []


# ---------------------------------------------------------------------------
# scan_directory
# ---------------------------------------------------------------------------


def test_scan_directory_empty(tmp_path: Path) -> None:
    """An empty directory produces an empty results dict."""
    results = scan_directory(tmp_path)

    assert results == {}


def test_scan_directory_with_files(tmp_path: Path) -> None:
    """Only .md files are scanned; .txt files are ignored."""
    (tmp_path / "a.md").write_text("- [ ] Item A\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("TODO: Item B\n", encoding="utf-8")
    (tmp_path / "c.txt").write_text("- [ ] Should be ignored\n", encoding="utf-8")

    results = scan_directory(tmp_path)

    # Only .md files should appear as keys
    result_names = {p.name for p in results}
    assert "a.md" in result_names
    assert "b.md" in result_names
    assert "c.txt" not in result_names
    assert len(results) == 2


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------


def test_format_report(tmp_path: Path) -> None:
    """format_report includes headings, items, and the total count."""
    # Use tmp_path as a fake repo root so relative paths work
    file_a = tmp_path / "research" / "raw" / "a.md"
    file_a.parent.mkdir(parents=True, exist_ok=True)
    file_a.touch()

    results = {
        file_a: ["- [ ] First item", "- [ ] Second item"],
    }

    report = format_report(results, tmp_path)

    assert "## Action items extracted from research/raw/" in report
    assert "### research/raw/a.md" in report
    assert "- [ ] First item" in report
    assert "- [ ] Second item" in report
    assert "Total: 2 action items from 1 files" in report


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_missing_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() returns gracefully when RESEARCH_DIR does not exist."""
    monkeypatch.setattr(module, "RESEARCH_DIR", Path("/nonexistent/research/raw"))

    # Pass empty argv so argparse does not consume pytest's sys.argv
    main([])


def test_main_output_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """main(--output) writes a report file with expected content."""
    # Set up a fake research directory with one .md file
    research_dir = tmp_path / "research" / "raw"
    research_dir.mkdir(parents=True)
    (research_dir / "sample.md").write_text(
        "- [ ] Output test item\n", encoding="utf-8"
    )

    # Point module constants at the temp layout
    monkeypatch.setattr(module, "RESEARCH_DIR", research_dir)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

    out_file = tmp_path / "out.md"
    main(["--output", str(out_file)])

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "Output test item" in content
    assert "Total:" in content
