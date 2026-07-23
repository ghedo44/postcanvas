from __future__ import annotations

from typing import Optional

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from ..models import ImageElementConfig, ImageFit, PaddingConfig, TextConfig
from .filters import apply_filter
from .loader import fit_image, load_image
from .text import render_text
from .utils import apply_rounded_corners, get_anchor_offset, parse_color, resolve


def render_image_element(
    canvas: Image.Image,
    cfg: ImageElementConfig,
    cw: int,
    ch: int,
    default_font_family: Optional[str] = None,
    default_font_path: Optional[str] = None,
) -> Image.Image:
    if not cfg.visible:
        return canvas

    image = load_image(cfg.src)
    if image is None:
        return canvas

    if cfg.flip_horizontal:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if cfg.flip_vertical:
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if cfg.brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(cfg.brightness)
    if cfg.contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(cfg.contrast)
    if cfg.saturation != 1.0:
        image = ImageEnhance.Color(image).enhance(cfg.saturation)
    for image_filter in cfg.filters:
        image = apply_filter(image, image_filter)

    if cfg.width is not None and cfg.height is not None:
        target_width = resolve(cfg.width, cw)
        target_height = resolve(cfg.height, ch)
    elif cfg.width is not None:
        target_width = resolve(cfg.width, cw)
        target_height = int(round(target_width / image.width * image.height))
    elif cfg.height is not None:
        target_height = resolve(cfg.height, ch)
        target_width = int(round(target_height / image.height * image.width))
    else:
        target_width, target_height = image.width, image.height

    image = fit_image(
        image,
        target_width,
        target_height,
        cfg.fit,
        cfg.focal_x,
        cfg.focal_y,
    )
    if cfg.fit == ImageFit.CONTAIN and image.size != (target_width, target_height):
        padded = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        padded.paste(
            image,
            (
                (target_width - image.width) // 2,
                (target_height - image.height) // 2,
            ),
            image,
        )
        image = padded

    if cfg.texts:
        local_padding = PaddingConfig()
        for text in sorted(cfg.texts, key=lambda item: item.z_index):
            updates = {}
            if text.width is None and text.max_width is None:
                updates["max_width"] = "100%"
            if text.font_family is None and text.font_path is None:
                if default_font_family is not None:
                    updates["font_family"] = default_font_family
                if default_font_path is not None:
                    updates["font_path"] = default_font_path
            local_config: TextConfig = (
                text.model_copy(update=updates) if updates else text
            )
            image = render_text(
                image,
                local_config,
                image.width,
                image.height,
                local_padding,
            )

    if cfg.border_radius > 0:
        image = apply_rounded_corners(image, cfg.border_radius)
    if cfg.opacity < 1.0:
        red, green, blue, alpha = image.split()
        alpha = alpha.point(lambda value: int(value * cfg.opacity))
        image = Image.merge("RGBA", (red, green, blue, alpha))

    if cfg.border:
        border_width = cfg.border.width
        bordered = Image.new(
            "RGBA",
            (image.width + border_width * 2, image.height + border_width * 2),
            (0, 0, 0, 0),
        )
        border_color = parse_color(cfg.border.color)
        border_draw = ImageDraw.Draw(bordered)
        if cfg.border_radius > 0:
            border_draw.rounded_rectangle(
                (0, 0, bordered.width, bordered.height),
                radius=cfg.border_radius + border_width,
                fill=border_color,
            )
        else:
            border_draw.rectangle(
                (0, 0, bordered.width, bordered.height),
                fill=border_color,
            )
        bordered.paste(image, (border_width, border_width), image)
        image = bordered

    if cfg.rotation:
        image = image.rotate(
            -cfg.rotation,
            expand=True,
            resample=Image.Resampling.BICUBIC,
        )

    x = resolve(cfg.x, cw)
    y = resolve(cfg.y, ch)
    offset_x, offset_y = get_anchor_offset(cfg.anchor, image.width, image.height)
    x += offset_x
    y += offset_y

    if cfg.shadow:
        shadow_color = parse_color(cfg.shadow.color)
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        mask_color = Image.new("RGBA", image.size, shadow_color)
        if image.mode == "RGBA":
            mask_color.putalpha(image.split()[3])
        shadow_x = x + int(cfg.shadow.offset_x)
        shadow_y = y + int(cfg.shadow.offset_y)
        shadow.paste(mask_color, (shadow_x, shadow_y), mask_color)
        if cfg.shadow.blur_radius > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(cfg.shadow.blur_radius))
        canvas = Image.alpha_composite(canvas, shadow)

    result_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    result_layer.paste(image, (x, y), image)
    return Image.alpha_composite(canvas, result_layer)
