"""Reusable template with variants, repeaters, fixtures, and serialization."""

from pathlib import Path

from postcanvas import LayoutNode, PreviewFixture, Template, TemplateVariant, Theme
from postcanvas.models import BackgroundConfig, LayoutPolicyConfig, PaddingConfig

OUT = Path("./output/examples/template")
OUT.mkdir(parents=True, exist_ok=True)

template = Template(
    name="metrics-editorial",
    version="1",
    default_variant="portrait",
    theme=Theme(
        colors={
            "text": "#FFFFFF",
            "muted": "#94A3B8",
            "accent": "#22D3EE",
            "surface": "#111827",
        },
        spacing={"sm": 16, "md": 28, "lg": 48},
        text_styles={
            "display": {
                "font_size": 92,
                "min_font_size": 38,
                "fit": "shrink",
                "overflow": "ellipsis",
                "wrap_mode": "balanced",
            }
        },
    ),
    variants={
        "portrait": TemplateVariant(
            profile="instagram_portrait",
            background=BackgroundConfig(color="#07111F"),
            required_slots=["headline"],
            max_chars_by_slot={"headline": 110},
            layout_policy=LayoutPolicyConfig(
                collision="error",
                safe_area="error",
                text_overflow="error",
            ),
            root=LayoutNode(
                kind="column",
                gap="md",
                padding=PaddingConfig.all(8),
                children=[
                    LayoutNode(
                        kind="text",
                        name="eyebrow",
                        basis=44,
                        color="#A78BFA",
                        font_size=22,
                    ),
                    LayoutNode(
                        kind="text",
                        name="headline",
                        grow=2,
                        text_style="display",
                        max_lines=4,
                    ),
                    LayoutNode(
                        kind="repeat",
                        repeat_from="metrics",
                        item_name="metric",
                        max_items=3,
                        repeat_direction="row",
                        basis=220,
                        gap="sm",
                        children=[
                            LayoutNode(
                                kind="column",
                                gap=8,
                                padding=PaddingConfig.all(18),
                                children=[
                                    LayoutNode(
                                        kind="text",
                                        name="metric.value",
                                        grow=1,
                                        font_size=44,
                                        min_font_size=28,
                                    ),
                                    LayoutNode(
                                        kind="text",
                                        name="metric.label",
                                        basis=28,
                                        font_size=18,
                                        color="#94A3B8",
                                    ),
                                ],
                            )
                        ],
                    ),
                    LayoutNode(
                        kind="text",
                        name="cta",
                        basis=70,
                        font_size=26,
                        color="#22D3EE",
                    ),
                ],
            ),
        ),
        "story": TemplateVariant(
            extends="portrait",
            profile="instagram_story",
            max_chars_by_slot={"headline": 85},
        ),
    },
    fixtures={
        "launch": PreviewFixture(
            variant="portrait",
            content={
                "eyebrow": "WEEKLY REPORT",
                "headline": "The content system is compounding.",
                "metrics": [
                    {"label": "Reach", "value": "1.2M"},
                    {"label": "Saves", "value": "42K"},
                    {"label": "CTR", "value": "7.4%"},
                ],
                "cta": "Read the full report →",
            },
        )
    },
)

template.to_file(OUT / "metrics-editorial.json")
for name, result in template.render_fixtures().items():
    result.images[0].save(OUT / f"{name}.png")
