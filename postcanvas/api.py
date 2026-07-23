from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, List

from PIL import Image

from .models import PostConfig
from .renderer import GenerateResult
from .renderer import generate as _generate
from .validation import LayoutReport, LayoutValidationError, validate_post


@dataclass
class RenderResult:
    images: List[Image.Image]
    paths: List[str]
    reports: List[LayoutReport]

    @property
    def warnings(self) -> List[Any]:
        return [issue for report in self.reports for issue in report.warnings]


def _validate(post: PostConfig) -> List[LayoutReport]:
    reports = validate_post(post)
    for report in reports:
        if report.errors:
            raise LayoutValidationError(report)
        for issue in report.warnings:
            warnings.warn(issue.message, UserWarning, stacklevel=3)
    return reports


def generate(
    post: PostConfig,
    save: bool = True,
    return_images: bool = False,
):
    """Validate a post layout, then render it with the legacy return contract."""

    reports = _validate(post)
    result = _generate(post, save=save, return_images=return_images)
    if isinstance(result, GenerateResult):
        result.reports = reports
    return result


def render(post: PostConfig, save: bool = False) -> RenderResult:
    """Render images and always return images, paths, and validation reports."""

    reports = _validate(post)
    result = _generate(post, save=save, return_images=True)
    if isinstance(result, GenerateResult):
        images = result.images
        paths = result.paths
    else:
        images = result
        paths = []
    return RenderResult(images=images, paths=paths, reports=reports)
