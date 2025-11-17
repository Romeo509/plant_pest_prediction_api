from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from api.routes import router
import os

app = FastAPI(
    title="AgriCom Pest Prediction API",
    description="API for predicting maize diseases using deep learning",
    version="1.0.0"
)

# Include API routes
app.include_router(router, prefix="/api", tags=["predictions"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serve the demo HTML page
    """
    with open("templates/index.html", "r") as f:
        return f.read()

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
