from __future__ import annotations
from typing import Optional
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
from .utils import parse_color, resolve, get_anchor_offset, apply_rounded_corners
from .loader import load_image, fit_image
from .filters import apply_filter
from .text import render_text
from ..models import ImageElementConfig, ImageFit, PaddingConfig, TextConfig

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

    img = load_image(cfg.src)
    if img is None:
        return canvas

    if cfg.flip_horizontal:
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if cfg.flip_vertical:
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    if cfg.brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(cfg.brightness)
    if cfg.contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(cfg.contrast)
    if cfg.saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(cfg.saturation)

    for f in cfg.filters:
        img = apply_filter(img, f)

    if cfg.width and cfg.height:
        tw = resolve(cfg.width, cw)
        th = resolve(cfg.height, ch)
    elif cfg.width:
        tw = resolve(cfg.width, cw)
        th = int(tw / img.width * img.height)
    elif cfg.height:
        th = resolve(cfg.height, ch)
        tw = int(th / img.height * img.width)
    else:
        tw, th = img.width, img.height

    img = fit_image(img, tw, th, cfg.fit)

    # pad CONTAIN result
    if cfg.fit == ImageFit.CONTAIN and img.size != (tw, th):
        pad = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        pad.paste(img, ((tw - img.width) // 2, (th - img.height) // 2), img)
        img = pad

    # Render child texts inside the element using local coordinates.
    if cfg.texts:
        local_padding = PaddingConfig(left=0, right=0, top=0, bottom=0)
        for txt in sorted(cfg.texts, key=lambda t: t.z_index):
            updates = {}
            if txt.max_width is None:
                updates["max_width"] = "100%"
            if txt.font_family is None and txt.font_path is None:
                if default_font_family is not None:
                    updates["font_family"] = default_font_family
                if default_font_path is not None:
                    updates["font_path"] = default_font_path
            local_cfg: TextConfig = txt.model_copy(update=updates) if updates else txt
            img = render_text(img, local_cfg, img.width, img.height, local_padding)

    if cfg.border_radius > 0:
        img = apply_rounded_corners(img, cfg.border_radius)

    if cfg.opacity < 1.0:
        r2, g2, b2, a2 = img.split()
        a2 = a2.point(lambda p: int(p * cfg.opacity))
        img = Image.merge("RGBA", (r2, g2, b2, a2))

    if cfg.border:
        bw = cfg.border.width
        bordered = Image.new("RGBA", (img.width + bw*2, img.height + bw*2), (0, 0, 0, 0))
        bc = parse_color(cfg.border.color)
        bd = ImageDraw.Draw(bordered)
        if cfg.border_radius > 0:
            bd.rounded_rectangle([0, 0, bordered.width, bordered.height],
                                  radius=cfg.border_radius + bw, fill=bc)
        else:
            bd.rectangle([0, 0, bordered.width, bordered.height], fill=bc)
        bordered.paste(img, (bw, bw), img)
        img = bordered

    if cfg.rotation:
        img = img.rotate(-cfg.rotation, expand=True, resample=Image.Resampling.BICUBIC)

    x = resolve(cfg.x, cw)
    y = resolve(cfg.y, ch)
    dx, dy = get_anchor_offset(cfg.anchor, img.width, img.height)
    x += dx
    y += dy

    if cfg.shadow:
        sh_c = parse_color(cfg.shadow.color)
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        mask_col = Image.new("RGBA", img.size,
                             (sh_c[0], sh_c[1], sh_c[2], sh_c[3]))
        if img.mode == "RGBA":
            mask_col.putalpha(img.split()[3])
        sx, sy = x + int(cfg.shadow.offset_x), y + int(cfg.shadow.offset_y)
        sh.paste(mask_col, (sx, sy), mask_col)
        if cfg.shadow.blur_radius > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(cfg.shadow.blur_radius))
        canvas = Image.alpha_composite(canvas, sh)

    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(img, (x, y), img)
    return Image.alpha_composite(canvas, tmp)
