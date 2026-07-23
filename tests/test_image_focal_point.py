from PIL import Image

from postcanvas.models import ImageFit
from postcanvas.renderer.loader import fit_image


def test_cover_crop_uses_focal_point():
    source = Image.new("RGB", (200, 100), "red")
    for x in range(100, 200):
        for y in range(100):
            source.putpixel((x, y), (0, 0, 255))
    left = fit_image(source, 80, 100, ImageFit.COVER, focal_x=0.0)
    right = fit_image(source, 80, 100, ImageFit.COVER, focal_x=1.0)
    assert left.getpixel((40, 50)) != right.getpixel((40, 50))
