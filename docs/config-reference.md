# Configuration reference

This reference summarizes public configuration models. Model validation remains the authoritative source for accepted values.

## `PostConfig`

Root configuration for one image or a carousel.

| Field | Purpose |
|---|---|
| `platform`, `format`, `profile_name` | target metadata |
| `width`, `height` | canvas dimensions |
| `background` | global background |
| `padding`, `safe_area` | layout insets |
| `exclusion_zones` | platform UI regions |
| `max_file_size_bytes` | encoded output limit |
| `layout_policy` | validation severity |
| `text_font_family`, `text_font_path` | inherited typography defaults |
| `texts`, `images`, `shapes`, `tables`, `charts` | global elements |
| `canvases` | carousel slides |
| `canvas_filters`, `watermark` | final effects |
| `output_dir`, `output_format`, `output_filename` | output |
| `quality`, `dpi` | encoding metadata |
| `meta` | non-rendered metadata |

`slide_count` returns at least one.

## `CanvasConfig`

Per-slide override. Important fields include dimensions, background, padding, safe area, exclusion zones, file-size limit, layout policy, inherited font defaults, element lists, `replace_elements`, filters, watermark, output filename, and metadata.

## `BackgroundConfig`

| Field | Purpose |
|---|---|
| `color` | solid color |
| `gradient` | linear/radial gradient |
| `image_path`, `image_url` | source |
| `image_fit` | cover/contain/fill/center |
| `image_opacity`, `image_blur` | source treatment |
| `overlay_color`, `overlay_opacity` | color overlay |

## `TextConfig`

### Identity and validation

- `id`
- `collision_group`
- `allow_overlap_with`
- `respect_safe_area`
- `respect_exclusion_zones`

### Geometry

- `x`, `y`
- `width`, `height`
- `max_width`, `max_height`
- `anchor`

### Fonts

- `font_family`, `font_path`
- `font_fallback_paths`
- `font_size`, `min_font_size`
- `font_weight`, `italic`
- `variation_name`, `variation_axes`

### Responsive behavior

- `fit`: none, shrink, truncate, error
- `overflow`: visible, clip, ellipsis, error
- `wrap_mode`: greedy, balanced
- `max_lines`
- `break_long_words`
- `preserve_newlines`
- `widow_control`
- `min_first_line_words`, `min_last_line_words`

### Type styling

- `color`
- `align`, `vertical_align`
- `transform`
- `line_spacing`, `paragraph_spacing`
- `letter_spacing`, `word_spacing`
- `decoration`
- `language`, `direction`, `features`
- auto contrast colors and threshold

### Effects

- shadow
- stroke
- text background, padding and radius
- opacity, rotation, blend mode
- z-index, visibility
- filters

## `ImageElementConfig`

- source: `src`
- geometry: x/y/width/height/anchor
- fit and focal mode
- manual focal coordinates
- radius, opacity, rotation and flips
- brightness, contrast and saturation
- shadow and border
- nested text
- blend mode, z-index, visibility
- filters
- validation identity fields

## `ShapeConfig`

- type and geometry
- fill color or gradient
- stroke
- radius
- polygon/star parameters
- opacity, rotation and blend mode
- z-index and visibility
- shadow
- nested text
- validation identity fields

## `TableElementConfig`

- headers, rows and column widths
- geometry
- font and size
- global, header, body, column and targeted cell alignment
- text and surface colors
- border/grid styling
- row/header heights
- opacity, rotation, blend mode, z-index, visibility and shadow

## `ChartElementConfig`

- chart type
- labels and series
- geometry
- title and typography
- min/max scale and grid steps
- legend, grid and point visibility
- line/point/bar styling
- palette and surfaces
- axis, grid and border styling
- plot padding
- opacity, rotation, blend mode, z-index, visibility and shadow

## Primitive models

### `PaddingConfig`

- `top`, `right`, `bottom`, `left`
- `PaddingConfig.all(value)`
- `PaddingConfig.symmetric(vertical=..., horizontal=...)`
- `PaddingConfig.only(...)`

### `GradientConfig`

- `type`
- `stops`
- `angle`
- radial center and radius

### `ShadowConfig`

- color
- x/y offset
- blur radius
- spread

### `StrokeConfig`

- color
- width

### `BorderConfig`

- color
- width
- radius
- style

### `FilterConfig`

- filter type
- value

## Layout models

### `LayoutPolicyConfig`

Policies: collision, canvas bounds, safe area, exclusion zones, text overflow, contrast, missing fonts, and file size. Additional settings include minimum contrast ratio and whether touching boxes are allowed.

### `ExclusionZone`

- name
- x/y/width/height
- description

### `PlatformProfile`

- name
- dimensions
- safe area
- exclusion zones
- description
- crop dimensions
- recommended format
- file-size limit

## Template models

See [Templates](templates.md) for all layout-node fields and behavior.

## Enums

Public enums include `Platform`, `PostFormat`, `GradientType`, `ImageFit`, `TextAlign`, `FontWeight`, `ShapeType`, `ChartType`, `BlendMode`, `OutputFormat`, `FilterType`, and `TextTransform`.
