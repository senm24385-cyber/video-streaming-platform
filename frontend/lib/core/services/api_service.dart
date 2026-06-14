/// API Service for backend communication
/// 
/// Handles all HTTP requests to the video streaming backend.
/// Uses Dio for HTTP client with interceptors for error handling.

import 'package:dio/dio.dart';
import 'package:video_streaming_platform/core/config/app_config.dart';

class ApiService {
  late Dio _dio;

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
        },
      ),
    );

    // Add interceptors for logging and error handling
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Add authorization token if available
        // options.headers['Authorization'] = 'Bearer $token';
        return handler.next(options);
      },
      onError: (DioException e, handler) {
        // Handle errors globally
        print('API Error: ${e.message}');
        return handler.next(e);
      },
    ));
  }

  /// Get list of videos with pagination
  Future<List<Map<String, dynamic>>> getVideos({
    int skip = 0,
    int limit = 10,
  }) async {
    try {
      final response = await _dio.get(
        '/videos',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get video metadata by ID
  Future<Map<String, dynamic>> getVideo(int videoId) async {
    try {
      final response = await _dio.get('/videos/$videoId');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Initiate video upload session
  Future<Map<String, dynamic>> initiateUpload(int videoId) async {
    try {
      final response = await _dio.post(
        '/uploads/initiate',
        data: {'video_id': videoId},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Upload video chunk
  /// 
  /// Called for each chunk of the video file.
  /// The chunk data is sent as multipart form data.
  Future<Map<String, dynamic>> uploadChunk({
    required int videoId,
    required int chunkIndex,
    required int totalChunks,
    required String chunkHash,
    required List<int> chunkData,
    Function(int, int)? onProgress,
  }) async {
    try:
      final formData = FormData.fromMap({
        'video_id': videoId,
        'chunk_index': chunkIndex,
        'total_chunks': totalChunks,
        'chunk_hash': chunkHash,
        'file': MultipartFile.fromBytes(
          chunkData,
          filename: 'chunk_$chunkIndex',
        ),
      });

      final response = await _dio.post(
        '/uploads/chunk',
        data: formData,
        onSendProgress: (int sent, int total) {
          onProgress?.call(sent, total);
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark upload as complete and start transcoding
  Future<Map<String, dynamic>> completeUpload(int videoId) async {
    try {
      final response = await _dio.post(
        '/uploads/complete',
        data: {'video_id': videoId},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get HLS master playlist URL for video
  String getPlaylistUrl(int videoId) {
    return '$${AppConfig.apiBaseUrl}/stream/videos/$videoId/playlist.m3u8';
  }

  /// Get transcoding status of video
  Future<Map<String, dynamic>> getTranscodingStatus(int videoId) async {
    try {
      final response = await _dio.get('/stream/videos/$videoId/status');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  String _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        return 'Connection timeout';
      case DioExceptionType.receiveTimeout:
        return 'Receive timeout';
      case DioExceptionType.badResponse:
        return 'Bad response: ${e.response?.statusCode}';
      case DioExceptionType.unknown:
        return 'Unknown error: ${e.message}';
      default:
        return 'Error: ${e.message}';
    }
  }
}
