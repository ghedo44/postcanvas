from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence

from PIL import Image, ImageDraw, ImageFilter

from ..models import PaddingConfig, TextAlign, TextConfig, TextTransform
from .filters import apply_filter
from .fonts import resolve_font
from .utils import get_anchor_offset, parse_color, resolve


@dataclass(frozen=True)
class TextLayout:
    lines: List[str]
    font: Any
    font_size: int
    width: int
    height: int
    line_height: int
    line_tops: List[int]
    max_width: int
    max_height: int
    overflowed: bool = False
    truncated: bool = False


def _get_font(cfg: TextConfig, size: int | None = None) -> Any:
    paths = [cfg.font_path, *cfg.font_fallback_paths]
    for path in paths:
        if not path:
            continue
        try:
            return resolve_font(path, cfg.font_family, size or cfg.font_size)
        except (OSError, ValueError):
            continue
    return resolve_font(None, cfg.font_family, size or cfg.font_size)


def _text_kwargs(cfg: TextConfig) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if cfg.direction:
        kwargs["direction"] = cfg.direction
    if cfg.language:
        kwargs["language"] = cfg.language
    if cfg.features:
        kwargs["features"] = cfg.features
    return kwargs


def _text_bbox(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: Any,
    cfg: TextConfig,
) -> tuple[int, int, int, int]:
    try:
        box = draw.textbbox((0, 0), text, font=font, **_text_kwargs(cfg))
    except (KeyError, TypeError, ValueError):
        box = draw.textbbox((0, 0), text, font=font)
    return tuple(int(value) for value in box)


def _text_length(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: Any,
    cfg: TextConfig,
) -> float:
    try:
        return float(draw.textlength(text, font=font, **_text_kwargs(cfg)))
    except (KeyError, TypeError, ValueError):
        return float(draw.textlength(text, font=font))


def _text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: Any,
    cfg: TextConfig,
) -> int:
    if not text:
        return 0
    if cfg.letter_spacing == 0:
        box = _text_bbox(draw, text, font, cfg)
        width = box[2] - box[0]
    else:
        width = int(sum(_text_length(draw, char, font, cfg) for char in text))
        width += cfg.letter_spacing * max(0, len(text) - 1)
    width += cfg.word_spacing * text.count(" ")
    return max(0, int(width))


def _split_long_token(
    token: str,
    draw: ImageDraw.ImageDraw,
    font: Any,
    max_width: int,
    cfg: TextConfig,
) -> List[str]:
    if not token:
        return [""]
    parts: List[str] = []
    current = ""
    for char in token:
        candidate = current + char
        if current and _text_width(draw, candidate, font, cfg) > max_width:
            parts.append(current)
            current = char
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def _tokens(
    paragraph: str,
    draw: ImageDraw.ImageDraw,
    font: Any,
    max_width: int,
    cfg: TextConfig,
) -> List[str]:
    words = paragraph.split()
    result: List[str] = []
    for word in words:
        if cfg.break_long_words and _text_width(draw, word, font, cfg) > max_width:
            result.extend(_split_long_token(word, draw, font, max_width, cfg))
        else:
            result.append(word)
    return result


def _greedy_wrap(
    tokens: Sequence[str],
    draw: ImageDraw.ImageDraw,
    font: Any,
    max_width: int,
    cfg: TextConfig,
) -> List[str]:
    lines: List[str] = []
    current = ""
    for token in tokens:
        candidate = token if not current else f"{current} {token}"
        if not current or _text_width(draw, candidate, font, cfg) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = token
    if current:
        lines.append(current)
    return lines


def _balanced_wrap(
    tokens: Sequence[str],
    draw: ImageDraw.ImageDraw,
    font: Any,
    max_width: int,
    cfg: TextConfig,
) -> List[str]:
    if len(tokens) > 120:
        return _greedy_wrap(tokens, draw, font, max_width, cfg)
    count = len(tokens)
    costs = [float("inf")] * (count + 1)
    next_break = [count] * (count + 1)
    costs[count] = 0.0
    for start in range(count - 1, -1, -1):
        for end in range(start + 1, count + 1):
            line = " ".join(tokens[start:end])
            width = _text_width(draw, line, font, cfg)
            if width > max_width:
                break
            slack = max_width - width
            penalty = 0.0 if end == count else float(slack * slack)
            candidate = penalty + costs[end]
            if candidate < costs[start]:
                costs[start] = candidate
                next_break[start] = end
    if costs[0] == float("inf"):
        return _greedy_wrap(tokens, draw, font, max_width, cfg)
    lines: List[str] = []
    index = 0
    while index < count:
        end = next_break[index]
        if end <= index:
            return _greedy_wrap(tokens, draw, font, max_width, cfg)
        lines.append(" ".join(tokens[index:end]))
        index = end
    return lines


def _wrap(
    text: str,
    font: Any,
    max_width: int,
    cfg: TextConfig,
) -> tuple[List[str], set[int]]:
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    paragraphs = text.split("\n") if cfg.preserve_newlines else [" ".join(text.split())]
    lines: List[str] = []
    paragraph_ends: set[int] = set()
    for paragraph in paragraphs:
        tokens = _tokens(paragraph, draw, font, max_width, cfg)
        if not tokens:
            wrapped = [""]
        elif cfg.wrap_mode == "balanced":
            wrapped = _balanced_wrap(tokens, draw, font, max_width, cfg)
        else:
            wrapped = _greedy_wrap(tokens, draw, font, max_width, cfg)
        lines.extend(wrapped)
        paragraph_ends.add(len(lines) - 1)
    return lines or [""], paragraph_ends


def _line_height(font: Any, spacing: float, fallback: int) -> int:
    try:
        ascent, descent = font.getmetrics()
        natural = ascent + descent
    except (AttributeError, TypeError):
        natural = fallback
    return max(1, int(round(natural * spacing)))


def _line_tops(
    line_count: int,
    line_height: int,
    paragraph_ends: set[int],
    paragraph_spacing: int,
) -> List[int]:
    result: List[int] = []
    current = 0
    for index in range(line_count):
        result.append(current)
        current += line_height
        if index in paragraph_ends and index < line_count - 1:
            current += paragraph_spacing
    return result


def _ellipsis(
    line: str,
    draw: ImageDraw.ImageDraw,
    font: Any,
    max_width: int,
    cfg: TextConfig,
) -> str:
    suffix = "…"
    if _text_width(draw, suffix, font, cfg) > max_width:
        return ""
    result = line.rstrip()
    while result and _text_width(draw, result + suffix, font, cfg) > max_width:
        result = result[:-1].rstrip()
    return result + suffix


def _transformed_content(cfg: TextConfig) -> str:
    if cfg.transform == TextTransform.UPPERCASE:
        return cfg.content.upper()
    if cfg.transform == TextTransform.LOWERCASE:
        return cfg.content.lower()
    if cfg.transform == TextTransform.CAPITALIZE:
        return cfg.content.title()
    return cfg.content


def measure_text(cfg: TextConfig, cw: int, ch: int, padding: PaddingConfig) -> TextLayout:
    max_width = max(1, cw - padding.left - padding.right)
    width_constraint = cfg.width if cfg.width is not None else cfg.max_width
    if width_constraint is not None:
        max_width = min(max_width, resolve(width_constraint, cw))

    max_height = max(1, ch - padding.top - padding.bottom)
    height_constraint = cfg.height if cfg.height is not None else cfg.max_height
    if height_constraint is not None:
        max_height = min(max_height, resolve(height_constraint, ch))

    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    content = _transformed_content(cfg)

    def at_size(size: int) -> TextLayout:
        font = _get_font(cfg, size)
        all_lines, paragraph_ends = _wrap(content, font, max_width, cfg)
        line_height = _line_height(font, cfg.line_spacing, size)
        paragraph_spacing = int(round(size * cfg.paragraph_spacing))
        all_tops = _line_tops(
            len(all_lines), line_height, paragraph_ends, paragraph_spacing
        )

        visible_count = len(all_lines)
        if cfg.max_lines is not None:
            visible_count = min(visible_count, cfg.max_lines)
        while visible_count > 0:
            candidate_height = all_tops[visible_count - 1] + line_height
            if candidate_height <= max_height:
                break
            visible_count -= 1
        visible_count = max(1, visible_count)
        lines = all_lines[:visible_count]
        tops = all_tops[:visible_count]
        widths = [_text_width(draw, line, font, cfg) for line in lines]
        width = max(widths, default=0)
        height = tops[-1] + line_height if tops else 0
        overflowed = (
            visible_count < len(all_lines)
            or width > max_width
            or height > max_height
        )
        return TextLayout(
            lines=lines,
            font=font,
            font_size=size,
            width=width,
            height=height,
            line_height=line_height,
            line_tops=tops,
            max_width=max_width,
            max_height=max_height,
            overflowed=overflowed,
        )

    layout = at_size(cfg.font_size)
    if cfg.fit == "shrink" and layout.overflowed:
        low = cfg.min_font_size
        high = cfg.font_size
        best = at_size(low)
        while low <= high:
            middle = (low + high) // 2
            candidate = at_size(middle)
            if candidate.overflowed:
                high = middle - 1
            else:
                best = candidate
                low = middle + 1
        layout = best

    truncate = cfg.fit == "truncate" or cfg.overflow == "ellipsis"
    if layout.overflowed and truncate and layout.lines:
        lines = list(layout.lines)
        lines[-1] = _ellipsis(lines[-1], draw, layout.font, max_width, cfg)
        widths = [_text_width(draw, line, layout.font, cfg) for line in lines]
        layout = TextLayout(
            lines=lines,
            font=layout.font,
            font_size=layout.font_size,
            width=max(widths, default=0),
            height=layout.height,
            line_height=layout.line_height,
            line_tops=layout.line_tops,
            max_width=layout.max_width,
            max_height=layout.max_height,
            overflowed=True,
            truncated=True,
        )

    if layout.overflowed and (cfg.overflow == "error" or cfg.fit == "error"):
        raise ValueError(
            "Text does not fit within configured bounds at minimum font size "
            f"{cfg.min_font_size}: {cfg.content!r}"
        )
    return layout


def _draw_spaced(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font: Any,
    fill: Any,
    cfg: TextConfig,
) -> None:
    x, y = position
    if cfg.letter_spacing == 0 and cfg.word_spacing == 0:
        try:
            draw.text((x, y), text, font=font, fill=fill, **_text_kwargs(cfg))
        except (KeyError, TypeError, ValueError):
            draw.text((x, y), text, font=font, fill=fill)
        return
    for char in text:
        try:
            draw.text((x, y), char, font=font, fill=fill, **_text_kwargs(cfg))
        except (KeyError, TypeError, ValueError):
            draw.text((x, y), char, font=font, fill=fill)
        x += int(_text_length(draw, char, font, cfg)) + cfg.letter_spacing
        if char == " ":
            x += cfg.word_spacing


def _adaptive_line_layer(
    cfg: TextConfig,
    canvas: Image.Image,
    font: Any,
    line: str,
    gx: int,
    gy: int,
) -> tuple[Image.Image, tuple[int, int]]:
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = _text_bbox(probe, line, font, cfg)
    width = max(1, _text_width(probe, line, font, cfg))
    height = max(1, box[3] - box[1])
    glyph = Image.new("L", (width, height), 0)
    _draw_spaced(ImageDraw.Draw(glyph), (-box[0], -box[1]), line, font, 255, cfg)

    left = max(0, gx + box[0])
    top = max(0, gy + box[1])
    right = min(canvas.width, gx + box[2])
    bottom = min(canvas.height, gy + box[3])
    if right <= left or bottom <= top:
        solid = Image.new("RGBA", (width, height), parse_color(cfg.color))
        solid.putalpha(glyph)
        return solid, (box[0], box[1])

    background = canvas.crop((left, top, right, bottom)).convert("RGB")
    background = background.resize((width, height), resample=Image.Resampling.BOX)
    luminance = background.convert("L")
    lookup = [255 if value < cfg.contrast_threshold else 0 for value in range(256)]
    dark_mask = luminance.point(lookup)
    light = Image.new("RGBA", (width, height), parse_color(cfg.contrast_light_color))
    dark = Image.new("RGBA", (width, height), parse_color(cfg.contrast_dark_color))
    mixed = Image.composite(light, dark, dark_mask)
    mixed.putalpha(glyph)
    return mixed, (box[0], box[1])


def _apply_clip(layer: Image.Image, margin: int, width: int, height: int) -> Image.Image:
    clip = Image.new("L", layer.size, 0)
    ImageDraw.Draw(clip).rectangle(
        (margin, margin, margin + width, margin + height),
        fill=255,
    )
    alpha = Image.composite(
        layer.getchannel("A"), Image.new("L", layer.size, 0), clip
    )
    result = layer.copy()
    result.putalpha(alpha)
    return result


def render_text(
    canvas: Image.Image,
    cfg: TextConfig,
    cw: int,
    ch: int,
    padding: PaddingConfig,
) -> Image.Image:
    if not cfg.visible:
        return canvas

    layout = measure_text(cfg, cw, ch, padding)
    x = resolve(cfg.x, cw)
    y = resolve(cfg.y, ch)
    margin = max(
        24,
        cfg.background_padding,
        (cfg.stroke.width if cfg.stroke else 0) + 4,
    )
    if cfg.shadow:
        shadow_extent = (
            abs(cfg.shadow.offset_x)
            + abs(cfg.shadow.offset_y)
            + cfg.shadow.blur_radius * 2
            + max(0, cfg.shadow.spread)
            + 4
        )
        margin = max(margin, int(shadow_extent))

    box_width = resolve(cfg.width, cw) if cfg.width is not None else layout.width
    box_height = resolve(cfg.height, ch) if cfg.height is not None else layout.height
    layer = Image.new(
        "RGBA",
        (max(1, box_width + margin * 2), max(1, box_height + margin * 2)),
        (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(layer)

    if cfg.background_color:
        draw.rounded_rectangle(
            (
                margin - cfg.background_padding,
                margin - cfg.background_padding,
                margin + box_width + cfg.background_padding,
                margin + box_height + cfg.background_padding,
            ),
            radius=cfg.background_radius,
            fill=parse_color(cfg.background_color),
        )

    if cfg.vertical_align == "middle":
        start_y = margin + max(0, (box_height - layout.height) // 2)
    elif cfg.vertical_align == "bottom":
        start_y = margin + max(0, box_height - layout.height)
    else:
        start_y = margin

    color = parse_color(cfg.color)
    color = (color[0], color[1], color[2], int(color[3] * cfg.opacity))
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for index, line in enumerate(layout.lines):
        line_width = _text_width(probe, line, layout.font, cfg)
        if cfg.align == TextAlign.LEFT:
            line_x = margin
        elif cfg.align == TextAlign.RIGHT:
            line_x = margin + box_width - line_width
        else:
            line_x = margin + (box_width - line_width) // 2
        line_y = start_y + layout.line_tops[index]

        if cfg.shadow:
            shadow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            _draw_spaced(
                ImageDraw.Draw(shadow_layer),
                (
                    line_x + int(cfg.shadow.offset_x),
                    line_y + int(cfg.shadow.offset_y),
                ),
                line,
                layout.font,
                parse_color(cfg.shadow.color),
                cfg,
            )
            if cfg.shadow.blur_radius > 0:
                shadow_layer = shadow_layer.filter(
                    ImageFilter.GaussianBlur(cfg.shadow.blur_radius)
                )
            layer = Image.alpha_composite(layer, shadow_layer)
            draw = ImageDraw.Draw(layer)

        if cfg.stroke:
            for delta_x in range(-cfg.stroke.width, cfg.stroke.width + 1):
                for delta_y in range(-cfg.stroke.width, cfg.stroke.width + 1):
                    if delta_x or delta_y:
                        _draw_spaced(
                            draw,
                            (line_x + delta_x, line_y + delta_y),
                            line,
                            layout.font,
                            parse_color(cfg.stroke.color),
                            cfg,
                        )

        if cfg.auto_contrast:
            anchor_x, anchor_y = get_anchor_offset(
                cfg.anchor, layer.width, layer.height
            )
            adaptive, offset = _adaptive_line_layer(
                cfg,
                canvas,
                layout.font,
                line,
                x + anchor_x + line_x,
                y + anchor_y + line_y,
            )
            layer.paste(
                adaptive,
                (line_x + offset[0], line_y + offset[1]),
                adaptive,
            )
        else:
            _draw_spaced(draw, (line_x, line_y), line, layout.font, color, cfg)

        if cfg.decoration != "none" and line:
            fraction = 0.9 if cfg.decoration == "underline" else 0.55
            decoration_y = line_y + int(layout.line_height * fraction)
            draw.line(
                (line_x, decoration_y, line_x + line_width, decoration_y),
                fill=color,
                width=max(1, layout.font_size // 18),
            )

    if cfg.overflow == "clip":
        layer = _apply_clip(layer, margin, box_width, box_height)
    for text_filter in cfg.filters:
        layer = apply_filter(layer, text_filter)
    if cfg.rotation:
        layer = layer.rotate(
            -cfg.rotation,
            expand=True,
            resample=Image.Resampling.BICUBIC,
        )
    dx, dy = get_anchor_offset(cfg.anchor, layer.width, layer.height)
    result_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    result_layer.paste(layer, (x + dx, y + dy), layer)
    return Image.alpha_composite(canvas, result_layer)
