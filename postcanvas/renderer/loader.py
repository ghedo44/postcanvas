from __future__ import annotations

from io import BytesIO
from typing import Optional

import requests
from PIL import Image

from ..models import ImageFit


def load_image(src: str) -> Optional[Image.Image]:
    if src.startswith(("http://", "https://")):
        try:
            response = requests.get(src, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
        except (requests.RequestException, OSError) as exc:
            print(f"Could not fetch image {src}: {exc}")
            return None
    try:
        return Image.open(src).convert("RGBA")
    except OSError as exc:
        print(f"Could not open image {src}: {exc}")
        return None


def fit_image(
    image: Image.Image,
    width: int,
    height: int,
    fit: ImageFit,
    focal_x: float = 0.5,
    focal_y: float = 0.5,
) -> Image.Image:
    """Fit an image into a target box using a normalized focal point for crops."""

    if fit == ImageFit.FILL:
        return image.resize((width, height), Image.Resampling.LANCZOS)
    image_ratio = image.width / image.height
    target_ratio = width / height
    if fit == ImageFit.COVER:
        new_width, new_height = (
            (width, int(round(width / image_ratio)))
            if image_ratio < target_ratio
            else (int(round(height * image_ratio)), height)
        )
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        max_left = max(0, resized.width - width)
        max_top = max(0, resized.height - height)
        left = int(round(max_left * min(1.0, max(0.0, focal_x))))
        top = int(round(max_top * min(1.0, max(0.0, focal_y))))
        return resized.crop((left, top, left + width, top + height))
    if fit == ImageFit.CONTAIN:
        new_width, new_height = (
            (width, int(round(width / image_ratio)))
            if image_ratio > target_ratio
            else (int(round(height * image_ratio)), height)
        )
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image.resize(
        (min(image.width, width), min(image.height, height)),
        Image.Resampling.LANCZOS,
    )
