"""Hatch build hook: bundle the canonical repo-root registries into the dist.

The registry YAML files live at the monorepo root (``registries/``), outside
this package's project directory, because they are shared across the simulator,
dashboard, and data pipelines. To make a built wheel/sdist self-contained (so a
non-editable ``pip install`` can still load them), this hook force-includes them
as ``wealthlens_sim/_registries/`` whenever the source directory is present.

Crucially it **no-ops when ``registries/`` is absent** — e.g. when pip builds a
wheel from an unpacked sdist, where the path above the project root does not
exist. That prevents the hard ``Forced include not found`` build failure that a
static ``force-include`` entry would cause, while still letting the sdist itself
carry the files (the hook runs at sdist-build time too, from the checkout).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class RegistriesBuildHook(BuildHookInterface):
    """Force-include the repo-root registries when they are available."""

    PLUGIN_NAME = "wlsim-registries"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        registries = Path(self.root).parent.parent / "registries"
        if registries.is_dir():
            force_include = build_data.setdefault("force_include", {})
            force_include[str(registries)] = "wealthlens_sim/_registries"
