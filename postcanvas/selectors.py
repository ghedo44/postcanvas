from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, TypeVar

VariantT = TypeVar("VariantT")


class VariantSelector(Protocol[VariantT]):
    """Select one variant name from already resolved template variants."""

    def __call__(
        self,
        content: Mapping[str, Any],
        variants: Mapping[str, VariantT],
    ) -> str: ...


@dataclass(frozen=True)
class PromptVariantSelector:
    """Adapt an LLM or prompt-based chooser to the variant-selector API.

    ``choose`` receives deterministic JSON and must return either a variant
    name or a JSON object containing ``{"variant": "name"}``.
    """

    choose: Callable[[str], str]
    include_content: bool = True

    def __call__(
        self,
        content: Mapping[str, Any],
        variants: Mapping[str, Any],
    ) -> str:
        variant_data = {}
        for name, variant in variants.items():
            variant_data[name] = {
                "profile": getattr(variant, "profile", None),
                "required_slots": list(
                    getattr(variant, "required_slots", [])
                ),
                "max_chars_by_slot": dict(
                    getattr(variant, "max_chars_by_slot", {})
                ),
            }
        payload: dict[str, Any] = {
            "instruction": (
                "Choose exactly one template variant. Return only its name or "
                'JSON in the form {"variant": "name"}.'
            ),
            "variants": variant_data,
        }
        if self.include_content:
            payload["content"] = dict(content)
        response = self.choose(
            json.dumps(payload, sort_keys=True, ensure_ascii=False)
        ).strip()
        try:
            decoded = json.loads(response)
        except json.JSONDecodeError:
            selected = response
        else:
            selected = (
                decoded.get("variant")
                if isinstance(decoded, dict)
                else decoded
            )
        if not isinstance(selected, str) or selected not in variants:
            available = ", ".join(sorted(variants))
            raise ValueError(
                f"Selector returned unknown variant {selected!r}; "
                f"available: {available}"
            )
        return selected


__all__ = ["PromptVariantSelector", "VariantSelector"]
