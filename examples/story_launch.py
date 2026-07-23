"""Story launch graphic with exclusion-zone-aware content."""

from postcanvas import render
from postcanvas.models import BackgroundConfig, LayoutPolicyConfig, ShapeConfig, ShapeType, TextConfig
from postcanvas.presets import instagram_story

post = instagram_story(
    background=BackgroundConfig(color="#090B16"),
    layout_policy=LayoutPolicyConfig(
        collision="error",
        canvas_bounds="error",
        safe_area="error",
        exclusion_zones="error",
        text_overflow="error",
    ),
    shapes=[
        ShapeConfig(
            type=ShapeType.CIRCLE,
            x="72%", y="20%", width=720, height=720,
            anchor="center", fill_color="#7C3AED",
            respect_safe_area=False, respect_exclusion_zones=False,
        ),
        ShapeConfig(
            type=ShapeType.CIRCLE,
            x="72%", y="20%", width=480, height=480,
            anchor="center", fill_color="#EC4899", opacity=0.68,
            respect_safe_area=False, respect_exclusion_zones=False,
            z_index=2,
        ),
        ShapeConfig(
            id="cta", collision_group="content",
            type=ShapeType.ROUNDED_RECTANGLE,
            x="8%", y="72%", width="84%", height="10%",
            anchor="topleft", fill_color="#FFFFFF", border_radius=32,
            texts=[
                TextConfig(
                    content="Join early access →",
                    x="8%", y="50%", width="84%", anchor="left",
                    font_size=38, min_font_size=26, fit="shrink",
                    color="#111827", align="left",
                )
            ],
        ),
    ],
    texts=[
        TextConfig(
            id="headline", collision_group="content",
            content="THE NEXT\nCHAPTER\nSTARTS.",
            x="8%", y="36%", width="84%", height="28%",
            anchor="topleft", font_size=116, min_font_size=52,
            fit="shrink", overflow="error", max_lines=4, align="left",
        ),
        TextConfig(
            id="subhead", collision_group="content",
            content="Designed once. Adapted everywhere.",
            x="8%", y="66%", width="84%", height="5%",
            anchor="topleft", font_size=30, min_font_size=22,
            fit="shrink", color="#CBD5E1", align="left",
        ),
    ],
    output_dir="./output/examples/story",
    output_filename="story-launch",
)

result = render(post, save=True)
print(result.paths)
