/// Video Provider - State management for video playback
/// 
/// Manages:
/// - Video list and metadata
/// - Current video playback state
/// - Quality selection and adaptive bitrate
/// - Loading and error states

import 'package:flutter/material.dart';
import 'package:video_streaming_platform/core/services/api_service.dart';

class VideoProvider extends ChangeNotifier {
  final ApiService apiService;

  List<Map<String, dynamic>> videos = [];
  Map<String, dynamic>? currentVideo;
  bool isLoading = false;
  String? error;
  String selectedQuality = '720p'; // Default quality

  VideoProvider({required this.apiService});

  /// Fetch videos list
  Future<void> fetchVideos({int skip = 0, int limit = 10}) async {
    isLoading = true;
    error = null;
    notifyListeners();

    try {
      videos = await apiService.getVideos(skip: skip, limit: limit);
      isLoading = false;
    } catch (e) {
      error = e.toString();
      isLoading = false;
    }
    notifyListeners();
  }

  /// Load specific video metadata
  Future<void> loadVideo(int videoId) async {
    isLoading = true;
    error = null;
    notifyListeners();

    try {
      currentVideo = await apiService.getVideo(videoId);
      isLoading = false;
    } catch (e) {
      error = e.toString();
      isLoading = false;
    }
    notifyListeners();
  }

  /// Get HLS playlist URL for current video
  String? getPlaylistUrl() {
    if (currentVideo == null) return null;
    return apiService.getPlaylistUrl(currentVideo!['id']);
  }

  /// Change video quality
  void setQuality(String quality) {
    selectedQuality = quality;
    notifyListeners();
  }

  /// Check video transcoding status
  Future<void> checkTranscodingStatus(int videoId) async {
    try {
      final status = await apiService.getTranscodingStatus(videoId);
      if (status['status'] == 'ready') {
        await loadVideo(videoId);
      }
    } catch (e) {
      error = e.toString();
    }
    notifyListeners();
  }
}
