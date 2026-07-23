# Backgrounds and images

## Solid backgrounds

```python
BackgroundConfig(color="#0F172A")
```

## Linear gradients

```python
from postcanvas.models import GradientConfig, GradientStop

BackgroundConfig(
    gradient=GradientConfig(
        type="linear",
        angle=135,
        stops=[
            GradientStop(color="#0F172A", position=0),
            GradientStop(color="#4C1D95", position=0.55),
            GradientStop(color="#0E7490", position=1),
        ],
    )
)
```

## Radial gradients

```python
GradientConfig(
    type="radial",
    center_x=0.72,
    center_y=0.24,
    radius=0.78,
    stops=[
        GradientStop(color="#F472B6", position=0),
        GradientStop(color="#111827", position=1),
    ],
)
```

## Background images

```python
BackgroundConfig(
    image_path="assets/cover.jpg",
    image_fit="cover",
    image_opacity=0.9,
    image_blur=2,
    overlay_color="#090B17",
    overlay_opacity=0.4,
)
```

Remote backgrounds use `image_url`.

## Image elements

```python
from postcanvas.models import ImageElementConfig

ImageElementConfig(
    src="assets/product.jpg",
    x="50%",
    y="40%",
    width="84%",
    height="48%",
    anchor="center",
    fit="cover",
    border_radius=32,
)
```

## Fit modes

| Mode | Behavior |
|---|---|
| `cover` | fill the box and crop overflow |
| `contain` | fit inside without cropping |
| `fill` | stretch to requested dimensions |
| `center` | retain source scale and center |

## Manual focal points

```python
ImageElementConfig(
    src="assets/portrait.jpg",
    fit="cover",
    focal_mode="manual",
    focal_x=0.68,
    focal_y=0.28,
)
```

## Automatic focal points

```python
ImageElementConfig(
    src="assets/portrait.jpg",
    fit="cover",
    focal_mode="auto",
)
```

Automatic focal selection is deterministic and does not require an external service.

## Image effects

```python
ImageElementConfig(
    src="assets/photo.jpg",
    brightness=1.05,
    contrast=1.12,
    saturation=0.88,
    opacity=0.96,
    rotation=-2,
)
```

## Borders and shadows

```python
from postcanvas.models import BorderConfig, ShadowConfig

ImageElementConfig(
    src="assets/photo.jpg",
    border=BorderConfig(color="#FFFFFF", width=3, radius=28),
    shadow=ShadowConfig(
        color="rgba(0,0,0,0.35)",
        offset_y=18,
        blur_radius=30,
    ),
)
```

## Filters

```python
from postcanvas.models import FilterConfig, FilterType

ImageElementConfig(
    src="assets/photo.jpg",
    filters=[
        FilterConfig(type=FilterType.GRAYSCALE, value=1),
        FilterConfig(type=FilterType.CONTRAST, value=1.1),
        FilterConfig(type=FilterType.VIGNETTE, value=0.35),
    ],
)
```

Available filters include blur, sharpen, grayscale, sepia, brightness, contrast, saturation, invert, and vignette.

## Nested text on images

```python
ImageElementConfig(
    src="assets/photo.jpg",
    x="50%",
    y="50%",
    width="84%",
    height="60%",
    anchor="center",
    fit="cover",
    texts=[
        TextConfig(
            content="Caption inside the media box",
            x="8%",
            y="88%",
            width="84%",
            anchor="bottomleft",
            color="#FFFFFF",
            shadow=ShadowConfig(blur_radius=18),
        )
    ],
)
```

Nested coordinates are relative to the image box.
