import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BASE_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_BACKEND_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.core.config import settings, UPLOAD_DIR, BASE_DIR
from app.api.endpoints import router as api_router
from app.core.logging import logger

app = FastAPI(
    title="ADAPTIX-FARM — Adaptive Multimodal AI for Accessible Crop Intelligence",
    description="Production-grade agentic crop advisory system featuring adaptive routing, RAG retrieval, multi-evidence fusion, and independent verification.",
    version="1.0.0"
)

# CORS middleware for open API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api")

# Static file serving for uploaded crop photographs
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Frontend directory
FRONTEND_DIR = BASE_DIR.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend_static")

    @app.get("/")
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse({"status": "ADAPTIX-FARM API running. Frontend index.html not found."})

@app.on_event("startup")
async def on_startup():
    logger.info(f"ADAPTIX-FARM Backend starting up on {settings.host}:{settings.port} (Env: {settings.app_env})")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
