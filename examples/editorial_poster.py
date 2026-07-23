"""Responsive editorial poster with strict layout validation."""

from postcanvas import render
from postcanvas.models import (
    BackgroundConfig,
    GradientConfig,
    GradientStop,
    LayoutPolicyConfig,
    ShadowConfig,
    ShapeConfig,
    ShapeType,
    TextConfig,
)
from postcanvas.presets import instagram_portrait

post = instagram_portrait(
    background=BackgroundConfig(
        gradient=GradientConfig(
            type="linear",
            angle=140,
            stops=[
                GradientStop(color="#080B16", position=0),
                GradientStop(color="#21103D", position=0.58),
                GradientStop(color="#073044", position=1),
            ],
        )
    ),
    layout_policy=LayoutPolicyConfig(
        collision="error",
        canvas_bounds="error",
        safe_area="error",
        text_overflow="error",
        contrast="warn",
    ),
    shapes=[
        ShapeConfig(
            type=ShapeType.CIRCLE,
            x="78%", y="23%", width=420, height=420,
            anchor="center", fill_color="#FB7185", opacity=0.92,
            z_index=1,
        ),
        ShapeConfig(
            type=ShapeType.CIRCLE,
            x="78%", y="23%", width=280, height=280,
            anchor="center", fill_color="#FBBF24", opacity=0.58,
            z_index=2,
        ),
        ShapeConfig(
            id="cta-card",
            collision_group="content",
            type=ShapeType.ROUNDED_RECTANGLE,
            x="8%", y="79%", width="84%", height="12%",
            anchor="topleft", fill_color="#FFFFFF", border_radius=28,
            shadow=ShadowConfig(color="rgba(0,0,0,0.25)", offset_y=16, blur_radius=28),
            z_index=3,
            texts=[
                TextConfig(
                    content="Explore the 1.0 documentation →",
                    x="7%", y="50%", width="86%", height="60%",
                    anchor="left", font_size=32, min_font_size=22,
                    fit="shrink", color="#111827", align="left",
                )
            ],
        ),
    ],
    texts=[
        TextConfig(
            id="eyebrow", collision_group="content",
            content="POSTCANVAS / EDITORIAL",
            x="8%", y="9%", width="58%", height="6%",
            anchor="topleft", font_size=24, min_font_size=18,
            fit="shrink", letter_spacing=4, color="#C4B5FD", align="left",
        ),
        TextConfig(
            id="headline", collision_group="content",
            content="DESIGN\nTHAT\nADAPTS.",
            x="8%", y="31%", width="84%", height="38%",
            anchor="topleft", font_size=112, min_font_size=48,
            max_lines=4, fit="shrink", overflow="error",
            wrap_mode="balanced", align="left", color="#FFFFFF",
        ),
    ],
    output_dir="./output/examples/editorial",
    output_filename="editorial-poster",
)

result = render(post, save=True)
print(result.paths)
print(result.reports[0].issues)
