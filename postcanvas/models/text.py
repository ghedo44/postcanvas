from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import TextAlign, FontWeight, BlendMode, TextTransform, Dimension
from .primitives import ShadowConfig, StrokeConfig, FilterConfig

class TextConfig(BaseModel):
    content: str

    # Position  (absolute px or "50%")
    x: Dimension = "50%"
    y: Dimension = "50%"

    # Font
    font_family:  Optional[str]   = None    # None = inherit (or fallback to Arial)
    font_path:    Optional[str]   = None    # path to .ttf/.otf
    font_size:    int             = 48
    font_weight:  FontWeight      = FontWeight.REGULAR
    italic:       bool            = False

    # Style
    color:          str             = "#FFFFFF"
    align:          TextAlign       = TextAlign.CENTER
    vertical_align: str             = "top"         # top | middle | bottom
    transform:      TextTransform   = TextTransform.NONE
    max_width:      Optional[Dimension] = None       # text wrapping boundary
    line_spacing:   float           = 1.3
    letter_spacing: int             = 0
    auto_contrast:  bool            = False          # adapt text against background under each line
    contrast_light_color: str       = "#FFFFFF"     # used on dark background
    contrast_dark_color:  str       = "#111111"     # used on light background
    contrast_threshold:   int       = Field(default=145, ge=0, le=255)

    # Decorations
    shadow:               Optional[ShadowConfig] = None
    stroke:               Optional[StrokeConfig] = None
    background_color:     Optional[str]          = None  # highlight/pill bg
    background_padding:   int                    = 10
    background_radius:    float                  = 6.0

    # Compositing
    opacity:    float     = Field(default=1.0, ge=0.0, le=1.0)
    rotation:   float     = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 10
    visible:    bool      = True

    # Anchor point for x/y position
    # Options: topleft | topcenter | topright | left | center | right
    #          bottomleft | bottomcenter | bottomright
    anchor: str = "center"

    # Per-element filters
    filters: List[FilterConfig] = Field(default_factory=list)
