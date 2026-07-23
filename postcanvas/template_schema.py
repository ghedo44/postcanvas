from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .models import BackgroundConfig, ImageFit, LayoutPolicyConfig, PaddingConfig, ShapeType, TextAlign

NodeKind = Literal[
    "column", "row", "grid", "overlay", "group", "align", "safe_area",
    "conditional", "repeat", "text", "image", "shape", "spacer",
]


class Theme(BaseModel):
    colors: Dict[str, str] = Field(default_factory=dict)
    fonts: Dict[str, str] = Field(default_factory=dict)
    spacing: Dict[str, int] = Field(default_factory=dict)
    text_styles: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class LayoutNode(BaseModel):
    kind: NodeKind
    name: Optional[str] = None
    id: Optional[str] = None
    children: List["LayoutNode"] = Field(default_factory=list)
    required: bool = False
    default: Any = None
    when_present: Optional[str] = None
    when_absent: Optional[str] = None
    hide_when_chars_over: Optional[int] = Field(default=None, ge=1)
    grow: float = Field(default=0.0, ge=0.0)
    basis: Optional[int | float | str] = None
    width: Optional[int | float | str] = None
    height: Optional[int | float | str] = None
    aspect_ratio: Optional[float] = Field(default=None, gt=0)
    gap: int | str = 0
    padding: PaddingConfig = Field(default_factory=PaddingConfig)
    columns: int = Field(default=2, ge=1)
    horizontal_align: Literal["left", "center", "right", "stretch"] = "stretch"
    box_vertical_align: Literal["top", "middle", "bottom", "stretch"] = "stretch"
    repeat_from: Optional[str] = None
    item_name: str = "item"
    max_items: Optional[int] = Field(default=None, ge=1)
    repeat_direction: Literal["column", "row", "grid"] = "column"
    z_index: int = 10
    collision_group: Optional[str] = "content"
    allow_overlap_with: List[str] = Field(default_factory=list)
    respect_safe_area: bool = True
    respect_exclusion_zones: bool = True
    text_style: Optional[str] = None
    font_size: int = Field(default=64, ge=1)
    min_font_size: int = Field(default=24, ge=1)
    max_lines: Optional[int] = Field(default=None, ge=1)
    fit: Literal["none", "shrink", "truncate", "error"] = "shrink"
    overflow: Literal["visible", "clip", "ellipsis", "error"] = "ellipsis"
    wrap_mode: Literal["greedy", "balanced"] = "balanced"
    align: TextAlign = TextAlign.LEFT
    vertical_align: Literal["top", "middle", "bottom"] = "top"
    color: Optional[str] = None
    background_color: Optional[str] = None
    widow_control: bool = True
    image_fit: ImageFit = ImageFit.COVER
    focal_mode: Literal["manual", "auto"] = "manual"
    focal_x: float = Field(default=0.5, ge=0.0, le=1.0)
    focal_y: float = Field(default=0.5, ge=0.0, le=1.0)
    border_radius: float = Field(default=0.0, ge=0.0)
    shape_type: ShapeType = ShapeType.RECTANGLE
    fill_color: Optional[str] = None


class TemplateVariant(BaseModel):
    profile: Optional[str] = None
    root: Optional[LayoutNode] = None
    extends: Optional[str] = None
    root_scope: Optional[Literal["safe_area", "canvas"]] = None
    background: Optional[BackgroundConfig] = None
    required_slots: List[str] = Field(default_factory=list)
    max_chars_by_slot: Dict[str, int] = Field(default_factory=dict)
    layout_policy: Optional[LayoutPolicyConfig] = None


class PreviewFixture(BaseModel):
    content: Dict[str, Any] = Field(default_factory=dict)
    variant: Optional[str] = None
