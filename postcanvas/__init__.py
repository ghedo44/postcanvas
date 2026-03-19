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
"""

from .renderer import generate, render_one
from . import models, presets

__version__ = "0.1.0"
__all__ = ["generate", "render_one", "models", "presets"]
