from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageChops, ImageStat


@dataclass(frozen=True)
class ImageDifference:
    mean_absolute_error: float
    changed_pixel_ratio: float
    bounding_box: tuple[int, int, int, int] | None


def image_difference(actual: Image.Image, expected: Image.Image) -> ImageDifference:
    """Calculate a deterministic, mode-independent visual regression metric."""

    if actual.size != expected.size:
        raise AssertionError(f"Image sizes differ: actual={actual.size}, expected={expected.size}")
    difference = ImageChops.difference(actual.convert("RGBA"), expected.convert("RGBA"))
    mean = sum(ImageStat.Stat(difference).mean) / 4
    rgb = difference.convert("RGB")
    changed = sum(1 for pixel in rgb.getdata() if pixel != (0, 0, 0))
    total = max(1, actual.width * actual.height)
    return ImageDifference(mean, changed / total, rgb.getbbox())


def assert_image_similar(actual: Image.Image, expected: Image.Image, *, max_mean_absolute_error: float = 0.0, max_changed_pixel_ratio: float = 0.0) -> None:
    difference = image_difference(actual, expected)
    if difference.mean_absolute_error > max_mean_absolute_error or difference.changed_pixel_ratio > max_changed_pixel_ratio:
        raise AssertionError(
            "Images differ beyond tolerance: "
            f"mean_absolute_error={difference.mean_absolute_error:.4f}, "
            f"changed_pixel_ratio={difference.changed_pixel_ratio:.4%}, "
            f"bounding_box={difference.bounding_box}"
        )
