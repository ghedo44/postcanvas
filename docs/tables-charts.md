# Tables and charts

## Tables

```python
from postcanvas.models import TableElementConfig, TextAlign

table = TableElementConfig(
    headers=["Metric", "Jan", "Feb", "Mar"],
    rows=[
        ["Reach", "28K", "31K", "37K"],
        ["Saves", "940", "1,106", "1,483"],
        ["CTR", "5.2%", "6.1%", "7.4%"],
    ],
    x="50%",
    y="58%",
    width="88%",
    height="48%",
    anchor="center",
    text_align=TextAlign.LEFT,
    column_alignments=[
        TextAlign.LEFT,
        TextAlign.CENTER,
        TextAlign.CENTER,
        TextAlign.CENTER,
    ],
    border_radius=24,
    header_background_color="#111827",
    background_color="rgba(255,255,255,0.94)",
)
```

## Alignment precedence

1. targeted `cell_alignments`
2. `column_alignments`
3. global `text_align`
4. `header_align` or `cell_align`

```python
from postcanvas.models import TableCellAlignmentConfig

table.cell_alignments = [
    TableCellAlignmentConfig(section="header", row=0, col=0, align="left"),
    TableCellAlignmentConfig(section="body", row=2, col=3, align="right"),
]
```

The table validates alignment list lengths and row/column bounds.

## Table sizing

- `column_widths` can define relative widths
- absent or invalid widths fall back to equal distribution
- `row_height` and `header_height` accept absolute or percentage dimensions
- rows are padded to the widest detected column count
- rounded corners clip inner fills and grid lines

## Bar charts

```python
from postcanvas.models import ChartElementConfig, ChartSeriesConfig, ChartType

chart = ChartElementConfig(
    type=ChartType.BAR,
    title="Engagement by format",
    labels=["Reels", "Carousel", "Static"],
    series=[
        ChartSeriesConfig(name="Current", values=[8.9, 7.2, 4.1], color="#22D3EE"),
        ChartSeriesConfig(name="Previous", values=[6.2, 5.8, 3.4], color="#8B5CF6"),
    ],
    x="50%",
    y="58%",
    width="90%",
    height="56%",
    anchor="center",
    bar_radius=10,
    show_legend=True,
)
```

## Line charts

```python
ChartElementConfig(
    type="line",
    title="Weekly growth",
    labels=["W1", "W2", "W3", "W4", "W5"],
    series=[
        ChartSeriesConfig(
            name="Reach",
            values=[22, 31, 28, 44, 57],
            color="#F472B6",
            line_width=5,
            point_radius=6,
        )
    ],
    min_value=0,
    grid_steps=5,
    show_points=True,
)
```

## Chart styling

Configure palette or per-series colors, grid and axes, chart/outer backgrounds, title and label typography, legend visibility, point/line size, grouped-bar spacing/radius, plot padding, borders, shadow, opacity, rotation, and blend mode.

## Data-visualization guidance

- use consistent units in labels
- start bar charts at zero unless truncation is explicit
- limit series count in social graphics
- use direct labels when possible
- validate contrast for text and data colors
- avoid overly dense tables on small canvases
