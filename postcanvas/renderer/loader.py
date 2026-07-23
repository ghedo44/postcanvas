from __future__ import annotations

from io import BytesIO
from typing import Optional

import requests
from PIL import Image, ImageFilter, ImageOps, ImageStat

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


def estimate_focal_point(image: Image.Image) -> tuple[float, float]:
    """Estimate a deterministic crop focal point from local contrast and edges."""

    preview = image.convert("RGB")
    preview.thumbnail((128, 128), Image.Resampling.BOX)
    grayscale = ImageOps.autocontrast(preview.convert("L"))
    edges = grayscale.filter(ImageFilter.FIND_EDGES)
    edge_values = list(edges.getdata())
    contrast = ImageStat.Stat(grayscale).stddev[0]
    if not edge_values or contrast < 2.0:
        return 0.5, 0.5

    width, height = edges.size
    total = weighted_x = weighted_y = 0.0
    for y in range(height):
        normalized_y = (y + 0.5) / height
        for x in range(width):
            normalized_x = (x + 0.5) / width
            edge = edge_values[y * width + x] / 255.0
            center_distance = ((normalized_x - 0.5) ** 2 + (normalized_y - 0.5) ** 2) ** 0.5
            center_bias = 1.15 - min(0.65, center_distance)
            weight = edge * center_bias
            total += weight
            weighted_x += normalized_x * weight
            weighted_y += normalized_y * weight
    if total <= 1e-6:
        return 0.5, 0.5
    return min(1.0, max(0.0, weighted_x / total)), min(1.0, max(0.0, weighted_y / total))


def fit_image(
    image: Image.Image,
    width: int,
    height: int,
    fit: ImageFit,
    focal_x: float = 0.5,
    focal_y: float = 0.5,
    focal_mode: str = "manual",
) -> Image.Image:
    """Fit an image into a target box using manual or automatic focal cropping."""

    if focal_mode == "auto":
        focal_x, focal_y = estimate_focal_point(image)
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
    return image.resize((min(image.width, width), min(image.height, height)), Image.Resampling.LANCZOS)
