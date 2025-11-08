from fastapi import APIRouter, HTTPException

from backend.src.ai_powered_functionalities.correction_pseudocode.corrector import CodeCorrector
from backend.src.ai_powered_functionalities.models.requests import CodeCorrectionRequest
from backend.src.ai_powered_functionalities.models.responses import CodeCorrectionResponse

router = APIRouter(prefix="/correction", tags=["Code Correction"])

corrector = CodeCorrector()


@router.post("/", response_model=CodeCorrectionResponse)
async def correct_pseudocode(request: CodeCorrectionRequest):
    """
    Correct Romanian pseudocode according to pbinfo.ro rules.

    - **code**: The pseudocode to correct
    - **provide_explanation**: Whether to include explanation of corrections
    """
    try:
        result = await corrector.correct_code(
            code=request.code,
            provide_explanation=request.provide_explanation
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))