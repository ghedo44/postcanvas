"""
postcanvas – Generate social-media images with Python.

Quick start
-----------
from postcanvas import generate
from postcanvas.presets import instagram_post
from postcanvas.models import BackgroundConfig, TextConfig, ShadowConfig

post = instagram_post(
    background=BackgroundConfig(color="#1a1a2e"),
    texts=[
        TextConfig(
            content="Hello World",
            y="45%",
            font_size=96,
            color="#e94560",
            shadow=ShadowConfig(blur_radius=12),
        )
    ],
    output_dir="./out",
)

paths = generate(post)

Cloud storage example
--------------------
from postcanvas import generate, image_to_bytes, GenerateResult
from postcanvas.models import OutputFormat

# Generate images without saving to disk
images = generate(post, save=False, return_images=True)

# Convert to bytes and upload to cloud storage
for img in images:
    data = image_to_bytes(img, format=OutputFormat.PNG)
    # s3_client.put_object(Bucket='bucket', Key='image.png', Body=data)

# Get both paths and images
result = generate(post, save=True, return_images=True)  # Returns GenerateResult
assert isinstance(result, GenerateResult)
paths = result.paths
images = result.images
"""

from .renderer import generate, render_one, image_to_bytes, save_image_to_path, GenerateResult
from . import models, presets

__version__ = "0.1.0"
__all__ = [
    "generate", "render_one", "image_to_bytes", "save_image_to_path", "GenerateResult",
    "models", "presets"
]
