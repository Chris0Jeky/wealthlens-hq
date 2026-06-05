"""Shared spreadsheet-cell parsing helpers for the data pipelines.

Several pipelines read numeric values out of ONS/HMRC spreadsheets, where a
"number" cell may actually be comma-grouped text ("14,200"), a genuinely
non-numeric label ("Source: ONS"), or a blank cell that pandas reads as NaN.
This module holds the single canonical parser so all pipelines reject the same
bad inputs identically (it was previously copied byte-for-byte into four files).
"""

from __future__ import annotations

import math


def to_finite_float(value: object) -> float | None:
    """Parse a spreadsheet cell to a *finite* float, or ``None`` if not numeric.

    Coerces via ``str()`` so comma-grouped text ("14,200") parses and the
    dynamically-typed pandas cell satisfies ``float()``. Returns ``None`` for a
    genuinely non-numeric cell (``float()`` raises) **and** for a blank cell that
    pandas reads as ``NaN``: ``str(nan)`` is ``"nan"``, which ``float()`` happily
    turns back into a NaN that would otherwise slip past a downstream ``<= 0`` guard
    and write a NaN into the published dataset. ``inf`` is rejected the same way.
    """
    # Fast path for the common case: a cell pandas already read as a float (incl.
    # numpy float64, a float subclass). This skips the str()/replace()/float()
    # round-trip and is behaviour-identical — a finite float round-trips through
    # ``float(str(x))`` to itself, and NaN/inf are rejected here exactly as below.
    # ``isinstance(value, float)`` deliberately excludes ``bool`` (an int subclass,
    # not float) and ``int``/numpy-int, so those keep their existing str()-path
    # handling (bool -> None, int -> value).
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        parsed = float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return None
    return parsed if math.isfinite(parsed) else None
