from __future__ import annotations
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from .enums import ImageFit, BlendMode, ShapeType, Dimension
from .primitives import ShadowConfig, BorderConfig, FilterConfig, GradientConfig
from .text import TextConfig

class ImageElementConfig(BaseModel):
    src: str                                 # local path or URL

    # Position & size
    x:      Dimension         = "50%"
    y:      Dimension         = "50%"
    width:  Optional[Dimension] = None       # None = intrinsic
    height: Optional[Dimension] = None
    fit:    ImageFit          = ImageFit.CONTAIN
    anchor: str               = "center"

    # Visual
    border_radius:   float  = 0.0
    opacity:         float  = Field(default=1.0, ge=0.0, le=1.0)
    rotation:        float  = 0.0
    flip_horizontal: bool   = False
    flip_vertical:   bool   = False

    # Adjustments (1.0 = neutral)
    brightness: float = 1.0
    contrast:   float = 1.0
    saturation: float = 1.0

    # Decorations
    shadow: Optional[ShadowConfig] = None
    border: Optional[BorderConfig] = None
    texts:  List[TextConfig]       = Field(default_factory=list)

    # Compositing
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 5
    visible:    bool      = True
    filters:    List[FilterConfig] = Field(default_factory=list)

class ShapeConfig(BaseModel):
    type: ShapeType = ShapeType.RECTANGLE

    # Position & size
    x:      Dimension = 0
    y:      Dimension = 0
    width:  Dimension = 100
    height: Dimension = 100
    anchor: str       = "topleft"

    # Fill
    fill_color:     Optional[str]            = None
    fill_gradient:  Optional[GradientConfig] = None

    # Stroke
    stroke_color: Optional[str] = None
    stroke_width: int           = 0

    # Shape-specific
    border_radius: float              = 0.0       # ROUNDED_RECTANGLE
    sides:         int                = 6         # POLYGON (regular)
    star_points:   int                = 5         # STAR
    star_inner_r:  float              = 0.4       # STAR inner ratio
    points:        Optional[List[Tuple[float, float]]] = None  # POLYGON custom

    # Compositing
    opacity:    float     = Field(default=1.0, ge=0.0, le=1.0)
    rotation:   float     = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index:    int       = 1
    visible:    bool      = True
    shadow:     Optional[ShadowConfig] = None
    texts:      List[TextConfig]       = Field(default_factory=list)
