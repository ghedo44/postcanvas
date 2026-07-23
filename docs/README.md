# Postcanvas documentation

<p align="center">
  <img src="assets/hero.svg" alt="Postcanvas 1.0 documentation" width="100%">
</p>

This documentation covers the complete public surface of Postcanvas 1.0: configuration models, rendering, responsive typography, rich text, template composition, platform profiles, validation, output pipelines, and extension points.

## Learning paths

### I need to generate my first image

1. [Getting started](getting-started.md)
2. [Core concepts](concepts.md)
3. [Examples cookbook](examples.md)
4. [Configuration reference](config-reference.md)

### I need a reusable design system

1. [Templates and responsive layout](templates.md)
2. [Typography](typography.md)
3. [Rich text](rich-text.md)
4. [Platform profiles](platform-profiles.md)
5. [Validation and accessibility](validation.md)

### I need production automation

1. [Output and cloud storage](output-cloud.md)
2. [Carousels](carousels.md)
3. [Assisted variant selection](assisted-selection.md)
4. [Renderer architecture](renderer-architecture.md)
5. [API reference](api-reference.md)

## Complete index

| Guide | What it covers |
|---|---|
| [Getting started](getting-started.md) | install, first render, output modes, common workflow |
| [Core concepts](concepts.md) | canvases, elements, dimensions, anchors, layering, inheritance |
| [Typography](typography.md) | fit, wrapping, overflow, multilingual text, variable fonts, accessibility |
| [Rich text](rich-text.md) | styled spans, mixed font scale, indentation, hyphenation |
| [Backgrounds and images](backgrounds-images.md) | gradients, remote/local images, fit, focal points, image effects |
| [Shapes and effects](shapes-effects.md) | drawing primitives, gradients, nested text, blend modes, filters |
| [Tables and charts](tables-charts.md) | table alignment, bar/line charts, data visuals |
| [Carousels](carousels.md) | multi-canvas posts, merge/replace behavior, slide output |
| [Templates](templates.md) | layout trees, variants, inheritance, themes, repeaters, fixtures, JSON/YAML |
| [Validation](validation.md) | collisions, safe areas, exclusion zones, contrast, fonts, file size |
| [Platform profiles](platform-profiles.md) | built-ins, custom profiles, crop and export guidance |
| [Output and cloud](output-cloud.md) | save modes, bytes, PIL, formats, cloud uploads, metadata |
| [Assisted selection](assisted-selection.md) | selectors, prompt/LLM adapters, deterministic validation |
| [Examples](examples.md) | task-oriented recipes and source files |
| [Gallery](gallery.md) | visual outputs and matching example code |
| [Configuration reference](config-reference.md) | model-by-model field reference |
| [API reference](api-reference.md) | public functions, classes, result objects |
| [Renderer architecture](renderer-architecture.md) | pipeline, merging, validation, compositing, extension points |
| [Migration to 1.0](migration-1.0.md) | upgrade guidance and stability commitments |

## Source examples

See [`../examples/`](../examples/) for complete executable scripts. The documentation workflow compiles every Python file in that directory.

## Reproducing the gallery

The SVG artwork in `docs/assets/` is committed for fast README rendering. The Python examples demonstrate the equivalent Postcanvas composition patterns. Run the gallery examples and replace assets with generated PNG/WebP files when maintaining screenshots for a release.
