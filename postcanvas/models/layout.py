from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from .primitives import PaddingConfig

CollisionPolicy = Literal["ignore", "warn", "error"]
BoundsPolicy = Literal["ignore", "warn", "error"]
SafeAreaPolicy = Literal["ignore", "warn", "error"]


class LayoutPolicyConfig(BaseModel):
    """Controls pre-render layout validation without changing legacy output."""

    collision: CollisionPolicy = "ignore"
    canvas_bounds: BoundsPolicy = "warn"
    safe_area: SafeAreaPolicy = "warn"
    text_overflow: BoundsPolicy = "warn"
    allow_touching: bool = True


class PlatformProfile(BaseModel):
    """Canvas dimensions and UI-safe insets for one social-media surface."""

    name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    safe_area: PaddingConfig = Field(default_factory=PaddingConfig)
    description: str = ""
    crop_width: Optional[int] = Field(default=None, gt=0)
    crop_height: Optional[int] = Field(default=None, gt=0)
