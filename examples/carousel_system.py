"""Four-slide carousel with shared branding and per-slide overrides."""

from postcanvas import generate
from postcanvas.models import BackgroundConfig, CanvasConfig, TextConfig
from postcanvas.presets import instagram_post

slides = [
    ("HOOK", "Your content needs a system.", "#111827", "#8B5CF6"),
    ("PROOF", "Responsive layouts survive real copy.", "#0F172A", "#06B6D4"),
    ("SYSTEM", "Templates turn design into an API.", "#1F2937", "#F97316"),
    ("ACTION", "Ship validated graphics automatically.", "#17112F", "#EC4899"),
]

canvases = []
for index, (eyebrow, headline, background, accent) in enumerate(slides, start=1):
    canvases.append(
        CanvasConfig(
            background=BackgroundConfig(color=background),
            output_filename=f"{index:02d}-{eyebrow.lower()}",
            texts=[
                TextConfig(
                    content=f"{index:02d} / {eyebrow}",
                    x="7%", y="8%", width="86%", anchor="topleft",
                    font_size=22, letter_spacing=4, color=accent, align="left",
                ),
                TextConfig(
                    content=headline,
                    x="7%", y="30%", width="86%", height="38%",
                    anchor="topleft", font_size=88, min_font_size=38,
                    max_lines=4, fit="shrink", overflow="ellipsis",
                    wrap_mode="balanced", align="left",
                ),
            ],
        )
    )

post = instagram_post(
    canvases=canvases,
    texts=[
        TextConfig(
            content="@postcanvas",
            x="7%", y="94%", anchor="bottomleft",
            font_size=22, opacity=0.68, align="left",
        )
    ],
    output_dir="./output/examples/carousel",
)

print(generate(post))
