"""Generate representative release previews with the installed package."""

from pathlib import Path
import runpy

EXAMPLES = [
    "editorial_poster.py",
    "data_dashboard.py",
    "story_launch.py",
    "carousel_system.py",
    "rich_text.py",
    "validation_report.py",
]

base = Path(__file__).resolve().parent
for example in EXAMPLES:
    print(f"running {example}")
    runpy.run_path(str(base / example), run_name="__main__")
