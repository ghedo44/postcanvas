from __future__ import annotations
import os
from typing import Optional
from PIL import Image
from ..models import ImageFit

def load_image(src: str) -> Optional[Image.Image]:
    if src.startswith(("http://", "https://")):
        try:
            import requests
            from io import BytesIO
            r = requests.get(src, timeout=10)
            r.raise_for_status()
            return Image.open(BytesIO(r.content)).convert("RGBA")
        except Exception as e:
            print(f"⚠  Could not fetch image {src}: {e}")
            return None
    try:
        return Image.open(src).convert("RGBA")
    except Exception as e:
        print(f"⚠  Could not open image {src}: {e}")
        return None

def fit_image(img: Image.Image, w: int, h: int, fit: ImageFit) -> Image.Image:
    if fit == ImageFit.FILL:
        return img.resize((w, h), Image.LANCZOS)
    ir, tr = img.width / img.height, w / h
    if fit == ImageFit.COVER:
        nw, nh = (w, int(w / ir)) if ir < tr else (int(h * ir), h)
        img = img.resize((nw, nh), Image.LANCZOS)
        l, t = (img.width - w) // 2, (img.height - h) // 2
        return img.crop((l, t, l + w, t + h))
    if fit == ImageFit.CONTAIN:
        nw, nh = (w, int(w / ir)) if ir > tr else (int(h * ir), h)
        return img.resize((nw, nh), Image.LANCZOS)
    # CENTER
    return img.resize((min(img.width, w), min(img.height, h)), Image.LANCZOS)
