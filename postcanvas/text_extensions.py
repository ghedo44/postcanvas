from __future__ import annotations

from typing import Any, List


def install() -> None:
    """Add variable-font selection and widow control to the text engine."""

    from .renderer import text

    if getattr(text, "_advanced_installed", False):
        return
    original_get_font = text._get_font
    original_wrap = text._wrap

    def get_font(cfg: Any, size: int | None = None) -> Any:
        font = original_get_font(cfg, size)
        try:
            if getattr(cfg, "variation_name", None):
                font.set_variation_by_name(cfg.variation_name)
            if getattr(cfg, "variation_axes", None):
                font.set_variation_by_axes(cfg.variation_axes)
        except (AttributeError, OSError, TypeError, ValueError):
            pass
        return font

    def wrap(value: str, font: Any, max_width: int, cfg: Any):
        lines, paragraph_ends = original_wrap(value, font, max_width, cfg)
        if not getattr(cfg, "widow_control", False) or len(lines) < 2:
            return lines, paragraph_ends
        adjusted: List[str] = list(lines)
        minimum = getattr(cfg, "min_last_line_words", 1)
        while len(adjusted[-1].split()) < minimum:
            previous = adjusted[-2].split()
            last = adjusted[-1].split()
            if len(previous) <= getattr(cfg, "min_first_line_words", 1):
                break
            candidate = " ".join([previous[-1], *last])
            probe = text.ImageDraw.Draw(text.Image.new("RGBA", (1, 1)))
            if text._text_width(probe, candidate, font, cfg) > max_width:
                break
            adjusted[-2] = " ".join(previous[:-1])
            adjusted[-1] = candidate
        return adjusted, paragraph_ends

    text._get_font = get_font
    text._wrap = wrap
    text._advanced_installed = True
