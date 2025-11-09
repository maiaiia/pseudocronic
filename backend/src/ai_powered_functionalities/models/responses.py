from pydantic import BaseModel, Field
from typing import Optional, List

class CodeCorrectionResponse(BaseModel):
    corrected_code: str
    has_errors: bool
    errors_found: Optional[List[str]] = None
    explanation: Optional[str] = None
    remaining_calls: Optional[int] = None

class OCRResponse(BaseModel):
    extracted_text: str
    confidence: Optional[str] = None
    preprocessing_applied: List[str]
    remaining_calls: Optional[int] = None


class GenerateProblemStatementResponse(BaseModel):
        enunt: str = Field(..., description="Enunțul problemei")
        date_intrare: str = Field(..., description="Descrierea datelor de intrare")
        date_iesire: str = Field(..., description="Descrierea datelor de ieșire")
        exemplu_intrare: str = Field(..., description="Exemplu de input")
        exemplu_iesire: str = Field(..., description="Exemplu de output")
        nivel_dificultate: Optional[str] = Field(default="mediu", description="Nivelul de dificultate")