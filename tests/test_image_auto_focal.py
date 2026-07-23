from PIL import Image, ImageDraw

from postcanvas.models import ImageFit
from postcanvas.renderer.loader import estimate_focal_point, fit_image


def test_auto_focal_point_tracks_high_contrast_subject():
    image = Image.new("RGB", (300, 120), "#777777")
    draw = ImageDraw.Draw(image)
    draw.rectangle((230, 20, 295, 105), fill="#ffffff")
    draw.rectangle((245, 35, 280, 90), fill="#000000")
    focal_x, focal_y = estimate_focal_point(image)
    assert focal_x > 0.55
    assert 0.2 < focal_y < 0.8
    automatic = fit_image(image, 100, 120, ImageFit.COVER, focal_mode="auto")
    centered = fit_image(image, 100, 120, ImageFit.COVER, focal_mode="manual", focal_x=0.5)
    assert automatic.tobytes() != centered.tobytes()
