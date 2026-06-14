"""FFmpeg transcoding service

This module handles video transcoding to HLS format with multiple bitrates.

Transcoding Pipeline:
1. Input: Raw video file (any format: mp4, mov, mkv, etc.)
2. FFmpeg processing:
   - Decode video/audio
   - Re-encode to H.264 video codec with multiple bitrates
   - Re-encode audio to AAC
   - Generate HLS segments (typically 10 seconds each)
3. Output: Master playlist + variant playlists for each bitrate

Example FFmpeg command:
```bash
ffmpeg -i input.mp4 \
  -preset medium \
  -vf "scale=640:360" \
  -b:v 500k -maxrate 500k -bufsize 1000k \
  -b:a 128k \
  -hls_time 10 \
  -hls_list_size 0 \
  output-360p.m3u8
```

For adaptive streaming, generate multiple bitrates:
- 360p: 500kbps
- 480p: 1000kbps
- 720p: 2000kbps
- 1080p: 5000kbps
"""

import asyncio
import os
import subprocess
from typing import Dict, List

from app.core.config import settings


class TranscodingService:
    """Service for video transcoding with FFmpeg"""

    # Video quality presets with bitrate and resolution
    QUALITY_PRESETS = {
        "360p": {"width": 640, "height": 360, "video_bitrate": "500k", "audio_bitrate": "128k"},
        "480p": {"width": 854, "height": 480, "video_bitrate": "1000k", "audio_bitrate": "128k"},
        "720p": {"width": 1280, "height": 720, "video_bitrate": "2000k", "audio_bitrate": "192k"},
        "1080p": {"width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "256k"},
    }

    @staticmethod
    async def transcode_to_hls(video_id: int, input_path: str, output_dir: str) -> Dict:
        """
        Transcode video to HLS format with multiple bitrate variants.
        
        Args:
            video_id: ID of the video being transcoded
            input_path: Path to input video file
            output_dir: Directory to store HLS output
            
        Returns:
            Dictionary with transcoding results and status
        """
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Transcode to each quality level
            tasks = []
            for quality in TranscodingService.QUALITY_PRESETS.keys():
                task = TranscodingService._transcode_quality(
                    input_path, output_dir, quality
                )
                tasks.append(task)

            # Run all transcoding tasks concurrently
            results = await asyncio.gather(*tasks)

            # Create master playlist
            master_playlist = TranscodingService._create_master_playlist(output_dir)

            return {
                "video_id": video_id,
                "status": "completed",
                "qualities": list(TranscodingService.QUALITY_PRESETS.keys()),
                "master_playlist": master_playlist,
                "results": results,
            }

        except Exception as e:
            return {
                "video_id": video_id,
                "status": "failed",
                "error": str(e),
            }

    @staticmethod
    async def _transcode_quality(input_path: str, output_dir: str, quality: str) -> Dict:
        """
        Transcode video to specific quality level using FFmpeg.
        
        Args:
            input_path: Path to input video
            output_dir: Output directory for HLS files
            quality: Quality preset (360p, 480p, 720p, 1080p)
            
        Returns:
            Transcoding result for this quality
        """
        preset = TranscodingService.QUALITY_PRESETS[quality]
        output_playlist = os.path.join(output_dir, f"playlist-{quality}.m3u8")

        # FFmpeg command for HLS transcoding
        cmd = [
            settings.FFMPEG_PATH,
            "-i", input_path,
            "-vf", f"scale={preset['width']}:{preset['height']}",
            "-c:v", "libx264",
            "-preset", "medium",
            "-b:v", preset["video_bitrate"],
            "-maxrate", preset["video_bitrate"],
            "-bufsize", str(int(preset["video_bitrate"].rstrip('k')) * 2) + "k",
            "-c:a", "aac",
            "-b:a", preset["audio_bitrate"],
            "-hls_time", str(settings.HLS_SEGMENT_DURATION),
            "-hls_list_size", "0",
            "-hls_segment_filename", os.path.join(output_dir, f"segment-{quality}-%05d.ts"),
            output_playlist,
        ]

        try:
            # Run FFmpeg command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {
                    "quality": quality,
                    "status": "failed",
                    "error": stderr.decode(),
                }

            return {
                "quality": quality,
                "status": "success",
                "output_playlist": output_playlist,
            }

        except Exception as e:
            return {
                "quality": quality,
                "status": "failed",
                "error": str(e),
            }

    @staticmethod
    def _create_master_playlist(output_dir: str) -> str:
        """
        Create HLS master playlist that references all quality variants.
        
        Master playlist allows player to:
        1. Implement adaptive bitrate switching
        2. Choose quality based on available bandwidth
        3. Switch quality mid-stream
        """
        master_content = "#EXTM3U\n#EXT-X-VERSION:3\n"

        # Add stream info for each quality
        bandwidth_map = {"360p": 500000, "480p": 1000000, "720p": 2000000, "1080p": 5000000}
        resolution_map = {"360p": "640x360", "480p": "854x480", "720p": "1280x720", "1080p": "1920x1080"}

        for quality in TranscodingService.QUALITY_PRESETS.keys():
            master_content += (
                f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth_map[quality]},"
                f"RESOLUTION={resolution_map[quality]}\n"
                f"playlist-{quality}.m3u8\n"
            )

        master_path = os.path.join(output_dir, "master.m3u8")
        with open(master_path, "w") as f:
            f.write(master_content)

        return master_path
