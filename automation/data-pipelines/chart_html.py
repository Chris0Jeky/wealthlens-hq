"""Shared utility for writing accessible chart HTML pages.

Wraps Plotly chart output in a proper HTML document with lang, viewport,
title, aria-label, skip link, and noscript fallback.
"""

from __future__ import annotations

import logging
from pathlib import Path

import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def write_accessible_chart(
    fig: go.Figure,
    out_path: Path,
    *,
    title: str,
    description: str,
) -> None:
    """Write a Plotly figure as a standalone accessible HTML page."""
    chart_div = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"responsive": True, "displayModeBar": True},
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — WealthLens UK</title>
  <meta name="description" content="{description}">
  <style>
    body {{ margin: 0; padding: 1rem; font-family: system-ui, -apple-system, sans-serif; background: #fff; }}
    .skip-link {{ position: absolute; top: -40px; left: 0; background: #1f77b4; color: #fff; padding: 8px 16px; z-index: 100; }}
    .skip-link:focus {{ top: 0; }}
    .chart-container {{ max-width: 1200px; margin: 0 auto; }}
    .back-link {{ display: inline-block; margin-bottom: 1rem; color: #1f77b4; text-decoration: none; font-size: 0.875rem; }}
    .back-link:hover {{ text-decoration: underline; }}
    a:focus-visible {{ outline: 3px solid #1f77b4; outline-offset: 2px; }}
  </style>
</head>
<body>
  <a class="skip-link" href="#chart">Skip to chart</a>
  <div class="chart-container">
    <a class="back-link" href="index.html">&larr; All charts</a>
    <div id="chart" role="img" aria-label="{description}">
      {chart_div}
    </div>
  </div>
  <noscript><p>This chart requires JavaScript to display.</p></noscript>
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")
    logger.info("Chart saved to %s", out_path)
