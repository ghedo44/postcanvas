from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from .enums import BlendMode, Dimension, FontWeight, TextAlign, TextTransform
from .primitives import FilterConfig, ShadowConfig, StrokeConfig

TextFit = Literal["none", "shrink", "truncate", "error"]
TextOverflow = Literal["visible", "clip", "ellipsis", "error"]
TextWrapMode = Literal["greedy", "balanced"]
TextDirection = Literal["ltr", "rtl", "ttb"]
TextDecoration = Literal["none", "underline", "strikethrough"]


class TextConfig(BaseModel):
    content: str
    id: Optional[str] = None
    collision_group: Optional[str] = None
    allow_overlap_with: List[str] = Field(default_factory=list)
    respect_safe_area: bool = True
    respect_exclusion_zones: bool = True

    x: Dimension = "50%"
    y: Dimension = "50%"
    width: Optional[Dimension] = None
    height: Optional[Dimension] = None
    max_width: Optional[Dimension] = None
    max_height: Optional[Dimension] = None

    font_family: Optional[str] = None
    font_path: Optional[str] = None
    font_fallback_paths: List[str] = Field(default_factory=list)
    font_size: int = Field(default=48, ge=1)
    min_font_size: int = Field(default=12, ge=1)
    font_weight: FontWeight = FontWeight.REGULAR
    italic: bool = False
    variation_name: Optional[str] = None
    variation_axes: List[float] = Field(default_factory=list)

    fit: TextFit = "none"
    overflow: TextOverflow = "visible"
    wrap_mode: TextWrapMode = "greedy"
    max_lines: Optional[int] = Field(default=None, ge=1)
    break_long_words: bool = True
    preserve_newlines: bool = True
    widow_control: bool = False
    min_first_line_words: int = Field(default=1, ge=1)
    min_last_line_words: int = Field(default=1, ge=1)

    color: str = "#FFFFFF"
    align: TextAlign = TextAlign.CENTER
    vertical_align: Literal["top", "middle", "bottom"] = "top"
    transform: TextTransform = TextTransform.NONE
    line_spacing: float = Field(default=1.3, gt=0)
    paragraph_spacing: float = Field(default=0.0, ge=0)
    letter_spacing: int = 0
    word_spacing: int = 0
    decoration: TextDecoration = "none"
    language: Optional[str] = None
    direction: Optional[TextDirection] = None
    features: List[str] = Field(default_factory=list)
    auto_contrast: bool = False
    contrast_light_color: str = "#FFFFFF"
    contrast_dark_color: str = "#111111"
    contrast_threshold: int = Field(default=145, ge=0, le=255)

    shadow: Optional[ShadowConfig] = None
    stroke: Optional[StrokeConfig] = None
    background_color: Optional[str] = None
    background_padding: int = Field(default=10, ge=0)
    background_radius: float = Field(default=6.0, ge=0)

    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    rotation: float = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index: int = 10
    visible: bool = True
    anchor: str = "center"
    filters: List[FilterConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_text_fit(self) -> "TextConfig":
        if self.min_font_size > self.font_size:
            raise ValueError("min_font_size cannot exceed font_size")
        return self
