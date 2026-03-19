from __future__ import annotations
import os
from typing import Optional, List
from PIL import Image

from postcanvas.models.elements import ImageElementConfig, ShapeConfig
from .background import render_background
from .text import render_text
from .shapes import render_shape
from .images import render_image_element
from .filters import apply_filter
from ..models import PostConfig, CanvasConfig, TextConfig, PaddingConfig, WatermarkConfig, OutputFormat

def _resolve_text_defaults(post: PostConfig, slide: Optional[CanvasConfig]) -> tuple[Optional[str], Optional[str]]:
    # Canvas-level font defaults override post-level defaults as a pair.
    if slide and (slide.text_font_family is not None or slide.text_font_path is not None):
        return slide.text_font_family, slide.text_font_path
    return post.text_font_family, post.text_font_path

def _apply_text_defaults(
    cfg: TextConfig,
    default_font_family: Optional[str],
    default_font_path: Optional[str],
) -> TextConfig:
    # Explicit font config on the text itself always wins.
    if cfg.font_family is not None or cfg.font_path is not None:
        return cfg
    updates = {}
    if default_font_family is not None:
        updates["font_family"] = default_font_family
    if default_font_path is not None:
        updates["font_path"] = default_font_path
    return cfg.model_copy(update=updates) if updates else cfg

def _watermark(canvas: Image.Image, wm: WatermarkConfig, cw: int, ch: int) -> Image.Image:
    if wm.text:
        pos_map = {
            "top_left":     (wm.padding, wm.padding, "topleft"),
            "top_right":    (cw - wm.padding, wm.padding, "topright"),
            "bottom_left":  (wm.padding, ch - wm.padding, "bottomleft"),
            "bottom_right": (cw - wm.padding, ch - wm.padding, "bottomright"),
            "center":       ("50%", "50%", "center"),
        }
        pos = pos_map.get(wm.position, (cw - wm.padding, ch - wm.padding, "bottomright"))
        cfg = TextConfig(
            content=wm.text, x=pos[0], y=pos[1],
            font_size=wm.font_size, color=wm.color,
            font_path=wm.font_path, opacity=wm.opacity, anchor=pos[2],
        )
        canvas = render_text(canvas, cfg, cw, ch, PaddingConfig())
    return canvas

def render_one(post: PostConfig, slide: Optional[CanvasConfig] = None) -> Image.Image:
    """Render a single slide."""
    w = (slide.width  if slide and slide.width  else None) or post.width
    h = (slide.height if slide and slide.height else None) or post.height

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    bg = (slide.background if slide and slide.background else None) or post.background
    if bg:
        canvas = render_background(canvas, bg)

    padding = (slide.padding if slide and slide.padding else None) or post.padding
    default_font_family, default_font_path = _resolve_text_defaults(post, slide)

    # Merge or replace elements
    if slide and slide.replace_elements:
        shapes = slide.shapes
        images = slide.images
        texts = slide.texts
    else:
        shapes = list(post.shapes) + (slide.shapes if slide else [])
        images = list(post.images) + (slide.images if slide else [])
        texts  = list(post.texts)  + (slide.texts  if slide else [])

    all_elements = (
        [el for el in shapes] +
        [el for el in images] +
        [el for el in texts]
    )
    all_elements.sort(key=lambda e: getattr(e, "z_index", 0))

    for el in all_elements:
        if isinstance(el, ShapeConfig):
            canvas = render_shape(
                canvas,
                el,
                w,
                h,
                default_font_family=default_font_family,
                default_font_path=default_font_path,
            )
        elif isinstance(el, ImageElementConfig):
            canvas = render_image_element(
                canvas,
                el,
                w,
                h,
                default_font_family=default_font_family,
                default_font_path=default_font_path,
            )
        elif isinstance(el, TextConfig):
            canvas = render_text(
                canvas,
                _apply_text_defaults(el, default_font_family, default_font_path),
                w,
                h,
                padding,
            )
        else:
            raise TypeError(f"Unknown element type: {type(el)}")

    # Post-process filters
    for f in (slide.canvas_filters if slide else []) or post.canvas_filters:
        canvas = apply_filter(canvas, f)

    # Watermark
    wm = (slide.watermark if slide else None) or post.watermark
    if wm:
        canvas = _watermark(canvas, wm, w, h)

    return canvas

def _save(img: Image.Image, path: str, fmt: OutputFormat, quality: int, dpi: int) -> None:
    if fmt in (OutputFormat.JPEG, OutputFormat.JPG):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        bg.save(path, "JPEG", quality=quality, dpi=(dpi, dpi))
    elif fmt == OutputFormat.WEBP:
        img.save(path, "WEBP", quality=quality)
    else:
        img.save(path, "PNG", dpi=(dpi, dpi))

def generate(post: PostConfig) -> List[str]:
    """
    Main entry point.  Returns a list of saved file paths.

    Single image  → `post.canvases` is empty  → one file.
    Carousel      → one file per CanvasConfig  in `post.canvases`.
    """
    os.makedirs(post.output_dir, exist_ok=True)
    ext = post.output_format.value.lower()
    paths: List[str] = []

    if not post.canvases:
        canvas = render_one(post)
        fname  = f"{post.output_filename}.{ext}"
        fpath  = os.path.join(post.output_dir, fname)
        _save(canvas, fpath, post.output_format, post.quality, post.dpi)
        print(f"✅  {fpath}")
        paths.append(fpath)
    else:
        for i, slide in enumerate(post.canvases):
            canvas = render_one(post, slide)
            name   = slide.output_filename or f"{post.output_filename}_{i+1:02d}"
            fname  = f"{name}.{ext}"
            fpath  = os.path.join(post.output_dir, fname)
            _save(canvas, fpath, post.output_format, post.quality, post.dpi)
            print(f"✅  {fpath}  ({i+1}/{len(post.canvases)})")
            paths.append(fpath)

    return paths
