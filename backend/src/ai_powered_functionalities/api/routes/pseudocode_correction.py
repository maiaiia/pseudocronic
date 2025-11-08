from fastapi import APIRouter, HTTPException

from ...correction_pseudocode.corrector import CodeCorrector
from ...models.requests import CodeCorrectionRequest
from ...models.responses import CodeCorrectionResponse

router = APIRouter(prefix="/correction", tags=["Code Correction"])

corrector = CodeCorrector()


@router.post("/", response_model=CodeCorrectionResponse)
async def correct_pseudocode(request: CodeCorrectionRequest):
    """
    Correct Romanian pseudocode according to pbinfo.ro rules.

    - **code**: The pseudocode to correct
    """
    try:
        result = await corrector.correct_code(
            code=request.code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))