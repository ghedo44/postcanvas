# API reference

## Rendering functions

### `generate(post, save=True, return_images=False)`

Validates and renders a `PostConfig`, preserving the legacy return contract. Returns paths, images, or `GenerateResult` depending on output flags.

### `render(post, save=False) -> RenderResult`

Validates and renders, always returning `images`, `paths`, and `reports`. `RenderResult.warnings` flattens warnings from all slide reports.

### `render_one(...)`

Low-level single-canvas rendering helper. Prefer `render()` for application code because it includes validation and structured reports.

### `image_to_bytes(image, format, quality=...)`

Encode a PIL image without writing a file.

### `save_image_to_path(image, path, ...)`

Save a PIL image to an explicit destination.

## Validation

### `validate_post(post)`

Return one `LayoutReport` per output canvas.

### `contrast_ratio(foreground, background)`

Return the contrast ratio between supported colors.

### `LayoutValidationError`

Raised when a configured policy produces an error.

### `LayoutReport`

Contains slide issues and convenience accessors for warnings/errors.

### `LayoutIssue`

Contains issue code, message, severity, and related geometry/element data where available.

## Templates

### `Template`

Key methods:

- `from_file(path)`
- `to_file(path)`
- `inherit(base)`
- `resolve_variant(name)`
- `select_variant(content, variant=None, selector=None)`
- `build(content, variant=None, selector=None, **overrides)`
- `render(content, variant=None, selector=None, **overrides)`
- `render_fixtures(selector=None)`

### `TemplateVariant`

Describes a profile, root layout, inheritance, required slots, content limits, background, and layout policy.

### `LayoutNode`

Declarative layout/content node. See [Templates](templates.md).

### `Theme`

Color, font, spacing, and text-style tokens.

### `PreviewFixture`

Named content and optional forced variant for preview/regression rendering.

## Rich text

### `RichTextSpan`

One independently styled span.

### `RichTextBlock`

A bounded responsive rich-text composition.

### `compose_rich_text(block, canvas_width, canvas_height, padding)`

Functional equivalent of `block.compose(...)`.

Result models: `RichTextComposition`, `RichTextLayout`, `RichTextLineLayout`, and `RichTextRunLayout`.

## Variant selection

### `VariantSelector`

Protocol for custom variant selection.

### `PromptVariantSelector`

Adapter for prompt/LLM-style completion callables.

## Presets

### `get_profile(name)`

Return a platform profile.

### `list_profiles()`

Return registered profiles.

### `preset(platform, format, **overrides)`

Build a post for a platform/format pair or custom dimensions.

### Named helpers

Instagram square/portrait/story/reel cover, TikTok story, LinkedIn post, X post/banner, YouTube thumbnail/banner, Facebook post, Reddit post, and blog Open Graph/cover.

## Public model namespace

```python
from postcanvas.models import (
    BackgroundConfig,
    CanvasConfig,
    ChartElementConfig,
    ImageElementConfig,
    LayoutPolicyConfig,
    PostConfig,
    ShapeConfig,
    TableElementConfig,
    TextConfig,
)
```

## Version

```python
import postcanvas

print(postcanvas.__version__)
```
