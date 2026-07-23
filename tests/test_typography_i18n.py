from postcanvas.models import PaddingConfig, TextConfig
from postcanvas.renderer.text import measure_text


def test_cjk_text_wraps_without_spaces():
    layout = measure_text(
        TextConfig(content="社交媒体图像模板应自动适应不同长度的文本内容", width=180, font_size=34, break_long_words=True),
        500, 500, PaddingConfig(),
    )
    assert len(layout.lines) > 1
    assert layout.width <= 180


def test_rtl_and_emoji_measurement_do_not_crash():
    rtl = measure_text(TextConfig(content="تصميم صور اجتماعية مرنة", width=260, direction="rtl", language="ar", font_size=36), 500, 500, PaddingConfig())
    emoji = measure_text(TextConfig(content="Launch 🚀✨", width=260, font_size=36), 500, 500, PaddingConfig())
    assert rtl.height > 0
    assert emoji.height > 0


def test_widow_control_avoids_single_word_last_line_when_possible():
    layout = measure_text(
        TextConfig(content="Build reliable responsive social graphics today", width=260, font_size=34, wrap_mode="greedy", widow_control=True, min_last_line_words=2),
        500, 500, PaddingConfig(),
    )
    if len(layout.lines) > 1:
        assert len(layout.lines[-1].split()) >= 2
