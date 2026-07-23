from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Literal, Optional, Sequence

from PIL import Image, ImageDraw
from pydantic import BaseModel, Field, model_validator

from .models import PaddingConfig, ShadowConfig, StrokeConfig, TextAlign, TextConfig
from .renderer.fonts import resolve_font
from .renderer.utils import get_anchor_offset, resolve

Dimension = int | float | str
RichTextFit = Literal["none", "shrink", "error"]
RichTextOverflow = Literal["visible", "clip", "ellipsis", "error"]


class RichTextSpan(BaseModel):
    """One styled span inside a responsive rich-text block."""

    text: str
    color: Optional[str] = None
    font_family: Optional[str] = None
    font_path: Optional[str] = None
    font_fallback_paths: List[str] = Field(default_factory=list)
    font_scale: float = Field(default=1.0, gt=0.0)
    letter_spacing: Optional[int] = None
    word_spacing: Optional[int] = None
    decoration: Literal["none", "underline", "strikethrough"] = "none"
    background_color: Optional[str] = None
    shadow: Optional[ShadowConfig] = None
    stroke: Optional[StrokeConfig] = None
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)


class RichTextBlock(BaseModel):
    """Lay out per-span styled text into ordinary validated TextConfig runs."""

    spans: List[RichTextSpan]
    x: Dimension = "50%"
    y: Dimension = "50%"
    width: Dimension = "80%"
    height: Dimension = "40%"
    anchor: str = "center"
    font_family: Optional[str] = None
    font_path: Optional[str] = None
    font_fallback_paths: List[str] = Field(default_factory=list)
    font_size: int = Field(default=64, ge=1)
    min_font_size: int = Field(default=20, ge=1)
    color: str = "#FFFFFF"
    letter_spacing: int = 0
    word_spacing: int = 0
    fit: RichTextFit = "shrink"
    overflow: RichTextOverflow = "ellipsis"
    max_lines: Optional[int] = Field(default=None, ge=1)
    line_spacing: float = Field(default=1.2, gt=0)
    paragraph_spacing: float = Field(default=0.25, ge=0)
    first_line_indent: int = Field(default=0, ge=0)
    hyphenate: bool = False
    hyphenation_language: str = "en_US"
    hyphen_character: str = "‐"
    break_long_words: bool = True
    align: TextAlign = TextAlign.LEFT
    vertical_align: Literal["top", "middle", "bottom"] = "top"
    id_prefix: str = "rich-text"
    collision_group: Optional[str] = "content"
    allow_overlap_with: List[str] = Field(default_factory=list)
    respect_safe_area: bool = True
    respect_exclusion_zones: bool = True
    z_index: int = 10

    @model_validator(mode="after")
    def validate_block(self) -> "RichTextBlock":
        if not self.spans:
            raise ValueError("RichTextBlock requires at least one span")
        if self.min_font_size > self.font_size:
            raise ValueError("min_font_size cannot exceed font_size")
        if len(self.hyphen_character) != 1:
            raise ValueError("hyphen_character must contain exactly one character")
        return self

    def compose(
        self,
        canvas_width: int,
        canvas_height: int,
        padding: Optional[PaddingConfig] = None,
    ) -> "RichTextComposition":
        return compose_rich_text(
            self,
            canvas_width,
            canvas_height,
            padding or PaddingConfig(),
        )


@dataclass(frozen=True)
class RichTextRunLayout:
    text: str
    span_index: int
    width: int
    font_size: int
    font: Any


@dataclass(frozen=True)
class RichTextLineLayout:
    runs: List[RichTextRunLayout]
    width: int
    height: int
    top: int
    indent: int
    paragraph_end: bool


@dataclass(frozen=True)
class RichTextLayout:
    lines: List[RichTextLineLayout]
    font_size: int
    width: int
    height: int
    max_width: int
    max_height: int
    overflowed: bool
    truncated: bool = False


@dataclass(frozen=True)
class RichTextComposition:
    texts: List[TextConfig]
    layout: RichTextLayout
    bounds: tuple[int, int, int, int]


@dataclass(frozen=True)
class _StyledChar:
    value: str
    span_index: int


@dataclass
class _RawLine:
    chars: List[_StyledChar]
    indent: int
    paragraph_end: bool = False


def _font_for_span(block: RichTextBlock, span: RichTextSpan, size: int) -> Any:
    actual_size = max(1, int(round(size * span.font_scale)))
    paths = [
        span.font_path,
        *span.font_fallback_paths,
        block.font_path,
        *block.font_fallback_paths,
    ]
    family = span.font_family or block.font_family
    for path in paths:
        if not path:
            continue
        try:
            return resolve_font(path, family, actual_size)
        except (OSError, ValueError):
            continue
    return resolve_font(None, family, actual_size)


def _span_font_size(span: RichTextSpan, size: int) -> int:
    return max(1, int(round(size * span.font_scale)))


def _spacing(block: RichTextBlock, span: RichTextSpan) -> tuple[int, int]:
    return (
        block.letter_spacing
        if span.letter_spacing is None
        else span.letter_spacing,
        block.word_spacing if span.word_spacing is None else span.word_spacing,
    )


def _text_width(
    draw: ImageDraw.ImageDraw,
    value: str,
    font: Any,
    letter: int,
    word: int,
) -> int:
    if not value:
        return 0
    if letter == 0:
        width = float(draw.textlength(value, font=font))
    else:
        width = sum(float(draw.textlength(char, font=font)) for char in value)
        width += letter * max(0, len(value) - 1)
    width += word * value.count(" ")
    return max(0, int(round(width)))


def _paragraphs(spans: Sequence[RichTextSpan]) -> List[List[_StyledChar]]:
    result: List[List[_StyledChar]] = [[]]
    for span_index, span in enumerate(spans):
        for char in span.text:
            if char == "\n":
                result.append([])
            else:
                result[-1].append(_StyledChar(char, span_index))
    return result


def _words(chars: Sequence[_StyledChar]) -> List[List[_StyledChar]]:
    result: List[List[_StyledChar]] = []
    current: List[_StyledChar] = []
    for char in chars:
        if char.value.isspace():
            if current:
                result.append(current)
                current = []
        else:
            current.append(char)
    if current:
        result.append(current)
    return result


def _groups(chars: Sequence[_StyledChar]) -> List[List[_StyledChar]]:
    groups: List[List[_StyledChar]] = []
    for char in chars:
        if not groups or groups[-1][0].span_index != char.span_index:
            groups.append([char])
        else:
            groups[-1].append(char)
    return groups


def _chars_width(
    chars: Sequence[_StyledChar],
    block: RichTextBlock,
    fonts: Sequence[Any],
    draw: ImageDraw.ImageDraw,
) -> int:
    total = 0
    for group in _groups(chars):
        span = block.spans[group[0].span_index]
        letter, word = _spacing(block, span)
        total += _text_width(
            draw,
            "".join(char.value for char in group),
            fonts[group[0].span_index],
            letter,
            word,
        )
    return total


def _space(span_index: int) -> _StyledChar:
    return _StyledChar(" ", span_index)


def _hyphen_positions(word: str, language: str) -> List[int]:
    try:
        import pyphen
    except ImportError as exc:
        raise ImportError(
            "Install postcanvas[typography] to enable dictionary hyphenation"
        ) from exc
    return list(pyphen.Pyphen(lang=language).positions(word))


def _split_word(
    word: List[_StyledChar],
    first_width: int,
    full_width: int,
    block: RichTextBlock,
    fonts: Sequence[Any],
    draw: ImageDraw.ImageDraw,
) -> List[List[_StyledChar]]:
    remaining = list(word)
    parts: List[List[_StyledChar]] = []
    available = max(1, first_width)
    while remaining:
        if _chars_width(remaining, block, fonts, draw) <= available:
            parts.append(remaining)
            break
        split_at = 0
        add_hyphen = False
        if block.hyphenate:
            plain = "".join(char.value for char in remaining)
            for position in _hyphen_positions(
                plain,
                block.hyphenation_language,
            ):
                candidate = [
                    *remaining[:position],
                    _StyledChar(
                        block.hyphen_character,
                        remaining[position - 1].span_index,
                    ),
                ]
                if _chars_width(candidate, block, fonts, draw) <= available:
                    split_at = position
                    add_hyphen = True
                else:
                    break
        if split_at == 0 and block.break_long_words:
            for position in range(1, len(remaining) + 1):
                if (
                    _chars_width(
                        remaining[:position],
                        block,
                        fonts,
                        draw,
                    )
                    <= available
                ):
                    split_at = position
                else:
                    break
        if split_at == 0:
            parts.append(remaining)
            break
        piece = list(remaining[:split_at])
        if add_hyphen:
            piece.append(
                _StyledChar(block.hyphen_character, piece[-1].span_index)
            )
        parts.append(piece)
        remaining = remaining[split_at:]
        available = max(1, full_width)
    return parts


def _line_height(
    block: RichTextBlock,
    fonts: Sequence[Any],
    fallback: int,
) -> int:
    natural = 0
    for font in fonts:
        try:
            ascent, descent = font.getmetrics()
            natural = max(natural, ascent + descent)
        except (AttributeError, TypeError):
            natural = max(natural, fallback)
    return max(1, int(round(natural * block.line_spacing)))


def _layout_at_size(
    block: RichTextBlock,
    size: int,
    max_width: int,
    max_height: int,
) -> RichTextLayout:
    fonts = [_font_for_span(block, span, size) for span in block.spans]
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    raw_lines: List[_RawLine] = []

    for paragraph in _paragraphs(block.spans):
        words = _words(paragraph)
        first_line = True
        current: List[_StyledChar] = []
        current_indent = block.first_line_indent
        if not words:
            raw_lines.append(
                _RawLine([], current_indent, paragraph_end=True)
            )
            continue
        for word in words:
            indent = current_indent if first_line else 0
            available = max(1, max_width - indent)
            separator = [_space(word[0].span_index)] if current else []
            candidate = [*current, *separator, *word]
            if _chars_width(candidate, block, fonts, draw) <= available:
                current = candidate
                continue
            if current:
                raw_lines.append(_RawLine(current, indent))
                current = []
                first_line = False
                indent = 0
                available = max_width
            if _chars_width(word, block, fonts, draw) <= available:
                current = list(word)
                continue
            pieces = _split_word(
                word,
                available,
                max_width,
                block,
                fonts,
                draw,
            )
            for piece_index, piece in enumerate(pieces):
                if (
                    piece_index == len(pieces) - 1
                    and _chars_width(piece, block, fonts, draw) <= max_width
                ):
                    current = piece
                else:
                    raw_lines.append(
                        _RawLine(piece, indent if first_line else 0)
                    )
                    first_line = False
                    indent = 0
        if current or not raw_lines:
            raw_lines.append(
                _RawLine(current, current_indent if first_line else 0)
            )
        raw_lines[-1].paragraph_end = True

    base_line_height = _line_height(block, fonts, size)
    paragraph_gap = int(round(size * block.paragraph_spacing))
    tops: List[int] = []
    current_top = 0
    for index, line in enumerate(raw_lines):
        tops.append(current_top)
        current_top += base_line_height
        if line.paragraph_end and index < len(raw_lines) - 1:
            current_top += paragraph_gap

    visible_count = len(raw_lines)
    if block.max_lines is not None:
        visible_count = min(visible_count, block.max_lines)
    while (
        visible_count > 0
        and tops[visible_count - 1] + base_line_height > max_height
    ):
        visible_count -= 1
    visible_count = max(1, visible_count)
    overflowed = visible_count < len(raw_lines)
    visible = raw_lines[:visible_count]
    visible_tops = tops[:visible_count]

    line_layouts: List[RichTextLineLayout] = []
    for raw, top in zip(visible, visible_tops):
        runs: List[RichTextRunLayout] = []
        width = 0
        for group in _groups(raw.chars):
            span_index = group[0].span_index
            span = block.spans[span_index]
            value = "".join(char.value for char in group)
            letter, word = _spacing(block, span)
            run_width = _text_width(
                draw,
                value,
                fonts[span_index],
                letter,
                word,
            )
            runs.append(
                RichTextRunLayout(
                    text=value,
                    span_index=span_index,
                    width=run_width,
                    font_size=_span_font_size(span, size),
                    font=fonts[span_index],
                )
            )
            width += run_width
        line_layouts.append(
            RichTextLineLayout(
                runs=runs,
                width=width,
                height=base_line_height,
                top=top,
                indent=raw.indent,
                paragraph_end=raw.paragraph_end,
            )
        )

    height = visible_tops[-1] + base_line_height if visible_tops else 0
    width = max(
        (line.width + line.indent for line in line_layouts),
        default=0,
    )
    return RichTextLayout(
        lines=line_layouts,
        font_size=size,
        width=width,
        height=height,
        max_width=max_width,
        max_height=max_height,
        overflowed=(
            overflowed or width > max_width or height > max_height
        ),
    )


def _truncate_last_line(
    block: RichTextBlock,
    layout: RichTextLayout,
) -> RichTextLayout:
    if not layout.lines:
        return layout
    lines = list(layout.lines)
    last = lines[-1]
    if not last.runs:
        return layout
    runs = list(last.runs)
    final = runs[-1]
    span = block.spans[final.span_index]
    letter, word = _spacing(block, span)
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    prefix_width = sum(run.width for run in runs[:-1])
    available = max(
        0,
        layout.max_width - last.indent - prefix_width,
    )
    value = final.text.rstrip()
    suffix = "…"
    while (
        value
        and _text_width(
            draw,
            value + suffix,
            final.font,
            letter,
            word,
        )
        > available
    ):
        value = value[:-1].rstrip()
    replacement = value + suffix if available > 0 else ""
    runs[-1] = RichTextRunLayout(
        text=replacement,
        span_index=final.span_index,
        width=_text_width(
            draw,
            replacement,
            final.font,
            letter,
            word,
        ),
        font_size=final.font_size,
        font=final.font,
    )
    width = sum(run.width for run in runs)
    lines[-1] = RichTextLineLayout(
        runs=runs,
        width=width,
        height=last.height,
        top=last.top,
        indent=last.indent,
        paragraph_end=last.paragraph_end,
    )
    return RichTextLayout(
        lines=lines,
        font_size=layout.font_size,
        width=max(
            (line.width + line.indent for line in lines),
            default=0,
        ),
        height=layout.height,
        max_width=layout.max_width,
        max_height=layout.max_height,
        overflowed=True,
        truncated=True,
    )


def compose_rich_text(
    block: RichTextBlock,
    canvas_width: int,
    canvas_height: int,
    padding: PaddingConfig,
) -> RichTextComposition:
    box_width = min(
        resolve(block.width, canvas_width),
        canvas_width - padding.left - padding.right,
    )
    box_height = min(
        resolve(block.height, canvas_height),
        canvas_height - padding.top - padding.bottom,
    )
    x = resolve(block.x, canvas_width)
    y = resolve(block.y, canvas_height)
    offset_x, offset_y = get_anchor_offset(
        block.anchor,
        box_width,
        box_height,
    )
    left = x + offset_x
    top = y + offset_y

    layout = _layout_at_size(
        block,
        block.font_size,
        box_width,
        box_height,
    )
    if block.fit == "shrink" and layout.overflowed:
        low, high = block.min_font_size, block.font_size
        best = _layout_at_size(
            block,
            low,
            box_width,
            box_height,
        )
        while low <= high:
            middle = (low + high) // 2
            candidate = _layout_at_size(
                block,
                middle,
                box_width,
                box_height,
            )
            if candidate.overflowed:
                high = middle - 1
            else:
                best = candidate
                low = middle + 1
        layout = best

    if layout.overflowed and block.overflow == "ellipsis":
        layout = _truncate_last_line(block, layout)
    if layout.overflowed and (
        block.fit == "error" or block.overflow == "error"
    ):
        raise ValueError(
            "Rich text does not fit within configured bounds at minimum font "
            f"size {block.min_font_size}"
        )

    if block.vertical_align == "middle":
        vertical_offset = max(0, (box_height - layout.height) // 2)
    elif block.vertical_align == "bottom":
        vertical_offset = max(0, box_height - layout.height)
    else:
        vertical_offset = 0

    texts: List[TextConfig] = []
    for line_index, line in enumerate(layout.lines):
        indent = line.indent if block.align == TextAlign.LEFT else 0
        if block.align == TextAlign.CENTER:
            line_left = left + (box_width - line.width) // 2
        elif block.align == TextAlign.RIGHT:
            line_left = left + box_width - line.width
        else:
            line_left = left + indent
        cursor = line_left
        for run_index, run in enumerate(line.runs):
            span = block.spans[run.span_index]
            run_width = max(1, run.width + 2)
            line_height = max(1, line.height)
            texts.append(
                TextConfig(
                    content=run.text,
                    id=(
                        f"{block.id_prefix}-{line_index + 1}-"
                        f"{run_index + 1}"
                    ),
                    collision_group=block.collision_group,
                    allow_overlap_with=block.allow_overlap_with,
                    respect_safe_area=block.respect_safe_area,
                    respect_exclusion_zones=(
                        block.respect_exclusion_zones
                    ),
                    x=cursor + run_width / 2,
                    y=(
                        top
                        + vertical_offset
                        + line.top
                        + line_height / 2
                    ),
                    width=run_width,
                    height=line_height,
                    anchor="center",
                    font_family=span.font_family or block.font_family,
                    font_path=span.font_path or block.font_path,
                    font_fallback_paths=[
                        *span.font_fallback_paths,
                        *block.font_fallback_paths,
                    ],
                    font_size=run.font_size,
                    min_font_size=run.font_size,
                    max_lines=1,
                    fit="none",
                    overflow=(
                        "clip" if block.overflow == "clip" else "visible"
                    ),
                    color=span.color or block.color,
                    align=TextAlign.LEFT,
                    vertical_align="middle",
                    letter_spacing=(
                        block.letter_spacing
                        if span.letter_spacing is None
                        else span.letter_spacing
                    ),
                    word_spacing=(
                        block.word_spacing
                        if span.word_spacing is None
                        else span.word_spacing
                    ),
                    decoration=span.decoration,
                    background_color=span.background_color,
                    shadow=span.shadow,
                    stroke=span.stroke,
                    opacity=span.opacity,
                    z_index=block.z_index,
                )
            )
            cursor += run_width

    return RichTextComposition(
        texts=texts,
        layout=layout,
        bounds=(left, top, box_width, box_height),
    )


__all__ = [
    "RichTextBlock",
    "RichTextComposition",
    "RichTextLayout",
    "RichTextLineLayout",
    "RichTextRunLayout",
    "RichTextSpan",
    "compose_rich_text",
]
