from pydantic import BaseModel, Field
from typing import Optional

class CodeCorrectionRequest(BaseModel):
    code: str = Field(..., description="Pseudocod in Romana care trebuie corectat")
    provide_explanation: bool = Field(default=True, description="Include explicatii pentur corectii")

class OCRRequest(BaseModel):
    # Will be handled via file upload in endpoint
    pass