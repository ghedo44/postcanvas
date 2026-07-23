from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from pydantic import BaseModel, Field

from .models import BackgroundConfig, LayoutPolicyConfig, PostConfig
from .selectors import VariantSelector
from .template_layout import Box, lookup, resolve_layout
from .template_schema import LayoutNode, PreviewFixture, TemplateVariant, Theme


class TemplateRenderResult(BaseModel):
    post: PostConfig
    images: List[Any]
    reports: List[Any]
    model_config = {"arbitrary_types_allowed": True}

    @property
    def warnings(self) -> List[Any]:
        return [issue for report in self.reports for issue in report.warnings]


class Template(BaseModel):
    name: str
    version: str = "1"
    variants: Dict[str, TemplateVariant]
    theme: Theme = Field(default_factory=Theme)
    default_variant: Optional[str] = None
    fixtures: Dict[str, PreviewFixture] = Field(default_factory=dict)

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
                raise ImportError(
                    "Install postcanvas[yaml] to load YAML templates"
                ) from exc
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
                raise ImportError(
                    "Install postcanvas[yaml] to write YAML templates"
                ) from exc
            path.write_text(
                yaml.safe_dump(
                    self.model_dump(mode="json"),
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            return
        raise ValueError("Template files must use .json, .yaml, or .yml")

    def inherit(self, base: "Template") -> "Template":
        styles = {
            name: {
                **base.theme.text_styles.get(name, {}),
                **self.theme.text_styles.get(name, {}),
            }
            for name in set(base.theme.text_styles) | set(self.theme.text_styles)
        }
        theme = Theme(
            colors={**base.theme.colors, **self.theme.colors},
            fonts={**base.theme.fonts, **self.theme.fonts},
            spacing={**base.theme.spacing, **self.theme.spacing},
            text_styles=styles,
        )
        return self.model_copy(
            update={
                "theme": theme,
                "variants": {**base.variants, **self.variants},
                "fixtures": {**base.fixtures, **self.fixtures},
                "default_variant": self.default_variant or base.default_variant,
            },
            deep=True,
        )

    def _resolve_variant(self, name: str, seen: set[str]) -> TemplateVariant:
        if name in seen:
            raise ValueError(
                f"Circular template variant inheritance involving {name!r}"
            )
        try:
            variant = self.variants[name]
        except KeyError as exc:
            raise KeyError(f"Unknown template variant: {name}") from exc
        if not variant.extends:
            if variant.profile is None or variant.root is None:
                raise ValueError(
                    f"Variant {name!r} must define profile and root or extend "
                    "another variant"
                )
            return variant.model_copy(
                update={
                    "background": variant.background or BackgroundConfig(),
                    "root_scope": variant.root_scope or "safe_area",
                },
                deep=True,
            )
        base = self._resolve_variant(variant.extends, seen | {name})
        updates = variant.model_dump(exclude_unset=True)
        updates.pop("extends", None)
        updates["required_slots"] = list(
            dict.fromkeys([*base.required_slots, *variant.required_slots])
        )
        updates["max_chars_by_slot"] = {
            **base.max_chars_by_slot,
            **variant.max_chars_by_slot,
        }
        return base.model_copy(update=updates, deep=True)

    def resolve_variant(self, name: str) -> TemplateVariant:
        return self._resolve_variant(name, set())

    def _eligible_variants(
        self,
        content: Mapping[str, Any],
    ) -> Dict[str, TemplateVariant]:
        result: Dict[str, TemplateVariant] = {}
        for name in self.variants:
            variant = self.resolve_variant(name)
            if any(
                not lookup(content, slot)
                for slot in variant.required_slots
            ):
                continue
            result[name] = variant
        return result

    def select_variant(
        self,
        content: Mapping[str, Any],
        variant: Optional[str] = None,
        selector: Optional[VariantSelector[TemplateVariant]] = None,
    ) -> tuple[str, TemplateVariant]:
        if variant:
            return variant, self.resolve_variant(variant)
        eligible = self._eligible_variants(content)
        if selector is not None and eligible:
            name = selector(content, eligible)
            if name not in eligible:
                available = ", ".join(sorted(eligible))
                raise ValueError(
                    f"Selector returned ineligible variant {name!r}; "
                    f"available: {available}"
                )
            return name, eligible[name]
        candidates = []
        for name, item in eligible.items():
            overflow = sum(
                max(
                    0,
                    len(str(lookup(content, slot, ""))) - maximum,
                )
                for slot, maximum in item.max_chars_by_slot.items()
            )
            candidates.append((overflow, name, item))
        if candidates:
            _, name, item = min(
                candidates,
                key=lambda value: (value[0], value[1]),
            )
            return name, item
        name = self.default_variant or next(iter(self.variants))
        return name, self.resolve_variant(name)

    def build(
        self,
        content: Mapping[str, Any],
        variant: Optional[str] = None,
        selector: Optional[VariantSelector[TemplateVariant]] = None,
        **overrides: Any,
    ) -> PostConfig:
        from .presets.platforms import get_profile

        variant_name, selected = self.select_variant(
            content,
            variant,
            selector,
        )
        assert selected.profile and selected.root
        profile = get_profile(selected.profile)
        canvas = Box(0, 0, profile.width, profile.height)
        safe = Box(
            profile.safe_area.left,
            profile.safe_area.top,
            profile.width - profile.safe_area.left - profile.safe_area.right,
            profile.height - profile.safe_area.top - profile.safe_area.bottom,
        )
        root_box = canvas if selected.root_scope == "canvas" else safe
        texts, images, shapes = resolve_layout(
            selected.root,
            root_box,
            content,
            self.theme,
            canvas,
            safe,
        )
        config: Dict[str, Any] = {
            "profile_name": profile.name,
            "width": profile.width,
            "height": profile.height,
            "background": selected.background or BackgroundConfig(),
            "padding": profile.safe_area,
            "safe_area": profile.safe_area,
            "exclusion_zones": profile.exclusion_zones,
            "max_file_size_bytes": profile.max_file_size_bytes,
            "output_format": profile.recommended_format,
            "layout_policy": selected.layout_policy
            or LayoutPolicyConfig(),
            "texts": texts,
            "images": images,
            "shapes": shapes,
            "meta": {"title": f"{self.name}:{variant_name}"},
        }
        config.update(overrides)
        return PostConfig(**config)

    def render(
        self,
        content: Mapping[str, Any],
        variant: Optional[str] = None,
        selector: Optional[VariantSelector[TemplateVariant]] = None,
        **overrides: Any,
    ) -> TemplateRenderResult:
        from .api import render

        post = self.build(content, variant, selector, **overrides)
        result = render(post, save=False)
        return TemplateRenderResult(
            post=post,
            images=result.images,
            reports=result.reports,
        )

    def render_fixtures(
        self,
        selector: Optional[VariantSelector[TemplateVariant]] = None,
    ) -> Dict[str, TemplateRenderResult]:
        return {
            name: self.render(
                fixture.content,
                fixture.variant,
                selector,
            )
            for name, fixture in self.fixtures.items()
        }


__all__ = [
    "LayoutNode",
    "PreviewFixture",
    "Template",
    "TemplateRenderResult",
    "TemplateVariant",
    "Theme",
]
