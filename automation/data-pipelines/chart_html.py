"""Shared utility for writing accessible chart HTML pages.

Wraps Plotly chart output in a proper HTML document with lang, viewport,
title, aria-label, skip link, and noscript fallback.
"""

from __future__ import annotations

import html
import logging
import os
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

    # Optional Plausible analytics — enabled when PLAUSIBLE_DOMAIN is set.
    plausible_domain = os.environ.get("PLAUSIBLE_DOMAIN", "").strip()
    plausible_tag = ""
    if plausible_domain:
        safe_domain = html.escape(plausible_domain, quote=True)
        plausible_tag = (
            f'  <script defer data-domain="{safe_domain}" '
            f'src="https://plausible.io/js/script.js"></script>\n'
        )

    safe_title = html.escape(title, quote=True)
    safe_desc = html.escape(description, quote=True)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} — WealthLens UK</title>
  <meta name="description" content="{safe_desc}">
{plausible_tag}  <style>
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
    <div id="chart" role="img" aria-label="{safe_desc}">
      {chart_div}
    </div>
  </div>
  <noscript><p>This chart requires JavaScript to display.</p></noscript>
</body>
</html>"""

    out_path.write_text(page, encoding="utf-8")
    logger.info("Chart saved to %s", out_path)
