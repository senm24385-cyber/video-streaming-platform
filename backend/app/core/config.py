"""Application configuration using Pydantic Settings"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App
    APP_NAME: str = "Video Streaming Platform"
    ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/video_streaming"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "video-streaming-bucket"
    AWS_REGION: str = "us-east-1"

    # Video Processing
    FFMPEG_PATH: str = "/usr/bin/ffmpeg"
    VIDEO_UPLOAD_DIR: str = "./uploads"
    VIDEO_CHUNK_SIZE: int = 10485760  # 10MB
    MAX_VIDEO_SIZE: int = 10737418240  # 10GB

    # HLS Configuration
    HLS_SEGMENT_DURATION: int = 10  # seconds
    HLS_OUTPUT_DIR: str = "./hls_output"
    HLS_BITRATES: List[int] = [360, 480, 720, 1080]  # p quality

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
