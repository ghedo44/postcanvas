"""
Instagram Table Example
A metrics-focused Instagram post with a stylized table element.
"""

from postcanvas import generate
from postcanvas.presets import instagram_post
from postcanvas.models import (
    BackgroundConfig,
    GradientConfig,
    GradientStop,
    ShapeConfig,
    ShapeType,
    TableElementConfig,
    TextConfig,
)

post = instagram_post(
    text_font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
    background=BackgroundConfig(
        gradient=GradientConfig(
            type="linear",
            angle=132,
            stops=[
                GradientStop(color="#fff8f2", position=0.0),
                GradientStop(color="#ffe4d6", position=0.52),
                GradientStop(color="#ffd1bf", position=1.0),
            ],
        )
    ),
    texts=[
        TextConfig(
            content="WEEKLY PERFORMANCE SNAPSHOT",
            x="50%",
            y="9%",
            anchor="center",
            font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
            font_size=56,
            color="#0f172a",
            z_index=8,
        ),
        TextConfig(
            content="Share-ready table design for KPI updates",
            x="50%",
            y="16%",
            anchor="center",
            font_path="examples/assets/Roboto/static/Roboto-Medium.ttf",
            font_size=27,
            color="#334155",
            z_index=8,
        ),
    ],
    shapes=[
        ShapeConfig(
            type=ShapeType.ELLIPSE,
            x="16%",
            y="8%",
            width="34%",
            height="16%",
            anchor="center",
            fill_color="rgba(14,165,233,0.2)",
            z_index=1,
        ),
        ShapeConfig(
            type=ShapeType.ELLIPSE,
            x="84%",
            y="86%",
            width="34%",
            height="20%",
            anchor="center",
            fill_color="rgba(245,158,11,0.26)",
            z_index=1,
        ),
    ],
    tables=[
        TableElementConfig(
            x="50%",
            y="56%",
            width="88%",
            height="56%",
            anchor="center",
            headers=["Metric", "Week 1", "Week 2", "Week 3"],
            rows=[
                ["Reach", "28.4K", "31.1K", "36.8K"],
                ["Saves", "940", "1,106", "1,483"],
                ["Shares", "312", "401", "527"],
                ["Profile Visits", "2,450", "2,882", "3,204"],
                ["CTR", "2.4%", "2.8%", "3.1%"],
            ],
            column_widths=[0.4, 0.2, 0.2, 0.2],
            font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
            font_size=23,
            header_font_size=24,
            text_color="#0f172a",
            header_text_color="#f8fafc",
            background_color="rgba(248,250,252,0.92)",
            header_background_color="#0f172a",
            row_background_colors=[
                "rgba(241,245,249,0.85)",
                "rgba(226,232,240,0.85)",
            ],
            border_color="rgba(100,116,139,0.75)",
            border_width=2,
            grid_color="rgba(148,163,184,0.58)",
            grid_width=1,
            border_radius=20,
            cell_padding=16,
            z_index=6,
        )
    ],
    output_dir="./output/examples",
    output_filename="instagram_table_kpi",
)

if __name__ == "__main__":
    paths = generate(post)
    print("Generated:", paths)
