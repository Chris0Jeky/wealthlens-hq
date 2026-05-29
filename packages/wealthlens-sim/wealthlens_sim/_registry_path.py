"""Locate the registries directory without hardcoding repo depth.

Both the assumptions loader and the baselines loader need to find the
``sources.yml`` / ``assumptions.yml`` / ``baselines.yml`` registry files.

Two resolution strategies, tried in order:

1. **In-repo / editable install** — walk up from this file until a directory
   named ``registries/`` is found (the canonical repo-root location). This is
   the source of truth during development.
2. **Installed wheel** — the build packages the canonical registries into the
   wheel as ``wealthlens_sim/_registries/`` (see the ``force-include`` entry in
   ``pyproject.toml``), so they ship alongside the code and resolve even when
   there is no repo checkout (a plain ``pip install`` of the built wheel).

If neither is found (e.g. a PyPI *sdist* install, which cannot carry files from
above the project root), a clear ``FileNotFoundError`` tells the caller to pass
an explicit path to ``load_assumptions()`` / ``load_baselines()``.
"""

from __future__ import annotations

from pathlib import Path

_MAX_WALK_UP = 10


def find_registries_dir(start: Path | None = None) -> Path:
    """Locate the directory containing the registry YAML files.

    Args:
        start: Directory to begin resolution from. Defaults to this module's
            directory. Exposed mainly so the resolution strategies can be tested.

    Returns:
        Path to the directory containing the registry YAML files.

    Raises:
        FileNotFoundError: if neither the canonical ``registries/`` (walking up)
            nor the packaged ``_registries/`` fallback can be located.
    """
    start_dir = start if start is not None else Path(__file__).resolve().parent

    # Strategy 1: walk up to the canonical repo-root registries/ directory.
    current = start_dir
    for _ in range(_MAX_WALK_UP):
        candidate = current / "registries"
        if candidate.is_dir():
            return candidate
        if current.parent == current:
            break
        current = current.parent

    # Strategy 2: registries packaged inside an installed wheel.
    packaged = start_dir / "_registries"
    if packaged.is_dir():
        return packaged

    msg = (
        "Could not locate the registries directory (neither a repo-root "
        "registries/ nor a packaged _registries/). Pass an explicit path to "
        "load_assumptions() / load_baselines()."
    )
    raise FileNotFoundError(msg)
