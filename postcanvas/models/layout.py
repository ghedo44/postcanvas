from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .enums import Dimension, OutputFormat
from .primitives import PaddingConfig

CollisionPolicy = Literal["ignore", "warn", "error"]
BoundsPolicy = Literal["ignore", "warn", "error"]
SafeAreaPolicy = Literal["ignore", "warn", "error"]


class ExclusionZone(BaseModel):
    """A platform UI region that important content should avoid."""

    name: str
    x: Dimension
    y: Dimension
    width: Dimension
    height: Dimension
    description: str = ""


class LayoutPolicyConfig(BaseModel):
    """Controls pre-render layout validation without changing legacy output."""

    collision: CollisionPolicy = "ignore"
    canvas_bounds: BoundsPolicy = "warn"
    safe_area: SafeAreaPolicy = "warn"
    exclusion_zones: BoundsPolicy = "warn"
    text_overflow: BoundsPolicy = "warn"
    contrast: BoundsPolicy = "warn"
    missing_fonts: BoundsPolicy = "warn"
    file_size: BoundsPolicy = "warn"
    min_contrast_ratio: float = Field(default=4.5, ge=1.0, le=21.0)
    allow_touching: bool = True


class PlatformProfile(BaseModel):
    """Canvas dimensions, export guidance, and UI-safe regions."""

    name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    safe_area: PaddingConfig = Field(default_factory=PaddingConfig)
    exclusion_zones: List[ExclusionZone] = Field(default_factory=list)
    description: str = ""
    crop_width: Optional[int] = Field(default=None, gt=0)
    crop_height: Optional[int] = Field(default=None, gt=0)
    recommended_format: OutputFormat = OutputFormat.PNG
    max_file_size_bytes: Optional[int] = Field(default=None, gt=0)
