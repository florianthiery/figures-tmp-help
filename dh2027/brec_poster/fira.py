"""Fira Sans for the figures: font files, text width and the SVG font attributes (shared by the three drawing scripts).

The font is named in the SVG, not embedded. Widths are measured with Pillow's BASIC layout engine (raqm is not on every machine,
and a width that differs between Windows and Linux would show up as a diff in every figure).
"""
from pathlib import Path

from PIL import ImageFont

FONTS = Path(__file__).resolve().parent / "fonts"
REGULAR, MEDIUM = FONTS / "FiraSans-Regular.ttf", FONTS / "FiraSans-Medium.ttf"
FAMILY = "Fira Sans"
_cache = {}


def tw(text, size, med=False):
    """Width of text in px at font size `size`; med=True for Fira Sans Medium (the bold of the figures)."""
    key = med
    if key not in _cache:
        _cache[key] = ImageFont.truetype(str(MEDIUM if med else REGULAR), 100, layout_engine=ImageFont.Layout.BASIC)
    return round(_cache[key].getlength(text) * size / 100, 1)


def chip_w(text, size=12):
    """Width of an amber chip: measured text plus 9 px padding each side."""
    return round(tw(text, size) + 18)
