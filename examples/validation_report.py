"""Inspect validation reports and allow intentional overlap."""

from postcanvas import LayoutValidationError, render
from postcanvas.models import BackgroundConfig, LayoutPolicyConfig, ShapeConfig, ShapeType, TextConfig
from postcanvas.presets import instagram_post

post = instagram_post(
    background=BackgroundConfig(color="#111827"),
    layout_policy=LayoutPolicyConfig(
        collision="error",
        canvas_bounds="error",
        safe_area="error",
        text_overflow="error",
        contrast="warn",
        missing_fonts="warn",
    ),
    shapes=[
        ShapeConfig(
            id="accent",
            type=ShapeType.CIRCLE,
            x="80%", y="18%", width=260, height=260,
            anchor="center", fill_color="#8B5CF6",
        )
    ],
    texts=[
        TextConfig(
            id="headline",
            collision_group="content",
            allow_overlap_with=["accent"],
            content="Validated before it ships.",
            x="8%", y="28%", width="84%", height="30%",
            anchor="topleft", font_size=88, min_font_size=36,
            fit="shrink", overflow="error", wrap_mode="balanced", align="left",
        )
    ],
    output_dir="./output/examples/validation",
)

try:
    result = render(post, save=True)
except LayoutValidationError as error:
    print(error)
    raise

for report in result.reports:
    for issue in report.issues:
        print(issue.code, issue.severity, issue.message)
