"""Generate validated, responsive social-media images with Python."""

from . import models, presets
from .text_extensions import install as _install_text_extensions
from .validation_extensions import install as _install_validation_extensions

_install_text_extensions()
_install_validation_extensions()

from .api import RenderResult, generate, render
from .renderer import GenerateResult, image_to_bytes, render_one, save_image_to_path
from .rich_text import (
    RichTextBlock,
    RichTextComposition,
    RichTextLayout,
    RichTextLineLayout,
    RichTextRunLayout,
    RichTextSpan,
    compose_rich_text,
)
from .selectors import PromptVariantSelector, VariantSelector
from .template import (
    LayoutNode,
    PreviewFixture,
    Template,
    TemplateRenderResult,
    TemplateVariant,
    Theme,
)
from .validation import (
    LayoutIssue,
    LayoutReport,
    LayoutValidationError,
    Rect,
    contrast_ratio,
    validate_post,
)

__version__ = "0.3.2"

__all__ = [
    "GenerateResult",
    "LayoutIssue",
    "LayoutNode",
    "LayoutReport",
    "LayoutValidationError",
    "PreviewFixture",
    "PromptVariantSelector",
    "Rect",
    "RenderResult",
    "RichTextBlock",
    "RichTextComposition",
    "RichTextLayout",
    "RichTextLineLayout",
    "RichTextRunLayout",
    "RichTextSpan",
    "Template",
    "TemplateRenderResult",
    "TemplateVariant",
    "Theme",
    "VariantSelector",
    "compose_rich_text",
    "contrast_ratio",
    "generate",
    "image_to_bytes",
    "models",
    "presets",
    "render",
    "render_one",
    "save_image_to_path",
    "validate_post",
]
