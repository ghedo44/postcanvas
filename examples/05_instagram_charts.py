"""
Instagram Charts Example
A two-slide Instagram carousel with bar and line chart elements.
"""

from postcanvas import generate
from postcanvas.presets import instagram_post
from postcanvas.models import (
    CanvasConfig,
    BackgroundConfig,
    GradientConfig,
    GradientStop,
    ChartElementConfig,
    ChartSeriesConfig,
    ChartType,
    TextConfig,
)

slides = [
    CanvasConfig(
        output_filename="instagram_chart_bar",
        background=BackgroundConfig(
            gradient=GradientConfig(
                type="linear",
                angle=128,
                stops=[
                    GradientStop(color="#f8fafc", position=0.0),
                    GradientStop(color="#e2e8f0", position=0.56),
                    GradientStop(color="#cbd5e1", position=1.0),
                ],
            )
        ),
        texts=[
            TextConfig(
                content="CONTENT MIX PERFORMANCE",
                x="50%",
                y="9%",
                anchor="center",
                font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                font_size=52,
                color="#0f172a",
                z_index=9,
            ),
            TextConfig(
                content="Bar chart example",
                x="50%",
                y="16%",
                anchor="center",
                font_path="examples/assets/Roboto/static/Roboto-Medium.ttf",
                font_size=26,
                color="#334155",
                z_index=9,
            ),
        ],
        charts=[
            ChartElementConfig(
                type=ChartType.BAR,
                x="50%",
                y="57%",
                width="90%",
                height="62%",
                anchor="center",
                title="Engagement by Format",
                labels=["Reels", "Carousels", "Static", "Stories"],
                series=[
                    ChartSeriesConfig(name="Current", values=[8.9, 7.2, 4.1, 3.7], color="#0ea5e9"),
                    ChartSeriesConfig(name="Previous", values=[6.2, 5.8, 3.4, 2.9], color="#334155"),
                ],
                min_value=0.0,
                max_value=10.0,
                grid_steps=5,
                font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
                title_font_size=30,
                font_size=18,
                label_color="#334155",
                title_color="#0f172a",
                background_color="rgba(255,255,255,0.86)",
                chart_background_color="rgba(248,250,252,0.78)",
                axis_color="#475569",
                grid_color="rgba(148,163,184,0.35)",
                border_color="rgba(148,163,184,0.72)",
                border_width=2,
                border_radius=18,
                bar_group_padding=0.28,
                bar_radius=7,
                z_index=7,
            )
        ],
    ),
    CanvasConfig(
        output_filename="instagram_chart_line",
        background=BackgroundConfig(
            gradient=GradientConfig(
                type="linear",
                angle=142,
                stops=[
                    GradientStop(color="#0f172a", position=0.0),
                    GradientStop(color="#1e3a8a", position=0.5),
                    GradientStop(color="#0ea5e9", position=1.0),
                ],
            )
        ),
        texts=[
            TextConfig(
                content="AUDIENCE GROWTH TREND",
                x="50%",
                y="9%",
                anchor="center",
                font_path="examples/assets/Roboto/static/Roboto-Black.ttf",
                font_size=52,
                color="#f8fafc",
                z_index=9,
            ),
            TextConfig(
                content="Line chart example",
                x="50%",
                y="16%",
                anchor="center",
                font_path="examples/assets/Roboto/static/Roboto-Medium.ttf",
                font_size=26,
                color="#bfdbfe",
                z_index=9,
            ),
        ],
        charts=[
            ChartElementConfig(
                type=ChartType.LINE,
                x="50%",
                y="57%",
                width="90%",
                height="62%",
                anchor="center",
                title="Followers and Saves (8 Weeks)",
                labels=["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
                series=[
                    ChartSeriesConfig(
                        name="Followers",
                        values=[2.1, 2.5, 2.8, 3.2, 3.6, 3.9, 4.3, 4.8],
                        color="#22d3ee",
                        line_width=4,
                        point_radius=4,
                    ),
                    ChartSeriesConfig(
                        name="Saves",
                        values=[0.6, 0.8, 1.1, 1.0, 1.4, 1.7, 1.9, 2.2],
                        color="#f59e0b",
                        line_width=3,
                        point_radius=4,
                    ),
                ],
                min_value=0.0,
                max_value=5.0,
                grid_steps=5,
                font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
                title_font_size=30,
                font_size=18,
                label_color="#dbeafe",
                title_color="#ffffff",
                background_color="rgba(15,23,42,0.72)",
                chart_background_color="rgba(15,23,42,0.64)",
                axis_color="#93c5fd",
                grid_color="rgba(191,219,254,0.24)",
                border_color="rgba(147,197,253,0.62)",
                border_width=2,
                border_radius=18,
                show_points=True,
                line_width=4,
                point_radius=4,
                z_index=7,
            )
        ],
    ),
]

post = instagram_post(
    text_font_path="examples/assets/Roboto/static/Roboto-Regular.ttf",
    canvases=slides,
    output_dir="./output/examples",
    output_filename="instagram_chart",
)

if __name__ == "__main__":
    paths = generate(post, save=True, return_images=False)
    print("Generated:")
    for path in paths:
        print(" -", path)
