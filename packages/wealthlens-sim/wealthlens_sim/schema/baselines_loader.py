"""Load and validate the baselines registry from YAML.

Blueprint v5 §3.1: baseline status matrix snapshot.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from wealthlens_sim.schema.baselines import BaselinesRegistry

_DEFAULT_PATH = Path(__file__).resolve().parents[4] / "registries" / "baselines.yml"


def load_baselines(path: Path | str | None = None) -> BaselinesRegistry:
    """Parse and validate registries/baselines.yml.

    Returns a BaselinesRegistry with validated PolicyBaseline entries.
    Raises FileNotFoundError if the file doesn't exist, or
    pydantic.ValidationError on schema violations.
    """
    p = Path(path) if path is not None else _DEFAULT_PATH
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if raw is None:
        msg = f"Baselines file is empty or contains only comments: {p}"
        raise ValueError(msg)
    return BaselinesRegistry.model_validate(raw)
