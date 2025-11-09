from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.ai_powered_functionalities.api.routes import ocr, pseudocode_correction, generate_problem_statement

app = FastAPI(
    title="Romanian Pseudocode Translator API",
    description="API for correcting and extracting Romanian pseudocode",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pseudocode_correction.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")

app.include_router(generate_problem_statement.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Romanian Pseudocode Translator API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}