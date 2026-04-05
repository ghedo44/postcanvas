# Configuration Reference

This page documents the core models used to build a post.

## Root Models

## `PostConfig`

Global defaults for a full post render.

Key fields:

- `platform`, `format`
- `width`, `height`
- `background`, `padding`
- `text_font_family`, `text_font_path`
- `texts`, `images`, `shapes`, `tables`, `charts`
- `canvases` (carousel slides)
- `canvas_filters`, `watermark`
- `output_dir`, `output_format`, `output_filename`, `quality`, `dpi`

Global element lists are applied to all slides unless a slide sets `replace_elements=True`.

## `CanvasConfig`

Per-slide overrides in a carousel.

Key fields:

- `width`, `height`
- `background`, `padding`
- `text_font_family`, `text_font_path`
- `texts`, `images`, `shapes`, `tables`, `charts`
- `replace_elements`
- `canvas_filters`
- `watermark`
- `output_filename`

If `replace_elements=False` (default), slide elements are merged with post-level elements.

## Element Models

## `TextConfig`

Text rendering with wrapping, alignment, shadows, stroke, transforms, and optional auto-contrast.

Important fields:

- content and geometry: `content`, `x`, `y`, `max_width`, `anchor`
- typography: `font_family`, `font_path`, `font_size`
- style: `color`, `align`, `line_spacing`, `transform`
- effects: `shadow`, `stroke`, `background_color`, `auto_contrast`
- compositing: `opacity`, `rotation`, `z_index`, `visible`

## `ImageElementConfig`

Places local or remote images with fit modes and decorations.

Important fields:

- source and geometry: `src`, `x`, `y`, `width`, `height`, `anchor`
- scaling: `fit` (`cover`, `contain`, `fill`, `center`)
- visual: `border_radius`, `opacity`, `rotation`, `flip_horizontal`, `flip_vertical`
- enhancements: `brightness`, `contrast`, `saturation`, `filters`
- decoration: `shadow`, `border`
- nested text: `texts`

## `ShapeConfig`

Generates vector-like primitives directly in PIL.

Important fields:

- shape and geometry: `type`, `x`, `y`, `width`, `height`, `anchor`
- fill: `fill_color`, `fill_gradient`
- stroke: `stroke_color`, `stroke_width`
- shape-specific: `border_radius`, `sides`, `star_points`, `star_inner_r`, `points`
- nested text: `texts`
- compositing: `opacity`, `rotation`, `z_index`, `visible`, `shadow`

## `TableElementConfig`

Renders a data table block with optional header, row striping, and grid lines.

Data fields:

- `headers: List[str]`
- `rows: List[List[str | int | float]]`
- `column_widths: Optional[List[float]]`

Layout fields:

- `x`, `y`, `width`, `height`, `anchor`
- `show_header`, `cell_padding`
- `row_height`, `header_height`

Typography fields:

- `font_family`, `font_path`
- `font_size`, `header_font_size`
- `cell_align`, `header_align`

Visual fields:

- `text_color`, `header_text_color`
- `background_color`, `header_background_color`
- `row_background_colors`
- `border_color`, `border_width`
- `grid_color`, `grid_width`
- `border_radius`

Compositing fields:

- `opacity`, `rotation`, `blend_mode`, `z_index`, `visible`, `shadow`

Behavior notes:

- Headers and row lengths are padded to match the widest row count.
- If `column_widths` is omitted or invalid, columns are distributed evenly.
- Rounded corners clip inner table fills and grid to keep visuals inside the border.

## `ChartSeriesConfig`

Defines one data series inside a chart.

Fields:

- `name`
- `values: List[float]`
- `color`
- `line_width`, `point_radius` (for line charts)

## `ChartElementConfig`

Renders bar or line charts with title, grid, axis labels, and legend.

Data fields:

- `type` (`ChartType.BAR` or `ChartType.LINE`)
- `labels`
- `series`

Scale fields:

- `min_value`, `max_value`
- `grid_steps`

Layout fields:

- `x`, `y`, `width`, `height`, `anchor`
- `padding_left`, `padding_right`, `padding_top`, `padding_bottom`

Typography fields:

- `title`, `font_family`, `font_path`
- `font_size`, `title_font_size`
- `label_color`, `title_color`

Visual fields:

- `show_grid`, `show_legend`, `show_points`
- `line_width`, `point_radius`
- `bar_group_padding`, `bar_radius`
- `palette`
- `background_color`, `chart_background_color`
- `axis_color`, `grid_color`
- `border_color`, `border_width`, `border_radius`

Compositing fields:

- `opacity`, `rotation`, `blend_mode`, `z_index`, `visible`, `shadow`

## z-index Order

Elements are composited in ascending `z_index` across all element types.

Default z-index values:

- shapes = 1
- images = 5
- tables = 6
- charts = 7
- texts = 10

## Font Inheritance

Text-capable renderers follow this precedence:

1. element-level `font_path` or `font_family`
2. canvas-level `text_font_path` or `text_font_family`
3. post-level `text_font_path` or `text_font_family`
4. renderer fallback font search
