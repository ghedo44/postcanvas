"""Cloud-friendly image and byte output."""

from pathlib import Path

from postcanvas import image_to_bytes, render, save_image_to_path
from postcanvas.models import BackgroundConfig, OutputFormat, TextConfig
from postcanvas.presets import blog_og

post = blog_og(
    background=BackgroundConfig(color="#111827"),
    texts=[
        TextConfig(
            content="Postcanvas 1.0 — social graphics built like software",
            x="7%", y="20%", width="86%", height="55%",
            anchor="topleft", font_size=72, min_font_size=30,
            fit="shrink", overflow="ellipsis", wrap_mode="balanced", align="left",
        )
    ],
)

result = render(post)
image = result.images[0]
payload = image_to_bytes(image, format=OutputFormat.WEBP, quality=90)
print(f"encoded {len(payload)} bytes")

Path("./output/examples/cloud").mkdir(parents=True, exist_ok=True)
save_image_to_path(image, "./output/examples/cloud/blog-og.webp")
