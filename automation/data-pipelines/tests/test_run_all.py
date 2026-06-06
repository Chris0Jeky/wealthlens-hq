"""Guard: run_all.py must run EVERY pipeline.

run_all.py's SCRIPTS list previously drifted from the actual fetch_*.py files
(child_poverty and generational_wealth were missing), so `python run_all.py`
silently skipped two shipped datasets even though deploy.yml regenerated them
via its `for script in fetch_*.py` glob. This test locks SCRIPTS to the real set
of pipelines so the list cannot drift again.
"""

from __future__ import annotations

import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from run_all import SCRIPTS  # noqa: E402


def test_scripts_matches_every_fetch_pipeline() -> None:
    """SCRIPTS must equal the set of fetch_*.py files in the pipeline dir."""
    on_disk = {p.name for p in PIPELINE_DIR.glob("fetch_*.py")}
    listed = set(SCRIPTS)

    missing = on_disk - listed
    extra = listed - on_disk
    assert not missing, f"fetch_*.py pipelines missing from run_all.SCRIPTS: {sorted(missing)}"
    assert not extra, f"run_all.SCRIPTS lists non-existent pipelines: {sorted(extra)}"


def test_scripts_has_no_duplicates() -> None:
    """A copy-paste slip that double-lists a pipeline would run it twice."""
    assert len(SCRIPTS) == len(set(SCRIPTS)), "run_all.SCRIPTS contains duplicates"
