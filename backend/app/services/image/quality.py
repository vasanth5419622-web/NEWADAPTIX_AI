import math
from typing import Tuple, List, Optional
from PIL import Image, ImageStat, ImageOps
import numpy as np
from app.core.config import settings
from app.schemas.shared import ImageQualityResult

class ImageQualityChecker:
    """
    Performs deterministic pre-flight image quality validation:
    - Blur detection (discrete Laplacian variance)
    - Brightness & Contrast analysis
    - Minimum resolution check
    - Actionable feedback generation
    """
    def __init__(
        self,
        min_blur_variance: float = settings.min_blur_variance,
        min_brightness: float = settings.min_brightness,
        max_brightness: float = settings.max_brightness,
        min_contrast: float = settings.min_contrast,
        min_resolution: int = settings.min_resolution,
    ):
        self.min_blur_variance = min_blur_variance
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_contrast = min_contrast
        self.min_resolution = min_resolution

    def check_quality(self, image_path: str) -> ImageQualityResult:
        issues: List[str] = []
        
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img) # Correct orientation
                width, height = img.size
                
                # 1. Resolution Check
                if width < self.min_resolution or height < self.min_resolution:
                    issues.append(f"Image resolution too low ({width}x{height}px). Minimum is {self.min_resolution}x{self.min_resolution}px.")

                # Convert to Grayscale for Blur and Photometric Analysis
                gray_img = img.convert("L")
                
                # 2. Photometric Analysis (Brightness & Contrast)
                stat = ImageStat.Stat(gray_img)
                mean_brightness = stat.mean[0]
                std_contrast = stat.stddev[0]
                
                if mean_brightness < self.min_brightness:
                    issues.append("Image is severely underexposed (too dark). Provide better illumination.")
                elif mean_brightness > self.max_brightness:
                    issues.append("Image is overexposed (glare / washed out). Avoid direct flash glare.")
                    
                if std_contrast < self.min_contrast:
                    issues.append("Image has low contrast; crop features are difficult to distinguish.")

                # 3. Blur Detection (Laplacian Kernel Variance)
                blur_score = self._calculate_laplacian_variance(gray_img)
                if blur_score < self.min_blur_variance:
                    issues.append(f"Image appears blurry (sharpness score {blur_score:.1f} < threshold {self.min_blur_variance}). Please hold the camera steady.")

                passed = len(issues) == 0
                actionable_msg = None
                if not passed:
                    actionable_msg = (
                        "The uploaded photograph does not meet quality requirements: "
                        + "; ".join(issues)
                        + ". Please upload a closer, focused, and well-lit photo of the affected plant parts."
                    )

                return ImageQualityResult(
                    passed=passed,
                    blur_score=round(float(blur_score), 2),
                    brightness_score=round(float(mean_brightness), 2),
                    contrast_score=round(float(std_contrast), 2),
                    resolution=[width, height],
                    issues=issues,
                    actionable_message=actionable_msg
                )

        except Exception as e:
            return ImageQualityResult(
                passed=False,
                blur_score=0.0,
                brightness_score=0.0,
                contrast_score=0.0,
                resolution=[0, 0],
                issues=[f"Unable to parse or read image file: {str(e)}"],
                actionable_message="The image format is invalid or corrupted. Please upload a valid JPG or PNG file."
            )

    def _calculate_laplacian_variance(self, gray_img: Image.Image) -> float:
        """
        Calculates Laplacian kernel variance using pure numpy without requiring heavy opencv.
        """
        arr = np.array(gray_img, dtype=np.float64)
        
        # Downsample large images for fast processing while maintaining sharpness ratio
        if arr.shape[0] > 600 or arr.shape[1] > 600:
            step_y = max(1, arr.shape[0] // 400)
            step_x = max(1, arr.shape[1] // 400)
            arr = arr[::step_y, ::step_x]

        # 3x3 Discrete Laplacian Kernel
        # [ 0,  1,  0 ]
        # [ 1, -4,  1 ]
        # [ 0,  1,  0 ]
        if arr.shape[0] < 3 or arr.shape[1] < 3:
            return 0.0

        top = arr[:-2, 1:-1]
        bottom = arr[2:, 1:-1]
        left = arr[1:-1, :-2]
        right = arr[1:-1, 2:]
        center = arr[1:-1, 1:-1]

        laplacian = top + bottom + left + right - 4 * center
        variance = float(np.var(laplacian))
        return variance

image_quality_checker = ImageQualityChecker()
