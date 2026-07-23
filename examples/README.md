# Postcanvas examples

All examples are self-contained and write to `./output/examples/...`.

| Script | Demonstrates |
|---|---|
| `editorial_poster.py` | responsive portrait typography, gradients, shapes, strict validation |
| `data_dashboard.py` | KPI cards, tables and bar charts |
| `story_launch.py` | story composition and platform UI-safe content |
| `carousel_system.py` | shared branding and per-slide overrides |
| `template_system.py` | themes, variants, repeaters, fixtures and serialization |
| `rich_text.py` | styled spans, mixed font scales and optional hyphenation |
| `validation_report.py` | reports and intentional overlap |
| `platform_pack.py` | one content system across platform presets |
| `cloud_output.py` | images, bytes and cloud-friendly output |
| `generate_gallery.py` | release-preview generation |

Run from the repository root:

```bash
python examples/editorial_poster.py
```

Optional features:

```bash
pip install -e ".[yaml,typography]"
```
