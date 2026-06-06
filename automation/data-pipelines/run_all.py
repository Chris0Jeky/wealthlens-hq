"""Cross-platform pipeline runner.

Runs all data fetch scripts then validates the output.
Usage: python automation/data-pipelines/run_all.py [--validate-only]
"""

from __future__ import annotations

import logging
import subprocess  # nosec B404 - runner invokes a static allow-list of local pipeline scripts.
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

PIPELINE_DIR = Path(__file__).resolve().parent
SCRIPT_TIMEOUT_SECONDS = 300

# Every fetch_*.py pipeline in this directory must be listed here so `run_all.py`
# runs the FULL set (matching deploy.yml, which globs `for script in fetch_*.py`).
# This previously omitted child_poverty and generational_wealth, so `run_all.py`
# silently skipped two shipped datasets. deploy.yml regenerates them at build time
# via its glob, BUT the scheduled weekly-data-update.yml runs run_all.py and then
# commits data/processed/ — so those two committed CSVs were never refreshed by the
# weekly job. test_run_all.py guards this list against drift. Alphabetical for diff.
SCRIPTS = [
    "fetch_boe_rates.py",
    "fetch_child_poverty.py",
    "fetch_generational_wealth.py",
    "fetch_hmrc_stats.py",
    "fetch_ons_gdhi.py",
    "fetch_ons_housing.py",
    "fetch_ons_wealth.py",
    "fetch_productivity_pay.py",
    "fetch_tax_composition.py",
    "fetch_wage_stagnation.py",
    "fetch_wid_data.py",
]


def run_pipelines() -> list[str]:
    """Run each pipeline script, returning names of any that failed."""
    failed: list[str] = []
    for script in SCRIPTS:
        path = PIPELINE_DIR / script
        logger.info("Running %s", script)
        try:
            result = subprocess.run(  # nosec B603 - script path is selected from SCRIPTS allow-list.
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
        result = subprocess.run(  # nosec B603 - validation script path is fixed within this repository.
            [sys.executable, str(PIPELINE_DIR / "validate.py")],
            timeout=SCRIPT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        logger.error("TIMEOUT: validate.py exceeded %ds", SCRIPT_TIMEOUT_SECONDS)
        return False
    return result.returncode == 0


def main() -> None:
    validate_only = "--validate-only" in sys.argv
    # --fetch-only runs the pipelines without the trailing validation pass.
    # `make pipelines` delegates here so there is ONE pipeline list (SCRIPTS,
    # guarded by test_run_all.py) instead of a second copy in the Makefile.
    fetch_only = "--fetch-only" in sys.argv
    if validate_only and fetch_only:
        logger.error("--validate-only and --fetch-only are mutually exclusive")
        sys.exit(2)

    failed: list[str] = []
    if not validate_only:
        failed = run_pipelines()
        logger.info("Ran %d pipelines, %d failed", len(SCRIPTS), len(failed))
        if failed:
            logger.error("Failed: %s", ", ".join(failed))

    ok = True
    if not fetch_only:
        ok = run_validation()

    if failed:
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
