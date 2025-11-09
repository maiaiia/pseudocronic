from fastapi import APIRouter, HTTPException, Request, Body

from ...correction_pseudocode.corrector import CodeCorrector
from ...models.requests import CodeCorrectionRequest
from ...models.responses import CodeCorrectionResponse
from ....rate_limiter import rate_limit

router = APIRouter(prefix="/correction", tags=["Code Correction"])

corrector = CodeCorrector()


@router.post("/", response_model=CodeCorrectionResponse)
@rate_limit(max_calls=10, window_hours=1)
async def correct_pseudocode(
        request: Request,
        request_data: CodeCorrectionRequest = Body(...)
):

    """
    Correct Romanian pseudocode according to pbinfo.ro rules.

    - **code**: The pseudocode to correct
    """
    try:
        result = await corrector.correct_code(
            code=request_data.code
        )
        result_dict = result.dict() if hasattr(result, 'dict') else result
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))