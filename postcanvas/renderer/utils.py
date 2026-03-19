from __future__ import annotations
import math
from typing import Tuple
from PIL import Image, ImageDraw, ImageColor

Dimension = int | float | str

def resolve(value: Dimension, canvas_size: int) -> int:
    """'50%' → 540, 200 → 200."""
    if isinstance(value, str):
        if value.endswith("%"):
            return int(float(value[:-1]) / 100 * canvas_size)
        return int(float(value))
    return int(value)

def parse_color(color: str) -> Tuple[int, int, int, int]:
    """Parse any CSS-like colour string to an RGBA tuple."""
    c = color.strip()
    if c.startswith("rgba"):
        parts = c[5:-1].split(",")
        return (int(parts[0]), int(parts[1]), int(parts[2]),
                int(float(parts[3]) * 255))
    if c.startswith("rgb"):
        parts = c[4:-1].split(",")
        return (int(parts[0]), int(parts[1]), int(parts[2]), 255)
    try:
        rgb = ImageColor.getrgb(c)
        return rgb if len(rgb) == 4 else rgb + (255,)
    except Exception:
        return (0, 0, 0, 255)

def get_anchor_offset(anchor: str, w: int, h: int) -> Tuple[int, int]:
    """Return (dx, dy) so that pasting at (x+dx, y+dy) honours the anchor."""
    return {
        "topleft":      (0,       0),
        "topcenter":    (-w // 2, 0),
        "topright":     (-w,      0),
        "left":         (0,       -h // 2),
        "center":       (-w // 2, -h // 2),
        "right":        (-w,      -h // 2),
        "bottomleft":   (0,       -h),
        "bottomcenter": (-w // 2, -h),
        "bottomright":  (-w,      -h),
    }.get(anchor, (-w // 2, -h // 2))

def apply_rounded_corners(img: Image.Image, radius: float) -> Image.Image:
    if radius <= 0:
        return img
    r = int(radius * min(img.width, img.height)) if radius <= 1.0 else int(radius)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.width, img.height], radius=r, fill=255
    )
    out = img.copy().convert("RGBA")
    out.putalpha(mask)
    return out

def composite(base: Image.Image, layer: Image.Image, x: int, y: int) -> Image.Image:
    """Paste a layer (RGBA) onto base at (x, y)."""
    tmp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    tmp.paste(layer, (x, y), layer)
    return Image.alpha_composite(base, tmp)
