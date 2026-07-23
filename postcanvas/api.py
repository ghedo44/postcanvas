from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from typing import Any, List, Sequence

from PIL import Image

from .models import PostConfig
from .renderer import GenerateResult, image_to_bytes
from .renderer import generate as _generate
from .validation import LayoutIssue, LayoutReport, LayoutValidationError, validate_post


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


def _policy_severity(value: str) -> str | None:
    if value == "ignore":
        return None
    return "error" if value == "error" else "warning"


def _file_limits(post: PostConfig) -> List[int | None]:
    if not post.canvases:
        return [post.max_file_size_bytes]
    return [canvas.max_file_size_bytes or post.max_file_size_bytes for canvas in post.canvases]


def _sizes_from_images(post: PostConfig, images: Sequence[Image.Image]) -> List[int]:
    return [len(image_to_bytes(image, format=post.output_format, quality=post.quality)) for image in images]


def _sizes_from_paths(paths: Sequence[str]) -> List[int]:
    return [os.path.getsize(path) for path in paths]


def _apply_output_validation(post: PostConfig, reports: List[LayoutReport], *, images: Sequence[Image.Image] = (), paths: Sequence[str] = ()) -> None:
    severity = _policy_severity(post.layout_policy.file_size)
    if severity is None:
        return
    sizes = _sizes_from_images(post, images) if images else _sizes_from_paths(paths)
    for index, (size, limit) in enumerate(zip(sizes, _file_limits(post))):
        if limit is None or size <= limit:
            continue
        issue = LayoutIssue(
            code="file-too-large",
            message=f"Rendered image is {size} bytes, exceeding the configured {limit}-byte platform limit",
            severity=severity,
        )
        reports[min(index, len(reports) - 1)].issues.append(issue)
        if severity == "warning":
            warnings.warn(issue.message, UserWarning, stacklevel=3)
        else:
            raise LayoutValidationError(reports[min(index, len(reports) - 1)])


def generate(post: PostConfig, save: bool = True, return_images: bool = False):
    """Validate a post layout, render it, and preserve the legacy return contract."""

    reports = _validate(post)
    result = _generate(post, save=save, return_images=return_images)
    if isinstance(result, GenerateResult):
        _apply_output_validation(post, reports, images=result.images, paths=result.paths)
        result.reports = reports
    elif result and isinstance(result[0], Image.Image):
        _apply_output_validation(post, reports, images=result)
    else:
        _apply_output_validation(post, reports, paths=result)
    return result


def render(post: PostConfig, save: bool = False) -> RenderResult:
    """Render images and always return images, paths, and validation reports."""

    reports = _validate(post)
    result = _generate(post, save=save, return_images=True)
    if isinstance(result, GenerateResult):
        images, paths = result.images, result.paths
    else:
        images, paths = result, []
    _apply_output_validation(post, reports, images=images, paths=paths)
    return RenderResult(images=images, paths=paths, reports=reports)
