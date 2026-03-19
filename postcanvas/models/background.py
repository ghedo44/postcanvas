from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from .enums import ImageFit
from .primitives import GradientConfig

class BackgroundConfig(BaseModel):
    # Solid colour (hex / rgb() / rgba())
    color: Optional[str] = None

    # Gradient (overrides colour when set)
    gradient: Optional[GradientConfig] = None

    # Image source (local path or URL)
    image_path:    Optional[str]   = None
    image_url:     Optional[str]   = None
    image_fit:     ImageFit        = ImageFit.COVER
    image_opacity: float           = Field(default=1.0, ge=0.0, le=1.0)
    image_blur:    float           = 0.0

    # Colour overlay painted on top of the image
    overlay_color:   Optional[str] = None
    overlay_opacity: float         = Field(default=0.4, ge=0.0, le=1.0)
