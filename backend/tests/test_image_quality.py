import pytest
import numpy as np
from PIL import Image
from app.services.image.quality import ImageQualityChecker

def test_image_quality_sharp_image(tmp_path):
    # Create sharp image with high variance
    img_path = tmp_path / "sharp_leaf.png"
    arr = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    Image.fromarray(arr).save(img_path)

    checker = ImageQualityChecker()
    res = checker.check_quality(str(img_path))
    assert res.resolution == [300, 300]
    assert res.blur_score > 0

def test_image_quality_blurry_low_resolution(tmp_path):
    # Create very small low res image
    img_path = tmp_path / "tiny_bad.jpg"
    arr = np.zeros((80, 80, 3), dtype=np.uint8)
    Image.fromarray(arr).save(img_path)

    checker = ImageQualityChecker(min_resolution=150)
    res = checker.check_quality(str(img_path))
    assert res.passed is False
    assert any("resolution too low" in issue for issue in res.issues)
    assert res.actionable_message is not None
