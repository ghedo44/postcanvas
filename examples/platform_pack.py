"""Render a shared headline across several platform presets."""

from postcanvas import render
from postcanvas.models import BackgroundConfig, TextConfig
from postcanvas.presets import (
    instagram_portrait,
    instagram_post,
    instagram_story,
    linkedin_post,
    x_post,
    youtube_thumbnail,
)

builders = {
    "instagram-square": instagram_post,
    "instagram-portrait": instagram_portrait,
    "instagram-story": instagram_story,
    "linkedin": linkedin_post,
    "x-post": x_post,
    "youtube": youtube_thumbnail,
}

for name, builder in builders.items():
    post = builder(
        background=BackgroundConfig(color="#0B1020"),
        texts=[
            TextConfig(
                content="One content system.\nEvery social surface.",
                x="8%", y="22%", width="84%", height="46%",
                anchor="topleft", font_size=92, min_font_size=32,
                max_lines=4, fit="shrink", overflow="ellipsis",
                wrap_mode="balanced", align="left",
            )
        ],
        output_dir="./output/examples/platform-pack",
        output_filename=name,
    )
    render(post, save=True)
