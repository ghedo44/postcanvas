# Templates and responsive layout

Templates turn a brand system into a reusable content API. A `Template` contains theme tokens and named variants. Each variant maps content into a layout tree.

<p align="center">
  <img src="assets/template-pipeline.svg" alt="Template pipeline" width="100%">
</p>

## Theme tokens

```python
from postcanvas import Theme

theme = Theme(
    colors={
        "text": "#FFFFFF",
        "muted": "#94A3B8",
        "accent": "#A78BFA",
        "surface": "#111827",
    },
    fonts={
        "display": "assets/fonts/InterVariable.ttf",
        "body": "assets/fonts/NotoSans-Regular.ttf",
    },
    spacing={"xs": 8, "sm": 16, "md": 32, "lg": 56},
    text_styles={
        "display": {
            "font_role": "display",
            "font_size": 104,
            "min_font_size": 40,
            "fit": "shrink",
            "overflow": "ellipsis",
            "wrap_mode": "balanced",
            "widow_control": True,
        },
        "body": {
            "font_role": "body",
            "font_size": 34,
            "min_font_size": 24,
            "fit": "shrink",
        },
    },
)
```

## Layout node types

| Node | Purpose |
|---|---|
| `column` | vertical flow |
| `row` | horizontal flow |
| `grid` | equal cell grid |
| `overlay` | stack children in one box |
| `group` | logical container |
| `align` | align a child within a box |
| `safe_area` | constrain children to safe-area bounds |
| `conditional` | show content conditionally |
| `repeat` | generate children from a list |
| `text` | create a text element |
| `image` | create an image element |
| `shape` | create a shape |
| `spacer` | reserve flow space |

## Flow sizing

Children can use `basis` for a fixed main-axis size, `grow` for weighted remaining space, explicit width/height, aspect ratio, and parent gap/padding.

```python
LayoutNode(
    kind="column",
    gap="md",
    padding=PaddingConfig.all(24),
    children=[
        LayoutNode(kind="text", name="eyebrow", basis=52),
        LayoutNode(kind="text", name="headline", grow=2),
        LayoutNode(kind="image", name="hero", grow=3),
        LayoutNode(kind="text", name="cta", basis=82),
    ],
)
```

## Complete template

```python
from postcanvas import LayoutNode, Template, TemplateVariant
from postcanvas.models import BackgroundConfig, LayoutPolicyConfig

template = Template(
    name="editorial",
    version="1",
    theme=theme,
    default_variant="portrait",
    variants={
        "portrait": TemplateVariant(
            profile="instagram_portrait",
            background=BackgroundConfig(color="#0B1020"),
            required_slots=["headline"],
            max_chars_by_slot={"headline": 120},
            layout_policy=LayoutPolicyConfig(
                collision="error",
                safe_area="error",
                text_overflow="error",
            ),
            root=LayoutNode(
                kind="column",
                gap="md",
                children=[
                    LayoutNode(kind="text", name="eyebrow", basis=48, color="#C4B5FD"),
                    LayoutNode(
                        kind="text",
                        name="headline",
                        grow=2,
                        text_style="display",
                        max_lines=4,
                    ),
                    LayoutNode(
                        kind="image",
                        name="hero",
                        grow=3,
                        image_fit="cover",
                        focal_mode="auto",
                        border_radius=30,
                    ),
                ],
            ),
        ),
    },
)
```

## Build versus render

```python
post = template.build(content)
result = template.render(content)
```

`build()` returns a `PostConfig` that can be modified before rendering. `render()` builds and renders immediately.

## Conditions

```python
LayoutNode(
    kind="conditional",
    when_present="hero",
    children=[LayoutNode(kind="image", name="hero")],
)
```

Visibility controls include `when_present`, `when_absent`, and `hide_when_chars_over`.

## Repeaters

```python
LayoutNode(
    kind="repeat",
    repeat_from="metrics",
    item_name="metric",
    max_items=3,
    repeat_direction="row",
    gap="sm",
    children=[
        LayoutNode(
            kind="column",
            children=[
                LayoutNode(kind="text", name="metric.value", grow=1),
                LayoutNode(kind="text", name="metric.label", basis=34),
            ],
        )
    ],
)
```

Repeat directions: `column`, `row`, `grid`.

## Alignment

```python
LayoutNode(
    kind="align",
    horizontal_align="center",
    box_vertical_align="middle",
    width="70%",
    height="30%",
    children=[LayoutNode(kind="text", name="quote")],
)
```

## Safe-area roots

Variants default to `root_scope="safe_area"`. Use `root_scope="canvas"` only for intentional full-bleed composition.

```python
TemplateVariant(
    profile="instagram_story",
    root_scope="canvas",
    root=LayoutNode(
        kind="overlay",
        children=[
            LayoutNode(
                kind="image",
                name="background",
                respect_safe_area=False,
                respect_exclusion_zones=False,
            ),
            LayoutNode(kind="safe_area", children=[...]),
        ],
    ),
)
```

## Variant inheritance

```python
variants={
    "base": TemplateVariant(profile="instagram_portrait", root=base_root),
    "data-heavy": TemplateVariant(
        extends="base",
        required_slots=["metrics"],
        max_chars_by_slot={"headline": 80},
        root=data_root,
    ),
}
```

Inheritance merges required slots and character limits. Circular inheritance is rejected.

## Template inheritance

```python
campaign = campaign_template.inherit(brand_base_template)
```

Themes, variants, fixtures, and defaults are merged, with the child taking precedence.

## Automatic variant selection

Without a custom selector, Postcanvas scores eligible variants by required slots and character overflow.

```python
name, selected = template.select_variant(content)
name, selected = template.select_variant(content, variant="portrait")
```

See [assisted selection](assisted-selection.md) for custom selectors.

## Preview fixtures

```python
from postcanvas import PreviewFixture

template.fixtures["long-headline"] = PreviewFixture(
    variant="portrait",
    content={
        "headline": "A deliberately long headline used for regression testing",
        "hero": "assets/product.jpg",
    },
)

results = template.render_fixtures()
```

## JSON and YAML

```python
template.to_file("templates/editorial.json")
template = Template.from_file("templates/editorial.json")
```

YAML requires `pip install "postcanvas[yaml]"`.

## Template design checklist

- define required slots and realistic character limits
- include short, long, missing-media, and multilingual fixtures
- use a safe-area root for important content
- use repeaters with `max_items`
- use bounded text nodes
- enable strict validation for production variants
- keep decorative overlays outside collision groups
