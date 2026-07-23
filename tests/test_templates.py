from pathlib import Path

import pytest

from postcanvas.template import LayoutNode, Template, TemplateVariant
from postcanvas.validation import validate_post


def _template() -> Template:
    return Template(
        name="editorial",
        variants={
            "portrait": TemplateVariant(
                profile="instagram_portrait",
                max_chars_by_slot={"headline": 120},
                root=LayoutNode(
                    kind="column",
                    gap=24,
                    children=[
                        LayoutNode(
                            kind="text",
                            name="headline",
                            id="headline",
                            grow=2,
                            font_size=96,
                            min_font_size=30,
                            max_lines=4,
                        ),
                        LayoutNode(
                            kind="text",
                            name="footer",
                            id="footer",
                            basis=80,
                            font_size=32,
                            max_lines=1,
                        ),
                    ],
                ),
            )
        },
    )


@pytest.mark.parametrize(
    "headline",
    [
        "Short title",
        "A very long headline that changes its line count without overlapping the footer or leaving the safe area",
    ],
)
def test_column_template_does_not_overlap(headline: str):
    post = _template().build({"headline": headline, "footer": "@postcanvas"})
    report = validate_post(post)[0]
    headline_box = report.elements["headline"]
    footer_box = report.elements["footer"]
    assert headline_box.bottom <= footer_box.y
    assert not any(issue.code == "outside-safe-area" for issue in report.issues)


def test_required_slot_is_enforced():
    template = Template(
        name="required",
        variants={
            "square": TemplateVariant(
                profile="instagram_square",
                root=LayoutNode(
                    kind="text",
                    name="headline",
                    required=True,
                ),
            )
        },
    )
    with pytest.raises(ValueError):
        template.build({})


def test_json_round_trip(tmp_path: Path):
    source = _template()
    path = tmp_path / "template.json"
    source.to_file(path)
    restored = Template.from_file(path)
    assert restored == source


def test_legacy_preset_dimensions_are_preserved():
    from postcanvas.presets import blog_cover

    post = blog_cover()
    assert (post.width, post.height) == (1600, 900)
