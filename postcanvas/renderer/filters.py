from __future__ import annotations
from PIL import Image, ImageFilter, ImageEnhance, ImageChops
from ..models import FilterConfig, FilterType

def apply_filter(img: Image.Image, f: FilterConfig) -> Image.Image:
    t = f.type
    if t == FilterType.BLUR:
        return img.filter(ImageFilter.GaussianBlur(radius=f.value))
    if t == FilterType.SHARPEN:
        return ImageEnhance.Sharpness(img).enhance(f.value)
    if t == FilterType.GRAYSCALE:
        gray = img.convert("L").convert("RGBA")
        return Image.blend(img, gray, max(0.0, min(1.0, f.value)))
    if t == FilterType.BRIGHTNESS:
        return ImageEnhance.Brightness(img).enhance(f.value)
    if t == FilterType.CONTRAST:
        return ImageEnhance.Contrast(img).enhance(f.value)
    if t == FilterType.SATURATION:
        return ImageEnhance.Color(img).enhance(f.value)
    if t == FilterType.INVERT:
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            inv = ImageChops.invert(Image.merge("RGB", (r, g, b)))
            return Image.merge("RGBA", (*inv.split(), a))
        return ImageChops.invert(img)
    if t == FilterType.SEPIA:
        gray = img.convert("L")
        sepia = Image.new("RGBA", img.size)
        gp, sp = gray.load(), sepia.load()
        for y in range(img.height):
            for x in range(img.width):
                g = gp[x, y]
                sp[x, y] = (min(255, int(g * 1.1)), min(255, int(g * 0.9)),
                             min(255, int(g * 0.7)), 255)
        return Image.blend(img.convert("RGBA"), sepia, max(0.0, min(1.0, f.value)))
    if t == FilterType.VIGNETTE:
        import math
        vig = Image.new("RGBA", img.size, (0, 0, 0, 0))
        from PIL import ImageDraw as ID
        draw = ID.Draw(vig)
        w, h = img.size
        for i in range(20):
            pct = i / 20
            alpha = int(255 * pct * f.value)
            pad = int(min(w, h) * 0.5 * (1 - pct))
            draw.ellipse([pad, pad, w - pad, h - pad],
                         fill=(0, 0, 0, 0), outline=(0, 0, 0, alpha), width=max(1, int(pad * 0.1)))
        return Image.alpha_composite(img.convert("RGBA"), vig)
    return img
