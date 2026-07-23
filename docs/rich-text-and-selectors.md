# Rich text and assisted template selection

Postcanvas 0.3.2 adds a compositional rich-text API without changing the core renderer. `RichTextBlock` measures, wraps, fits, and converts styled spans into ordinary `TextConfig` elements, so existing validation, collision detection, safe areas, filters, and z-index behavior continue to apply.

```python
from postcanvas import RichTextBlock, RichTextSpan

block = RichTextBlock(
    spans=[
        RichTextSpan(text="Build ", color="#ffffff"),
        RichTextSpan(
            text="better",
            color="#ff4d67",
            font_scale=1.2,
            decoration="underline",
        ),
        RichTextSpan(text=" social graphics", color="#ffffff"),
    ],
    x="50%",
    y="20%",
    width="84%",
    height="30%",
    font_size=88,
    min_font_size=36,
    max_lines=4,
    first_line_indent=24,
)

composition = block.compose(1080, 1350)
post.texts.extend(composition.texts)
```

Dictionary hyphenation is available with `pip install postcanvas[typography]` and `hyphenate=True`. The layout preserves paragraph breaks, supports first-line indentation, mixed font scales, colors, decorations, spacing, backgrounds, shadows, strokes, automatic shrinking, clipping, and ellipsis overflow.

`Template.select_variant()`, `build()`, and `render()` accept a pluggable `selector`. `PromptVariantSelector` converts a prompt-based or LLM chooser into the validated selector contract while keeping layout generation deterministic after a variant has been selected.

```python
from postcanvas import PromptVariantSelector

selector = PromptVariantSelector(my_model_complete)
result = template.render(content, selector=selector)
```

The selector can return a plain variant name or `{"variant": "name"}`. Unknown or ineligible selections are rejected before rendering.
