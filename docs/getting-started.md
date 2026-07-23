# Getting started

## Requirements

- Python 3.10–3.13
- Pillow-compatible fonts for custom typography
- Network access only when you use remote image URLs

## Install

```bash
pip install postcanvas
```

Optional features:

```bash
pip install "postcanvas[yaml]"         # YAML templates
pip install "postcanvas[typography]"   # dictionary hyphenation
pip install "postcanvas[yaml,typography]"
```

## Your first image

```python
from postcanvas import generate
from postcanvas.models import BackgroundConfig, TextConfig
from postcanvas.presets import instagram_post

post = instagram_post(
    background=BackgroundConfig(color="#111827"),
    texts=[
        TextConfig(
            content="Hello, postcanvas.",
            x="50%",
            y="50%",
            width="82%",
            height="28%",
            anchor="center",
            font_size=90,
            min_font_size=36,
            fit="shrink",
            wrap_mode="balanced",
            color="#FFFFFF",
        )
    ],
    output_dir="./output",
    output_filename="hello",
)

paths = generate(post)
print(paths[0])
```

## Prefer `render()` for applications

`render()` always returns a structured `RenderResult`.

```python
from postcanvas import render

result = render(post)
image = result.images[0]
report = result.reports[0]

image.save("preview.png")
print(report.errors)
print(report.warnings)
```

## Output modes

```python
from postcanvas import generate

paths = generate(post, save=True, return_images=False)
images = generate(post, save=False, return_images=True)
both = generate(post, save=True, return_images=True)
```

| Arguments | Return value |
|---|---|
| `save=True, return_images=False` | list of output paths |
| `save=False, return_images=True` | list of PIL images |
| `save=True, return_images=True` | `GenerateResult` with paths, images and reports |

At least one output mode must be enabled.

## Choose a canvas

```python
from postcanvas.presets import (
    instagram_post,
    instagram_portrait,
    instagram_story,
    youtube_thumbnail,
)

square = instagram_post()
portrait = instagram_portrait()
story = instagram_story()
thumbnail = youtube_thumbnail()
```

Use `preset()` or `PostConfig` for custom sizes.

```python
from postcanvas.models import Platform, PostFormat
from postcanvas.presets import preset

custom = preset(
    Platform.CUSTOM,
    PostFormat.CUSTOM,
    width=1440,
    height=900,
)
```

## Add elements

Postcanvas renders shapes, images, tables, charts, and text in ascending `z_index`.

```python
from postcanvas.models import ImageElementConfig, ShapeConfig, ShapeType, TextConfig

post.shapes.append(
    ShapeConfig(
        type=ShapeType.ROUNDED_RECTANGLE,
        x="8%",
        y="10%",
        width="84%",
        height="80%",
        border_radius=36,
        fill_color="#1F2937",
        z_index=1,
    )
)

post.images.append(
    ImageElementConfig(
        src="assets/photo.jpg",
        x="50%",
        y="38%",
        width="76%",
        height="42%",
        anchor="center",
        fit="cover",
        focal_mode="auto",
        border_radius=28,
        z_index=5,
    )
)

post.texts.append(
    TextConfig(
        content="A complete composition",
        x="12%",
        y="68%",
        width="76%",
        height="16%",
        anchor="topleft",
        font_size=64,
        min_font_size=30,
        fit="shrink",
        z_index=10,
    )
)
```

## Add validation

```python
from postcanvas.models import LayoutPolicyConfig

post.layout_policy = LayoutPolicyConfig(
    collision="error",
    canvas_bounds="error",
    safe_area="error",
    exclusion_zones="error",
    text_overflow="error",
    contrast="warn",
    missing_fonts="error",
    file_size="warn",
)
```

Give important elements IDs and collision groups.

```python
TextConfig(
    id="headline",
    collision_group="content",
    content="No accidental overlap",
)
```

## Common project layout

```text
project/
├── assets/
│   ├── photos/
│   └── fonts/
├── templates/
│   └── launch.json
├── examples/
├── output/
└── render.py
```

## Next steps

- [Core concepts](concepts.md)
- [Typography](typography.md)
- [Templates](templates.md)
- [Validation](validation.md)
- [Examples](examples.md)
