# Migration to 1.0

Postcanvas 1.0 promotes the existing rendering and template systems to a stable public release. The release is designed to be source-compatible with 0.3.2 for documented APIs.

## Upgrade

```bash
pip install --upgrade "postcanvas==1.0.0"
```

## Versioned stability

The following areas are stable public API:

- root rendering functions
- result objects
- configuration models and enums
- platform preset helpers
- layout validation
- template and layout-node models
- rich-text composition
- variant selector protocol
- image byte/save helpers

Additive fields and new helpers may appear in minor releases. Breaking changes require a new major version.

## Recommended changes for older code

### Prefer `render()` for application workflows

```python
result = render(post)
image = result.images[0]
report = result.reports[0]
```

`generate()` remains supported.

### Bound variable-length text

```python
TextConfig(
    content=headline,
    width="84%",
    height="30%",
    font_size=96,
    min_font_size=36,
    max_lines=4,
    fit="shrink",
    overflow="ellipsis",
    wrap_mode="balanced",
)
```

### Enable validation

```python
post.layout_policy = LayoutPolicyConfig(
    collision="error",
    canvas_bounds="error",
    safe_area="error",
    text_overflow="error",
)
```

### Use profiles for platform-sensitive surfaces

Prefer named presets/profiles over copied dimensions when safe areas or UI zones matter.

### Use templates for repeated designs

Convert repeated coordinate scripts into a `Template` with named content slots and fixtures.

## Optional dependencies

```bash
pip install "postcanvas[yaml,typography]"
```

## Verify a migration

1. render existing fixtures
2. compare dimensions and filenames
3. inspect validation reports
4. test maximum-length content
5. verify custom fonts in deployment
6. test output size with production encoder settings
7. update stored template version metadata if needed
