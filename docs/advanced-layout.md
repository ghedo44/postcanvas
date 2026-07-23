# Advanced responsive layouts

Postcanvas 0.3.1 completes the responsive template system with template and variant inheritance, repeaters, explicit alignment/group/safe-area nodes, UI exclusion zones, platform file limits, automatic image focal points, accessibility diagnostics, multilingual typography checks, and visual regression helpers.

## Repeatable responsive content

Use `LayoutNode(kind="repeat", repeat_from="metrics")` with `repeat_direction` set to `column`, `row`, or `grid`. Child slots can read nested values such as `item.label`; generated element IDs receive deterministic numeric suffixes.

## Platform-aware validation

Platform profiles can define safe insets, exclusion zones, recommended export formats, crop metadata, and maximum file sizes. Configure `LayoutPolicyConfig` to warn or fail on collisions, clipping, safe-area violations, platform UI overlap, missing fonts, low contrast, text overflow, or oversized output.

## Template QA

Store short, medium, and extreme content in `PreviewFixture` entries and render them with `Template.render_fixtures()`. Use `postcanvas.testing.assert_image_similar()` for deterministic golden-image comparisons with explicit tolerances.
