from pydantic import BaseModel
from typing import Optional, List

class CodeCorrectionResponse(BaseModel):
    corrected_code: str
    has_errors: bool
    errors_found: Optional[List[str]] = None
    explanation: Optional[str] = None

class OCRResponse(BaseModel):
    extracted_text: str
    confidence: Optional[str] = None
    preprocessing_applied: List[str]