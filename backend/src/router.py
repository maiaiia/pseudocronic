from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from . import service

router = APIRouter()


class PseudocodeRequest(BaseModel):
    pseudocode: str


@router.post("/ptc")
def pseudocode_to_cpp(request: PseudocodeRequest):
    cpp_code = service.pseudocode_to_cpp(request.pseudocode)
    if not cpp_code:
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"cpp_code": cpp_code}
