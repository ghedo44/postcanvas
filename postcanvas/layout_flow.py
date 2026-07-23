from __future__ import annotations

from typing import Any, List, Optional


def resolve_flow_boxes(
    node: Any,
    box: Any,
    children: List[Any],
    theme: Any,
    vertical: bool,
) -> List[Any]:
    """Allocate fixed and flexible flow children without cumulative overlap."""

    from . import template as template_module

    gap = template_module._spacing(node.gap, theme)
    main_total = box.height if vertical else box.width
    cross_total = box.width if vertical else box.height
    available = max(0, main_total - gap * max(0, len(children) - 1))
    fixed: List[Optional[int]] = [
        template_module._child_main_size(child, main_total, vertical)
        for child in children
    ]
    fixed_sum = sum(value or 0 for value in fixed)
    flexible = [index for index, value in enumerate(fixed) if value is None]
    remaining_flexible = max(0, available - fixed_sum)
    remaining_weight = sum(
        max(children[index].grow, 1.0) for index in flexible
    ) or 1.0
    flexible_used = 0
    cursor = box.y if vertical else box.x
    result: List[Any] = []

    for index, child in enumerate(children):
        main = fixed[index]
        if main is None:
            flexible_used += 1
            weight = max(child.grow, 1.0)
            if flexible_used == len(flexible):
                main = remaining_flexible
            else:
                main = int(round(remaining_flexible * weight / remaining_weight))
                remaining_flexible = max(0, remaining_flexible - main)
                remaining_weight = max(0.0, remaining_weight - weight)
        cross_explicit = child.width if vertical else child.height
        cross = (
            template_module.resolve(cross_explicit, cross_total)
            if cross_explicit is not None
            else cross_total
        )
        if vertical:
            child_box = type(box)(
                box.x,
                cursor,
                min(cross, box.width),
                max(0, main),
            )
            cursor += main + gap
        else:
            child_box = type(box)(
                cursor,
                box.y,
                max(0, main),
                min(cross, box.height),
            )
            cursor += main + gap
        result.append(
            template_module._fit_aspect(child_box, child.aspect_ratio)
        )
    return result
