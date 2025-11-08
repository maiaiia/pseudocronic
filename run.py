import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.ai_powered_functionalities.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )