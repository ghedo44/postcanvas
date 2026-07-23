from pathlib import Path

import pytest

from postcanvas import render
from postcanvas.models import BackgroundConfig, ExclusionZone, LayoutPolicyConfig, PostConfig, TextConfig
from postcanvas.validation import LayoutValidationError, contrast_ratio, validate_post


def test_detects_platform_exclusion_zone_overlap():
    post = PostConfig(
        width=500,
        height=500,
        exclusion_zones=[ExclusionZone(name="controls", x=400, y=0, width=100, height=500)],
        layout_policy=LayoutPolicyConfig(safe_area="ignore", canvas_bounds="ignore", exclusion_zones="error", contrast="ignore"),
        texts=[TextConfig(id="title", content="Title", x=350, y=100, width=140, height=100, anchor="topleft")],
    )
    assert any(issue.code == "platform-ui-overlap" for issue in validate_post(post)[0].errors)


def test_detects_low_contrast_text():
    post = PostConfig(
        width=500,
        height=500,
        background=BackgroundConfig(color="#111111"),
        layout_policy=LayoutPolicyConfig(safe_area="ignore", canvas_bounds="ignore", exclusion_zones="ignore", contrast="error"),
        texts=[TextConfig(id="title", content="Title", color="#222222", x=50, y=50, width=200, height=100, anchor="topleft")],
    )
    assert any(issue.code == "low-contrast" for issue in validate_post(post)[0].errors)
    assert contrast_ratio("#ffffff", "#000000") == pytest.approx(21.0)


def test_reports_missing_explicit_font(tmp_path: Path):
    missing = tmp_path / "missing.ttf"
    post = PostConfig(
        width=500,
        height=500,
        layout_policy=LayoutPolicyConfig(safe_area="ignore", canvas_bounds="ignore", exclusion_zones="ignore", contrast="ignore", missing_fonts="error"),
        texts=[TextConfig(id="title", content="Title", font_path=str(missing), x=50, y=50, width=200, height=100, anchor="topleft")],
    )
    assert any(issue.code == "missing-font" for issue in validate_post(post)[0].errors)


def test_enforces_rendered_file_size():
    post = PostConfig(
        width=64,
        height=64,
        background=BackgroundConfig(color="#ffffff"),
        max_file_size_bytes=1,
        layout_policy=LayoutPolicyConfig(safe_area="ignore", canvas_bounds="ignore", exclusion_zones="ignore", contrast="ignore", file_size="error"),
    )
    with pytest.raises(LayoutValidationError):
        render(post)
