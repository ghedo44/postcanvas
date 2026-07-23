from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List
from PIL import Image, ImageDraw, ImageFilter
from .utils import parse_color, resolve, get_anchor_offset
from .fonts import resolve_font
from ..models import TextConfig, PaddingConfig, TextAlign, TextTransform


@dataclass(frozen=True)
class TextLayout:
    lines: List[str]
    font: Any
    font_size: int
    width: int
    height: int
    line_height: int
    overflowed: bool = False


def _get_font(cfg: TextConfig, size: int | None = None) -> Any:
    return resolve_font(cfg.font_path, cfg.font_family, size or cfg.font_size)


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: Any, letter_spacing: int) -> int:
    if not text:
        return 0
    if letter_spacing == 0:
        box = draw.textbbox((0, 0), text, font=font)
        return int(box[2] - box[0])
    return sum(int(draw.textlength(char, font=font)) for char in text) + letter_spacing * max(0, len(text) - 1)


def _split_long_token(token: str, draw: ImageDraw.ImageDraw, font: Any, max_w: int, letter_spacing: int) -> List[str]:
    if not token:
        return [""]
    parts: List[str] = []
    current = ""
    for char in token:
        candidate = current + char
        if current and _text_width(draw, candidate, font, letter_spacing) > max_w:
            parts.append(current)
            current = char
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def _wrap_paragraph(paragraph: str, draw: ImageDraw.ImageDraw, font: Any, max_w: int, letter_spacing: int, break_long_words: bool) -> List[str]:
    if paragraph == "":
        return [""]
    words = paragraph.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = ""
    for word in words:
        tokens = [word]
        if break_long_words and _text_width(draw, word, font, letter_spacing) > max_w:
            tokens = _split_long_token(word, draw, font, max_w, letter_spacing)
        for token in tokens:
            candidate = token if not current else f"{current} {token}"
            if not current or _text_width(draw, candidate, font, letter_spacing) <= max_w:
                current = candidate
            else:
                lines.append(current)
                current = token
    if current:
        lines.append(current)
    return lines


def _wrap(text: str, font: Any, max_w: int, letter_spacing: int = 0, break_long_words: bool = True, preserve_newlines: bool = True) -> List[str]:
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    paragraphs = text.split("\n") if preserve_newlines else [" ".join(text.split())]
    lines: List[str] = []
    for paragraph in paragraphs:
        lines.extend(_wrap_paragraph(paragraph, draw, font, max_w, letter_spacing, break_long_words))
    return lines or [""]


def _line_height(font: Any, spacing: float, fallback: int) -> int:
    try:
        ascent, descent = font.getmetrics()
        natural = ascent + descent
    except (AttributeError, TypeError):
        natural = fallback
    return max(1, int(round(natural * spacing)))


def _ellipsis(line: str, draw: ImageDraw.ImageDraw, font: Any, max_w: int, letter_spacing: int) -> str:
    suffix = "…"
    if _text_width(draw, suffix, font, letter_spacing) > max_w:
        return ""
    result = line.rstrip()
    while result and _text_width(draw, result + suffix, font, letter_spacing) > max_w:
        result = result[:-1].rstrip()
    return result + suffix


def measure_text(cfg: TextConfig, cw: int, ch: int, padding: PaddingConfig) -> TextLayout:
    max_w = cw - padding.left - padding.right
    if cfg.width is not None:
        max_w = min(max_w, resolve(cfg.width, cw))
    if cfg.max_width is not None:
        max_w = min(max_w, resolve(cfg.max_width, cw))
    max_w = max(1, max_w)

    max_h = ch - padding.top - padding.bottom
    if cfg.height is not None:
        max_h = min(max_h, resolve(cfg.height, ch))
    if cfg.max_height is not None:
        max_h = min(max_h, resolve(cfg.max_height, ch))
    max_h = max(1, max_h)

    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    def at_size(size: int) -> TextLayout:
        font = _get_font(cfg, size)
        lines = _wrap(cfg.content, font, max_w, cfg.letter_spacing, cfg.break_long_words, cfg.preserve_newlines)
        line_height = _line_height(font, cfg.line_spacing, size)
        allowed_lines = max(1, max_h // line_height)
        if cfg.max_lines is not None:
            allowed_lines = min(allowed_lines, cfg.max_lines)
        overflowed = len(lines) > allowed_lines
        visible = lines[:allowed_lines]
        widths = [_text_width(draw, line, font, cfg.letter_spacing) for line in visible]
        width = max(widths, default=0)
        height = line_height * len(visible)
        return TextLayout(visible, font, size, width, height, line_height, overflowed or width > max_w or height > max_h)

    layout = at_size(cfg.font_size)
    if cfg.fit == "shrink" and layout.overflowed:
        low, high = cfg.min_font_size, cfg.font_size
        best = at_size(low)
        while low <= high:
            mid = (low + high) // 2
            candidate = at_size(mid)
            if candidate.overflowed:
                high = mid - 1
            else:
                best = candidate
                low = mid + 1
        layout = best

    if layout.overflowed and (cfg.overflow == "ellipsis" or cfg.fit == "truncate") and layout.lines:
        lines = list(layout.lines)
        lines[-1] = _ellipsis(lines[-1], draw, layout.font, max_w, cfg.letter_spacing)
        widths = [_text_width(draw, line, layout.font, cfg.letter_spacing) for line in lines]
        layout = TextLayout(lines, layout.font, layout.font_size, max(widths, default=0), layout.height, layout.line_height, True)

    if layout.overflowed and (cfg.overflow == "error" or cfg.fit == "error"):
        raise ValueError(f"Text does not fit within configured bounds at minimum font size {cfg.min_font_size}: {cfg.content!r}")
    return layout


def _draw_spaced(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font: Any, fill: Any, spacing: int) -> None:
    x, y = position
    if spacing == 0:
        draw.text((x, y), text, font=font, fill=fill)
        return
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += int(draw.textlength(char, font=font)) + spacing


def render_text(canvas: Image.Image, cfg: TextConfig, cw: int, ch: int, padding: PaddingConfig) -> Image.Image:
    if not cfg.visible:
        return canvas

    if cfg.transform == TextTransform.UPPERCASE:
        cfg = cfg.model_copy(update={"content": cfg.content.upper()})
    elif cfg.transform == TextTransform.LOWERCASE:
        cfg = cfg.model_copy(update={"content": cfg.content.lower()})
    elif cfg.transform == TextTransform.CAPITALIZE:
        cfg = cfg.model_copy(update={"content": cfg.content.title()})

    layout = measure_text(cfg, cw, ch, padding)
    x, y = resolve(cfg.x, cw), resolve(cfg.y, ch)
    margin = max(24, cfg.background_padding, (cfg.stroke.width if cfg.stroke else 0) + 4)
    if cfg.shadow:
        margin = max(margin, int(abs(cfg.shadow.offset_x) + abs(cfg.shadow.offset_y) + cfg.shadow.blur_radius * 2 + 4))

    box_w = resolve(cfg.width, cw) if cfg.width is not None else layout.width
    box_h = resolve(cfg.height, ch) if cfg.height is not None else layout.height
    layer = Image.new("RGBA", (max(1, box_w + margin * 2), max(1, box_h + margin * 2)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    if cfg.background_color:
        draw.rounded_rectangle(
            [margin - cfg.background_padding, margin - cfg.background_padding, margin + box_w + cfg.background_padding, margin + box_h + cfg.background_padding],
            radius=cfg.background_radius,
            fill=parse_color(cfg.background_color),
        )

    if cfg.vertical_align == "middle":
        start_y = margin + max(0, (box_h - layout.height) // 2)
    elif cfg.vertical_align == "bottom":
        start_y = margin + max(0, box_h - layout.height)
    else:
        start_y = margin

    color = parse_color(cfg.color)
    color = (color[0], color[1], color[2], int(color[3] * cfg.opacity))
    cy = start_y
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for line in layout.lines:
        line_w = _text_width(probe, line, layout.font, cfg.letter_spacing)
        if cfg.align == TextAlign.LEFT:
            lx = margin
        elif cfg.align == TextAlign.RIGHT:
            lx = margin + box_w - line_w
        else:
            lx = margin + (box_w - line_w) // 2

        if cfg.shadow:
            shadow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            _draw_spaced(ImageDraw.Draw(shadow_layer), (lx + int(cfg.shadow.offset_x), cy + int(cfg.shadow.offset_y)), line, layout.font, parse_color(cfg.shadow.color), cfg.letter_spacing)
            if cfg.shadow.blur_radius > 0:
                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(cfg.shadow.blur_radius))
            layer = Image.alpha_composite(layer, shadow_layer)
            draw = ImageDraw.Draw(layer)

        if cfg.stroke:
            for dx in range(-cfg.stroke.width, cfg.stroke.width + 1):
                for dy in range(-cfg.stroke.width, cfg.stroke.width + 1):
                    if dx or dy:
                        _draw_spaced(draw, (lx + dx, cy + dy), line, layout.font, parse_color(cfg.stroke.color), cfg.letter_spacing)
        _draw_spaced(draw, (lx, cy), line, layout.font, color, cfg.letter_spacing)
        cy += layout.line_height

    if cfg.rotation:
        layer = layer.rotate(-cfg.rotation, expand=True, resample=Image.Resampling.BICUBIC)
    dx, dy = get_anchor_offset(cfg.anchor, layer.width, layer.height)
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(layer, (x + dx, y + dy), layer)
    return Image.alpha_composite(canvas, tmp)
