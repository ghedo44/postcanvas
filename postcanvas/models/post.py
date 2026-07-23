from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .background import BackgroundConfig
from .canvas import CanvasConfig
from .elements import (
    ChartElementConfig,
    ImageElementConfig,
    ShapeConfig,
    TableElementConfig,
)
from .enums import OutputFormat, Platform, PostFormat
from .layout import LayoutPolicyConfig
from .meta import MetaConfig
from .primitives import FilterConfig, PaddingConfig
from .text import TextConfig
from .watermark import WatermarkConfig


class PostConfig(BaseModel):
    """Root configuration for a social-media post or carousel."""

    platform: Platform = Platform.INSTAGRAM
    format: PostFormat = PostFormat.SQUARE
    width: int = Field(default=1080, gt=0)
    height: int = Field(default=1080, gt=0)
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    padding: PaddingConfig = Field(default_factory=PaddingConfig)
    safe_area: Optional[PaddingConfig] = None
    layout_policy: LayoutPolicyConfig = Field(default_factory=LayoutPolicyConfig)
    text_font_family: Optional[str] = None
    text_font_path: Optional[str] = None
    texts: List[TextConfig] = Field(default_factory=list)
    images: List[ImageElementConfig] = Field(default_factory=list)
    shapes: List[ShapeConfig] = Field(default_factory=list)
    tables: List[TableElementConfig] = Field(default_factory=list)
    charts: List[ChartElementConfig] = Field(default_factory=list)
    canvases: List[CanvasConfig] = Field(default_factory=list)
    canvas_filters: List[FilterConfig] = Field(default_factory=list)
    watermark: Optional[WatermarkConfig] = None
    output_dir: str = "./output"
    output_format: OutputFormat = OutputFormat.PNG
    output_filename: str = "post"
    quality: int = Field(default=95, ge=1, le=100)
    dpi: int = Field(default=96, gt=0)
    meta: MetaConfig = Field(default_factory=MetaConfig)

    @property
    def slide_count(self) -> int:
        return max(1, len(self.canvases))
