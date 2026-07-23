# Typography

Postcanvas text is measured before it is drawn. Bounded text can react to content length instead of overflowing silently.

## Bounded text

```python
TextConfig(
    content=headline,
    x="8%",
    y="14%",
    width="84%",
    height="34%",
    anchor="topleft",
    font_size=112,
    min_font_size=42,
    max_lines=4,
    fit="shrink",
    overflow="ellipsis",
    wrap_mode="balanced",
)
```

## Fit strategies

| `fit` | Behavior |
|---|---|
| `none` | keep the requested font size |
| `shrink` | binary-search down to `min_font_size` |
| `truncate` | keep the size and truncate visible lines |
| `error` | raise when text does not fit |

`overflow` controls the final treatment: `visible`, `clip`, `ellipsis`, or `error`.

For production layouts, combine `fit="shrink"` with `overflow="ellipsis"` or `"error"`.

## Wrapping

```python
TextConfig(
    content="A longer headline that needs a deliberate shape",
    width=760,
    wrap_mode="balanced",
)
```

- `greedy` fills one line at a time.
- `balanced` minimizes uneven line lengths.
- `break_long_words=True` prevents one oversized token from escaping.
- `preserve_newlines=True` keeps explicit paragraph breaks.

## Line and paragraph controls

```python
TextConfig(
    content="First paragraph.\nSecond paragraph.",
    line_spacing=1.18,
    paragraph_spacing=0.35,
)
```

## Widow control

```python
TextConfig(
    content=headline,
    widow_control=True,
    min_first_line_words=2,
    min_last_line_words=2,
)
```

## Alignment

```python
TextConfig(align="left", vertical_align="middle")
```

Horizontal values: `left`, `center`, `right`, `justify`. Vertical values: `top`, `middle`, `bottom`.

## Letter and word spacing

```python
TextConfig(content="WIDE LABEL", letter_spacing=5, word_spacing=8)
```

## Transforms and decorations

```python
TextConfig(
    content="Launch notes",
    transform="uppercase",
    decoration="underline",
)
```

## Shadows, strokes and text backgrounds

```python
from postcanvas.models import ShadowConfig, StrokeConfig

TextConfig(
    content="Readable over media",
    color="#FFFFFF",
    shadow=ShadowConfig(
        color="rgba(0,0,0,0.55)",
        offset_x=0,
        offset_y=8,
        blur_radius=20,
    ),
    stroke=StrokeConfig(color="#111827", width=2),
    background_color="rgba(15,23,42,0.72)",
    background_padding=18,
    background_radius=14,
)
```

## Auto contrast

```python
TextConfig(
    content="Adaptive caption",
    auto_contrast=True,
    contrast_light_color="#FFFFFF",
    contrast_dark_color="#111827",
    contrast_threshold=145,
)
```

## Font paths and fallbacks

```python
TextConfig(
    content="Brand typography",
    font_path="assets/fonts/BrandVariable.ttf",
    font_fallback_paths=[
        "assets/fonts/NotoSans-Regular.ttf",
        "assets/fonts/NotoColorEmoji.ttf",
    ],
)
```

Missing fonts can be warnings or errors through `LayoutPolicyConfig`.

## Variable fonts

```python
TextConfig(
    content="Variable",
    font_path="assets/fonts/InterVariable.ttf",
    variation_name="Bold",
    variation_axes=[750],
)
```

## Multilingual text

```python
TextConfig(
    content="مرحبا بالعالم",
    direction="rtl",
    language="ar",
    features=["-liga"],
    align="right",
)
```

```python
TextConfig(
    content="ポストキャンバス",
    language="ja",
    break_long_words=True,
)
```

Use fallback paths that cover required scripts. Emoji rendering depends on the installed font and Pillow build.

## Accessibility checklist

- use `LayoutPolicyConfig(contrast="warn" | "error")`
- give text a bounded box
- test realistic maximum content
- include multilingual fixtures
- maintain sufficient line spacing
- avoid relying on color alone for meaning
