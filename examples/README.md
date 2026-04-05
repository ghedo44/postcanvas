# Examples

This folder contains polished, ready-to-run examples.

## Files

- 01_instagram_single.py
  - Editorial-style single post with bold hierarchy and clean CTA
  - Output: ./output/examples/instagram_single_nightfall.png

- 02_carousel.py
  - 4-slide modern carousel with strong composition and readable pacing
  - Output: ./output/examples/instagram_carousel_studio_01.png ... _04.png

- 03_cloud_storage_example.py
  - Demonstrates local save, in-memory generation, and cloud-upload workflows

- 04_instagram_table.py
  - Instagram single post with a KPI table element
  - Output: ./output/examples/instagram_table_kpi.png

- 05_instagram_charts.py
  - 2-slide Instagram chart carousel (bar chart + line chart)
  - Output: ./output/examples/instagram_chart_bar.png and instagram_chart_line.png

## Run

From workspace root:

```bash
python examples/01_instagram_single.py
python examples/02_carousel.py
python examples/03_cloud_storage_example.py
python examples/04_instagram_table.py
python examples/05_instagram_charts.py
```

## Notes

- These examples use bundled assets from examples/assets/
- They use Roboto from: examples/assets/Roboto/static/*.ttf
- Font fallback still works if the Roboto path is changed or removed
