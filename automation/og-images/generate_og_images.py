"""Generate Open Graph images for WealthLens UK social sharing.

Creates 1200x630 PNG images matching the broadsheet newspaper aesthetic:
- Newsprint cream (#F4EFE6) background
- Ink black (#111111) text
- Pillar-box red (#C8161D) accents
- No blue anywhere

Output: projects/wealthlens-dashboard/frontend/public/og/
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "projects" / "wealthlens-dashboard" / "frontend" / "public" / "og"

CREAM = (244, 239, 230)
INK = (17, 17, 17)
RED = (200, 22, 29)
MUTED = (90, 85, 80)
RULE = (216, 209, 193)
CREAM_TINT = (236, 230, 218)


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try system fonts, fall back to PIL default."""
    candidates = [
        "C:/Windows/Fonts/georgia.ttf" if not bold else "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/times.ttf" if not bold else "C:/Windows/Fonts/timesbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _get_sans_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _get_mono_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _draw_rule(draw: ImageDraw.ImageDraw, y: int, width: int, thick: bool = False) -> None:
    h = 4 if thick else 1
    color = INK if thick else RULE
    draw.rectangle([(60, y), (width - 60, y + h)], fill=color)


def _draw_red_rule(draw: ImageDraw.ImageDraw, y: int, width: int) -> None:
    draw.rectangle([(60, y), (width - 60, y + 4)], fill=RED)


def generate_landing_og() -> Path:
    """Generate the main landing page OG image."""
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)

    font_title = _get_font(72, bold=True)
    font_subtitle = _get_font(28)
    font_eyebrow = _get_mono_font(14)
    font_stat = _get_font(48, bold=True)
    font_stat_label = _get_sans_font(16)

    _draw_red_rule(draw, 40, w)

    draw.text((60, 56), "WEALTHLENS", fill=INK, font=font_eyebrow)

    draw.text((60, 90), "UK Wealth", fill=INK, font=font_title)
    draw.text((60, 170), "Inequality", fill=INK, font=font_title)

    uk_text = "UK"
    uk_bbox = draw.textbbox((0, 0), "UK Wealth", font=font_title)
    draw.text((60, 90), "UK Wealth", fill=INK, font=font_title)

    _draw_rule(draw, 265, w, thick=True)

    draw.text(
        (60, 285),
        "Open-source, source-backed data on wealth\ninequality in the United Kingdom.",
        fill=MUTED,
        font=font_subtitle,
    )

    _draw_rule(draw, 380, w)

    stats = [
        ("57%", "of wealth held\nby top 10%"),
        ("£85bn", "in rent paid\nper year"),
        ("3.6×", "house price to\nearnings gap"),
        ("93%", "of tax from\nwork, not wealth"),
    ]

    stat_x = 60
    stat_w = (w - 120) // 4
    for i, (value, label) in enumerate(stats):
        x = stat_x + i * stat_w
        draw.text((x, 400), value, fill=RED, font=font_stat)
        draw.text((x, 460), label, fill=MUTED, font=font_stat_label)

        if i < 3:
            draw.line([(x + stat_w - 10, 400), (x + stat_w - 10, 500)], fill=RULE, width=1)

    _draw_rule(draw, 530, w)

    draw.text((60, 550), "wealthlens.uk", fill=MUTED, font=font_eyebrow)
    draw.text((60, 575), "Data from ONS · WID · HMRC · Land Registry", fill=MUTED, font=font_eyebrow)

    dot_y = 560
    draw.ellipse([(w - 100, dot_y), (w - 90, dot_y + 10)], fill=RED)

    out = OUT_DIR / "og-landing.png"
    img.save(out, "PNG", quality=95)
    logger.info("Generated %s (%dx%d)", out, w, h)
    return out


def generate_chart_og(
    title: str,
    stat_value: str,
    stat_label: str,
    filename: str,
) -> Path:
    """Generate an OG image for a specific chart page."""
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)

    font_title = _get_font(52, bold=True)
    font_stat = _get_font(96, bold=True)
    font_label = _get_sans_font(22)
    font_eyebrow = _get_mono_font(14)
    font_source = _get_sans_font(16)

    _draw_red_rule(draw, 40, w)

    draw.text((60, 56), "WEALTHLENS UK", fill=INK, font=font_eyebrow)

    _draw_rule(draw, 85, w, thick=True)

    lines = []
    words = title.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_title)
        if bbox[2] - bbox[0] > w - 140:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)

    y = 105
    for line_text in lines[:3]:
        draw.text((60, y), line_text, fill=INK, font=font_title)
        y += 60

    _draw_rule(draw, y + 15, w)

    stat_y = y + 40
    draw.text((60, stat_y), stat_value, fill=RED, font=font_stat)
    draw.text((60, stat_y + 110), stat_label, fill=MUTED, font=font_label)

    draw.rectangle([(60, h - 80), (w - 60, h - 76)], fill=RULE)
    draw.text((60, h - 65), "wealthlens.uk", fill=MUTED, font=font_eyebrow)
    draw.ellipse([(w - 100, h - 65), (w - 90, h - 55)], fill=RED)

    out = OUT_DIR / filename
    img.save(out, "PNG", quality=95)
    logger.info("Generated %s (%dx%d)", out, w, h)
    return out


def generate_favicon() -> Path:
    """Generate a simple 32x32 favicon with WL monogram."""
    size = 32
    img = Image.new("RGB", (size, size), RED)
    draw = ImageDraw.Draw(img)

    font = _get_sans_font(18, bold=True)
    bbox = draw.textbbox((0, 0), "W", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "W", fill=(255, 255, 255), font=font)

    out = OUT_DIR.parent / "favicon.png"
    img.save(out, "PNG")
    logger.info("Generated %s", out)
    return out


def generate_apple_touch_icon() -> Path:
    """Generate a 180x180 Apple touch icon."""
    size = 180
    img = Image.new("RGB", (size, size), RED)
    draw = ImageDraw.Draw(img)

    font = _get_sans_font(80, bold=True)
    bbox = draw.textbbox((0, 0), "WL", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "WL", fill=(255, 255, 255), font=font)

    out = OUT_DIR.parent / "apple-touch-icon.png"
    img.save(out, "PNG")
    logger.info("Generated %s", out)
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    generate_landing_og()

    charts = [
        {
            "title": "Top 1% Wealth Share Since 1820",
            "stat_value": "21%",
            "stat_label": "Top 1% share of net personal wealth (2023)",
            "filename": "og-wealth-shares.png",
        },
        {
            "title": "Housing Affordability by Region",
            "stat_value": "3.6×",
            "stat_label": "House price to earnings ratio, England avg",
            "filename": "og-housing-affordability.png",
        },
        {
            "title": "Wealth Distribution by Decile",
            "stat_value": "57%",
            "stat_label": "Net wealth held by the top 10% of households",
            "filename": "og-wealth-by-decile.png",
        },
        {
            "title": "Capital Gains Concentration",
            "stat_value": "77%",
            "stat_label": "Capital gains from top 1% of realisations",
            "filename": "og-cgt-concentration.png",
        },
        {
            "title": "UK Productivity vs Pay Gap",
            "stat_value": "2×",
            "stat_label": "Productivity growth vs real pay since 1970",
            "filename": "og-productivity-pay.png",
        },
    ]

    for chart in charts:
        generate_chart_og(**chart)

    generate_favicon()
    generate_apple_touch_icon()

    logger.info("All OG images generated in %s", OUT_DIR)


if __name__ == "__main__":
    main()
