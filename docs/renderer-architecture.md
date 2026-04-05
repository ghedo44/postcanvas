# Renderer Architecture

This document explains how rendering is orchestrated internally.

## Render Pipeline

Main entry points:

- `generate(post, ...)` in `postcanvas/renderer/canvas.py`
- `render_one(post, slide)` in `postcanvas/renderer/canvas.py`

High-level flow:

1. Resolve active dimensions (`PostConfig` overridden by `CanvasConfig`)
2. Create blank RGBA canvas
3. Render background
4. Resolve padding and text defaults
5. Merge or replace element lists
6. Sort all elements by `z_index`
7. Dispatch each element to specialized renderer
8. Apply canvas-level filters
9. Apply watermark
10. Save and/or return image objects

## Element Dispatch

`render_one` supports these element classes:

- `ShapeConfig` -> `render_shape`
- `ImageElementConfig` -> `render_image_element`
- `TableElementConfig` -> `render_table`
- `ChartElementConfig` -> `render_chart`
- `TextConfig` -> `render_text`

Unknown classes raise a `TypeError`.

## Merge Behavior

When a slide exists:

- if `replace_elements=True`: use only slide element lists
- otherwise: concatenate post-level and slide-level lists

This applies to shapes, images, tables, charts, and texts.

## Shared Font Utility

A centralized utility exists in `postcanvas/renderer/fonts.py`.

Exports:

- `FONT_DIRS`
- `FONT_MAP`
- `find_font(name, size)`
- `resolve_font(path, family, size)`

Benefits:

- One source of truth for fallback font search
- Consistent behavior in text/table/chart renderers
- Easier future extension (cache, extra aliases, custom user directories)

## Table Rendering Notes

`render_table` creates a rounded clip mask when `border_radius > 0` and applies it to:

- base background fill
- header background fill
- striped row fills
- grid overlay

This prevents internal fills from bleeding outside rounded corners.

## Chart Rendering Notes

`render_chart` computes chart bounds and scale from labels and series.

- bar chart: grouped bars using `bar_group_padding`
- line chart: polyline with optional points
- optional legend wrapping for long names
- optional grid and explicit min/max overrides

## Extending with New Elements

Recommended pattern:

1. Add new model class under `postcanvas/models/elements.py`
2. Add element lists to `PostConfig` and `CanvasConfig` if needed
3. Export symbols from `postcanvas/models/__init__.py`
4. Create renderer module in `postcanvas/renderer/`
5. Add dispatch branch in `render_one`
6. Add docs and runnable examples

## Performance Considerations

- Keep heavy per-element operations minimized inside loops.
- Reuse computed values (fonts, bounds, masks) when possible.
- Avoid unnecessary conversions between RGB/RGBA.
- For large carousels, prefer writing to disk in one pass with `generate`.
