"""Generate validated, responsive social-media images with Python."""

from . import models, presets
from .api import RenderResult, generate, render
from .renderer import (
    GenerateResult,
    image_to_bytes,
    render_one,
    save_image_to_path,
)
from .template import LayoutNode, Template, TemplateRenderResult, TemplateVariant, Theme
from .validation import (
    LayoutIssue,
    LayoutReport,
    LayoutValidationError,
    Rect,
    validate_post,
)

from . import template as _template_module
from .layout_flow import resolve_flow_boxes as _resolve_flow_boxes

_template_module._flow_boxes = _resolve_flow_boxes

__version__ = "0.3.0"

__all__ = [
    "GenerateResult",
    "LayoutIssue",
    "LayoutNode",
    "LayoutReport",
    "LayoutValidationError",
    "Rect",
    "RenderResult",
    "Template",
    "TemplateRenderResult",
    "TemplateVariant",
    "Theme",
    "generate",
    "image_to_bytes",
    "models",
    "presets",
    "render",
    "render_one",
    "save_image_to_path",
    "validate_post",
]
