"""
Instagram Carousel Example
A 4-slide carousel with a sharp, modern visual system.
"""

from postcanvas import generate
from postcanvas.presets import instagram_post
from postcanvas.models import (
    CanvasConfig,
    BackgroundConfig,
    GradientConfig,
    GradientStop,
    ShapeConfig,
    ShapeType,
    TextConfig,
    ImageElementConfig,
    ImageFit,
)

base = dict(
    text_font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
    output_dir="./output/examples",
    output_filename="instagram_carousel_studio",
)

slides = [
    CanvasConfig(
        output_filename="instagram_carousel_studio_01",
        background=BackgroundConfig(
            gradient=GradientConfig(
                type="linear",
                angle=138,
                stops=[
                    GradientStop(color="#fffaf0", position=0.0),
                    GradientStop(color="#ffe4d6", position=0.55),
                    GradientStop(color="#ffd1bf", position=1.0),
                ],
            )
        ),
        shapes=[
            ShapeConfig(
                type=ShapeType.ELLIPSE,
                x="18%",
                y="16%",
                width="36%",
                height="18%",
                anchor="center",
                fill_color="rgba(14,165,233,0.2)",
                z_index=1,
            ),
            ShapeConfig(
                type=ShapeType.ELLIPSE,
                x="84%",
                y="86%",
                width="34%",
                height="18%",
                anchor="center",
                fill_color="rgba(245,158,11,0.22)",
                z_index=1,
            ),
            ShapeConfig(
                type=ShapeType.ROUNDED_RECTANGLE,
                x="50%",
                y="58%",
                width="88%",
                height="70%",
                anchor="center",
                fill_color="rgba(17, 24, 39, 0.9)",
                border_radius=32,
                z_index=2,
                texts=[
                    TextConfig(
                        content="THE BOLD FEED",
                        x="50%",
                        y="24%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                        font_size=74,
                        color="#f8fafc",
                        z_index=5,
                    ),
                    TextConfig(
                        content="4 moves for posts people actually stop on",
                        x="50%",
                        y="41%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Medium.ttf",
                        font_size=30,
                        color="#cbd5e1",
                        z_index=5,
                    ),
                    TextConfig(
                        content="Swipe 1/4",
                        x="50%",
                        y="84%",
                        anchor="center",
                        font_size=25,
                        color="#f59e0b",
                        z_index=5,
                    ),
                ],
            )
        ],
    ),
    CanvasConfig(
        output_filename="instagram_carousel_studio_02",
        text_font_path="examples/assets/Roboto/static/Roboto-Medium.ttf",
        background=BackgroundConfig(color="#fffdf8"),
        images=[
            ImageElementConfig(
                src="examples/assets/foo.jpg",
                x="64%",
                y="51%",
                width="64%",
                height="74%",
                fit=ImageFit.COVER,
                anchor="center",
                border_radius=26,
                z_index=2,
            )
        ],
        shapes=[
            ShapeConfig(
                type=ShapeType.ROUNDED_RECTANGLE,
                x="27%",
                y="51%",
                width="42%",
                height="65%",
                anchor="center",
                fill_color="#101828",
                border_radius=24,
                z_index=3,
                texts=[
                    TextConfig(
                        content="01",
                        x="50%",
                        y="16%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                        font_size=68,
                        color="#f59e0b",
                    ),
                    TextConfig(
                        content="Use contrast as structure, not decoration.",
                        x="50%",
                        y="52%",
                        anchor="center",
                        max_width="82%",
                        line_spacing=1.45,
                        font_size=29,
                        color="#e2e8f0",
                    ),
                ],
            )
        ],
        texts=[
            TextConfig(
                content="Slide 2/4",
                x="86%",
                y="95%",
                anchor="bottomright",
                font_size=22,
                color="#334155",
                z_index=6,
            ),
        ],
    ),
    CanvasConfig(
        output_filename="instagram_carousel_studio_03",
        background=BackgroundConfig(
            gradient=GradientConfig(
                type="linear",
                angle=110,
                stops=[
                    GradientStop(color="#0f172a", position=0.0),
                    GradientStop(color="#1d4ed8", position=0.52),
                    GradientStop(color="#0ea5e9", position=1.0),
                ],
            )
        ),
        shapes=[
            ShapeConfig(
                type=ShapeType.ROUNDED_RECTANGLE,
                x="28%",
                y="52%",
                width="40%",
                height="68%",
                anchor="center",
                fill_color="rgba(15,23,42,0.82)",
                border_radius=26,
                z_index=2,
                texts=[
                    TextConfig(
                        content="02",
                        x="50%",
                        y="18%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                        font_size=66,
                        color="#f8fafc",
                    ),
                    TextConfig(
                        content="Type rhythm",
                        x="50%",
                        y="38%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Bold.ttf",
                        font_size=34,
                        color="#93c5fd",
                    ),
                    TextConfig(
                        content="Pick one hero size, one support size, and one accent color.",
                        x="50%",
                        y="64%",
                        anchor="center",
                        max_width="82%",
                        line_spacing=1.35,
                        font_size=24,
                        color="#e2e8f0",
                    ),
                ],
            ),
            ShapeConfig(
                type=ShapeType.ROUNDED_RECTANGLE,
                x="72%",
                y="36%",
                width="38%",
                height="18%",
                anchor="center",
                fill_color="rgba(255,255,255,0.14)",
                border_radius=18,
                z_index=2,
                texts=[
                    TextConfig(
                        content="Hierarchy\nbeats clutter",
                        x="50%",
                        y="50%",
                        anchor="center",
                        line_spacing=1.2,
                        font_path="examples/assets/Roboto/static/Roboto-Bold.ttf",
                        font_size=28,
                        color="#f8fafc",
                    )
                ],
            ),
            ShapeConfig(
                type=ShapeType.ROUNDED_RECTANGLE,
                x="72%",
                y="62%",
                width="38%",
                height="18%",
                anchor="center",
                fill_color="rgba(15,23,42,0.7)",
                border_radius=18,
                z_index=2,
                texts=[
                    TextConfig(
                        content="Whitespace\ncreates pace",
                        x="50%",
                        y="50%",
                        anchor="center",
                        line_spacing=1.2,
                        font_path="examples/assets/Roboto/static/Roboto-Bold.ttf",
                        font_size=28,
                        color="#f8fafc",
                    )
                ],
            )
        ],
        texts=[
            TextConfig(
                content="Slide 3/4",
                x="86%",
                y="95%",
                anchor="bottomright",
                font_size=22,
                color="#e2e8f0",
                z_index=3,
            ),
        ],
    ),
    CanvasConfig(
        output_filename="instagram_carousel_studio_04",
        background=BackgroundConfig(color="#0a0a0a"),
        images=[
            ImageElementConfig(
                src="examples/assets/foo.jpg",
                x="50%",
                y="42%",
                width="92%",
                height="54%",
                fit=ImageFit.COVER,
                border_radius=22,
                anchor="center",
                opacity=0.84,
                z_index=1,
            )
        ],
        shapes=[
            ShapeConfig(
                type=ShapeType.ROUNDED_RECTANGLE,
                x="50%",
                y="80%",
                width="86%",
                height="24%",
                anchor="center",
                fill_color="rgba(15,23,42,0.88)",
                border_radius=24,
                z_index=3,
                texts=[
                    TextConfig(
                        content="03  BUILD A REPEATABLE SYSTEM",
                        x="50%",
                        y="34%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Bold.ttf",
                        font_size=34,
                        color="#f8fafc",
                    ),
                    TextConfig(
                        content="Define palette • type scale • layout rhythm",
                        x="50%",
                        y="56%",
                        anchor="center",
                        font_size=24,
                        color="#cbd5e1",
                    ),
                    TextConfig(
                        content="SAVE THIS  |  SHARE WITH YOUR TEAM",
                        x="50%",
                        y="80%",
                        anchor="center",
                        font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                        font_size=25,
                        color="#f59e0b",
                    ),
                ],
            )
        ],
        texts=[
            TextConfig(
                content="Slide 4/4",
                x="86%",
                y="95%",
                anchor="bottomright",
                font_size=22,
                color="#e2e8f0",
                z_index=4,
            )
        ],
    ),
]

post = instagram_post(canvases=slides, **base)

if __name__ == "__main__":
    paths = generate(post)
    print("Generated:")
    for path in paths:
        print(" -", path)
