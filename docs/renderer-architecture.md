# Renderer architecture

## Pipeline

The high-level pipeline is:

1. resolve post and slide configuration
2. merge post-level and canvas-level values
3. apply font inheritance
4. measure layout geometry
5. run pre-render validation
6. render backgrounds and elements
7. composite by z-index and blend mode
8. apply canvas filters and watermark
9. encode/save requested outputs
10. validate output file size
11. return images, paths, and reports

## Configuration resolution

A `PostConfig` may contain no canvases or multiple `CanvasConfig` values.

- no canvases: render one effective canvas from the post
- canvases: merge each slide with post defaults
- `replace_elements=True`: skip global element merging for that slide

## Font resolution

Font precedence is element, canvas default, post default, then renderer font-family search/fallback. Fallback paths let one text element cover multiple scripts.

## Text measurement

Text is measured with Pillow before drawing. The engine handles explicit paragraphs, long tokens, greedy/balanced wrapping, bounded height, maximum lines, shrink-to-fit, ellipsis, clipping, variable font controls, and language/direction/features.

Rich text has its own compositor that converts measured span runs into normal text elements.

## Template resolution

The template layer is separate from the renderer:

1. select and resolve a variant
2. choose profile and root scope
3. create canvas and safe-area boxes
4. resolve the layout tree
5. emit ordinary text, image, and shape configuration
6. construct a `PostConfig`
7. run the normal rendering pipeline

This separation keeps templates serializable and the renderer backward compatible.

## Validation

Pre-render validation uses measured boxes and element metadata. Checks include collisions, bounds, safe area, exclusion zones, text overflow, contrast, and fonts. File-size validation happens after encoding because it depends on format and quality.

## Compositing

Elements from all supported types are sorted by `z_index`. Each layer can apply opacity, rotation, blend mode, shadow, and relevant filters before alpha compositing.

Nested text is rendered in a child coordinate system before the parent is placed on the canvas.

## Images

Image processing includes local/remote source loading, fit calculation, manual/automatic focal crop, brightness/contrast/saturation, flips/rotation, radius masking, border/shadow, filters, and nested text.

## Tables and charts

Tables and charts are rendered as dedicated layers, then participate in the same compositing order as other elements.

## Extension principles

- keep configuration declarative and serializable
- measure before drawing
- expose validation geometry
- avoid special-casing templates in the renderer
- preserve deterministic output
- add fixtures and tests for extreme content
- document z-index and inheritance behavior
