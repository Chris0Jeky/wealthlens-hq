"""Load and validate the assumption registry from YAML.

Blueprint v5 §7.6: machine-readable registry of every modelling assumption.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from wealthlens_sim.assumptions.schema import AssumptionRegistry

_DEFAULT_PATH = Path(__file__).resolve().parents[4] / "registries" / "assumptions.yml"


def load_assumptions(path: Path | str | None = None) -> AssumptionRegistry:
    """Parse and validate registries/assumptions.yml.

    Returns an AssumptionRegistry with validated Assumption entries.
    Raises FileNotFoundError if the file doesn't exist, or
    pydantic.ValidationError on schema violations.
    """
    p = Path(path) if path is not None else _DEFAULT_PATH
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if raw is None:
        raw = {"assumptions": []}
    return AssumptionRegistry.model_validate(raw)
