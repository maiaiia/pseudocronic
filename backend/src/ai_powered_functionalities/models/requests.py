from pydantic import BaseModel, Field
from typing import Optional

class CodeCorrectionRequest(BaseModel):
    code: str = Field(..., description="Pseudocod in Romana care trebuie corectat")

class OCRRequest(BaseModel):
    # Will be handled via file upload in endpoint
    pass