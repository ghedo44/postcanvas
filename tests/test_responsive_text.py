from PIL import Image
import pytest

from postcanvas.models import PaddingConfig, TextConfig
from postcanvas.renderer.text import measure_text, render_text


def test_preserves_manual_newlines():
    config = TextConfig(content="First line\nSecond line", max_width=500)
    layout = measure_text(config, 1080, 1080, PaddingConfig())
    assert layout.lines == ["First line", "Second line"]


def test_breaks_long_tokens_to_fit_width():
    config = TextConfig(content="x" * 100, max_width=140, font_size=32)
    layout = measure_text(config, 1080, 1080, PaddingConfig())
    assert len(layout.lines) > 1
    assert layout.width <= 140


def test_shrinks_text_to_bounds():
    config = TextConfig(
        content="A long social headline that adapts to the available box",
        width=420,
        height=150,
        font_size=72,
        min_font_size=18,
        max_lines=3,
        fit="shrink",
        overflow="ellipsis",
    )
    layout = measure_text(config, 1080, 1080, PaddingConfig())
    assert 18 <= layout.font_size <= 72
    assert len(layout.lines) <= 3
    assert layout.width <= 420
    assert layout.height <= 150


def test_error_policy_rejects_unfittable_text():
    config = TextConfig(
        content="This content cannot fit",
        width=40,
        height=20,
        font_size=48,
        min_font_size=48,
        max_lines=1,
        fit="error",
    )
    with pytest.raises(ValueError):
        measure_text(config, 1080, 1080, PaddingConfig())


def test_letter_and_word_spacing_affect_measurement():
    normal = measure_text(
        TextConfig(content="SOCIAL POST", font_size=40),
        1080,
        1080,
        PaddingConfig(),
    )
    spaced = measure_text(
        TextConfig(
            content="SOCIAL POST",
            font_size=40,
            letter_spacing=4,
            word_spacing=12,
        ),
        1080,
        1080,
        PaddingConfig(),
    )
    assert spaced.width > normal.width


def test_balanced_wrapping_fits_each_line():
    config = TextConfig(
        content="Build adaptable social graphics without manual positioning",
        width=320,
        font_size=42,
        wrap_mode="balanced",
    )
    layout = measure_text(config, 1080, 1080, PaddingConfig())
    assert len(layout.lines) >= 2
    assert layout.width <= 320


def test_render_with_clipping_and_decoration_is_stable():
    canvas = Image.new("RGBA", (500, 500), (10, 10, 10, 255))
    config = TextConfig(
        content="Responsive title that is deliberately long",
        x=250,
        y=250,
        width=320,
        height=100,
        max_lines=2,
        fit="shrink",
        overflow="clip",
        decoration="underline",
        vertical_align="bottom",
        anchor="center",
    )
    result = render_text(canvas, config, 500, 500, PaddingConfig())
    assert result.size == (500, 500)
    assert result.mode == "RGBA"


def test_invalid_min_font_size():
    with pytest.raises(ValueError):
        TextConfig(content="bad", font_size=20, min_font_size=21)
