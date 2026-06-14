"""FastAPI application entry point with database and authentication setup"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database import init_db
from app.api.routes import videos, uploads, streaming, health, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management
    
    Handles startup and shutdown events:
    - Startup: Initialize database tables
    - Shutdown: Clean up resources
    """
    # Startup
    print("🚀 Video Streaming Platform starting...")
    init_db()  # Initialize database tables
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


# ==================== Root Health Check ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Application health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "video-streaming-platform"},
    )


# ==================== API Routes ====================

# Authentication routes (public)
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

# Health routes
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

# Video management routes (protected)
app.include_router(
    videos.router,
    prefix="/api/v1/videos",
    tags=["Videos"],
)

# Video upload routes (protected)
app.include_router(
    uploads.router,
    prefix="/api/v1/uploads",
    tags=["Uploads"],
)

# Video streaming routes (public - HLS delivery)
app.include_router(
    streaming.router,
    prefix="/api/v1/stream",
    tags=["Streaming"],
)


# ==================== API Documentation ====================

@app.get("/", tags=["Documentation"])
async def root():
    """
    Welcome endpoint with API documentation links.
    
    Returns useful information about the API and links to documentation.
    """
    return {
        "service": "Video Streaming Platform API",
        "version": "0.1.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "auth": {
                "signup": "POST /api/v1/auth/signup",
                "login": "POST /api/v1/auth/login",
                "me": "GET /api/v1/auth/me",
                "refresh": "POST /api/v1/auth/refresh",
                "logout": "POST /api/v1/auth/logout",
            },
            "videos": {
                "list": "GET /api/v1/videos",
                "get": "GET /api/v1/videos/{video_id}",
                "create": "POST /api/v1/videos",
                "update": "PUT /api/v1/videos/{video_id}",
                "delete": "DELETE /api/v1/videos/{video_id}",
            },
            "uploads": {
                "initiate": "POST /api/v1/uploads/initiate",
                "chunk": "POST /api/v1/uploads/chunk",
                "complete": "POST /api/v1/uploads/complete",
            },
            "streaming": {
                "playlist": "GET /api/v1/stream/videos/{video_id}/playlist.m3u8",
                "variant": "GET /api/v1/stream/videos/{video_id}/playlist-{quality}.m3u8",
                "segment": "GET /api/v1/stream/videos/{video_id}/segments/{segment_name}",
                "status": "GET /api/v1/stream/videos/{video_id}/status",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development",
    )
