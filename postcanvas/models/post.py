from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import Platform, PostFormat, OutputFormat
from .background import BackgroundConfig
from .text import TextConfig
from .elements import ImageElementConfig, ShapeConfig, TableElementConfig, ChartElementConfig
from .watermark import WatermarkConfig
from .meta import MetaConfig
from .primitives import PaddingConfig, FilterConfig
from .canvas import CanvasConfig

class PostConfig(BaseModel):
    """
    Root configuration for a social-media post.

    All settings here act as DEFAULTS for every canvas.
    A CanvasConfig inside `canvases` can override any of them.

    Single image  → leave `canvases` empty.
    Carousel      → populate `canvases` (one entry per slide).
    """

    # ── Platform & format preset ─────────────────────────────────────────────
    platform: Platform   = Platform.INSTAGRAM
    format:   PostFormat = PostFormat.SQUARE

    # ── Canvas dimensions ────────────────────────────────────────────────────
    width:  int = 1080
    height: int = 1080

    # ── Background (default for all slides) ──────────────────────────────────
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)

    # ── Safe-area padding ────────────────────────────────────────────────────
    padding: PaddingConfig = Field(default_factory=PaddingConfig)

    # ── Default text font (can be overridden by canvas/text) ───────────────
    text_font_family: Optional[str] = None
    text_font_path:   Optional[str] = None

    # ── Global elements (appear on EVERY slide unless overridden) ────────────
    texts:  List[TextConfig]         = Field(default_factory=list)
    images: List[ImageElementConfig] = Field(default_factory=list)
    shapes: List[ShapeConfig]        = Field(default_factory=list)
    tables: List[TableElementConfig] = Field(default_factory=list)
    charts: List[ChartElementConfig] = Field(default_factory=list)

    # ── Slides (carousel / multi-image) ──────────────────────────────────────
    canvases: List[CanvasConfig] = Field(default_factory=list)

    # ── Post-processing ──────────────────────────────────────────────────────
    canvas_filters: List[FilterConfig]    = Field(default_factory=list)
    watermark:      Optional[WatermarkConfig] = None

    # ── Output ───────────────────────────────────────────────────────────────
    output_dir:      str          = "./output"
    output_format:   OutputFormat = OutputFormat.PNG
    output_filename: str          = "post"
    quality:         int          = Field(default=95, ge=1, le=100)
    dpi:             int          = 96

    # ── Metadata ─────────────────────────────────────────────────────────────
    meta: MetaConfig = Field(default_factory=MetaConfig)

    @property
    def slide_count(self) -> int:
        return max(1, len(self.canvases))
