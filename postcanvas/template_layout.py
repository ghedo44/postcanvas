from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .models import ImageElementConfig, PaddingConfig, ShapeConfig, TextConfig
from .renderer.loader import estimate_focal_point, load_image
from .renderer.utils import resolve
from .template_schema import LayoutNode, Theme


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    def inset(self, padding: PaddingConfig) -> "Box":
        return Box(
            self.x + padding.left,
            self.y + padding.top,
            max(0, self.width - padding.left - padding.right),
            max(0, self.height - padding.top - padding.bottom),
        )


_MISSING = object()


def lookup(content: Any, path: Optional[str], default: Any = None) -> Any:
    if not path:
        return default
    current = content
    for part in path.split("."):
        if isinstance(current, Mapping):
            current = current.get(part, _MISSING)
        elif isinstance(current, (list, tuple)) and part.isdigit():
            index = int(part)
            current = current[index] if index < len(current) else _MISSING
        else:
            current = getattr(current, part, _MISSING)
        if current is _MISSING:
            return default
    return current


def _visible(node: LayoutNode, content: Mapping[str, Any]) -> bool:
    if node.when_present and not lookup(content, node.when_present):
        return False
    if node.when_absent and lookup(content, node.when_absent):
        return False
    if node.hide_when_chars_over is not None and node.name:
        return len(str(lookup(content, node.name, node.default or ""))) <= node.hide_when_chars_over
    return True


def _spacing(value: int | str, theme: Theme) -> int:
    return int(theme.spacing.get(value, value)) if isinstance(value, str) else int(value)


def _aspect(box: Box, ratio: Optional[float]) -> Box:
    if not ratio or box.width <= 0 or box.height <= 0:
        return box
    if box.width / box.height > ratio:
        width = int(round(box.height * ratio))
        return Box(box.x + (box.width - width) // 2, box.y, width, box.height)
    height = int(round(box.width / ratio))
    return Box(box.x, box.y + (box.height - height) // 2, box.width, height)


def _aligned(node: LayoutNode, parent: Box) -> Box:
    width = resolve(node.width, parent.width) if node.width is not None else parent.width
    height = resolve(node.height, parent.height) if node.height is not None else parent.height
    width, height = min(width, parent.width), min(height, parent.height)
    x = parent.x
    y = parent.y
    if node.horizontal_align == "center":
        x += (parent.width - width) // 2
    elif node.horizontal_align == "right":
        x += parent.width - width
    if node.box_vertical_align == "middle":
        y += (parent.height - height) // 2
    elif node.box_vertical_align == "bottom":
        y += parent.height - height
    return _aspect(Box(x, y, width, height), node.aspect_ratio)


def _flow(node: LayoutNode, box: Box, children: List[LayoutNode], theme: Theme, vertical: bool) -> List[Box]:
    gap = _spacing(node.gap, theme)
    total = box.height if vertical else box.width
    cross_total = box.width if vertical else box.height
    available = max(0, total - gap * max(0, len(children) - 1))
    fixed = []
    for child in children:
        value = child.basis
        if value is None:
            value = child.height if vertical else child.width
        fixed.append(resolve(value, total) if value is not None else None)
    remaining = max(0, available - sum(value or 0 for value in fixed))
    flexible = [index for index, value in enumerate(fixed) if value is None]
    remaining_weight = sum(max(children[index].grow, 1.0) for index in flexible) or 1.0
    cursor = box.y if vertical else box.x
    output: List[Box] = []
    for index, child in enumerate(children):
        main = fixed[index]
        if main is None:
            weight = max(child.grow, 1.0)
            main = remaining if len(flexible) == 1 else int(round(remaining * weight / remaining_weight))
            remaining -= main
            remaining_weight -= weight
            flexible.pop(0)
        cross_value = child.width if vertical else child.height
        stretch = child.horizontal_align == "stretch" if vertical else child.box_vertical_align == "stretch"
        cross = cross_total if stretch or cross_value is None else min(resolve(cross_value, cross_total), cross_total)
        raw = Box(box.x, cursor, box.width, main) if vertical else Box(cursor, box.y, main, box.height)
        if vertical:
            x = raw.x if child.horizontal_align != "center" else raw.x + (raw.width - cross) // 2
            if child.horizontal_align == "right":
                x = raw.x + raw.width - cross
            child_box = Box(x, raw.y, cross, raw.height)
        else:
            y = raw.y if child.box_vertical_align != "middle" else raw.y + (raw.height - cross) // 2
            if child.box_vertical_align == "bottom":
                y = raw.y + raw.height - cross
            child_box = Box(raw.x, y, raw.width, cross)
        output.append(_aspect(child_box, child.aspect_ratio))
        cursor += main + gap
    return output


def _grid(node: LayoutNode, box: Box, count: int, theme: Theme) -> List[Box]:
    if count <= 0:
        return []
    gap = _spacing(node.gap, theme)
    columns = max(1, min(node.columns, count))
    rows = (count + columns - 1) // columns
    width = max(0, (box.width - gap * (columns - 1)) // columns)
    height = max(0, (box.height - gap * (rows - 1)) // rows)
    return [Box(box.x + (i % columns) * (width + gap), box.y + (i // columns) * (height + gap), width, height) for i in range(count)]


def _allowlist(node: LayoutNode, suffix: Optional[str]) -> List[str]:
    return [f"{value}-{suffix}" for value in node.allow_overlap_with] if suffix else list(node.allow_overlap_with)


def resolve_layout(
    root: LayoutNode,
    root_box: Box,
    content: Mapping[str, Any],
    theme: Theme,
    canvas_box: Box,
    safe_box: Box,
) -> tuple[List[TextConfig], List[ImageElementConfig], List[ShapeConfig]]:
    texts: List[TextConfig] = []
    images: List[ImageElementConfig] = []
    shapes: List[ShapeConfig] = []

    def children(nodes: List[LayoutNode], box: Box, scoped: Mapping[str, Any], suffix: Optional[str]) -> None:
        for child in nodes:
            visit(child, _aligned(child, box), scoped, suffix)

    def visit(node: LayoutNode, box: Box, scoped: Mapping[str, Any], suffix: Optional[str] = None) -> None:
        if not _visible(node, scoped):
            return
        inner = box.inset(node.padding)
        visible = [child for child in node.children if _visible(child, scoped)]
        if node.kind in {"column", "row"}:
            for child, child_box in zip(visible, _flow(node, inner, visible, theme, node.kind == "column")):
                visit(child, child_box, scoped, suffix)
            return
        if node.kind == "grid":
            for child, child_box in zip(visible, _grid(node, inner, len(visible), theme)):
                visit(child, _aspect(child_box, child.aspect_ratio), scoped, suffix)
            return
        if node.kind in {"overlay", "group", "align", "conditional"}:
            children(visible, inner, scoped, suffix)
            return
        if node.kind == "safe_area":
            children(visible, safe_box.inset(node.padding), scoped, suffix)
            return
        if node.kind == "repeat":
            source = node.repeat_from or node.name
            items = lookup(scoped, source, []) or []
            if isinstance(items, (str, bytes)) or not isinstance(items, Iterable):
                raise TypeError(f"Repeat source {source!r} must be an iterable")
            item_list = list(items)[: node.max_items] if node.max_items else list(items)
            if node.repeat_direction == "grid":
                boxes = _grid(node, inner, len(item_list), theme)
            else:
                virtual = [LayoutNode(kind="group", grow=1) for _ in item_list]
                boxes = _flow(node, inner, virtual, theme, node.repeat_direction == "column")
            for index, (item, item_box) in enumerate(zip(item_list, boxes), 1):
                child_scope: Dict[str, Any] = dict(scoped)
                child_scope[node.item_name] = item
                child_scope[f"{node.item_name}_index"] = index - 1
                child_suffix = f"{suffix}-{index}" if suffix else str(index)
                children(visible, item_box, child_scope, child_suffix)
            return
        if node.kind == "spacer":
            return

        element_id = node.id or node.name
        if element_id and suffix:
            element_id = f"{element_id}-{suffix}"
        common = dict(
            id=element_id,
            collision_group=node.collision_group,
            allow_overlap_with=_allowlist(node, suffix),
            respect_safe_area=node.respect_safe_area,
            respect_exclusion_zones=node.respect_exclusion_zones,
            x=box.x, y=box.y, width=box.width, height=box.height,
            anchor="topleft", z_index=node.z_index,
        )
        if node.kind == "text":
            value = lookup(scoped, node.name, node.default)
            if value is None:
                if node.required:
                    raise ValueError(f"Missing required text slot: {node.name}")
                return
            style = dict(theme.text_styles.get(node.text_style or "", {}))
            font_path = style.pop("font_path", None)
            font_role = style.pop("font_role", None)
            if font_role:
                font_path = theme.fonts.get(font_role, font_path)
            config = dict(
                **common, content=str(value), font_size=node.font_size,
                min_font_size=node.min_font_size, max_lines=node.max_lines,
                fit=node.fit, overflow=node.overflow, wrap_mode=node.wrap_mode,
                align=node.align, vertical_align=node.vertical_align,
                widow_control=node.widow_control,
                min_last_line_words=2 if node.widow_control else 1,
                color=node.color or style.pop("color", None) or theme.colors.get("text", "#FFFFFF"),
                background_color=node.background_color, font_path=font_path,
            )
            config.update(style)
            texts.append(TextConfig(**config))
        elif node.kind == "image":
            value = lookup(scoped, node.name, node.default)
            if value is None:
                if node.required:
                    raise ValueError(f"Missing required image slot: {node.name}")
                return
            focal_x, focal_y = node.focal_x, node.focal_y
            if node.focal_mode == "auto":
                loaded = load_image(str(value))
                if loaded is not None:
                    focal_x, focal_y = estimate_focal_point(loaded)
            images.append(ImageElementConfig(**common, src=str(value), fit=node.image_fit, focal_mode=node.focal_mode, focal_x=focal_x, focal_y=focal_y, border_radius=node.border_radius))
        elif node.kind == "shape":
            shapes.append(ShapeConfig(**common, type=node.shape_type, fill_color=node.fill_color or theme.colors.get("surface")))

    visit(root, root_box, content)
    return texts, images, shapes
