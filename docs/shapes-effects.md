# Shapes, effects and compositing

## Shape types

Postcanvas supports rectangle, rounded rectangle, circle, ellipse, line, triangle, polygon, and star.

```python
from postcanvas.models import ShapeConfig, ShapeType

ShapeConfig(
    type=ShapeType.ROUNDED_RECTANGLE,
    x="50%",
    y="50%",
    width="82%",
    height="36%",
    anchor="center",
    fill_color="#111827",
    border_radius=32,
)
```

## Gradient fills

```python
ShapeConfig(
    type="rounded_rectangle",
    fill_gradient=GradientConfig(
        type="linear",
        angle=30,
        stops=[
            GradientStop(color="#8B5CF6", position=0),
            GradientStop(color="#EC4899", position=1),
        ],
    ),
)
```

## Strokes and shadows

```python
ShapeConfig(
    type="circle",
    x="75%",
    y="22%",
    width=240,
    height=240,
    anchor="center",
    fill_color="#FBBF24",
    stroke_color="#FFFFFF",
    stroke_width=5,
    shadow=ShadowConfig(offset_y=16, blur_radius=28),
)
```

## Polygons and stars

```python
ShapeConfig(
    type="polygon",
    points=[(0, 80), (120, 0), (240, 80), (180, 220), (60, 220)],
    fill_color="#22D3EE",
)
```

```python
ShapeConfig(
    type="star",
    star_points=7,
    star_inner_r=0.46,
    fill_color="#F472B6",
)
```

## Nested text

```python
ShapeConfig(
    type="rounded_rectangle",
    x="50%",
    y="75%",
    width="84%",
    height="16%",
    anchor="center",
    fill_color="#FFFFFF",
    texts=[
        TextConfig(
            content="Read the report →",
            x="8%",
            y="50%",
            width="84%",
            anchor="left",
            color="#111827",
            font_size=34,
        )
    ],
)
```

## Blend modes

Available values: normal, multiply, screen, overlay, darken, lighten, difference, and exclusion.

```python
ShapeConfig(fill_color="#EC4899", opacity=0.72, blend_mode="screen")
```

## Rotation and opacity

```python
ShapeConfig(rotation=8, opacity=0.86)
```

## Canvas filters

```python
post.canvas_filters = [
    FilterConfig(type="vignette", value=0.2),
]
```

## Watermarks

```python
from postcanvas.models import WatermarkConfig

post.watermark = WatermarkConfig(
    text="@brand",
    position="bottom_right",
    opacity=0.5,
)
```

## Compositing advice

- reserve low z-index values for backgrounds and decoration
- keep content images around 5
- place data elements around 6–7
- keep text at 10 or above
- use collision groups only for elements that must not overlap
- omit collision groups for intentional ambient decoration
