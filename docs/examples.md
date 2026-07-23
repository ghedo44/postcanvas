# Examples cookbook

Complete scripts live in [`../examples/`](../examples/). This page provides task-oriented recipes.

## Branded quote card

```python
post = instagram_post(
    background=BackgroundConfig(color="#111827"),
    shapes=[
        ShapeConfig(
            type="rounded_rectangle",
            x="50%",
            y="50%",
            width="86%",
            height="72%",
            anchor="center",
            fill_color="#1F2937",
            border_radius=36,
        )
    ],
    texts=[
        TextConfig(
            content="“Systems create consistency without killing creativity.”",
            x="50%",
            y="46%",
            width="74%",
            height="38%",
            anchor="center",
            font_size=70,
            min_font_size=30,
            fit="shrink",
            wrap_mode="balanced",
        ),
        TextConfig(
            content="POSTCANVAS 1.0",
            x="50%",
            y="78%",
            anchor="center",
            font_size=24,
            letter_spacing=4,
            color="#A78BFA",
        ),
    ],
)
```

## Photo headline card

```python
post = instagram_portrait(
    background=BackgroundConfig(color="#090B17"),
    images=[
        ImageElementConfig(
            src="assets/photo.jpg",
            x="50%",
            y="34%",
            width="88%",
            height="48%",
            anchor="center",
            fit="cover",
            focal_mode="auto",
            border_radius=30,
        )
    ],
    texts=[
        TextConfig(
            content="A headline that survives real content.",
            x="6%",
            y="65%",
            width="88%",
            height="24%",
            anchor="topleft",
            font_size=86,
            min_font_size=34,
            max_lines=4,
            fit="shrink",
            overflow="ellipsis",
            wrap_mode="balanced",
        )
    ],
)
```

## Chart post

```python
post.charts.append(
    ChartElementConfig(
        type="bar",
        title="Engagement by format",
        labels=["Reels", "Carousel", "Static"],
        series=[
            ChartSeriesConfig(name="Current", values=[8.9, 7.2, 4.1]),
            ChartSeriesConfig(name="Previous", values=[6.2, 5.8, 3.4]),
        ],
        x="50%",
        y="60%",
        width="88%",
        height="52%",
        anchor="center",
    )
)
```

## Validate without saving

```python
result = render(post, save=False)

for warning in result.warnings:
    print(warning.code, warning.message)
```

## Export WebP bytes

```python
image = render(post).images[0]
payload = image_to_bytes(image, format=OutputFormat.WEBP, quality=88)
```

## Build from a template

```python
template = Template.from_file("templates/editorial.json")
result = template.render(content)
```

## Full example list

- [`editorial_poster.py`](../examples/editorial_poster.py)
- [`data_dashboard.py`](../examples/data_dashboard.py)
- [`story_launch.py`](../examples/story_launch.py)
- [`carousel_system.py`](../examples/carousel_system.py)
- [`template_system.py`](../examples/template_system.py)
- [`rich_text.py`](../examples/rich_text.py)
- [`validation_report.py`](../examples/validation_report.py)
- [`platform_pack.py`](../examples/platform_pack.py)
- [`cloud_output.py`](../examples/cloud_output.py)
