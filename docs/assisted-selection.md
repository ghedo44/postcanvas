# Assisted variant selection

Postcanvas supports a pluggable `VariantSelector` protocol. A selector chooses among eligible template variants; Postcanvas still validates the result and performs deterministic layout/rendering afterward.

## Why use a selector

A content system may have short-headline, long-headline, media-free, data-heavy, quote, story, portrait, or multilingual variants. The built-in selector scores required slots and character overflow. A custom selector can incorporate editorial intent, campaign metadata, content category, or an external model.

## Protocol

A selector receives the template name, content mapping, eligible variant names, and structured candidate requirements. It returns a variant name.

```python
from postcanvas import VariantSelector

class EditorialSelector:
    def select_variant(self, *, template_name, content, candidates):
        if content.get("metrics"):
            return "data-heavy"
        if len(content.get("headline", "")) > 80:
            return "long-copy"
        return "portrait"
```

Pass it to selection, build, render, or fixture rendering.

```python
selector = EditorialSelector()

name, variant = template.select_variant(content, selector=selector)
post = template.build(content, selector=selector)
result = template.render(content, selector=selector)
```

## Prompt adapter

`PromptVariantSelector` adapts a callable that accepts a prompt.

```python
from postcanvas import PromptVariantSelector

def complete(prompt: str) -> str:
    return my_model.generate(prompt)

selector = PromptVariantSelector(complete)
result = template.render(content, selector=selector)
```

The callable may return a plain variant name or `{"variant": "portrait"}`.

## Safety and validation

Postcanvas rejects unknown variants, variants outside the eligible candidate set, and malformed selector results. The selector cannot mutate the layout tree or bypass template validation.

## Deterministic production behavior

- log the selected variant
- store the selector/model version
- keep model temperature low
- cache decisions by content hash
- provide a deterministic fallback
- include fixture tests for every variant
- never let a model generate arbitrary executable configuration

## Human-in-the-loop workflow

1. selector recommends a variant
2. template builds a preview
3. validation runs
4. editor approves or chooses another variant
5. store the chosen variant with the content record
6. production rendering uses the stored variant explicitly
