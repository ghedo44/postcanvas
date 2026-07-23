"""Rich text with per-span styling and responsive fitting."""

from postcanvas import RichTextBlock, RichTextSpan, render
from postcanvas.models import BackgroundConfig, LayoutPolicyConfig, ShadowConfig, StrokeConfig
from postcanvas.presets import instagram_portrait

post = instagram_portrait(
    background=BackgroundConfig(color="#0B1020"),
    layout_policy=LayoutPolicyConfig(
        canvas_bounds="error",
        safe_area="error",
        text_overflow="error",
    ),
    output_dir="./output/examples/rich-text",
    output_filename="rich-text",
)

block = RichTextBlock(
    spans=[
        RichTextSpan(text="Build ", color="#FFFFFF"),
        RichTextSpan(
            text="beautiful",
            color="#F472B6",
            font_scale=1.18,
            decoration="underline",
            shadow=ShadowConfig(offset_y=8, blur_radius=18),
        ),
        RichTextSpan(text=" social graphics ", color="#FFFFFF"),
        RichTextSpan(
            text="from code.",
            color="#111827",
            background_color="#FDE68A",
            font_scale=1.08,
            stroke=StrokeConfig(color="#FFFFFF", width=1),
        ),
    ],
    x="8%", y="22%", width="84%", height="48%", anchor="topleft",
    font_size=92, min_font_size=38, max_lines=5,
    fit="shrink", overflow="ellipsis",
    line_spacing=1.18, paragraph_spacing=0.35, first_line_indent=18,
)

composition = block.compose(post.width, post.height, post.padding)
post.texts.extend(composition.texts)

result = render(post, save=True)
print(result.paths)
print(composition.layout)
