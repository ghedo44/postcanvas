from __future__ import annotations
from typing import Any, Optional
from PIL import Image, ImageDraw, ImageFilter
from .utils import parse_color, resolve, get_anchor_offset
from .fonts import resolve_font
from ..models import ChartElementConfig, ChartType


def _truncate_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> str:
    if max_width <= 0:
        return ""
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text

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


def _format_value(v: float) -> str:
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if abs(v) >= 100:
        return f"{v:.0f}"
    if abs(v) >= 10:
        return f"{v:.1f}".rstrip("0").rstrip(".")
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _compute_value_range(cfg: ChartElementConfig, values: list[float]) -> tuple[float, float]:
    if not values:
        return (0.0, 1.0)

    min_value = cfg.min_value if cfg.min_value is not None else min(values)
    max_value = cfg.max_value if cfg.max_value is not None else max(values)

    if cfg.type == ChartType.BAR:
        min_value = min(min_value, 0.0)
        max_value = max(max_value, 0.0)

    if min_value == max_value:
        delta = abs(min_value) * 0.1 or 1.0
        min_value -= delta
        max_value += delta

    return (float(min_value), float(max_value))


def _value_to_y(value: float, min_value: float, max_value: float, top: int, bottom: int) -> int:
    ratio = (value - min_value) / (max_value - min_value)
    return int(round(bottom - (ratio * (bottom - top))))


def render_chart(
    canvas: Image.Image,
    cfg: ChartElementConfig,
    cw: int,
    ch: int,
    default_font_family: Optional[str] = None,
    default_font_path: Optional[str] = None,
) -> Image.Image:
    if not cfg.visible:
        return canvas

    if not cfg.series:
        return canvas

    width = max(4, resolve(cfg.width, cw))
    height = max(4, resolve(cfg.height, ch))

    point_count = max(
        len(cfg.labels),
        max((len(series.values) for series in cfg.series), default=0),
    )
    if point_count == 0:
        return canvas

    labels = list(cfg.labels)
    if len(labels) < point_count:
        labels.extend([str(i + 1) for i in range(len(labels), point_count)])

    normalized_values: list[list[float]] = []
    flat_values: list[float] = []
    for series in cfg.series:
        vals = [float(v) for v in series.values]
        if len(vals) < point_count:
            vals.extend([0.0] * (point_count - len(vals)))
        else:
            vals = vals[:point_count]
        normalized_values.append(vals)
        flat_values.extend(vals)

    min_value, max_value = _compute_value_range(cfg, flat_values)

    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    border_radius = int(cfg.border_radius) if cfg.border_radius > 1 else int(cfg.border_radius * min(width, height))
    bg = parse_color(cfg.background_color)
    if border_radius > 0:
        draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=border_radius, fill=bg)
    else:
        draw.rectangle([0, 0, width - 1, height - 1], fill=bg)

    left = max(24, min(width - 16, cfg.padding_left))
    right = max(16, min(width - 8, cfg.padding_right))
    top = max(20, min(height - 16, cfg.padding_top + (18 if cfg.title else 0)))
    bottom = max(28, min(height - 8, cfg.padding_bottom))

    plot_x0 = left
    plot_y0 = top
    plot_x1 = max(plot_x0 + 8, width - right)
    plot_y1 = max(plot_y0 + 8, height - bottom)
    if plot_x1 <= plot_x0 or plot_y1 <= plot_y0:
        return canvas

    if cfg.chart_background_color:
        chart_bg = parse_color(cfg.chart_background_color)
        draw.rounded_rectangle([plot_x0, plot_y0, plot_x1, plot_y1], radius=8, fill=chart_bg)

    base_font_path = cfg.font_path if cfg.font_path is not None else default_font_path
    base_font_family = cfg.font_family if cfg.font_family is not None else default_font_family
    label_font = resolve_font(base_font_path, base_font_family, cfg.font_size)
    title_font = resolve_font(base_font_path, base_font_family, cfg.title_font_size)
    legend_font = resolve_font(base_font_path, base_font_family, max(12, cfg.font_size - 1))

    label_color = parse_color(cfg.label_color)
    title_color = parse_color(cfg.title_color)
    axis_color = parse_color(cfg.axis_color)

    if cfg.title:
        title = _truncate_text(draw, cfg.title, title_font, width - 32)
        tb = draw.textbbox((0, 0), title, font=title_font)
        tw = tb[2] - tb[0]
        draw.text(((width - tw) // 2, 10), title, font=title_font, fill=title_color)

    if cfg.show_grid:
        grid_color = parse_color(cfg.grid_color)
        for i in range(cfg.grid_steps + 1):
            t = i / cfg.grid_steps
            value = min_value + ((max_value - min_value) * t)
            y = _value_to_y(value, min_value, max_value, plot_y0, plot_y1)
            draw.line([(plot_x0, y), (plot_x1, y)], fill=grid_color, width=1)

            label = _format_value(value)
            lb = draw.textbbox((0, 0), label, font=label_font)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
            lx = max(4, plot_x0 - lw - 10)
            ly = y - (lh // 2)
            draw.text((lx, ly), label, font=label_font, fill=label_color)

    zero_y = _value_to_y(0.0, min_value, max_value, plot_y0, plot_y1) if min_value <= 0.0 <= max_value else plot_y1
    draw.line([(plot_x0, plot_y0), (plot_x0, plot_y1)], fill=axis_color, width=2)
    draw.line([(plot_x0, zero_y), (plot_x1, zero_y)], fill=axis_color, width=2)

    plot_width = max(1, plot_x1 - plot_x0)
    step = plot_width / point_count
    x_positions = [plot_x0 + ((i + 0.5) * step) for i in range(point_count)]

    palette = cfg.palette or ["#0ea5e9"]

    if cfg.type == ChartType.BAR:
        series_count = len(cfg.series)
        group_width = step * (1.0 - cfg.bar_group_padding)
        bar_width = group_width / max(1, series_count)

        for i in range(point_count):
            group_left = x_positions[i] - (group_width / 2)
            for s_idx, series in enumerate(cfg.series):
                val = normalized_values[s_idx][i]
                y = _value_to_y(val, min_value, max_value, plot_y0, plot_y1)
                y0 = min(zero_y, y)
                y1 = max(zero_y, y)
                x0 = int(round(group_left + (s_idx * bar_width) + 1))
                x1 = int(round(group_left + ((s_idx + 1) * bar_width) - 1))
                if x1 <= x0 or y1 <= y0:
                    continue

                color = parse_color(series.color or palette[s_idx % len(palette)])
                radius = max(0, min(cfg.bar_radius, (x1 - x0) // 2, (y1 - y0) // 2))
                if radius > 0:
                    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=color)
                else:
                    draw.rectangle([x0, y0, x1, y1], fill=color)

    elif cfg.type == ChartType.LINE:
        for s_idx, series in enumerate(cfg.series):
            pts = [
                (
                    int(round(x_positions[i])),
                    _value_to_y(normalized_values[s_idx][i], min_value, max_value, plot_y0, plot_y1),
                )
                for i in range(point_count)
            ]
            if len(pts) < 2:
                continue

            color = parse_color(series.color or palette[s_idx % len(palette)])
            width_px = max(1, series.line_width if series.line_width > 0 else cfg.line_width)
            draw.line(pts, fill=color, width=width_px)

            if cfg.show_points:
                point_radius = max(1, series.point_radius if series.point_radius > 0 else cfg.point_radius)
                for px, py in pts:
                    draw.ellipse(
                        [px - point_radius, py - point_radius, px + point_radius, py + point_radius],
                        fill=color,
                        outline=parse_color("#ffffff"),
                        width=1,
                    )

    label_y = plot_y1 + 8
    for i, raw_label in enumerate(labels):
        max_label_width = int(max(8, step * 0.92))
        label = _truncate_text(draw, str(raw_label), label_font, max_label_width)
        lb = draw.textbbox((0, 0), label, font=label_font)
        lw = lb[2] - lb[0]
        draw.text((int(round(x_positions[i] - (lw / 2))), label_y), label, font=label_font, fill=label_color)

    if cfg.show_legend and cfg.series:
        legend_y = max(8, plot_y0 - max(18, cfg.font_size + 4))
        cursor_x = plot_x0
        row_h = max(18, cfg.font_size + 4)

        for s_idx, series in enumerate(cfg.series):
            legend_name = series.name or f"Series {s_idx + 1}"
            legend_color = parse_color(series.color or palette[s_idx % len(palette)])
            name_box = draw.textbbox((0, 0), legend_name, font=legend_font)
            name_w = name_box[2] - name_box[0]
            required = 20 + name_w + 18

            if cursor_x + required > width - 12:
                cursor_x = plot_x0
                legend_y += row_h

            draw.rectangle([cursor_x, legend_y + 5, cursor_x + 12, legend_y + 17], fill=legend_color)
            draw.text((cursor_x + 18, legend_y + 3), legend_name, font=legend_font, fill=label_color)
            cursor_x += required

    if cfg.border_width > 0:
        border = parse_color(cfg.border_color)
        if border_radius > 0:
            draw.rounded_rectangle(
                [0, 0, width - 1, height - 1],
                radius=border_radius,
                outline=border,
                width=cfg.border_width,
            )
        else:
            draw.rectangle([0, 0, width - 1, height - 1], outline=border, width=cfg.border_width)

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
        shadow_color = parse_color(cfg.shadow.color)
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_layer = Image.new("RGBA", layer.size, shadow_color)
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
