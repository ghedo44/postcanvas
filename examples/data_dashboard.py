"""Data-rich social dashboard with cards, table and chart."""

from postcanvas import render
from postcanvas.models import (
    BackgroundConfig,
    ChartElementConfig,
    ChartSeriesConfig,
    ChartType,
    LayoutPolicyConfig,
    ShapeConfig,
    ShapeType,
    TableElementConfig,
    TextAlign,
    TextConfig,
)
from postcanvas.presets import instagram_post


def metric_card(x: str, label: str, value: str, color: str) -> ShapeConfig:
    return ShapeConfig(
        type=ShapeType.ROUNDED_RECTANGLE,
        x=x,
        y="23%",
        width="27%",
        height="17%",
        anchor="center",
        fill_color="#111827",
        border_radius=24,
        texts=[
            TextConfig(
                content=label,
                x="9%", y="22%", width="82%", anchor="topleft",
                font_size=18, color="#94A3B8", align="left",
            ),
            TextConfig(
                content=value,
                x="9%", y="52%", width="82%", height="36%",
                anchor="topleft", font_size=46, min_font_size=28,
                fit="shrink", color=color, align="left",
            ),
        ],
    )


post = instagram_post(
    background=BackgroundConfig(color="#07111F"),
    layout_policy=LayoutPolicyConfig(
        canvas_bounds="error",
        safe_area="error",
        text_overflow="error",
        contrast="warn",
        file_size="warn",
    ),
    shapes=[
        metric_card("18%", "REACH", "1.28M", "#FFFFFF"),
        metric_card("50%", "SAVES", "42.6K", "#A78BFA"),
        metric_card("82%", "CTR", "7.4%", "#22D3EE"),
    ],
    texts=[
        TextConfig(
            content="SOCIAL PERFORMANCE",
            x="7%", y="6%", width="86%", anchor="topleft",
            font_size=22, letter_spacing=4, color="#93C5FD", align="left",
        )
    ],
    charts=[
        ChartElementConfig(
            type=ChartType.BAR,
            title="Engagement by format",
            labels=["Reels", "Carousel", "Static"],
            series=[
                ChartSeriesConfig(name="Current", values=[8.9, 7.2, 4.1], color="#22D3EE"),
                ChartSeriesConfig(name="Previous", values=[6.2, 5.8, 3.4], color="#8B5CF6"),
            ],
            x="50%", y="57%", width="88%", height="42%", anchor="center",
            background_color="#111827", chart_background_color="#0B1324",
            title_color="#FFFFFF", label_color="#CBD5E1",
            axis_color="#64748B", grid_color="rgba(148,163,184,0.22)",
            border_color="rgba(148,163,184,0.18)", border_radius=26,
            show_legend=True,
        )
    ],
    tables=[
        TableElementConfig(
            headers=["Metric", "W1", "W2", "W3"],
            rows=[
                ["Reach", "920K", "1.08M", "1.28M"],
                ["Saves", "31K", "37K", "42.6K"],
            ],
            x="50%", y="86%", width="88%", height="17%", anchor="center",
            text_align=TextAlign.LEFT,
            column_alignments=[
                TextAlign.LEFT, TextAlign.CENTER, TextAlign.CENTER, TextAlign.CENTER,
            ],
            font_size=16, header_font_size=17,
            background_color="#F8FAFC", header_background_color="#1E293B",
            border_radius=20,
        )
    ],
    output_dir="./output/examples/dashboard",
    output_filename="analytics-dashboard",
)

result = render(post, save=True)
print(result.paths)
