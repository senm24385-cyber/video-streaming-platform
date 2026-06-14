"""Health check routes"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "video-streaming-api"}
