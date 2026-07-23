from PIL import Image, ImageDraw
import pytest

from postcanvas.testing import assert_image_similar, image_difference


def test_image_difference_detects_regression():
    expected = Image.new("RGBA", (40, 40), "white")
    actual = expected.copy()
    ImageDraw.Draw(actual).rectangle((10, 10, 20, 20), fill="black")
    difference = image_difference(actual, expected)
    assert difference.changed_pixel_ratio > 0
    assert difference.bounding_box == (10, 10, 21, 21)
    with pytest.raises(AssertionError):
        assert_image_similar(actual, expected)


def test_identical_images_are_exactly_similar():
    image = Image.new("RGBA", (40, 40), "white")
    assert_image_similar(image, image.copy())
