from fastapi import FastAPI

from .router import router
from fastapi.middleware.cors import CORSMiddleware
from .ai_powered_functionalities.api.routes import ocr, pseudocode_correction

app = FastAPI(title="Pseudocronic")

app.include_router(router)
app.include_router(pseudocode_correction.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
