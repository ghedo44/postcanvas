from postcanvas import LayoutNode, PreviewFixture, Template, TemplateVariant, Theme
from postcanvas.validation import validate_post


def test_variant_inheritance_and_template_inheritance():
    base = Template(
        name="base",
        theme=Theme(colors={"text": "#ffffff"}, spacing={"md": 24}),
        variants={
            "square": TemplateVariant(
                profile="instagram_square",
                root=LayoutNode(kind="text", name="headline", id="headline", font_size=80),
                required_slots=["headline"],
            )
        },
        fixtures={"short": PreviewFixture(content={"headline": "Short"})},
    )
    child = Template(
        name="child",
        theme=Theme(colors={"accent": "#ff0000"}),
        variants={"compact": TemplateVariant(extends="square", max_chars_by_slot={"headline": 60})},
        default_variant="compact",
    ).inherit(base)
    resolved = child.resolve_variant("compact")
    assert resolved.profile == "instagram_square"
    assert resolved.root is not None
    assert resolved.required_slots == ["headline"]
    assert child.theme.colors == {"text": "#ffffff", "accent": "#ff0000"}
    assert "short" in child.fixtures


def test_repeat_grid_creates_unique_non_overlapping_slots():
    template = Template(
        name="metrics",
        variants={
            "square": TemplateVariant(
                profile="instagram_square",
                root=LayoutNode(
                    kind="repeat",
                    repeat_from="metrics",
                    repeat_direction="grid",
                    columns=2,
                    gap=20,
                    children=[LayoutNode(kind="text", name="item.label", id="metric", font_size=48, min_font_size=20, max_lines=2)],
                ),
            )
        },
    )
    post = template.build({"metrics": [{"label": value} for value in ["Reach", "Saves", "Shares", "Clicks"]]})
    report = validate_post(post)[0]
    assert set(report.elements) >= {"metric-1", "metric-2", "metric-3", "metric-4"}
    boxes = [report.elements[f"metric-{index}"] for index in range(1, 5)]
    for index, left in enumerate(boxes):
        for right in boxes[index + 1:]:
            assert not left.intersects(right)


def test_canvas_root_can_reenter_safe_area():
    template = Template(
        name="full-bleed",
        variants={
            "story": TemplateVariant(
                profile="instagram_story",
                root_scope="canvas",
                root=LayoutNode(kind="overlay", children=[
                    LayoutNode(kind="shape", id="background-panel", fill_color="#111111", respect_safe_area=False, respect_exclusion_zones=False),
                    LayoutNode(kind="safe_area", children=[LayoutNode(kind="text", name="headline", id="headline", font_size=80)]),
                ]),
            )
        },
    )
    post = template.build({"headline": "Safe headline"})
    report = validate_post(post)[0]
    assert report.elements["background-panel"].x == 0
    assert report.elements["headline"].x >= post.safe_area.left
    assert not any(issue.element_id == "headline" and issue.code == "outside-safe-area" for issue in report.issues)


def test_preview_fixtures_render():
    template = Template(
        name="fixture",
        variants={"square": TemplateVariant(profile="instagram_square", root=LayoutNode(kind="text", name="headline", font_size=48))},
        fixtures={
            "short": PreviewFixture(content={"headline": "Short"}),
            "long": PreviewFixture(content={"headline": "A longer headline that exercises fitting"}),
        },
    )
    results = template.render_fixtures()
    assert set(results) == {"short", "long"}
    assert all(result.images[0].size == (1080, 1080) for result in results.values())
