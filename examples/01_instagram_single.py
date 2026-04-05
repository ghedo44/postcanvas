"""
Instagram Single Post Example
A bold editorial Instagram poster.
"""

from postcanvas import generate
from postcanvas.models.enums import TextAlign
from postcanvas.presets import instagram_post
from postcanvas.models import (
    BackgroundConfig,
    GradientConfig,
    GradientStop,
    ShapeConfig,
    ShapeType,
    TextConfig,
    ImageElementConfig,
    ImageFit,
)
 

post = instagram_post(
    text_font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
    background=BackgroundConfig(
        gradient=GradientConfig(
            type="linear",
            angle=132,
            stops=[
                GradientStop(color="#fff7ed", position=0.0),
                GradientStop(color="#ffe7d6", position=0.48),
                GradientStop(color="#ffd5c2", position=1.0),
            ],
        )
    ),
    texts=[
        TextConfig(
            content="EDITORIAL DROP",
            x="10%",
            y="8%",
            anchor="topleft",
            font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
            font_size=58,
            color="#111827",
            z_index=8,
        ),
        TextConfig(
            content="Visual storytelling for creators who want punch, not noise.",
            x="10%",
            y="18%",
            anchor="topleft",
            max_width="68%",
            line_spacing=1.3,
            align=TextAlign.LEFT,
            font_path="examples/assets/Roboto/static/Roboto-Mono.ttf",
            font_size=50,
            # color="#334155",
            auto_contrast=True,
            contrast_light_color="#FFFFFF",  # used on dark bg
            contrast_dark_color="#111111",   # used on light bg
            contrast_threshold=145,          # higher => switches to dark sooner
            z_index=8,
        ),
    ],
    images=[
        ImageElementConfig(
            src="examples/assets/foo.jpg",
            x="66%",
            y="52%",
            width="56%",
            height="72%",
            fit=ImageFit.COVER,
            border_radius=30,
            anchor="center",
            opacity=0.94,
            z_index=4,
            texts=[
                TextConfig(
                    content="WILD / REFINED",
                    x="8%",
                    y="92%",
                    anchor="bottomleft",
                    font_path="examples/assets/Roboto/static/Roboto-Bold.ttf",
                    font_size=30,
                    color="#f8fafc",
                    background_color="rgba(15, 23, 42, 0.58)",
                    background_padding=8,
                    background_radius=12,
                    z_index=3,
                )
            ],
        )
    ],
    shapes=[
        ShapeConfig(
            type=ShapeType.ELLIPSE,
            x="5%",
            y="-6%",
            width="40%",
            height="22%",
            anchor="topleft",
            fill_color="rgba(14, 165, 233, 0.22)",
            z_index=1,
        ),
        ShapeConfig(
            type=ShapeType.ELLIPSE,
            x="64%",
            y="86%",
            width="42%",
            height="20%",
            anchor="center",
            fill_color="rgba(245, 158, 11, 0.26)",
            z_index=2,
        ),
        ShapeConfig(
            type=ShapeType.ROUNDED_RECTANGLE,
            x="25%",
            y="54%",
            width="34%",
            height="42%",
            anchor="center",
            fill_color="rgba(17, 24, 39, 0.9)",
            border_radius=24,
            z_index=5,
            texts=[
                TextConfig(
                    content="01",
                    x="14%",
                    y="16%",
                    anchor="topleft",
                    font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                    font_size=52,
                    color="#f59e0b",
                    z_index=2,
                ),
                TextConfig(
                    content="Strong contrast",
                    x="50%",
                    y="36%",
                    anchor="center",
                    font_path="examples/assets/Roboto/static/Roboto-Medium.ttf",
                    font_size=25,
                    color="#f8fafc",
                    z_index=2,
                ),
                TextConfig(
                    content="Purposeful spacing",
                    x="50%",
                    y="52%",
                    anchor="center",
                    font_size=25,
                    color="#f8fafc",
                    z_index=2,
                ),
                TextConfig(
                    content="One clear call-to-action",
                    x="50%",
                    y="68%",
                    anchor="center",
                    max_width="84%",
                    font_size=23,
                    color="#f8fafc",
                    z_index=2,
                ),
            ],
        ),
        ShapeConfig(
            type=ShapeType.ROUNDED_RECTANGLE,
            x="50%",
            y="93%",
            width="76%",
            height="9%",
            anchor="center",
            fill_color="#111827",
            border_radius=14,
            z_index=9,
            texts=[
                TextConfig(
                    content="SAVE THIS LAYOUT • POST TODAY",
                    x="50%",
                    y="54%",
                    anchor="center",
                    font_path="examples/assets/Roboto/static/Roboto-Bold.ttf",
                    font_size=24,
                    color="#f8fafc",
                )
            ],
        ),
    ],
    output_dir="./output/examples",
    output_filename="instagram_single_nightfall",
)

if __name__ == "__main__":
    paths = generate(post)
    print("Generated:", paths)
