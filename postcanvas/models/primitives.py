from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import FilterType

class ShadowConfig(BaseModel):
    color:        str   = "rgba(0,0,0,0.5)"
    offset_x:     float = 4.0
    offset_y:     float = 4.0
    blur_radius:  float = 8.0
    spread:       float = 0.0

class StrokeConfig(BaseModel):
    color: str = "#000000"
    width: int  = 2

class GradientStop(BaseModel):
    color:    str
    position: float = Field(ge=0.0, le=1.0)

class GradientConfig(BaseModel):
    """Linear or radial gradient."""
    type:     str             = "linear"   # "linear" | "radial"
    stops:    List[GradientStop] = Field(default_factory=list)
    angle:    float           = 0.0        # degrees (linear only)
    center_x: float           = 0.5        # radial center (0-1)
    center_y: float           = 0.5
    radius:   float           = 0.7        # radial extent (0-1)

class PaddingConfig(BaseModel):
    top:    int = 0
    right:  int = 0
    bottom: int = 0
    left:   int = 0

    @classmethod
    def all(cls, v: int) -> "PaddingConfig":
        return cls(top=v, right=v, bottom=v, left=v)

    @classmethod
    def symmetric(cls, vertical: int = 0, horizontal: int = 0) -> "PaddingConfig":
        return cls(top=vertical, right=horizontal, bottom=vertical, left=horizontal)

    @classmethod
    def only(cls, *, top: int = 0, right: int = 0, bottom: int = 0, left: int = 0) -> "PaddingConfig":
        return cls(top=top, right=right, bottom=bottom, left=left)

class BorderConfig(BaseModel):
    color:  str   = "#000000"
    width:  int   = 2
    radius: float = 0.0
    style:  str   = "solid"    # solid | dashed | dotted

class FilterConfig(BaseModel):
    """Single image / layer filter."""
    type:  FilterType = FilterType.NONE
    value: float      = 1.0    # intensity / radius depending on filter type
