"""Locate the registries/ directory without hardcoding repo depth.

Both the assumptions loader and the baselines loader need to find
``registries/`` relative to the package source tree.  The old approach
used ``Path(__file__).resolve().parents[4]``, which breaks when the
package is installed via pip into site-packages.

This module walks up from its own location until it finds a directory
named ``registries/``, with a reasonable depth limit.  If the directory
is not found (e.g. a pure pip install with no local checkout), a clear
``FileNotFoundError`` tells the caller to pass an explicit path.
"""

from __future__ import annotations

from pathlib import Path


def find_registries_dir() -> Path:
    """Walk up from this file to find the ``registries/`` directory."""
    current = Path(__file__).resolve().parent
    for _ in range(10):  # reasonable depth limit
        candidate = current / "registries"
        if candidate.is_dir():
            return candidate
        if current.parent == current:
            break
        current = current.parent
    msg = (
        "Could not locate registries/ directory. "
        "Pass an explicit path to load_assumptions() / load_baselines()."
    )
    raise FileNotFoundError(msg)
