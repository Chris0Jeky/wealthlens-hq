"""Execute the refresh workflow's Git snippets against disposable, offline repos."""

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/weekly-data-update.yml"
CHART = "projects/wealthlens-dashboard/charts/example.html"
DATA = "projects/wealthlens-dashboard/frontend/public/data/datasets.json"
NEW_DATA = "projects/wealthlens-dashboard/frontend/public/data/new.csv"
IGNORED = "projects/wealthlens-dashboard/data/processed/example.csv"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


@pytest.mark.parametrize("change", ["data", "chart", "new-data", "new-chart", "deleted", "none", "ignored"])
def test_refresh_detects_and_stages_served_artifacts(tmp_path: Path, change: str) -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    step = workflow.split("      - name: Check for changes\n", 1)[1]
    snippet = textwrap.dedent(step.split("        run: |\n", 1)[1].split("      - name:", 1)[0])
    stage = "\n".join(line.strip() for line in workflow.splitlines() if line.strip().startswith("git add "))
    bash = r"C:\Program Files\Git\bin\bash.exe" if sys.platform == "win32" else shutil.which("bash")
    assert bash, "The workflow integration test requires Bash"
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / ".gitignore").write_bytes((ROOT / ".gitignore").read_bytes())

    def write(name: str) -> None:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("changed\n", encoding="utf-8")

    for name in (CHART, DATA):
        write(name)
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")
    changed = {"data": DATA, "chart": CHART, "new-data": NEW_DATA,
               "new-chart": CHART.replace("example", "new"), "deleted": DATA}.get(change)
    if change == "deleted":
        (repo / DATA).unlink()
    elif changed:
        write(changed)
        if change in ("data", "chart"):
            (repo / changed).write_text("updated\n", encoding="utf-8")
    write(IGNORED)
    write("projects/wealthlens-dashboard/frontend/public/data/not-whitelisted.json")
    write("unrelated.txt")
    output = tmp_path / "output"
    env = dict(os.environ, GITHUB_OUTPUT=output.as_posix())
    subprocess.run([bash, "-e", "-o", "pipefail", "-c", snippet], cwd=repo, env=env, check=True,
                   capture_output=True, text=True)
    assert output.read_text().strip() == f"changed={'true' if changed else 'false'}"
    if changed:
        subprocess.run([bash, "-e", "-o", "pipefail", "-c", stage], cwd=repo, check=True,
                       capture_output=True, text=True)
        assert git(repo, "diff", "--cached", "--name-only").splitlines() == [changed]


def test_refresh_generates_static_api_after_pipelines() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert workflow.index("python automation/data-pipelines/run_all.py") < workflow.index(
        "python scripts/generate_static_api.py"
    ) < workflow.index("      - name: Check for changes")
    assert "\non:\n  workflow_dispatch:\n" in workflow
    assert "\n  schedule:" not in workflow


def test_refresh_stops_on_git_failure(tmp_path: Path) -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    step = workflow.split("      - name: Check for changes\n", 1)[1]
    snippet = textwrap.dedent(step.split("        run: |\n", 1)[1].split("      - name:", 1)[0])
    bash = r"C:\Program Files\Git\bin\bash.exe" if sys.platform == "win32" else shutil.which("bash")
    assert bash
    output = tmp_path / "output"
    result = subprocess.run([bash, "-e", "-o", "pipefail", "-c", snippet], cwd=tmp_path,
                            env=dict(os.environ, GITHUB_OUTPUT=output.as_posix()), capture_output=True, text=True)
    assert result.returncode != 0
    assert not output.exists()
