"""Video streaming routes (HLS)

This module handles:
- HLS playlist serving (.m3u8 files)
- Segment serving (.ts files)
- Adaptive bitrate selection
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
import os

from app.core.config import settings

router = APIRouter()


@router.get("/videos/{video_id}/playlist.m3u8")
async def get_hls_playlist(video_id: int):
    """
    Serve HLS master playlist (.m3u8).
    
    The master playlist contains references to variant playlists
    for different quality levels. Client uses this to implement
    adaptive bitrate streaming.
    
    Example playlist structure:
    ```
    #EXTM3U
    #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
    playlist-360p.m3u8
    #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
    playlist-480p.m3u8
    #EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720
    playlist-720p.m3u8
    #EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
    playlist-1080p.m3u8
    ```
    """
    # TODO: Read from storage and return master playlist
    playlist_path = os.path.join(
        settings.HLS_OUTPUT_DIR, f"video_{video_id}", "master.m3u8"
    )

    if not os.path.exists(playlist_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    return FileResponse(playlist_path, media_type="application/vnd.apple.mpegurl")


@router.get("/videos/{video_id}/playlist-{quality}.m3u8")
async def get_variant_playlist(video_id: int, quality: str):
    """
    Serve HLS variant playlist for specific quality.
    
    This playlist contains references to actual video segments (.ts files).
    
    - **video_id**: ID of the video
    - **quality**: Quality level (360p, 480p, 720p, 1080p)
    
    Example variant playlist:
    ```
    #EXTM3U
    #EXT-X-VERSION:3
    #EXT-X-TARGETDURATION:10
    #EXT-X-MEDIA-SEQUENCE:0
    #EXTINF:10.0,
    segment-0000.ts
    #EXTINF:10.0,
    segment-0001.ts
    ...
    #EXT-X-ENDLIST
    ```
    """
    # TODO: Read variant playlist from storage
    playlist_path = os.path.join(
        settings.HLS_OUTPUT_DIR, f"video_{video_id}", f"playlist-{quality}.m3u8"
    )

    if not os.path.exists(playlist_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quality variant not found"
        )

    return FileResponse(playlist_path, media_type="application/vnd.apple.mpegurl")


@router.get("/videos/{video_id}/segments/{segment_name}")
async def get_segment(video_id: int, segment_name: str):
    """
    Serve individual video segment (TS file).
    
    Segments are typically 10 seconds of video. Client requests these
    based on the variant playlist and implements adaptive bitrate by
    choosing quality based on available bandwidth.
    
    - **video_id**: ID of the video
    - **segment_name**: Name of segment file (e.g., segment-0000.ts)
    """
    segment_path = os.path.join(
        settings.HLS_OUTPUT_DIR, f"video_{video_id}", "segments", segment_name
    )

    if not os.path.exists(segment_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found"
        )

    return FileResponse(segment_path, media_type="video/mp2t")


@router.get("/videos/{video_id}/status")
async def get_streaming_status(video_id: int):
    """
    Get video transcoding and availability status.
    
    Returns which quality levels are available for streaming.
    """
    # TODO: Query database for video status
    return {
        "video_id": video_id,
        "status": "ready",
        "available_qualities": ["360p", "480p", "720p", "1080p"],
        "message": "Video ready for streaming",
    }
