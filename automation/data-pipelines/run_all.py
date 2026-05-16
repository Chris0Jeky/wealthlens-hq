"""Cross-platform pipeline runner.

Runs all data fetch scripts then validates the output.
Usage: python automation/data-pipelines/run_all.py [--validate-only]
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

PIPELINE_DIR = Path(__file__).resolve().parent
SCRIPT_TIMEOUT_SECONDS = 300

SCRIPTS = [
    "fetch_wid_data.py",
    "fetch_ons_housing.py",
    "fetch_ons_wealth.py",
    "fetch_hmrc_stats.py",
]


def run_pipelines() -> list[str]:
    """Run each pipeline script, returning names of any that failed."""
    failed: list[str] = []
    for script in SCRIPTS:
        path = PIPELINE_DIR / script
        logger.info("Running %s", script)
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                cwd=str(PIPELINE_DIR),
                timeout=SCRIPT_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failed.append(script)
            logger.error("TIMEOUT: %s exceeded %ds", script, SCRIPT_TIMEOUT_SECONDS)
            continue
        if result.returncode != 0:
            failed.append(script)
            logger.error("FAILED: %s (exit code %d)", script, result.returncode)
    return failed


def run_validation() -> bool:
    """Run the validation module; returns True if all checks pass."""
    logger.info("Validating processed datasets")
    try:
        result = subprocess.run(
            [sys.executable, str(PIPELINE_DIR / "validate.py")],
            timeout=SCRIPT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        logger.error("TIMEOUT: validate.py exceeded %ds", SCRIPT_TIMEOUT_SECONDS)
        return False
    return result.returncode == 0


def main() -> None:
    validate_only = "--validate-only" in sys.argv

    if not validate_only:
        failed = run_pipelines()
        logger.info("Ran %d pipelines, %d failed", len(SCRIPTS), len(failed))
        if failed:
            logger.error("Failed: %s", ", ".join(failed))

    ok = run_validation()

    if not validate_only and failed:
        sys.exit(1)
    if not ok:
        sys.exit(1)
    logger.info("All done.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
