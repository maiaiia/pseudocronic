from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from ...config import get_settings
from ...models.responses import OCRResponse
from ...ocr.text_extractor import TextExtractor
from ....rate_limiter import rate_limit

router = APIRouter(prefix="/ocr", tags=["Image to Text"])

text_extractor = TextExtractor()
settings = get_settings()


@router.post("/", response_model=OCRResponse)
@rate_limit(max_calls=3, window_hours=1)
async def extract_pseudocode_from_image(
        request: Request,
        image: UploadFile = File(..., description="Image containing pseudocode")
):
    """
    Extract Romanian pseudocode from an image.

    Supported formats: JPG, JPEG, PNG, BMP
    Max size: 10MB
    """
    # Validate file type
    if image.content_type not in [f"image/{fmt}" for fmt in settings.ALLOWED_IMAGE_FORMATS]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_IMAGE_FORMATS}"
        )

    # Read image bytes
    image_bytes = await image.read()

    # Validate file size
    if len(image_bytes) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_IMAGE_SIZE_MB}MB"
        )

    try:
        result = await text_extractor.extract_and_clean(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))