# Video Streaming Platform

A YouTube-like video streaming platform built with FastAPI (backend) and Flutter (frontend).

## Project Structure

- **backend/**: FastAPI server for video metadata, uploads, and streaming
- **frontend/**: Flutter mobile app with video player and feed

## Features

- Video upload with FFmpeg transcoding to HLS format
- Adaptive bitrate streaming (HLS)
- Vertical/horizontal video feed
- Chunked video upload and download
- Video metadata management

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
flutter pub get
flutter run
```

## Architecture

### Transcoding Pipeline
1. User uploads video chunks
2. Backend stores raw chunks
3. FFmpeg transcodes to HLS (multiple bitrates)
4. HLS segments stored in object storage
5. Frontend streams via HLS with adaptive bitrate
