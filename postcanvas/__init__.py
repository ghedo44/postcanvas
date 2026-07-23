"""Generate validated, responsive social-media images with Python."""

from . import models, presets
from .text_extensions import install as _install_text_extensions
from .validation_extensions import install as _install_validation_extensions

_install_text_extensions()
_install_validation_extensions()

from .api import RenderResult, generate, render
from .renderer import GenerateResult, image_to_bytes, render_one, save_image_to_path
from .template import LayoutNode, PreviewFixture, Template, TemplateRenderResult, TemplateVariant, Theme
from .validation import LayoutIssue, LayoutReport, LayoutValidationError, Rect, contrast_ratio, validate_post

__version__ = "0.3.1"

__all__ = [
    "GenerateResult", "LayoutIssue", "LayoutNode", "LayoutReport",
    "LayoutValidationError", "PreviewFixture", "Rect", "RenderResult",
    "Template", "TemplateRenderResult", "TemplateVariant", "Theme",
    "contrast_ratio", "generate", "image_to_bytes", "models", "presets",
    "render", "render_one", "save_image_to_path", "validate_post",
]
