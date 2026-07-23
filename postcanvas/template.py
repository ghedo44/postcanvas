from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional

from pydantic import BaseModel, Field

from .models import (
    BackgroundConfig,
    ImageElementConfig,
    ImageFit,
    PaddingConfig,
    PostConfig,
    ShapeConfig,
    ShapeType,
    TextAlign,
    TextConfig,
)
from .renderer.utils import resolve

NodeKind = Literal[
    "column",
    "row",
    "grid",
    "overlay",
    "text",
    "image",
    "shape",
    "spacer",
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
    z_index: int = 10
    collision_group: Optional[str] = "content"
    allow_overlap_with: List[str] = Field(default_factory=list)
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
    image_fit: ImageFit = ImageFit.COVER
    focal_x: float = Field(default=0.5, ge=0.0, le=1.0)
    focal_y: float = Field(default=0.5, ge=0.0, le=1.0)
    border_radius: float = Field(default=0.0, ge=0.0)
    shape_type: ShapeType = ShapeType.RECTANGLE
    fill_color: Optional[str] = None


class TemplateVariant(BaseModel):
    profile: str
    root: LayoutNode
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    required_slots: List[str] = Field(default_factory=list)
    max_chars_by_slot: Dict[str, int] = Field(default_factory=dict)


class Template(BaseModel):
    name: str
    version: str = "1"
    variants: Dict[str, TemplateVariant]
    theme: Theme = Field(default_factory=Theme)
    default_variant: Optional[str] = None

    @classmethod
    def from_file(cls, path: str | Path) -> "Template":
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            return cls.model_validate_json(content)
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as exc:
                raise ImportError("Install postcanvas[yaml] to load YAML templates") from exc
            return cls.model_validate(yaml.safe_load(content))
        raise ValueError("Template files must use .json, .yaml, or .yml")

    def to_file(self, path: str | Path) -> None:
        path = Path(path)
        if path.suffix.lower() == ".json":
            path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
            return
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as exc:
                raise ImportError("Install postcanvas[yaml] to write YAML templates") from exc
            path.write_text(
                yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False),
                encoding="utf-8",
            )
            return
        raise ValueError("Template files must use .json, .yaml, or .yml")

    def select_variant(
        self,
        content: Mapping[str, Any],
        variant: Optional[str] = None,
    ) -> tuple[str, TemplateVariant]:
        if variant is not None:
            return variant, self.variants[variant]
        candidates: List[tuple[int, str, TemplateVariant]] = []
        for name, item in self.variants.items():
            if any(not content.get(slot) for slot in item.required_slots):
                continue
            overflow = sum(
                max(0, len(str(content.get(slot, ""))) - maximum)
                for slot, maximum in item.max_chars_by_slot.items()
            )
            candidates.append((overflow, name, item))
        if candidates:
            _, name, item = min(candidates, key=lambda value: (value[0], value[1]))
            return name, item
        name = self.default_variant or next(iter(self.variants))
        return name, self.variants[name]

    def build(
        self,
        content: Mapping[str, Any],
        variant: Optional[str] = None,
        **post_overrides: Any,
    ) -> PostConfig:
        from .presets.platforms import get_profile

        _, selected = self.select_variant(content, variant)
        profile = get_profile(selected.profile)
        texts: List[TextConfig] = []
        images: List[ImageElementConfig] = []
        shapes: List[ShapeConfig] = []
        root_box = _Box(
            profile.safe_area.left,
            profile.safe_area.top,
            profile.width - profile.safe_area.left - profile.safe_area.right,
            profile.height - profile.safe_area.top - profile.safe_area.bottom,
        )
        _resolve_node(
            selected.root,
            root_box,
            content,
            self.theme,
            texts,
            images,
            shapes,
        )
        config: Dict[str, Any] = {
            "width": profile.width,
            "height": profile.height,
            "background": selected.background,
            "padding": profile.safe_area,
            "safe_area": profile.safe_area,
            "texts": texts,
            "images": images,
            "shapes": shapes,
        }
        config.update(post_overrides)
        return PostConfig(**config)

    def render(
        self,
        content: Mapping[str, Any],
        variant: Optional[str] = None,
        **post_overrides: Any,
    ) -> "TemplateRenderResult":
        from .api import render

        post = self.build(content, variant, **post_overrides)
        result = render(post, save=False)
        return TemplateRenderResult(post=post, images=result.images, reports=result.reports)


@dataclass
class TemplateRenderResult:
    post: PostConfig
    images: List[Any]
    reports: List[Any]

    @property
    def warnings(self) -> List[Any]:
        return [issue for report in self.reports for issue in report.warnings]


@dataclass(frozen=True)
class _Box:
    x: int
    y: int
    width: int
    height: int

    def inset(self, padding: PaddingConfig) -> "_Box":
        return _Box(
            self.x + padding.left,
            self.y + padding.top,
            max(0, self.width - padding.left - padding.right),
            max(0, self.height - padding.top - padding.bottom),
        )


def _spacing(value: int | str, theme: Theme) -> int:
    if isinstance(value, str) and value in theme.spacing:
        return int(theme.spacing[value])
    return int(value)


def _visible(node: LayoutNode, content: Mapping[str, Any]) -> bool:
    if node.when_present and not content.get(node.when_present):
        return False
    if node.when_absent and content.get(node.when_absent):
        return False
    if node.hide_when_chars_over is not None and node.name:
        value = str(content.get(node.name, node.default or ""))
        if len(value) > node.hide_when_chars_over:
            return False
    return True


def _fit_aspect(box: _Box, ratio: Optional[float]) -> _Box:
    if not ratio or box.width <= 0 or box.height <= 0:
        return box
    current = box.width / box.height
    if current > ratio:
        width = int(round(box.height * ratio))
        return _Box(box.x + (box.width - width) // 2, box.y, width, box.height)
    height = int(round(box.width / ratio))
    return _Box(box.x, box.y + (box.height - height) // 2, box.width, height)


def _child_main_size(node: LayoutNode, total: int, vertical: bool) -> Optional[int]:
    if node.basis is not None:
        return resolve(node.basis, total)
    explicit = node.height if vertical else node.width
    return resolve(explicit, total) if explicit is not None else None


def _flow_boxes(
    node: LayoutNode,
    box: _Box,
    children: List[LayoutNode],
    theme: Theme,
    vertical: bool,
) -> List[_Box]:
    gap = _spacing(node.gap, theme)
    main_total = box.height if vertical else box.width
    cross_total = box.width if vertical else box.height
    available = max(0, main_total - gap * max(0, len(children) - 1))
    fixed = [_child_main_size(child, main_total, vertical) for child in children]
    fixed_sum = sum(value or 0 for value in fixed)
    flexible = [index for index, value in enumerate(fixed) if value is None]
    weight_sum = sum(max(children[index].grow, 1.0) for index in flexible) or 1.0
    remaining = max(0, available - fixed_sum)
    cursor = box.y if vertical else box.x
    result: List[_Box] = []
    flexible_used = 0
    for index, child in enumerate(children):
        main = fixed[index]
        if main is None:
            flexible_used += 1
            if flexible_used == len(flexible):
                used = sum(item.height if vertical else item.width for item in result)
                main = max(0, available - used)
            else:
                main = int(round(remaining * max(child.grow, 1.0) / weight_sum))
        cross_explicit = child.width if vertical else child.height
        cross = resolve(cross_explicit, cross_total) if cross_explicit is not None else cross_total
        if vertical:
            child_box = _Box(box.x, cursor, min(cross, box.width), max(0, main))
            cursor += main + gap
        else:
            child_box = _Box(cursor, box.y, max(0, main), min(cross, box.height))
            cursor += main + gap
        result.append(_fit_aspect(child_box, child.aspect_ratio))
    return result


def _resolve_node(
    node: LayoutNode,
    box: _Box,
    content: Mapping[str, Any],
    theme: Theme,
    texts: List[TextConfig],
    images: List[ImageElementConfig],
    shapes: List[ShapeConfig],
) -> None:
    if not _visible(node, content):
        return
    inner = box.inset(node.padding)
    children = [child for child in node.children if _visible(child, content)]
    if node.kind in {"column", "row"}:
        boxes = _flow_boxes(node, inner, children, theme, vertical=node.kind == "column")
        for child, child_box in zip(children, boxes):
            _resolve_node(child, child_box, content, theme, texts, images, shapes)
        return
    if node.kind == "grid":
        gap = _spacing(node.gap, theme)
        columns = max(1, node.columns)
        rows = max(1, (len(children) + columns - 1) // columns)
        cell_width = max(0, (inner.width - gap * (columns - 1)) // columns)
        cell_height = max(0, (inner.height - gap * (rows - 1)) // rows)
        for index, child in enumerate(children):
            column = index % columns
            row = index // columns
            child_box = _Box(
                inner.x + column * (cell_width + gap),
                inner.y + row * (cell_height + gap),
                cell_width,
                cell_height,
            )
            _resolve_node(
                child,
                _fit_aspect(child_box, child.aspect_ratio),
                content,
                theme,
                texts,
                images,
                shapes,
            )
        return
    if node.kind == "overlay":
        for child in children:
            child_box = inner
            if child.width is not None:
                width = resolve(child.width, inner.width)
                child_box = _Box(
                    inner.x + (inner.width - width) // 2,
                    child_box.y,
                    width,
                    child_box.height,
                )
            if child.height is not None:
                height = resolve(child.height, inner.height)
                child_box = _Box(
                    child_box.x,
                    inner.y + (inner.height - height) // 2,
                    child_box.width,
                    height,
                )
            _resolve_node(
                child,
                _fit_aspect(child_box, child.aspect_ratio),
                content,
                theme,
                texts,
                images,
                shapes,
            )
        return
    if node.kind == "spacer":
        return

    element_id = node.id or node.name
    if node.kind == "text":
        value = content.get(node.name or "", node.default)
        if value is None:
            if node.required:
                raise ValueError(f"Missing required text slot: {node.name}")
            return
        style = dict(theme.text_styles.get(node.text_style or "", {}))
        font_path = style.pop("font_path", None)
        font_role = style.pop("font_role", None)
        if font_role:
            font_path = theme.fonts.get(font_role, font_path)
        color = node.color or style.pop("color", None) or theme.colors.get("text", "#FFFFFF")
        config = {
            "content": str(value),
            "id": element_id,
            "collision_group": node.collision_group,
            "allow_overlap_with": node.allow_overlap_with,
            "x": box.x,
            "y": box.y,
            "width": box.width,
            "height": box.height,
            "anchor": "topleft",
            "font_size": node.font_size,
            "min_font_size": node.min_font_size,
            "max_lines": node.max_lines,
            "fit": node.fit,
            "overflow": node.overflow,
            "wrap_mode": node.wrap_mode,
            "align": node.align,
            "vertical_align": node.vertical_align,
            "color": color,
            "background_color": node.background_color,
            "font_path": font_path,
            "z_index": node.z_index,
        }
        config.update(style)
        texts.append(TextConfig(**config))
        return
    if node.kind == "image":
        value = content.get(node.name or "", node.default)
        if value is None:
            if node.required:
                raise ValueError(f"Missing required image slot: {node.name}")
            return
        images.append(
            ImageElementConfig(
                id=element_id,
                collision_group=node.collision_group,
                allow_overlap_with=node.allow_overlap_with,
                src=str(value),
                x=box.x,
                y=box.y,
                width=box.width,
                height=box.height,
                anchor="topleft",
                fit=node.image_fit,
                focal_x=node.focal_x,
                focal_y=node.focal_y,
                border_radius=node.border_radius,
                z_index=node.z_index,
            )
        )
        return
    if node.kind == "shape":
        shapes.append(
            ShapeConfig(
                id=element_id,
                collision_group=node.collision_group,
                allow_overlap_with=node.allow_overlap_with,
                type=node.shape_type,
                x=box.x,
                y=box.y,
                width=box.width,
                height=box.height,
                anchor="topleft",
                fill_color=node.fill_color or theme.colors.get("surface"),
                z_index=node.z_index,
            )
        )
