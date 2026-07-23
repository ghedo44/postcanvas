from postcanvas import PromptVariantSelector, RichTextBlock, RichTextSpan
from postcanvas.models import BackgroundConfig, PostConfig, TextAlign
from postcanvas.renderer import render_one


def test_rich_text_composes_styled_runs_without_overlap():
    block = RichTextBlock(
        spans=[
            RichTextSpan(text="Build ", color="#ffffff"),
            RichTextSpan(
                text="better",
                color="#ff0000",
                font_scale=1.2,
                decoration="underline",
            ),
            RichTextSpan(text=" social graphics", color="#ffffff"),
        ],
        x=40,
        y=40,
        width=420,
        height=180,
        anchor="topleft",
        font_size=52,
        min_font_size=24,
        max_lines=3,
        align=TextAlign.LEFT,
        id_prefix="headline",
    )
    composition = block.compose(500, 300)
    assert composition.texts
    assert {text.color for text in composition.texts} >= {
        "#ffffff",
        "#ff0000",
    }
    assert len({text.id for text in composition.texts}) == len(
        composition.texts
    )
    boxes = []
    for text in composition.texts:
        boxes.append(
            (
                float(text.x) - float(text.width) / 2,
                float(text.x) + float(text.width) / 2,
                float(text.y),
            )
        )
    for index, left in enumerate(boxes):
        for right in boxes[index + 1 :]:
            if left[2] == right[2]:
                assert left[1] <= right[0] or right[1] <= left[0]


def test_rich_text_hyphenation_and_first_line_indent():
    block = RichTextBlock(
        spans=[
            RichTextSpan(
                text="Representation internationalization"
            )
        ],
        x=0,
        y=0,
        width=180,
        height=220,
        anchor="topleft",
        font_size=36,
        min_font_size=36,
        max_lines=5,
        first_line_indent=30,
        hyphenate=True,
        overflow="visible",
        id_prefix="body",
    )
    composition = block.compose(300, 300)
    assert any("‐" in text.content for text in composition.texts)
    first = next(
        text
        for text in composition.texts
        if text.id.startswith("body-1-")
    )
    second = next(
        text
        for text in composition.texts
        if text.id.startswith("body-2-")
    )
    first_left = float(first.x) - float(first.width) / 2
    second_left = float(second.x) - float(second.width) / 2
    assert first_left >= second_left + 25


def test_rich_text_shrinks_and_renders_as_normal_text_elements():
    block = RichTextBlock(
        spans=[
            RichTextSpan(
                text=(
                    "A very long styled headline that must shrink to stay "
                    "inside its box"
                )
            )
        ],
        width=260,
        height=100,
        font_size=72,
        min_font_size=18,
        max_lines=2,
    )
    composition = block.compose(500, 500)
    assert composition.layout.font_size < 72
    post = PostConfig(
        width=500,
        height=500,
        background=BackgroundConfig(color="#111111"),
        texts=composition.texts,
    )
    assert render_one(post).size == (500, 500)


def test_prompt_variant_selector_uses_validated_choice():
    from postcanvas import LayoutNode, Template, TemplateVariant

    template = Template(
        name="selector",
        variants={
            "square": TemplateVariant(
                profile="instagram_square",
                root=LayoutNode(kind="text", name="headline"),
            ),
            "portrait": TemplateVariant(
                profile="instagram_portrait",
                root=LayoutNode(kind="text", name="headline"),
            ),
        },
    )
    selector = PromptVariantSelector(
        lambda prompt: '{"variant": "portrait"}'
    )
    name, variant = template.select_variant(
        {"headline": "Hello"},
        selector=selector,
    )
    assert name == "portrait"
    assert variant.profile == "instagram_portrait"
