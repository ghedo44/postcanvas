from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from .background import BackgroundConfig
from .text import TextConfig
from .elements import ImageElementConfig, ShapeConfig
from .watermark import WatermarkConfig
from .meta import MetaConfig
from .primitives import PaddingConfig, FilterConfig

class CanvasConfig(BaseModel):
    """
    One slide / frame in a carousel (or the only frame for a single image).

    Every field is optional – unset fields fall back to the parent PostConfig.
    Elements (texts, images, shapes) are MERGED with the parent's by default;
    set replace_elements=True to use ONLY the elements defined here.
    """

    # Override parent dimensions
    width:  Optional[int] = None
    height: Optional[int] = None

    # Override parent background / padding
    background: Optional[BackgroundConfig] = None
    padding:    Optional[PaddingConfig]    = None

    # Default text font for this canvas (overrides PostConfig defaults)
    text_font_family: Optional[str] = None
    text_font_path:   Optional[str] = None

    # Canvas-specific elements (merged with parent unless replace_elements=True)
    texts:  List[TextConfig]         = Field(default_factory=list)
    images: List[ImageElementConfig] = Field(default_factory=list)
    shapes: List[ShapeConfig]        = Field(default_factory=list)

    # If True, these elements replace (not extend) the parent's element lists
    replace_elements: bool = False

    # Per-canvas post-processing
    canvas_filters: List[FilterConfig] = Field(default_factory=list)

    # Watermark override (None = use parent watermark)
    watermark: Optional[WatermarkConfig] = None

    # Output filename without extension (e.g. "slide_01")
    output_filename: Optional[str] = None

    meta: MetaConfig = Field(default_factory=MetaConfig)
