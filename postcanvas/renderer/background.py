from __future__ import annotations
from PIL import Image, ImageFilter
from .utils import parse_color
from .gradient import create_gradient
from .loader import load_image, fit_image
from ..models import BackgroundConfig

def render_background(canvas: Image.Image, bg: BackgroundConfig) -> Image.Image:
    w, h = canvas.size

    if bg.color:
        canvas = Image.alpha_composite(
            canvas, Image.new("RGBA", (w, h), parse_color(bg.color))
        )

    if bg.gradient and bg.gradient.stops:
        canvas = Image.alpha_composite(canvas, create_gradient(w, h, bg.gradient))

    src = bg.image_path or bg.image_url
    if src:
        img = load_image(src)
        if img:
            img = fit_image(img, w, h, bg.image_fit)
            # pad CONTAIN result
            if img.size != (w, h):
                pad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                pad.paste(img, ((w - img.width) // 2, (h - img.height) // 2), img)
                img = pad
            if bg.image_blur > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=bg.image_blur))
            if bg.image_opacity < 1.0:
                r, g, b, a = img.split()
                a = a.point(lambda p: int(p * bg.image_opacity))
                img = Image.merge("RGBA", (r, g, b, a))
            canvas = Image.alpha_composite(canvas, img)

    if bg.overlay_color:
        c = parse_color(bg.overlay_color)
        ov = Image.new("RGBA", (w, h), (c[0], c[1], c[2], int(bg.overlay_opacity * 255)))
        canvas = Image.alpha_composite(canvas, ov)

    return canvas
