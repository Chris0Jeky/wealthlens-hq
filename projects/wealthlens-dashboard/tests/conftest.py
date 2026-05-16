"""Pytest configuration — add backend directory to import path."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports like ``from app.main import app`` when running pytest from
# the wealthlens-dashboard project root.
_backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
