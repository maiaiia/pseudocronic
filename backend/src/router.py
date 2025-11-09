from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from . import service

router = APIRouter()


class PseudocodeRequest(BaseModel):
    pseudocode: str


class CppRequest(BaseModel):
    cpp_code: str

class StepByStepRequest(BaseModel):
    pseudocode: str

@router.post("/ptc")
def pseudocode_to_cpp(request: PseudocodeRequest):
    cpp_code = service.pseudocode_to_cpp(request.pseudocode)
    if not cpp_code:
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"cpp_code": cpp_code}


@router.post("/ctp")
def cpp_to_pseudocode(request: CppRequest):
    pseudocode = service.cpp_to_pseudocode(request.cpp_code)
    if not pseudocode:
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"pseudocode": pseudocode}

@router.post("/sbs")
def step_by_step_execution(request: StepByStepRequest):
    trace = service.step_by_step_execution(request.pseudocode)
    if not trace:
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"json_execution": trace}