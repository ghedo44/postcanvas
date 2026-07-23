# Rich text

`RichTextBlock` composes independently styled spans into ordinary `TextConfig` runs. The resulting runs participate in the normal rendering, collision, safe-area, exclusion-zone, filter, and z-index systems.

## Basic composition

```python
from postcanvas import RichTextBlock, RichTextSpan

block = RichTextBlock(
    spans=[
        RichTextSpan(text="Build ", color="#FFFFFF"),
        RichTextSpan(
            text="beautiful",
            color="#F472B6",
            font_scale=1.18,
            decoration="underline",
        ),
        RichTextSpan(text=" graphics from code.", color="#FFFFFF"),
    ],
    x="8%",
    y="15%",
    width="84%",
    height="32%",
    anchor="topleft",
    font_size=92,
    min_font_size=38,
    max_lines=4,
    fit="shrink",
    overflow="ellipsis",
)

composition = block.compose(1080, 1350)
post.texts.extend(composition.texts)
```

The composition contains generated text runs, the measured layout, and final block bounds.

## Span styling

Each `RichTextSpan` supports color, font family/path, fallback paths, font scale, letter and word spacing, decoration, background color, shadow, stroke, and opacity.

```python
from postcanvas.models import ShadowConfig, StrokeConfig

RichTextSpan(
    text="1.0",
    color="#111827",
    background_color="#FDE68A",
    font_scale=1.35,
    letter_spacing=2,
    stroke=StrokeConfig(color="#FFFFFF", width=1),
    shadow=ShadowConfig(offset_y=6, blur_radius=14),
)
```

## Block layout

`RichTextBlock` supports bounded width/height, shrink-to-fit, error on overflow, clipping or ellipsis, maximum lines, line and paragraph spacing, first-line indentation, horizontal/vertical alignment, optional hyphenation, and collision/safe-area metadata.

## First-line indentation

```python
RichTextBlock(
    spans=[RichTextSpan(text=body)],
    first_line_indent=36,
    paragraph_spacing=0.4,
)
```

## Dictionary hyphenation

```bash
pip install "postcanvas[typography]"
```

```python
RichTextBlock(
    spans=[RichTextSpan(text=long_copy)],
    hyphenate=True,
    hyphenation_language="en_US",
    hyphen_character="‐",
)
```

If `pyphen` is not installed, composition raises an explicit import error.

## Adding to a template result

```python
post = template.build(content)

rich = RichTextBlock(
    spans=[
        RichTextSpan(text=content["prefix"]),
        RichTextSpan(text=content["highlight"], color="#A78BFA", font_scale=1.15),
    ],
    x="8%",
    y="12%",
    width="84%",
    height="25%",
)

post.texts.extend(rich.compose(post.width, post.height, post.padding).texts)
result = render(post)
```

## Collision behavior

Generated runs use the block’s collision group, overlap permissions, safe-area flags, and z-index. Runs within one rich-text block are an intentional internal composition.

## Debugging

```python
composition = block.compose(1080, 1350)

print(composition.layout.font_size)
print(composition.layout.overflowed)
print(composition.layout.truncated)

for line in composition.layout.lines:
    print(line.width, [run.text for run in line.runs])
```
