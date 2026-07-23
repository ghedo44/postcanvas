# Responsive templates and layout validation

Postcanvas 0.3 introduces bounded text, flow-based templates, platform safe areas,
collision diagnostics, and focal-point image cropping.

## Bounded text

```python
TextConfig(
    content=headline,
    width="84%",
    height="30%",
    font_size=96,
    min_font_size=36,
    max_lines=4,
    fit="shrink",
    overflow="ellipsis",
    wrap_mode="balanced",
)
```

Text is measured before drawing. Explicit newlines are retained, oversized tokens
are split, and font size is selected with a binary search.

## Layout validation

Assign IDs and a collision group to elements that must not overlap:

```python
post = instagram_portrait(
    layout_policy=LayoutPolicyConfig(collision="error", safe_area="error"),
    texts=[
        TextConfig(id="title", collision_group="content", ...),
        TextConfig(id="footer", collision_group="content", ...),
    ],
)

reports = validate_post(post)
```

Background shapes and intentional overlays can omit `collision_group`, or declare
`allow_overlap_with=["element-id"]`.

## Flow templates

```python
from postcanvas import LayoutNode, Template, TemplateVariant

template = Template(
    name="editorial",
    variants={
        "portrait": TemplateVariant(
            profile="instagram_portrait",
            root=LayoutNode(
                kind="column",
                gap=32,
                children=[
                    LayoutNode(
                        kind="text",
                        name="headline",
                        grow=2,
                        font_size=96,
                        min_font_size=36,
                        max_lines=4,
                    ),
                    LayoutNode(kind="image", name="hero", grow=3),
                    LayoutNode(kind="text", name="footer", basis=80),
                ],
            ),
        )
    },
)

result = template.render(
    {"headline": "Variable-length content", "hero": "photo.jpg", "footer": "@brand"}
)
```

Supported layout nodes are `column`, `row`, `grid`, `overlay`, `text`, `image`,
`shape`, and `spacer`. Templates can be stored as JSON. YAML loading and writing is
available with `pip install postcanvas[yaml]`.

## Platform profiles

`get_profile()` returns canvas dimensions, conservative safe-area insets, and
optional crop metadata. Available helpers include `instagram_reel_cover()` in
addition to the existing feed and Story helpers.
