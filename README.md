# postcanvas 🎨

> Generate pixel-perfect social-media images from Python — just describe what you want.

## Install

```bash
pip install postcanvas
```

## Documentation

- docs/README.md
- docs/getting-started.md
- docs/config-reference.md
- docs/renderer-architecture.md
- docs/examples.md

## Quick start

```python
from postcanvas import generate
from postcanvas.presets import instagram_post
from postcanvas.models import BackgroundConfig, TextConfig, ShadowConfig

post = instagram_post(
    background=BackgroundConfig(color="#1a1a2e"),
    texts=[
        TextConfig(
            content="Hello World!",
            y="50%",
            font_size=96,
            color="#e94560",
            shadow=ShadowConfig(blur_radius=12),
        )
    ],
    output_dir="./output",
)

generate(post)   # → ./output/post.png
```

## Cloud Storage & Return Raw Images

Generate images without saving to disk for direct cloud uploads:

```python
from postcanvas import generate, image_to_bytes, GenerateResult
from postcanvas.models import OutputFormat

# Get raw PIL Images without saving to disk
images = generate(post, save=False, return_images=True)

# Convert to bytes for cloud storage
for img in images:
    data = image_to_bytes(img, format=OutputFormat.PNG)
    # s3_client.put_object(Bucket='bucket', Key='image.png', Body=data)

# Or save to custom locations
from postcanvas import save_image_to_path
save_image_to_path(images[0], "./custom/path/image.png")

# Get both: save locally AND return images
result = generate(post, save=True, return_images=True)  # Returns GenerateResult
print(result.paths)    # List of saved file paths
print(result.images)   # List of PIL Image objects
```

### Generate Parameters & Return Types

```python
generate(
    post,
    save=True,              # Save to disk
    return_images=False     # Return PIL Image objects
)
```

**Return types:**
- `save=True, return_images=False` (default) → `List[str]` (file paths only)
- `save=False, return_images=True` → `List[Image.Image]` (PIL Images only)
- `save=True, return_images=True` → `GenerateResult` (consistent dataclass with both)

**Error handling:**
- `save=False, return_images=False` → raises `ValueError` (must specify at least one output type)

## Platforms & formats

| Helper | Size |
|---|---|
| `instagram_post()` | 1080 × 1080 |
| `instagram_portrait()` | 1080 × 1350 |
| `instagram_story()` | 1080 × 1920 |
| `x_post()` | 1600 × 900 |
| `reddit_post()` | 1920 × 1080 |
| `blog_og()` | 1200 × 628 |
| `linkedin_post()` | 1080 × 1080 |
| `youtube_thumbnail()` | 1280 × 720 |
| `facebook_post()` | 1080 × 1080 |
| `tiktok_story()` | 1080 × 1920 |

Use `preset(Platform.CUSTOM, PostFormat.CUSTOM, width=800, height=600)` for custom sizes.

## Carousel / multi-image

```python
from postcanvas.models import CanvasConfig, BackgroundConfig

post = instagram_post(
    canvases=[
        CanvasConfig(background=BackgroundConfig(color="#e94560"),
                     texts=[TextConfig(content="Slide 1", ...)]),
        CanvasConfig(background=BackgroundConfig(color="#0f3460"),
                     texts=[TextConfig(content="Slide 2", ...)]),
    ]
)
```

## Key model reference

### `PostConfig` (root)
| Field | Type | Description |
|---|---|---|
| `platform` | `Platform` | Target platform |
| `width` / `height` | `int` | Canvas size in px |
| `background` | `BackgroundConfig` | Global background |
| `padding` | `PaddingConfig` | Safe-area insets |
| `texts` | `List[TextConfig]` | Global text elements |
| `images` | `List[ImageElementConfig]` | Global image elements |
| `shapes` | `List[ShapeConfig]` | Global shapes |
| `tables` | `List[TableElementConfig]` | Global table elements |
| `charts` | `List[ChartElementConfig]` | Global chart elements |
| `canvases` | `List[CanvasConfig]` | Slides (carousel) |
| `watermark` | `WatermarkConfig` | Applied to every slide |
| `output_dir` | `str` | Where to save files |
| `output_format` | `OutputFormat` | `png` / `jpeg` / `webp` |

### Positioning
Every `x`, `y`, `width`, `height` accepts:
- **Absolute pixels**: `540`, `200`
- **Relative string**: `"50%"`, `"80%"`

### Anchors
`anchor` can be: `topleft`, `topcenter`, `topright`, `left`, `center`,
`right`, `bottomleft`, `bottomcenter`, `bottomright`

### z_index
Elements are composited in ascending `z_index` order across all types
(shapes, images, tables, charts, texts).
Default values: shapes=1, images=5, tables=6, charts=7, texts=10.

### Tables and charts

```python
from postcanvas.models import (
    TextAlign,
    TableCellAlignmentConfig,
    TableElementConfig,
    ChartElementConfig,
    ChartSeriesConfig,
    ChartType,
)

tables = [
    TableElementConfig(
        headers=["Metric", "Jan", "Feb", "Mar"],
        rows=[
            ["Reach", "28K", "31K", "37K"],
            ["Saves", "940", "1106", "1483"],
        ],
        text_align=TextAlign.LEFT,
        column_alignments=[TextAlign.LEFT, TextAlign.CENTER, TextAlign.CENTER, TextAlign.CENTER],
        cell_alignments=[
            TableCellAlignmentConfig(section="header", row=0, col=0, align=TextAlign.LEFT),
            TableCellAlignmentConfig(section="body", row=1, col=3, align=TextAlign.RIGHT),
        ],
        x="50%", y="56%", width="88%", height="52%", anchor="center",
    )
]

charts = [
    ChartElementConfig(
        type=ChartType.BAR,
        labels=["Reels", "Carousel", "Static"],
        series=[
            ChartSeriesConfig(name="Current", values=[8.9, 7.2, 4.1]),
            ChartSeriesConfig(name="Previous", values=[6.2, 5.8, 3.4]),
        ],
        x="50%", y="56%", width="90%", height="60%", anchor="center",
    )
]
```

Supported chart types: `ChartType.BAR` and `ChartType.LINE`.

### Text inside images and shapes
Both `ImageElementConfig` and `ShapeConfig` now support a `texts` list:

```python
from postcanvas.models import ImageElementConfig, ShapeConfig, ShapeType, TextConfig

ShapeConfig(
    type=ShapeType.ROUNDED_RECTANGLE,
    x="50%", y="35%", width="70%", height="30%", anchor="center",
    fill_color="#1f3b4d",
    texts=[
        TextConfig(content="Inside Shape", x="50%", y="50%", anchor="center")
    ],
)

ImageElementConfig(
    src="assets/photo.jpg",
    x="50%", y="70%", width="60%", height="35%", anchor="center",
    texts=[
        TextConfig(content="Inside Image", x="50%", y="88%", anchor="bottomcenter")
    ],
)
```

Nested text coordinates are resolved relative to the element's own box, not the full canvas.

### Font inheritance (Post > Canvas > Text override)
You can define default text font at post level, override it per canvas, and still override per text:

```python
from postcanvas.presets import instagram_post
from postcanvas.models import CanvasConfig, TextConfig

post = instagram_post(
    text_font_path="Roboto/static/Roboto-Regular.ttf",   # default for whole post
    texts=[
        TextConfig(content="Uses post default", x="50%", y="15%"),
        TextConfig(content="Custom text font", x="50%", y="25%", font_path="Roboto/static/Roboto-Bold.ttf"),
    ],
    canvases=[
        CanvasConfig(
            text_font_path="Roboto/static/Roboto-Italic.ttf",  # overrides post default on this slide
            texts=[
                TextConfig(content="Uses canvas override", x="50%", y="50%"),
                TextConfig(content="Text-level still wins", x="50%", y="60%", font_path="Roboto/static/Roboto-Medium.ttf"),
            ],
        )
    ],
)
```

Precedence: `TextConfig` > `CanvasConfig` > `PostConfig` > internal Arial fallback.
