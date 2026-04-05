# Getting Started

## Install

```bash
pip install postcanvas
```

For local development from the repository root:

```bash
pip install -e .
```

## Minimal Example

```python
from postcanvas import generate
from postcanvas.presets import instagram_post
from postcanvas.models import BackgroundConfig, TextConfig

post = instagram_post(
    background=BackgroundConfig(color="#0f172a"),
    texts=[
        TextConfig(
            content="Hello postcanvas",
            x="50%",
            y="50%",
            anchor="center",
            font_size=84,
            color="#f8fafc",
        )
    ],
    output_dir="./output",
    output_filename="hello",
)

paths = generate(post)
print(paths)
```

## Return Types from `generate`

`generate(post, save=True, return_images=False)` is the default and returns file paths.

- `save=True, return_images=False` -> `List[str]`
- `save=False, return_images=True` -> `List[PIL.Image.Image]`
- `save=True, return_images=True` -> `GenerateResult` (with `.paths` and `.images`)

## Coordinates and Sizing

Most element positions and dimensions accept either:

- absolute pixels (e.g. `320`)
- percentage strings (e.g. `"50%"`)

This allows layouts to stay proportional when you change output sizes.

## Common Workflow

1. Pick a preset size from `postcanvas.presets`
2. Define global background and reusable elements
3. Add per-slide overrides in `CanvasConfig` when building a carousel
4. Tune element `z_index` for compositing order
5. Render with `generate` and inspect output files

## New in This Version

- Native table element support via `TableElementConfig`
- Native chart element support via `ChartElementConfig`
  - `ChartType.BAR`
  - `ChartType.LINE`
