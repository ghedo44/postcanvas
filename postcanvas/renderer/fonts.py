from __future__ import annotations
import os
from typing import Any, Optional
from PIL import ImageFont

FONT_DIRS = [
    "/usr/share/fonts", "/usr/local/share/fonts",
    "/System/Library/Fonts", "/Library/Fonts",
    "C:/Windows/Fonts",
    os.path.expanduser("~/Library/Fonts"),
]

FONT_MAP = {
    "arial": ["Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
    "helvetica": ["Helvetica.ttf", "helvetica.ttf", "LiberationSans-Regular.ttf"],
    "times": ["Times New Roman.ttf", "times.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "courier": ["Courier New.ttf", "cour.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"],
    "roboto": ["Roboto-Regular.ttf", "Roboto.ttf"],
    "open sans": ["OpenSans-Regular.ttf"],
    "inter": ["Inter-Regular.ttf", "Inter.ttf"],
}


def find_font(name: Optional[str], size: int) -> Any:
    if not name:
        name = "Arial"

    candidates = FONT_MAP.get(name.lower(), [name + ".ttf", name + "-Regular.ttf"])

    for font_dir in FONT_DIRS:
        if not os.path.isdir(font_dir):
            continue

        for candidate in candidates:
            direct_path = os.path.join(font_dir, candidate)
            if os.path.isfile(direct_path):
                try:
                    return ImageFont.truetype(direct_path, size)
                except Exception:
                    pass

            for sub in os.listdir(font_dir):
                nested_path = os.path.join(font_dir, sub, candidate)
                if os.path.isfile(nested_path):
                    try:
                        return ImageFont.truetype(nested_path, size)
                    except Exception:
                        pass

    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def resolve_font(path: Optional[str], family: Optional[str], size: int) -> Any:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return find_font(family, size)
