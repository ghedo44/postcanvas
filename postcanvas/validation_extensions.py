from __future__ import annotations

import os
from typing import Any, List, Optional

from .models import CanvasConfig, ExclusionZone, PostConfig, TextConfig
from .renderer.utils import parse_color, resolve


def _severity(value: str) -> Optional[str]:
    if value == "ignore":
        return None
    return "error" if value == "error" else "warning"


def _luminance(color: tuple[int, int, int, int]) -> float:
    def channel(value: int) -> float:
        normalized = value / 255.0
        return normalized / 12.92 if normalized <= 0.03928 else ((normalized + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color[0]) + 0.7152 * channel(color[1]) + 0.0722 * channel(color[2])


def contrast_ratio(foreground: str, background: str) -> float:
    left = _luminance(parse_color(foreground))
    right = _luminance(parse_color(background))
    lighter, darker = max(left, right), min(left, right)
    return (lighter + 0.05) / (darker + 0.05)


def _merged(post: PostConfig, slide: Optional[CanvasConfig]) -> List[Any]:
    if slide and slide.replace_elements:
        return [*slide.shapes, *slide.images, *slide.tables, *slide.charts, *slide.texts]
    return [
        *post.shapes, *(slide.shapes if slide else []),
        *post.images, *(slide.images if slide else []),
        *post.tables, *(slide.tables if slide else []),
        *post.charts, *(slide.charts if slide else []),
        *post.texts, *(slide.texts if slide else []),
    ]


def _zone_rect(validation: Any, zone: ExclusionZone, width: int, height: int) -> Any:
    return validation.Rect(
        resolve(zone.x, width), resolve(zone.y, height),
        resolve(zone.width, width), resolve(zone.height, height),
    )


def install() -> None:
    """Extend the base validator with platform UI, font, and contrast checks."""

    from . import validation

    if getattr(validation, "_advanced_installed", False):
        return
    original = validation.validate_post

    def validate_post(post: PostConfig):
        reports = original(post)
        slides: List[Optional[CanvasConfig]] = list(post.canvases) or [None]
        for report, slide in zip(reports, slides):
            width = (slide.width if slide and slide.width else None) or post.width
            height = (slide.height if slide and slide.height else None) or post.height
            elements = _merged(post, slide)
            zones = (
                slide.exclusion_zones
                if slide and slide.exclusion_zones is not None
                else post.exclusion_zones
            )
            policy = (slide.layout_policy if slide and slide.layout_policy else None) or post.layout_policy
            background = (slide.background if slide and slide.background else None) or post.background
            background_color = background.color if background else None

            zone_severity = _severity(policy.exclusion_zones)
            contrast_severity = _severity(policy.contrast)
            font_severity = _severity(policy.missing_fonts)
            for index, element in enumerate(elements):
                if not getattr(element, "visible", True):
                    continue
                element_id = validation._element_id(element, index)
                bounds = report.elements.get(element_id)
                if bounds is None:
                    continue
                if zone_severity and getattr(element, "respect_exclusion_zones", True):
                    for zone in zones:
                        if bounds.intersects(_zone_rect(validation, zone, width, height), policy.allow_touching):
                            report.issues.append(validation.LayoutIssue(
                                code="platform-ui-overlap",
                                message=f"{element_id} overlaps platform UI zone {zone.name!r}",
                                severity=zone_severity,
                                element_id=element_id,
                                bounds=bounds,
                            ))
                if isinstance(element, TextConfig):
                    if font_severity:
                        for path in [element.font_path, *element.font_fallback_paths]:
                            if path and not os.path.isfile(path):
                                report.issues.append(validation.LayoutIssue(
                                    code="missing-font",
                                    message=f"{element_id} references missing font {path!r}",
                                    severity=font_severity,
                                    element_id=element_id,
                                    bounds=bounds,
                                ))
                    if contrast_severity and not element.auto_contrast:
                        surface = element.background_color or background_color
                        if surface:
                            ratio = contrast_ratio(element.color, surface)
                            if ratio < policy.min_contrast_ratio:
                                report.issues.append(validation.LayoutIssue(
                                    code="low-contrast",
                                    message=(f"{element_id} contrast ratio {ratio:.2f}:1 is below "
                                             f"{policy.min_contrast_ratio:.2f}:1"),
                                    severity=contrast_severity,
                                    element_id=element_id,
                                    bounds=bounds,
                                ))
        return reports

    validation.validate_post = validate_post
    validation.contrast_ratio = contrast_ratio
    validation._advanced_installed = True
