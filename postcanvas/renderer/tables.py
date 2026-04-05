from __future__ import annotations
import os
from typing import Any, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from .utils import parse_color, resolve, get_anchor_offset
from ..models import TableElementConfig, TextAlign

_FONT_DIRS = [
    "/usr/share/fonts", "/usr/local/share/fonts",
    "/System/Library/Fonts", "/Library/Fonts",
    "C:/Windows/Fonts",
    os.path.expanduser("~/Library/Fonts"),
]
_FONT_MAP = {
    "arial": ["Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
    "helvetica": ["Helvetica.ttf", "helvetica.ttf", "LiberationSans-Regular.ttf"],
    "times": ["Times New Roman.ttf", "times.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "courier": ["Courier New.ttf", "cour.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"],
    "roboto": ["Roboto-Regular.ttf", "Roboto.ttf"],
    "open sans": ["OpenSans-Regular.ttf"],
    "inter": ["Inter-Regular.ttf", "Inter.ttf"],
}


def _find_font(name: Optional[str], size: int) -> Any:
    if not name:
        name = "Arial"
    candidates = _FONT_MAP.get(name.lower(), [name + ".ttf", name + "-Regular.ttf"])
    for font_dir in _FONT_DIRS:
        if not os.path.isdir(font_dir):
            continue
        for candidate in candidates:
            p = os.path.join(font_dir, candidate)
            if os.path.isfile(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
            for sub in os.listdir(font_dir):
                p2 = os.path.join(font_dir, sub, candidate)
                if os.path.isfile(p2):
                    try:
                        return ImageFont.truetype(p2, size)
                    except Exception:
                        pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _resolve_font(path: Optional[str], family: Optional[str], size: int) -> Any:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return _find_font(family, size)


def _truncate_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> str:
    if max_width <= 0:
        return ""
    probe = text
    if draw.textbbox((0, 0), probe, font=font)[2] <= max_width:
        return probe

    ellipsis = "..."
    low = 0
    high = len(text)
    best = ""
    while low <= high:
        mid = (low + high) // 2
        candidate = text[:mid].rstrip() + ellipsis
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width:
            best = candidate
            low = mid + 1
        else:
            high = mid - 1
    return best or ellipsis


def _draw_cell_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    rect: tuple[int, int, int, int],
    font: Any,
    fill: tuple[int, int, int, int],
    align: TextAlign,
    padding: int,
) -> None:
    x0, y0, x1, y1 = rect
    max_width = max(0, (x1 - x0) - (padding * 2))
    value = _truncate_text(draw, text, font, max_width)
    if not value:
        return

    bbox = draw.textbbox((0, 0), value, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    if align == TextAlign.LEFT:
        tx = x0 + padding
    elif align == TextAlign.RIGHT:
        tx = x1 - padding - tw
    else:
        tx = x0 + ((x1 - x0) - tw) // 2

    ty = y0 + ((y1 - y0) - th) // 2
    draw.text((tx, ty), value, font=font, fill=fill)


def _normalize_column_widths(column_widths: Optional[list[float]], col_count: int) -> list[float]:
    if col_count <= 0:
        return []
    if column_widths and len(column_widths) == col_count:
        cleaned = [max(0.0, float(v)) for v in column_widths]
        total = sum(cleaned)
        if total > 0:
            return [v / total for v in cleaned]
    return [1.0 / col_count] * col_count


def render_table(
    canvas: Image.Image,
    cfg: TableElementConfig,
    cw: int,
    ch: int,
    default_font_family: Optional[str] = None,
    default_font_path: Optional[str] = None,
) -> Image.Image:
    if not cfg.visible:
        return canvas

    w = max(2, resolve(cfg.width, cw))
    h = max(2, resolve(cfg.height, ch))

    headers = [str(v) for v in cfg.headers]
    rows = [[str(cell) for cell in row] for row in cfg.rows]
    col_count = max(len(headers), max((len(r) for r in rows), default=0))
    if col_count == 0:
        return canvas

    if len(headers) < col_count:
        headers = headers + [""] * (col_count - len(headers))

    for i, row in enumerate(rows):
        if len(row) < col_count:
            rows[i] = row + [""] * (col_count - len(row))

    col_widths = _normalize_column_widths(cfg.column_widths, col_count)

    has_header = bool(cfg.show_header and headers)
    header_h = (
        max(1, resolve(cfg.header_height, h)) if cfg.header_height is not None
        else max(1, int((cfg.header_font_size or max(cfg.font_size + 2, cfg.font_size)) * 1.8))
    )
    if not has_header:
        header_h = 0

    available_h = max(1, h - header_h)
    row_count = max(1, len(rows))
    row_h = (
        max(1, resolve(cfg.row_height, h)) if cfg.row_height is not None
        else max(1, available_h // row_count)
    )

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    border_radius = int(cfg.border_radius) if cfg.border_radius > 1 else int(cfg.border_radius * min(w, h))

    bg = parse_color(cfg.background_color)
    if border_radius > 0:
        draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=border_radius, fill=bg)
    else:
        draw.rectangle([0, 0, w - 1, h - 1], fill=bg)

    x_edges = [0]
    acc = 0.0
    for ratio in col_widths:
        acc += ratio
        x_edges.append(int(round(acc * w)))
    x_edges[-1] = w

    if has_header:
        header_bg = parse_color(cfg.header_background_color)
        draw.rectangle([0, 0, w, min(h, header_h)], fill=header_bg)

    row_colors = cfg.row_background_colors or []
    row_start_y = header_h
    for i, row in enumerate(rows):
        y0 = row_start_y + i * row_h
        if y0 >= h:
            break
        y1 = min(h, y0 + row_h)
        if row_colors:
            color = parse_color(row_colors[i % len(row_colors)])
            draw.rectangle([0, y0, w, y1], fill=color)

    base_font_path = cfg.font_path if cfg.font_path is not None else default_font_path
    base_font_family = cfg.font_family if cfg.font_family is not None else default_font_family
    cell_font = _resolve_font(base_font_path, base_font_family, cfg.font_size)
    header_font = _resolve_font(
        base_font_path,
        base_font_family,
        cfg.header_font_size or max(cfg.font_size + 2, cfg.font_size),
    )

    text_color = parse_color(cfg.text_color)
    header_text_color = parse_color(cfg.header_text_color)

    if has_header:
        for c in range(col_count):
            rect = (x_edges[c], 0, x_edges[c + 1], min(h, header_h))
            _draw_cell_text(
                draw,
                headers[c],
                rect,
                header_font,
                header_text_color,
                cfg.header_align,
                cfg.cell_padding,
            )

    for i, row in enumerate(rows):
        y0 = row_start_y + i * row_h
        if y0 >= h:
            break
        y1 = min(h, y0 + row_h)
        for c in range(col_count):
            rect = (x_edges[c], y0, x_edges[c + 1], y1)
            _draw_cell_text(
                draw,
                row[c],
                rect,
                cell_font,
                text_color,
                cfg.cell_align,
                cfg.cell_padding,
            )

    if cfg.grid_width > 0:
        grid = parse_color(cfg.grid_color)
        for x_edge in x_edges[1:-1]:
            draw.line([(x_edge, 0), (x_edge, h)], fill=grid, width=cfg.grid_width)

        if has_header:
            draw.line([(0, header_h), (w, header_h)], fill=grid, width=cfg.grid_width)

        if rows:
            for i in range(1, len(rows)):
                y_edge = row_start_y + i * row_h
                if y_edge >= h:
                    break
                draw.line([(0, y_edge), (w, y_edge)], fill=grid, width=cfg.grid_width)

    if cfg.border_width > 0:
        border = parse_color(cfg.border_color)
        if border_radius > 0:
            draw.rounded_rectangle(
                [0, 0, w - 1, h - 1],
                radius=border_radius,
                outline=border,
                width=cfg.border_width,
            )
        else:
            draw.rectangle([0, 0, w - 1, h - 1], outline=border, width=cfg.border_width)

    if cfg.opacity < 1.0:
        alpha = layer.split()[3].point(lambda p: int(p * cfg.opacity))
        layer.putalpha(alpha)

    if cfg.rotation:
        layer = layer.rotate(-cfg.rotation, expand=True, resample=Image.Resampling.BICUBIC)

    x = resolve(cfg.x, cw)
    y = resolve(cfg.y, ch)
    dx, dy = get_anchor_offset(cfg.anchor, layer.width, layer.height)
    x += dx
    y += dy

    if cfg.shadow:
        sh_color = parse_color(cfg.shadow.color)
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_layer = Image.new("RGBA", layer.size, sh_color)
        shadow_layer.putalpha(layer.split()[3])
        sx = x + int(cfg.shadow.offset_x)
        sy = y + int(cfg.shadow.offset_y)
        shadow.paste(shadow_layer, (sx, sy), shadow_layer)
        if cfg.shadow.blur_radius > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(cfg.shadow.blur_radius))
        canvas = Image.alpha_composite(canvas, shadow)

    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(layer, (x, y), layer)
    return Image.alpha_composite(canvas, tmp)
