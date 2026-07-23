# Validation and accessibility

Postcanvas validates geometry before rendering and output limits after rendering. Validation is controlled by `LayoutPolicyConfig`.

<p align="center">
  <img src="assets/validation-report.svg" alt="Validation report" width="100%">
</p>

## Configure policies

```python
from postcanvas.models import LayoutPolicyConfig

policy = LayoutPolicyConfig(
    collision="error",
    canvas_bounds="error",
    safe_area="error",
    exclusion_zones="error",
    text_overflow="error",
    contrast="warn",
    missing_fonts="error",
    file_size="warn",
    min_contrast_ratio=4.5,
    allow_touching=True,
)
```

Each policy accepts `ignore`, `warn`, or `error`.

## Layout reports

```python
from postcanvas import render

result = render(post)

for report in result.reports:
    for issue in report.issues:
        print(issue.code, issue.severity, issue.message)
```

Errors raise `LayoutValidationError` through the high-level API. Warnings are emitted and remain in the report.

## Collision detection

Elements only collide when they share a `collision_group`.

```python
TextConfig(id="headline", collision_group="content")
ImageElementConfig(id="hero", collision_group="content", src="hero.jpg")
```

Allow intentional overlap by ID:

```python
TextConfig(
    id="caption",
    collision_group="content",
    allow_overlap_with=["hero"],
)
```

Decorative elements can omit a collision group.

## Canvas bounds

Canvas-bound validation catches elements that extend beyond output dimensions. Rotated or shadowed content may require intentional allowances.

## Safe areas

```python
post.safe_area = PaddingConfig(
    top=120,
    right=72,
    bottom=140,
    left=72,
)
```

Elements with `respect_safe_area=True` are checked against this rectangle.

## Platform UI exclusion zones

```python
from postcanvas.models import ExclusionZone

post.exclusion_zones = [
    ExclusionZone(
        name="bottom-controls",
        x=0,
        y="82%",
        width="100%",
        height="18%",
        description="Reserved for platform controls and captions.",
    )
]
```

Elements with `respect_exclusion_zones=True` are checked against these regions.

## Text overflow

```python
TextConfig(
    width="84%",
    height="30%",
    font_size=96,
    min_font_size=36,
    fit="shrink",
    overflow="error",
)
```

## Contrast

```python
LayoutPolicyConfig(contrast="warn", min_contrast_ratio=4.5)
```

```python
from postcanvas import contrast_ratio

print(contrast_ratio("#FFFFFF", "#111827"))
```

Contrast analysis is most reliable for solid or known backgrounds. Complex media should be reviewed visually or use text backgrounds/strokes.

## Missing fonts

```python
LayoutPolicyConfig(missing_fonts="error")
```

Use explicit font paths and fallback paths for deterministic production rendering.

## File-size validation

```python
post.max_file_size_bytes = 2_000_000
post.layout_policy.file_size = "error"
```

The final encoded image is checked with the configured output format and quality.

## Accessibility recommendations

- target at least 4.5:1 for normal-size text
- use larger text for mobile surfaces
- keep critical content inside safe areas
- avoid platform UI zones
- do not communicate meaning through color alone
- provide strong text backgrounds over detailed photos
- test translated strings and text expansion
- avoid dense tables in story formats
- include alt text when publishing generated images downstream

## Strict production preset

```python
STRICT = LayoutPolicyConfig(
    collision="error",
    canvas_bounds="error",
    safe_area="error",
    exclusion_zones="error",
    text_overflow="error",
    contrast="error",
    missing_fonts="error",
    file_size="error",
)
```

Use warnings during design exploration and errors in release automation.
