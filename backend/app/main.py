"""FastAPI application entry point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import videos, uploads, streaming, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    print("🚀 Video Streaming Platform starting...")
    yield
    # Shutdown
    print("🛑 Video Streaming Platform shutting down...")


app = FastAPI(
    title="Video Streaming Platform API",
    description="YouTube-like video streaming backend with HLS support",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Route
@app.get("/health", tags=["Health"])
async def health_check():
    """Application health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "video-streaming-platform"},
    )


# Include API Routes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["Videos"])
app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["Uploads"])
app.include_router(streaming.router, prefix="/api/v1/stream", tags=["Streaming"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development",
    )
