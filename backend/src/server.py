from fastapi import FastAPI

from .router import router
from fastapi.middleware.cors import CORSMiddleware
from .ai_powered_functionalities.api.routes import ocr, pseudocode_correction
from .ws import router as ws_router

app = FastAPI(title="Pseudocronic")

app.include_router(router)
app.include_router(pseudocode_correction.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")
app.include_router(ws_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
