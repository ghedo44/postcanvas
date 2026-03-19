from __future__ import annotations
import os
from typing import Any, List, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from .utils import parse_color, resolve, get_anchor_offset
from ..models import TextConfig, PaddingConfig, TextAlign, TextTransform

_FONT_DIRS = [
    "/usr/share/fonts", "/usr/local/share/fonts",
    "/System/Library/Fonts", "/Library/Fonts",
    "C:/Windows/Fonts",
    os.path.expanduser("~/Library/Fonts"),
]
_FONT_MAP = {
    "arial":        ["Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
    "helvetica":    ["Helvetica.ttf", "helvetica.ttf", "LiberationSans-Regular.ttf"],
    "times":        ["Times New Roman.ttf", "times.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "courier":      ["Courier New.ttf", "cour.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"],
    "roboto":       ["Roboto-Regular.ttf", "Roboto.ttf"],
    "open sans":    ["OpenSans-Regular.ttf"],
    "inter":        ["Inter-Regular.ttf", "Inter.ttf"],
}

def _find_font(name: Optional[str], size: int) -> Any:
    if not name:
        name = "Arial"
    candidates = _FONT_MAP.get(name.lower(), [name + ".ttf", name + "-Regular.ttf"])
    for font_dir in _FONT_DIRS:
        if not os.path.isdir(font_dir):
            continue
        for c in candidates:
            p = os.path.join(font_dir, c)
            if os.path.isfile(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
            for sub in os.listdir(font_dir):
                p2 = os.path.join(font_dir, sub, c)
                if os.path.isfile(p2):
                    try:
                        return ImageFont.truetype(p2, size)
                    except Exception:
                        pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def _get_font(cfg: TextConfig) -> Any:
    if cfg.font_path:
        try:
            return ImageFont.truetype(cfg.font_path, cfg.font_size)
        except Exception:
            pass
    return _find_font(cfg.font_family, cfg.font_size)

def _adaptive_line_layer(
    cfg: TextConfig,
    canvas: Image.Image,
    font: Any,
    line: str,
    gx: int,
    gy: int,
) -> tuple[Image.Image, tuple[int, int]]:
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    raw_bx = probe.textbbox((0, 0), line, font=font)
    bx = (int(raw_bx[0]), int(raw_bx[1]), int(raw_bx[2]), int(raw_bx[3]))
    w = max(1, int(bx[2] - bx[0]))
    h = max(1, int(bx[3] - bx[1]))

    glyph = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glyph)
    gd.text((-bx[0], -bx[1]), line, font=font, fill=255)

    left = max(0, gx + bx[0])
    top = max(0, gy + bx[1])
    right = min(canvas.width, gx + bx[2])
    bottom = min(canvas.height, gy + bx[3])

    # Fallback if the text line is out of canvas bounds.
    if right <= left or bottom <= top:
        solid = Image.new("RGBA", (w, h), parse_color(cfg.color))
        solid.putalpha(glyph)
        return solid, (int(bx[0]), int(bx[1]))

    bg = canvas.crop((left, top, right, bottom)).convert("RGB")
    bg = bg.resize((w, h), resample=Image.Resampling.BOX)
    lum = bg.convert("L")

    # On dark pixels we use light text, on light pixels we use dark text.
    threshold = int(cfg.contrast_threshold)
    lut = [255 if i < threshold else 0 for i in range(256)]
    dark_bg_mask = lum.point(lut)
    light_img = Image.new("RGBA", (w, h), parse_color(cfg.contrast_light_color))
    dark_img = Image.new("RGBA", (w, h), parse_color(cfg.contrast_dark_color))
    mixed = Image.composite(light_img, dark_img, dark_bg_mask)
    mixed.putalpha(glyph)
    return mixed, (int(bx[0]), int(bx[1]))

def _wrap(text: str, font, max_w: int) -> List[str]:
    words, lines, cur = text.split(), [], []
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for word in words:
        test = " ".join(cur + [word])
        bx = probe.textbbox((0, 0), test, font=font)
        if bx[2] - bx[0] <= max_w:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    return lines or [text]

def render_text(
    canvas: Image.Image,
    cfg: TextConfig,
    cw: int,
    ch: int,
    padding: PaddingConfig,
) -> Image.Image:
    if not cfg.visible:
        return canvas

    content = cfg.content
    if cfg.transform == TextTransform.UPPERCASE:
        content = content.upper()
    elif cfg.transform == TextTransform.LOWERCASE:
        content = content.lower()
    elif cfg.transform == TextTransform.CAPITALIZE:
        content = content.title()

    font = _get_font(cfg)
    x = resolve(cfg.x, cw)
    y = resolve(cfg.y, ch)

    max_w = cw - padding.left - padding.right
    if cfg.max_width:
        max_w = min(max_w, resolve(cfg.max_width, cw))

    lines = _wrap(content, font, max_w)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    widths, heights = [], []
    for ln in lines:
        bx = probe.textbbox((0, 0), ln, font=font)
        widths.append(bx[2] - bx[0])
        heights.append(bx[3] - bx[1])

    mlw = max(widths) if widths else 0
    lh  = max(heights) if heights else cfg.font_size
    total_h = int(lh * cfg.line_spacing * len(lines))
    pad = 24

    layer = Image.new("RGBA", (mlw + pad * 2, total_h + pad * 2), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)

    # highlight / pill background
    if cfg.background_color:
        bg_c = parse_color(cfg.background_color)
        bp = cfg.background_padding
        draw.rounded_rectangle(
            [pad - bp, pad - bp, mlw + pad + bp, total_h + pad + bp],
            radius=cfg.background_radius, fill=bg_c
        )

    color = parse_color(cfg.color)
    color = (color[0], color[1], color[2], int(color[3] * cfg.opacity))
    cy = pad

    for i, line in enumerate(lines):
        lw = widths[i]
        if cfg.align == TextAlign.LEFT:
            lx = pad
        elif cfg.align == TextAlign.RIGHT:
            lx = mlw - lw + pad
        else:
            lx = (mlw - lw) // 2 + pad

        # shadow
        if cfg.shadow:
            sh_c = parse_color(cfg.shadow.color)
            sh_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh_layer).text(
                (lx + cfg.shadow.offset_x, cy + cfg.shadow.offset_y),
                line, font=font, fill=sh_c
            )
            if cfg.shadow.blur_radius > 0:
                sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(cfg.shadow.blur_radius))
            layer = Image.alpha_composite(layer, sh_layer)
            draw  = ImageDraw.Draw(layer)

        # stroke
        if cfg.stroke:
            sc = parse_color(cfg.stroke.color)
            sw = cfg.stroke.width
            for dx in range(-sw, sw + 1):
                for dy in range(-sw, sw + 1):
                    if dx or dy:
                        draw.text((lx + dx, cy + dy), line, font=font, fill=sc)

        if cfg.auto_contrast:
            adx, ady = get_anchor_offset(cfg.anchor, layer.width, layer.height)
            global_x = x + adx + lx
            global_y = y + ady + cy
            adaptive_line, (off_x, off_y) = _adaptive_line_layer(
                cfg=cfg,
                canvas=canvas,
                font=font,
                line=line,
                gx=global_x,
                gy=global_y,
            )
            layer.paste(adaptive_line, (lx + off_x, cy + off_y), adaptive_line)
        else:
            draw.text((lx, cy), line, font=font, fill=color)
        cy += int(lh * cfg.line_spacing)

    if cfg.rotation:
        layer = layer.rotate(-cfg.rotation, expand=True, resample=Image.Resampling.BICUBIC)

    dx, dy = get_anchor_offset(cfg.anchor, layer.width, layer.height)
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(layer, (x + dx, y + dy), layer)
    return Image.alpha_composite(canvas, tmp)
