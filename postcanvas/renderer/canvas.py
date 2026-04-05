from __future__ import annotations
import os
from io import BytesIO
from typing import Optional, List, Union, Literal, overload
from dataclasses import dataclass
from PIL import Image

from postcanvas.models.elements import (
    ImageElementConfig,
    ShapeConfig,
    TableElementConfig,
    ChartElementConfig,
)
from .background import render_background
from .text import render_text
from .shapes import render_shape
from .images import render_image_element
from .tables import render_table
from .charts import render_chart
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
        tables = slide.tables
        charts = slide.charts
    else:
        shapes = list(post.shapes) + (slide.shapes if slide else [])
        images = list(post.images) + (slide.images if slide else [])
        texts  = list(post.texts)  + (slide.texts  if slide else [])
        tables = list(post.tables) + (slide.tables if slide else [])
        charts = list(post.charts) + (slide.charts if slide else [])

    all_elements = (
        [el for el in shapes] +
        [el for el in images] +
        [el for el in tables] +
        [el for el in charts] +
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
        elif isinstance(el, TableElementConfig):
            canvas = render_table(
                canvas,
                el,
                w,
                h,
                default_font_family=default_font_family,
                default_font_path=default_font_path,
            )
        elif isinstance(el, ChartElementConfig):
            canvas = render_chart(
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

def _prepare_image_for_format(img: Image.Image, fmt: OutputFormat) -> Image.Image:
    """
    Prepare image for the target format.
    Converts RGBA to RGB for JPEG (required).
    """
    if fmt in (OutputFormat.JPEG, OutputFormat.JPG):
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            return bg
    return img


def _save_image(img: Image.Image, buffer_or_path: Union[BytesIO, str], fmt: OutputFormat, quality: int, dpi: int = 96) -> None:
    """
    Generic image save function for both file and buffer output.
    
    Args:
        img: Prepared PIL Image (already converted if needed)
        buffer_or_path: Either a BytesIO buffer or file path (string)
        fmt: Output format
        quality: JPEG/WEBP quality (1-100)
        dpi: DPI for PNG (unused for JPEG/WEBP in buffer mode)
    """
    if fmt in (OutputFormat.JPEG, OutputFormat.JPG):
        img.save(buffer_or_path, "JPEG", quality=quality, dpi=(dpi, dpi) if isinstance(buffer_or_path, str) else None)
    elif fmt == OutputFormat.WEBP:
        img.save(buffer_or_path, "WEBP", quality=quality)
    else:  # PNG
        img.save(buffer_or_path, "PNG", dpi=(dpi, dpi) if isinstance(buffer_or_path, str) else None)


def _save(img: Image.Image, path: str, fmt: OutputFormat, quality: int, dpi: int) -> str:
    """Save image to disk and return the saved file path."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    prepared_img = _prepare_image_for_format(img, fmt)
    _save_image(prepared_img, path, fmt, quality, dpi)
    return path


@dataclass
class GenerateResult:
    """
    Result container for generate() function with consistent interface.
    
    Attributes:
        images: PIL Image objects generated
        paths: File paths if save=True, None otherwise
    """
    images: List[Image.Image]
    paths: List[str]

    def __repr__(self) -> str:
        paths_info = f", {len(self.paths)} files saved" if self.paths else ""
        return f"GenerateResult({len(self.images)} image(s){paths_info})"


# Type overloads for better IDE support
@overload
def generate(post: PostConfig, save: Literal[True], return_images: Literal[False] = False) -> List[str]: ...

@overload
def generate(post: PostConfig, save: Literal[False], return_images: Literal[True]) -> List[Image.Image]: ...

@overload
def generate(post: PostConfig, save: Literal[True], return_images: Literal[True]) -> GenerateResult: ...

@overload
def generate(post: PostConfig, save: bool = True, return_images: bool = False) -> Union[List[str], List[Image.Image], GenerateResult]: ...


def generate(
    post: PostConfig,
    save: bool = True,
    return_images: bool = False,
) -> Union[List[str], List[Image.Image], GenerateResult]:
    """
    Generate post image(s) with flexible output options.

    Args:
        post: PostConfig object with layout and content configuration
        save: If True, save images to disk (default: True)
        return_images: If True, return PIL Image objects (default: False)

    Returns:
        Return type depends on parameters:
        - save=True, return_images=False (default): List[str] - file paths only
        - save=False, return_images=True: List[Image.Image] - images only
        - save=True, return_images=True: GenerateResult - both paths and images

    Raises:
        ValueError: If save=False and return_images=False (nothing to return)

    Examples:
        # Default: save to disk, return file paths (backward compatible)
        paths = generate(post)
        assert isinstance(paths, list) and isinstance(paths[0], str)

        # Return raw images only (no disk I/O)
        images = generate(post, save=False, return_images=True)
        assert isinstance(images, list) and isinstance(images[0], Image.Image)

        # Get both: save to disk AND return images
        result = generate(post, save=True, return_images=True)
        assert isinstance(result, GenerateResult)
        assert result.paths and result.images
    """
    if not save and not return_images:
        raise ValueError("Must specify at least one of: save=True or return_images=True")

    if save:
        os.makedirs(post.output_dir, exist_ok=True)

    ext = post.output_format.value.lower()
    paths: List[str] = []
    images_list: List[Image.Image] = []

    # Render single image or carousel
    slides_to_render = [(None, None)] if not post.canvases else [
        (i, slide) for i, slide in enumerate(post.canvases)
    ]

    for idx, (i, slide) in enumerate(slides_to_render):
        canvas = render_one(post, slide)
        images_list.append(canvas)

        if save:
            # Determine output filename
            if slide and slide.output_filename:
                name = slide.output_filename
            elif i is not None:
                name = f"{post.output_filename}_{i+1:02d}"
            else:
                name = post.output_filename

            fname = f"{name}.{ext}"
            fpath = os.path.join(post.output_dir, fname)

            # Save the image
            saved_path = _save(canvas, fpath, post.output_format, post.quality, post.dpi)
            paths.append(saved_path)

            # Print progress
            if post.canvases:
                print(f"✅  {fpath}  ({idx+1}/{len(post.canvases)})")
            else:
                print(f"✅  {fpath}")

    # Return based on configuration
    if save and return_images:
        return GenerateResult(images=images_list, paths=paths)
    elif return_images:
        return images_list
    else:
        return paths


def image_to_bytes(img: Image.Image, format: OutputFormat = OutputFormat.PNG, quality: int = 95) -> bytes:
    """
    Convert a PIL Image to bytes for storage/upload to cloud.

    Args:
        img: PIL Image object
        format: Output format (PNG, JPEG, WEBP)
        quality: JPEG/WEBP quality (1-100)

    Returns:
        Image data as bytes

    Example:
        images = generate(post, save=False, return_images=True)
        for i, img in enumerate(images):
            data = image_to_bytes(img, format=OutputFormat.PNG)
            s3_client.put_object(Bucket='my-bucket', Key=f'image_{i}.png', Body=data)
    """
    buffer = BytesIO()
    prepared_img = _prepare_image_for_format(img, format)
    _save_image(prepared_img, buffer, format, quality)
    return buffer.getvalue()


def save_image_to_path(img: Image.Image, path: str, format: OutputFormat = OutputFormat.PNG, quality: int = 95) -> str:
    """
    Save a PIL Image to a specific path.

    Args:
        img: PIL Image object
        path: File path to save to
        format: Output format (PNG, JPEG, WEBP)
        quality: JPEG/WEBP quality (1-100)

    Returns:
        The saved file path

    Example:
        images = generate(post, save=False, return_images=True)
        for i, img in enumerate(images):
            save_image_to_path(img, f"./custom_output/image_{i}.png")
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    prepared_img = _prepare_image_for_format(img, format)
    _save_image(prepared_img, path, format, quality)
    return path
