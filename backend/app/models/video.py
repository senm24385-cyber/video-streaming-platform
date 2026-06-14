"""Video model and related schemas"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text, func, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VideoStatus(str, Enum):
    """Video processing status"""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCODING = "transcoding"
    READY = "ready"
    FAILED = "failed"


class VideoQuality(str, Enum):
    """HLS video quality options"""

    P360 = "360p"
    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"


class VideoDB(Base):
    """Video database model with relationship to User
    
    Stores video metadata and tracks transcoding status.
    Each video is linked to a user (creator).
    """

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    hls_playlist_url = Column(String(500), nullable=True)
    status = Column(String(50), default=VideoStatus.UPLOADED)
    duration = Column(Integer, nullable=True)  # in seconds
    file_size = Column(Integer)  # in bytes
    views = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    transcoded_at = Column(DateTime, nullable=True)


class VideoUploadSchema(BaseModel):
    """Schema for video upload request"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    is_public: bool = True


class VideoMetadataSchema(BaseModel):
    """Schema for video metadata response"""

    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: str
    duration: Optional[int]
    file_size: int
    views: int
    is_public: bool
    hls_playlist_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    transcoded_at: Optional[datetime]

    class Config:
        from_attributes = True


class VideoDetailSchema(BaseModel):
    """Detailed video schema with user info"""

    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: str
    duration: Optional[int]
    file_size: int
    views: int
    is_public: bool
    hls_playlist_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoChunkUploadSchema(BaseModel):
    """Schema for chunked video upload"""

    chunk_index: int = Field(..., ge=0)
    total_chunks: int = Field(..., ge=1)
    chunk_hash: str = Field(..., description="MD5 hash of chunk for verification")


class VideoUpdateSchema(BaseModel):
    """Schema for updating video metadata"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    is_public: Optional[bool] = None
