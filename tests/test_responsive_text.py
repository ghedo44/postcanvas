from PIL import Image
import pytest

from postcanvas.models import PaddingConfig, TextConfig
from postcanvas.renderer.text import measure_text, render_text


def test_preserves_manual_newlines():
    cfg = TextConfig(content="First line\nSecond line", max_width=500)
    layout = measure_text(cfg, 1080, 1080, PaddingConfig())
    assert layout.lines == ["First line", "Second line"]


def test_breaks_long_tokens_to_fit_width():
    cfg = TextConfig(content="x" * 100, max_width=140, font_size=32)
    layout = measure_text(cfg, 1080, 1080, PaddingConfig())
    assert len(layout.lines) > 1
    assert layout.width <= 140


def test_shrinks_text_to_bounds():
    cfg = TextConfig(content="A long social headline that adapts to the available box", width=420, height=150, font_size=72, min_font_size=18, max_lines=3, fit="shrink", overflow="ellipsis")
    layout = measure_text(cfg, 1080, 1080, PaddingConfig())
    assert 18 <= layout.font_size <= 72
    assert len(layout.lines) <= 3
    assert layout.width <= 420
    assert layout.height <= 150


def test_error_policy_rejects_unfittable_text():
    cfg = TextConfig(content="This content cannot fit", width=40, height=20, font_size=48, min_font_size=48, max_lines=1, fit="error")
    with pytest.raises(ValueError):
        measure_text(cfg, 1080, 1080, PaddingConfig())


def test_letter_spacing_affects_measurement():
    normal = measure_text(TextConfig(content="POST", font_size=40), 1080, 1080, PaddingConfig())
    spaced = measure_text(TextConfig(content="POST", font_size=40, letter_spacing=8), 1080, 1080, PaddingConfig())
    assert spaced.width > normal.width


def test_render_is_stable():
    canvas = Image.new("RGBA", (500, 500), (10, 10, 10, 255))
    cfg = TextConfig(content="Responsive title", x=250, y=250, width=320, height=180, max_lines=2, fit="shrink", vertical_align="bottom", anchor="center")
    result = render_text(canvas, cfg, 500, 500, PaddingConfig())
    assert result.size == (500, 500)
    assert result.mode == "RGBA"


def test_invalid_min_font_size():
    with pytest.raises(ValueError):
        TextConfig(content="bad", font_size=20, min_font_size=21)
