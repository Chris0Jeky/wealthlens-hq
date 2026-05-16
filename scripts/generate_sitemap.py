#!/usr/bin/env python3
"""Generate sitemap.xml and robots.txt for the WealthLens UK dashboard.

Reads route definitions (static pages, chart names, dataset slugs) and produces
a valid sitemap.xml plus a robots.txt in the frontend public directory.

Configuration:
    SITE_URL env var overrides the default base URL.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get(
    "SITE_URL", "https://chris0jeky.github.io/wealthlens-hq"
).rstrip("/")

# Output directory: frontend/public relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PUBLIC_DIR = REPO_ROOT / "projects" / "wealthlens-dashboard" / "frontend" / "public"

# ---------------------------------------------------------------------------
# Route definitions
# ---------------------------------------------------------------------------

STATIC_ROUTES: list[dict[str, str | float]] = [
    {"path": "/", "changefreq": "weekly", "priority": 1.0},
    {"path": "/about", "changefreq": "monthly", "priority": 0.6},
    {"path": "/methodology", "changefreq": "monthly", "priority": 0.6},
    {"path": "/contribute", "changefreq": "monthly", "priority": 0.6},
    {"path": "/tools/wealth-calculator", "changefreq": "monthly", "priority": 0.6},
]

CHART_NAMES: list[str] = [
    "wealth-shares",
    "housing-affordability",
    "wealth-by-decile",
    "cgt-concentration",
]

DATASET_SLUGS: list[str] = [
    "wealth-shares",
    "housing-affordability",
    "wealth-by-decile",
    "cgt-concentration",
    "productivity-pay",
    "gdhi-by-region",
    "tax-composition",
    "boe-rates",
    "child-poverty",
    "generational-wealth",
]

# ---------------------------------------------------------------------------
# Sitemap generation
# ---------------------------------------------------------------------------


def build_sitemap() -> ElementTree:
    """Build an ElementTree representing sitemap.xml."""
    today = date.today().isoformat()

    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    def add_url(path: str, changefreq: str, priority: float) -> None:
        url_el = SubElement(urlset, "url")
        loc = SubElement(url_el, "loc")
        loc.text = f"{BASE_URL}{path}"
        lastmod = SubElement(url_el, "lastmod")
        lastmod.text = today
        cf = SubElement(url_el, "changefreq")
        cf.text = changefreq
        pri = SubElement(url_el, "priority")
        pri.text = f"{priority:.1f}"

    # Static routes
    for route in STATIC_ROUTES:
        add_url(
            path=str(route["path"]),
            changefreq=str(route["changefreq"]),
            priority=float(route["priority"]),
        )

    # Chart routes
    for name in CHART_NAMES:
        add_url(path=f"/charts/{name}", changefreq="weekly", priority=0.8)

    # Dataset routes
    for slug in DATASET_SLUGS:
        add_url(path=f"/datasets/{slug}", changefreq="weekly", priority=0.7)

    indent(urlset, space="  ")
    return ElementTree(urlset)


def generate_robots_txt() -> str:
    """Generate robots.txt content."""
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # Write sitemap.xml
    sitemap_path = PUBLIC_DIR / "sitemap.xml"
    tree = build_sitemap()
    tree.write(
        sitemap_path,
        xml_declaration=True,
        encoding="UTF-8",
    )
    with open(sitemap_path, "a", encoding="utf-8") as f:
        f.write("\n")
    print(f"Generated: {sitemap_path}")

    # Write robots.txt
    robots_path = PUBLIC_DIR / "robots.txt"
    robots_path.write_text(generate_robots_txt(), encoding="utf-8")
    print(f"Generated: {robots_path}")


if __name__ == "__main__":
    main()
