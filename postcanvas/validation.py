from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional

from PIL import Image

from .models import (
    CanvasConfig,
    ChartElementConfig,
    ImageElementConfig,
    LayoutPolicyConfig,
    PaddingConfig,
    PostConfig,
    ShapeConfig,
    TableElementConfig,
    TextConfig,
)
from .renderer.text import measure_text
from .renderer.utils import get_anchor_offset, resolve


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def contains(self, other: "Rect") -> bool:
        return (
            other.x >= self.x
            and other.y >= self.y
            and other.right <= self.right
            and other.bottom <= self.bottom
        )

    def intersects(self, other: "Rect", allow_touching: bool = True) -> bool:
        if allow_touching:
            return not (
                self.right <= other.x
                or other.right <= self.x
                or self.bottom <= other.y
                or other.bottom <= self.y
            )
        return not (
            self.right < other.x
            or other.right < self.x
            or self.bottom < other.y
            or other.bottom < self.y
        )


@dataclass(frozen=True)
class LayoutIssue:
    code: str
    message: str
    severity: str
    element_id: Optional[str] = None
    related_element_id: Optional[str] = None
    bounds: Optional[Rect] = None


@dataclass
class LayoutReport:
    width: int
    height: int
    elements: dict[str, Rect] = field(default_factory=dict)
    issues: List[LayoutIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LayoutIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> List[LayoutIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def valid(self) -> bool:
        return not self.errors


class LayoutValidationError(ValueError):
    def __init__(self, report: LayoutReport):
        self.report = report
        details = "; ".join(issue.message for issue in report.errors)
        super().__init__(details or "Layout validation failed")


def _severity(policy: str) -> Optional[str]:
    if policy == "ignore":
        return None
    return "error" if policy == "error" else "warning"


def _element_id(element: Any, index: int) -> str:
    configured = getattr(element, "id", None)
    if configured:
        return str(configured)
    name = type(element).__name__.removesuffix("Config").lower()
    return f"{name}-{index + 1}"


def _rotated_bounds(rect: Rect, degrees: float) -> Rect:
    if not degrees:
        return rect
    radians = math.radians(abs(degrees) % 180)
    width = abs(rect.width * math.cos(radians)) + abs(
        rect.height * math.sin(radians)
    )
    height = abs(rect.width * math.sin(radians)) + abs(
        rect.height * math.cos(radians)
    )
    center_x = rect.x + rect.width / 2
    center_y = rect.y + rect.height / 2
    return Rect(
        int(round(center_x - width / 2)),
        int(round(center_y - height / 2)),
        int(math.ceil(width)),
        int(math.ceil(height)),
    )


def _intrinsic_image_size(element: ImageElementConfig) -> tuple[int, int]:
    if element.width is not None and element.height is not None:
        return 0, 0
    if element.src.startswith(("http://", "https://")) or not os.path.exists(
        element.src
    ):
        return 0, 0
    with Image.open(element.src) as image:
        return image.size


def resolve_element_bounds(
    element: Any,
    canvas_width: int,
    canvas_height: int,
    padding: PaddingConfig,
) -> tuple[Rect, Optional[bool]]:
    overflowed: Optional[bool] = None
    if isinstance(element, TextConfig):
        layout = measure_text(element, canvas_width, canvas_height, padding)
        width = (
            resolve(element.width, canvas_width)
            if element.width is not None
            else layout.width
        )
        height = (
            resolve(element.height, canvas_height)
            if element.height is not None
            else layout.height
        )
        overflowed = layout.overflowed
    elif isinstance(element, ImageElementConfig):
        intrinsic_width, intrinsic_height = _intrinsic_image_size(element)
        width = (
            resolve(element.width, canvas_width)
            if element.width is not None
            else intrinsic_width
        )
        height = (
            resolve(element.height, canvas_height)
            if element.height is not None
            else intrinsic_height
        )
    elif isinstance(element, (ShapeConfig, TableElementConfig, ChartElementConfig)):
        width = resolve(element.width, canvas_width)
        height = resolve(element.height, canvas_height)
    else:
        raise TypeError(f"Unsupported element type for validation: {type(element)!r}")

    width = max(0, int(width))
    height = max(0, int(height))
    x = resolve(element.x, canvas_width)
    y = resolve(element.y, canvas_height)
    dx, dy = get_anchor_offset(element.anchor, width, height)
    rect = Rect(x + dx, y + dy, width, height)
    return _rotated_bounds(
        rect, float(getattr(element, "rotation", 0.0))
    ), overflowed


def validate_elements(
    elements: Iterable[Any],
    canvas_width: int,
    canvas_height: int,
    padding: PaddingConfig,
    safe_area: Optional[PaddingConfig] = None,
    policy: Optional[LayoutPolicyConfig] = None,
) -> LayoutReport:
    policy = policy or LayoutPolicyConfig()
    report = LayoutReport(width=canvas_width, height=canvas_height)
    canvas_rect = Rect(0, 0, canvas_width, canvas_height)
    safe = safe_area or padding
    safe_rect = Rect(
        safe.left,
        safe.top,
        max(0, canvas_width - safe.left - safe.right),
        max(0, canvas_height - safe.top - safe.bottom),
    )
    tracked: List[tuple[Any, str, Rect]] = []

    for index, element in enumerate(elements):
        if not getattr(element, "visible", True):
            continue
        element_id = _element_id(element, index)
        try:
            bounds, overflowed = resolve_element_bounds(
                element,
                canvas_width,
                canvas_height,
                padding,
            )
        except (OSError, ValueError, TypeError) as exc:
            report.issues.append(
                LayoutIssue(
                    code="unmeasurable",
                    message=f"Could not measure {element_id}: {exc}",
                    severity="warning",
                    element_id=element_id,
                )
            )
            continue
        report.elements[element_id] = bounds

        bounds_severity = _severity(policy.canvas_bounds)
        if bounds_severity and not canvas_rect.contains(bounds):
            report.issues.append(
                LayoutIssue(
                    code="outside-canvas",
                    message=f"{element_id} extends outside the canvas",
                    severity=bounds_severity,
                    element_id=element_id,
                    bounds=bounds,
                )
            )

        safe_severity = _severity(policy.safe_area)
        if safe_severity and not safe_rect.contains(bounds):
            report.issues.append(
                LayoutIssue(
                    code="outside-safe-area",
                    message=f"{element_id} extends outside the configured safe area",
                    severity=safe_severity,
                    element_id=element_id,
                    bounds=bounds,
                )
            )

        overflow_severity = _severity(policy.text_overflow)
        if overflow_severity and overflowed:
            report.issues.append(
                LayoutIssue(
                    code="text-overflow",
                    message=f"{element_id} text exceeds its configured box",
                    severity=overflow_severity,
                    element_id=element_id,
                    bounds=bounds,
                )
            )
        tracked.append((element, element_id, bounds))

    collision_severity = _severity(policy.collision)
    if collision_severity:
        for left_index, (left, left_id, left_bounds) in enumerate(tracked):
            left_group = getattr(left, "collision_group", None)
            if not left_group or left_bounds.width == 0 or left_bounds.height == 0:
                continue
            for right, right_id, right_bounds in tracked[left_index + 1 :]:
                right_group = getattr(right, "collision_group", None)
                if left_group != right_group:
                    continue
                allowed_left = set(getattr(left, "allow_overlap_with", []))
                allowed_right = set(getattr(right, "allow_overlap_with", []))
                if right_id in allowed_left or left_id in allowed_right:
                    continue
                if left_bounds.intersects(right_bounds, policy.allow_touching):
                    report.issues.append(
                        LayoutIssue(
                            code="collision",
                            message=f"{left_id} overlaps {right_id}",
                            severity=collision_severity,
                            element_id=left_id,
                            related_element_id=right_id,
                            bounds=left_bounds,
                        )
                    )
    return report


def _merged_elements(post: PostConfig, slide: Optional[CanvasConfig]) -> List[Any]:
    if slide and slide.replace_elements:
        return [
            *slide.shapes,
            *slide.images,
            *slide.tables,
            *slide.charts,
            *slide.texts,
        ]
    return [
        *post.shapes,
        *(slide.shapes if slide else []),
        *post.images,
        *(slide.images if slide else []),
        *post.tables,
        *(slide.tables if slide else []),
        *post.charts,
        *(slide.charts if slide else []),
        *post.texts,
        *(slide.texts if slide else []),
    ]


def validate_post(post: PostConfig) -> List[LayoutReport]:
    slides: List[Optional[CanvasConfig]] = list(post.canvases) or [None]
    reports: List[LayoutReport] = []
    for slide in slides:
        width = (slide.width if slide and slide.width else None) or post.width
        height = (slide.height if slide and slide.height else None) or post.height
        padding = (slide.padding if slide and slide.padding else None) or post.padding
        safe_area = (
            (slide.safe_area if slide and slide.safe_area else None)
            or post.safe_area
        )
        policy = (
            (slide.layout_policy if slide and slide.layout_policy else None)
            or post.layout_policy
        )
        reports.append(
            validate_elements(
                _merged_elements(post, slide),
                width,
                height,
                padding,
                safe_area=safe_area,
                policy=policy,
            )
        )
    return reports
