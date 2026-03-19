from __future__ import annotations
import math
from typing import Optional
from PIL import Image, ImageDraw
from .utils import parse_color, resolve, get_anchor_offset
from .gradient import create_gradient
from .text import render_text
from ..models import ShapeConfig, ShapeType, PaddingConfig, TextConfig

def render_shape(
    canvas: Image.Image,
    s: ShapeConfig,
    cw: int,
    ch: int,
    default_font_family: Optional[str] = None,
    default_font_path: Optional[str] = None,
) -> Image.Image:
    if not s.visible:
        return canvas

    x = resolve(s.x, cw)
    y = resolve(s.y, ch)
    w = resolve(s.width, cw)
    h = resolve(s.height, ch)
    dx, dy = get_anchor_offset(s.anchor, w, h)
    x += dx
    y += dy

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)

    fill   = parse_color(s.fill_color)   if s.fill_color   else None
    stroke = parse_color(s.stroke_color) if s.stroke_color else None
    if fill and s.opacity < 1.0:
        fill = (fill[0], fill[1], fill[2], int(fill[3] * s.opacity))

    r = int(s.border_radius) if s.border_radius > 1 else int(s.border_radius * min(w, h))

    if s.type == ShapeType.RECTANGLE:
        draw.rectangle([x, y, x+w, y+h], fill=fill, outline=stroke, width=s.stroke_width)
    elif s.type == ShapeType.ROUNDED_RECTANGLE:
        draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=stroke, width=s.stroke_width)
    elif s.type in (ShapeType.CIRCLE, ShapeType.ELLIPSE):
        draw.ellipse([x, y, x+w, y+h], fill=fill, outline=stroke, width=s.stroke_width)
    elif s.type == ShapeType.LINE:
        draw.line([x, y, x+w, y+h], fill=fill or stroke, width=max(s.stroke_width, 1))
    elif s.type == ShapeType.TRIANGLE:
        draw.polygon([(x+w//2, y), (x, y+h), (x+w, y+h)], fill=fill, outline=stroke)
    elif s.type == ShapeType.POLYGON:
        if s.points:
            pts = [(x + int(px*w), y + int(py*h)) for px, py in s.points]
        else:
            cx2, cy2 = x+w//2, y+h//2
            rx, ry = w//2, h//2
            n = s.sides
            pts = [(cx2 + rx*math.cos(2*math.pi*i/n - math.pi/2),
                    cy2 + ry*math.sin(2*math.pi*i/n - math.pi/2)) for i in range(n)]
        draw.polygon(pts, fill=fill, outline=stroke)
    elif s.type == ShapeType.STAR:
        cx2, cy2 = x+w//2, y+h//2
        outer = min(w, h)//2
        inner = int(outer * s.star_inner_r)
        pts = []
        for i in range(s.star_points * 2):
            angle = math.pi * i / s.star_points - math.pi/2
            rr = outer if i % 2 == 0 else inner
            pts.append((cx2 + rr*math.cos(angle), cy2 + rr*math.sin(angle)))
        draw.polygon(pts, fill=fill, outline=stroke)

    # gradient fill overlay
    if s.fill_gradient and s.fill_gradient.stops:
        grad = create_gradient(w, h, s.fill_gradient)
        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        if s.type in (ShapeType.CIRCLE, ShapeType.ELLIPSE):
            md.ellipse([0, 0, w, h], fill=255)
        elif s.type == ShapeType.ROUNDED_RECTANGLE:
            md.rounded_rectangle([0, 0, w, h], radius=r, fill=255)
        else:
            md.rectangle([0, 0, w, h], fill=255)
        grad.putalpha(mask)
        gl = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        gl.paste(grad, (x, y), grad)
        layer = Image.alpha_composite(layer, gl)

    # Render child texts inside the shape using local coordinates.
    if s.texts:
        text_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        local_padding = PaddingConfig(left=0, right=0, top=0, bottom=0)
        for txt in sorted(s.texts, key=lambda t: t.z_index):
            updates = {}
            if txt.max_width is None:
                updates["max_width"] = "100%"
            if txt.font_family is None and txt.font_path is None:
                if default_font_family is not None:
                    updates["font_family"] = default_font_family
                if default_font_path is not None:
                    updates["font_path"] = default_font_path
            local_cfg: TextConfig = txt.model_copy(update=updates) if updates else txt
            text_layer = render_text(text_layer, local_cfg, w, h, local_padding)
        layer.paste(text_layer, (x, y), text_layer)

    if s.rotation:
        layer = layer.rotate(-s.rotation, center=(x+w//2, y+h//2), resample=Image.Resampling.BICUBIC)

    if s.shadow:
        from .utils import parse_color as pc
        sh_c = pc(s.shadow.color)
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        # shift layer as shadow
        sh.paste(layer, (int(s.shadow.offset_x), int(s.shadow.offset_y)), layer)
        r_vals = sh.split()
        sh = Image.merge("RGBA", (
            Image.new("L", canvas.size, sh_c[0]),
            Image.new("L", canvas.size, sh_c[1]),
            Image.new("L", canvas.size, sh_c[2]),
            r_vals[3],
        ))
        if s.shadow.blur_radius > 0:
            sh = sh.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(s.shadow.blur_radius))
        canvas = Image.alpha_composite(canvas, sh)

    return Image.alpha_composite(canvas, layer)
