# Core concepts

## Post, canvas and element

A `PostConfig` is the root render request. A post can represent one image or a carousel.

- Post-level elements are global defaults.
- Each `CanvasConfig` represents one slide.
- Canvas values can inherit, merge with, or replace post-level values.
- Every render produces one image and one layout report per slide.

## Dimensions

Most geometry fields accept integers or floats for absolute pixels and percentage strings such as `"50%"`.

```python
TextConfig(x="8%", y=120, width="84%", height=360)
```

Percentages are resolved against the current canvas or containing layout box.

## Anchors

An anchor controls which point of an element is placed at `x, y`.

Common anchors: `topleft`, `topcenter`, `topright`, `left`, `center`, `right`, `bottomleft`, `bottomcenter`, and `bottomright`.

```python
TextConfig(x="50%", y="50%", anchor="center")
TextConfig(x=64, y=64, anchor="topleft")
```

## Layering

All element types share one compositing order through `z_index`.

| Element | Default |
|---|---:|
| shape | 1 |
| image | 5 |
| table | 6 |
| chart | 7 |
| text | 10 |

## Global and slide-level inheritance

Text font defaults can be set at post, canvas, and element level.

```python
post.text_font_path = "assets/fonts/Inter-Regular.ttf"

slide = CanvasConfig(
    text_font_path="assets/fonts/Inter-Medium.ttf",
    texts=[
        TextConfig(content="Uses canvas font"),
        TextConfig(content="Uses explicit font", font_path="assets/fonts/Inter-Bold.ttf"),
    ],
)
```

Precedence: element, canvas, post, renderer fallback.

## Nested text

Images and shapes can contain text. Nested coordinates are relative to the parent box.

```python
ShapeConfig(
    type="rounded_rectangle",
    x="50%",
    y="50%",
    width="70%",
    height="30%",
    anchor="center",
    fill_color="#FFFFFF",
    texts=[
        TextConfig(
            content="Inside the card",
            x="50%",
            y="50%",
            width="80%",
            anchor="center",
            color="#111827",
        )
    ],
)
```

## Merge versus replace

When a post has `canvases`, post-level elements are merged into each slide by default. Set `replace_elements=True` on a canvas to use only that slide’s elements.

## Profiles, safe areas and UI zones

A platform profile can supply dimensions, safe-area padding, exclusion zones for platform UI, crop metadata, output format guidance, and file-size limits.

The template engine places its root inside the safe area unless a variant uses `root_scope="canvas"`.

## Validation model

Validation happens before rendering for layout issues and after rendering for output-size limits. Each slide returns a `LayoutReport` containing issues with a code, message, and severity.

## Configuration is serializable

Postcanvas uses Pydantic models. Templates have first-class JSON and optional YAML persistence.

```python
template.to_file("templates/launch.json")
loaded = Template.from_file("templates/launch.json")
```
