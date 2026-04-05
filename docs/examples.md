# Examples Guide

Run all scripts from repository root.

## Core Examples

- `examples/01_instagram_single.py`
  - Single-image editorial layout
  - Output: `./output/examples/instagram_single_nightfall.png`

- `examples/02_carousel.py`
  - Four-slide carousel layout
  - Output: `./output/examples/instagram_carousel_studio_01.png` ... `_04.png`

- `examples/03_cloud_storage_example.py`
  - Demonstrates save modes, in-memory rendering, and cloud-upload style flow

## New Data Visualization Examples

- `examples/04_instagram_table.py`
  - Uses `TableElementConfig`
  - Output: `./output/examples/instagram_table_kpi.png`

- `examples/05_instagram_charts.py`
  - Uses `ChartElementConfig` for both bar and line charts
  - Output:
    - `./output/examples/instagram_chart_bar.png`
    - `./output/examples/instagram_chart_line.png`

## Commands

```bash
python examples/01_instagram_single.py
python examples/02_carousel.py
python examples/03_cloud_storage_example.py
python examples/04_instagram_table.py
python examples/05_instagram_charts.py
```

## Tips

- If custom fonts are unavailable, renderer fallback fonts are used.
- Keep `output/` ignored in git to avoid checking in generated files.
- Use `generate(..., save=False, return_images=True)` for cloud upload pipelines.
