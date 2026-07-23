from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .background import BackgroundConfig
from .elements import ChartElementConfig, ImageElementConfig, ShapeConfig, TableElementConfig
from .layout import ExclusionZone, LayoutPolicyConfig
from .meta import MetaConfig
from .primitives import FilterConfig, PaddingConfig
from .text import TextConfig
from .watermark import WatermarkConfig


class CanvasConfig(BaseModel):
    """One slide or frame in a carousel."""

    width: Optional[int] = Field(default=None, gt=0)
    height: Optional[int] = Field(default=None, gt=0)
    background: Optional[BackgroundConfig] = None
    padding: Optional[PaddingConfig] = None
    safe_area: Optional[PaddingConfig] = None
    exclusion_zones: Optional[List[ExclusionZone]] = None
    max_file_size_bytes: Optional[int] = Field(default=None, gt=0)
    layout_policy: Optional[LayoutPolicyConfig] = None
    text_font_family: Optional[str] = None
    text_font_path: Optional[str] = None
    texts: List[TextConfig] = Field(default_factory=list)
    images: List[ImageElementConfig] = Field(default_factory=list)
    shapes: List[ShapeConfig] = Field(default_factory=list)
    tables: List[TableElementConfig] = Field(default_factory=list)
    charts: List[ChartElementConfig] = Field(default_factory=list)
    replace_elements: bool = False
    canvas_filters: List[FilterConfig] = Field(default_factory=list)
    watermark: Optional[WatermarkConfig] = None
    output_filename: Optional[str] = None
    meta: MetaConfig = Field(default_factory=MetaConfig)
