from __future__ import annotations
from typing import Any, Optional
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from .utils import parse_color, resolve, get_anchor_offset
from .fonts import resolve_font
from ..models import TableElementConfig, TextAlign


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


def _build_cell_alignment_map(cfg: TableElementConfig) -> dict[tuple[str, int, int], TextAlign]:
    mapping: dict[tuple[str, int, int], TextAlign] = {}
    for override in cfg.cell_alignments:
        key = (override.section, override.row, override.col)
        mapping[key] = override.align
    return mapping


def _resolve_alignment(
    cfg: TableElementConfig,
    section: str,
    row: int,
    col: int,
    cell_alignment_map: dict[tuple[str, int, int], TextAlign],
) -> TextAlign:
    if cfg.text_align is not None:
        align = cfg.text_align
    else:
        align = cfg.header_align if section == "header" else cfg.cell_align

    if cfg.column_alignments is not None and col < len(cfg.column_alignments):
        align = cfg.column_alignments[col]

    return cell_alignment_map.get((section, row, col), align)


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

    clip_mask = Image.new("L", (w, h), 0)
    clip_draw = ImageDraw.Draw(clip_mask)
    if border_radius > 0:
        clip_draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=border_radius, fill=255)
    else:
        clip_draw.rectangle([0, 0, w - 1, h - 1], fill=255)

    fills = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fill_draw = ImageDraw.Draw(fills)

    bg = parse_color(cfg.background_color)
    fill_draw.rectangle([0, 0, w - 1, h - 1], fill=bg)

    x_edges = [0]
    acc = 0.0
    for ratio in col_widths:
        acc += ratio
        x_edges.append(int(round(acc * w)))
    x_edges[-1] = w

    if has_header:
        header_bg = parse_color(cfg.header_background_color)
        fill_draw.rectangle([0, 0, w - 1, min(h - 1, header_h)], fill=header_bg)

    row_colors = cfg.row_background_colors or []
    row_start_y = header_h
    for i, row in enumerate(rows):
        y0 = row_start_y + i * row_h
        if y0 >= h:
            break
        y1 = min(h, y0 + row_h)
        if row_colors:
            color = parse_color(row_colors[i % len(row_colors)])
            fill_draw.rectangle([0, y0, w - 1, max(y0, y1 - 1)], fill=color)

    fills_alpha = ImageChops.multiply(fills.split()[3], clip_mask)
    fills.putalpha(fills_alpha)
    layer = Image.alpha_composite(layer, fills)
    draw = ImageDraw.Draw(layer)

    base_font_path = cfg.font_path if cfg.font_path is not None else default_font_path
    base_font_family = cfg.font_family if cfg.font_family is not None else default_font_family
    cell_font = resolve_font(base_font_path, base_font_family, cfg.font_size)
    header_font = resolve_font(
        base_font_path,
        base_font_family,
        cfg.header_font_size or max(cfg.font_size + 2, cfg.font_size),
    )

    text_color = parse_color(cfg.text_color)
    header_text_color = parse_color(cfg.header_text_color)
    cell_alignment_map = _build_cell_alignment_map(cfg)

    if has_header:
        for c in range(col_count):
            rect = (x_edges[c], 0, x_edges[c + 1], min(h, header_h))
            _draw_cell_text(
                draw,
                headers[c],
                rect,
                header_font,
                header_text_color,
                _resolve_alignment(cfg, "header", 0, c, cell_alignment_map),
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
                _resolve_alignment(cfg, "body", i, c, cell_alignment_map),
                cfg.cell_padding,
            )

    if cfg.grid_width > 0:
        grid_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        grid_draw = ImageDraw.Draw(grid_layer)
        grid = parse_color(cfg.grid_color)
        for x_edge in x_edges[1:-1]:
            grid_draw.line([(x_edge, 0), (x_edge, h)], fill=grid, width=cfg.grid_width)

        if has_header:
            grid_draw.line([(0, header_h), (w, header_h)], fill=grid, width=cfg.grid_width)

        if rows:
            for i in range(1, len(rows)):
                y_edge = row_start_y + i * row_h
                if y_edge >= h:
                    break
                grid_draw.line([(0, y_edge), (w, y_edge)], fill=grid, width=cfg.grid_width)

        grid_alpha = ImageChops.multiply(grid_layer.split()[3], clip_mask)
        grid_layer.putalpha(grid_alpha)
        layer = Image.alpha_composite(layer, grid_layer)
        draw = ImageDraw.Draw(layer)

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
