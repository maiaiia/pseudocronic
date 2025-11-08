from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Tuple

class ImageProcessor:
    @staticmethod
    def preprocess_image(image_bytes: bytes) -> Tuple[Image.Image, list]:
        """Preprocess image for better OCR results"""
        preprocessing_steps = []

        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        preprocessing_steps.append("Loaded image")

        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
            preprocessing_steps.append("Converted to grayscale")

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        preprocessing_steps.append("Enhanced contrast")

        # Apply sharpening
        image = image.filter(ImageFilter.SHARPEN)
        preprocessing_steps.append("Applied sharpening")

        # Increase size if too small (helps OCR)
        width, height = image.size
        if width < 1000 or height < 1000:
            scale = 2.0
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            preprocessing_steps.append(f"Upscaled by {scale}x")

        return image, preprocessing_steps