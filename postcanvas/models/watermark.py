from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

class WatermarkConfig(BaseModel):
    text:        Optional[str] = None
    image_path:  Optional[str] = None
    # top_left | top_right | bottom_left | bottom_right | center
    position:    str   = "bottom_right"
    opacity:     float = Field(default=0.6, ge=0.0, le=1.0)
    padding:     int   = 20
    font_size:   int   = 24
    color:       str   = "#FFFFFF"
    font_path:   Optional[str] = None
    scale:       float = 1.0
