from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator
from .enums import TextAlign, FontWeight, BlendMode, TextTransform, Dimension
from .primitives import ShadowConfig, StrokeConfig, FilterConfig


TextFit = Literal["none", "shrink", "truncate", "error"]
TextOverflow = Literal["visible", "clip", "ellipsis", "error"]


class TextConfig(BaseModel):
    content: str

    # Position (absolute px or "50%")
    x: Dimension = "50%"
    y: Dimension = "50%"

    # Optional bounded text box. max_width remains backward compatible.
    width: Optional[Dimension] = None
    height: Optional[Dimension] = None
    max_width: Optional[Dimension] = None
    max_height: Optional[Dimension] = None

    # Font
    font_family: Optional[str] = None
    font_path: Optional[str] = None
    font_size: int = Field(default=48, ge=1)
    min_font_size: int = Field(default=12, ge=1)
    font_weight: FontWeight = FontWeight.REGULAR
    italic: bool = False

    # Responsive fitting
    fit: TextFit = "none"
    overflow: TextOverflow = "visible"
    max_lines: Optional[int] = Field(default=None, ge=1)
    break_long_words: bool = True
    preserve_newlines: bool = True

    # Style
    color: str = "#FFFFFF"
    align: TextAlign = TextAlign.CENTER
    vertical_align: Literal["top", "middle", "bottom"] = "top"
    transform: TextTransform = TextTransform.NONE
    line_spacing: float = Field(default=1.3, gt=0)
    letter_spacing: int = 0
    auto_contrast: bool = False
    contrast_light_color: str = "#FFFFFF"
    contrast_dark_color: str = "#111111"
    contrast_threshold: int = Field(default=145, ge=0, le=255)

    # Decorations
    shadow: Optional[ShadowConfig] = None
    stroke: Optional[StrokeConfig] = None
    background_color: Optional[str] = None
    background_padding: int = Field(default=10, ge=0)
    background_radius: float = Field(default=6.0, ge=0)

    # Compositing
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    rotation: float = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index: int = 10
    visible: bool = True

    # Anchor point for x/y position
    anchor: str = "center"

    # Per-element filters
    filters: List[FilterConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_text_fit(self) -> "TextConfig":
        if self.min_font_size > self.font_size:
            raise ValueError("min_font_size cannot exceed font_size")
        if self.fit == "shrink" and not (self.height or self.max_height or self.max_lines):
            # Width-only shrinking is still useful and intentionally supported.
            return self
        return self
