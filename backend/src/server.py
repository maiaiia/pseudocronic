from fastapi import FastAPI

from .router import router

app = FastAPI(title="Pseudocronic")

app.include_router(router)
