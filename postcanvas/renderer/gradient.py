from __future__ import annotations
import math
from typing import List, Tuple
from PIL import Image
from .utils import parse_color
from ..models import GradientConfig

def _interp(stops, t: float) -> Tuple[int, int, int, int]:
    ss = sorted(stops, key=lambda s: s.position)
    if t <= ss[0].position:
        return parse_color(ss[0].color)
    if t >= ss[-1].position:
        return parse_color(ss[-1].color)
    for a, b in zip(ss, ss[1:]):
        if a.position <= t <= b.position:
            f = (t - a.position) / (b.position - a.position) if b.position != a.position else 0
            ca, cb = parse_color(a.color), parse_color(b.color)
            return tuple(int(ca[i] + f * (cb[i] - ca[i])) for i in range(4))
    return parse_color(ss[-1].color)

def create_gradient(w: int, h: int, cfg: GradientConfig) -> Image.Image:
    import numpy as np
    img = Image.new("RGBA", (w, h))
    px = img.load()

    if cfg.type == "linear":
        rad = math.radians(cfg.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        for y in range(h):
            for x in range(w):
                nx, ny = x / w - 0.5, y / h - 0.5
                t = max(0.0, min(1.0, nx * cos_a + ny * sin_a + 0.5))
                px[x, y] = _interp(cfg.stops, t)

    elif cfg.type == "radial":
        cx, cy = cfg.center_x * w, cfg.center_y * h
        maxr = cfg.radius * math.sqrt(w ** 2 + h ** 2)
        for y in range(h):
            for x in range(w):
                t = min(math.hypot(x - cx, y - cy) / maxr, 1.0)
                px[x, y] = _interp(cfg.stops, t)

    return img
