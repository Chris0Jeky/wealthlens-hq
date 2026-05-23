"""Load and validate the assumption registry from YAML.

Blueprint v5 §7.6: machine-readable registry of every modelling assumption.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from wealthlens_sim._registry_path import find_registries_dir
from wealthlens_sim.assumptions.schema import AssumptionRegistry


def load_assumptions(path: Path | str | None = None) -> AssumptionRegistry:
    """Parse and validate registries/assumptions.yml.

    Returns an AssumptionRegistry with validated Assumption entries.
    Raises FileNotFoundError if the file doesn't exist, ValueError if the
    file is empty, or pydantic.ValidationError on schema violations.
    """
    p = Path(path) if path is not None else find_registries_dir() / "assumptions.yml"
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if raw is None:
        msg = f"Assumptions file is empty or contains only comments: {p}"
        raise ValueError(msg)
    return AssumptionRegistry.model_validate(raw)
