/// Application configuration and constants

class AppConfig {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';
  static const String apiTimeout = '30000'; // 30 seconds in milliseconds

  // Video Configuration
  static const int videoChunkSize = 10 * 1024 * 1024; // 10MB
  static const List<String> supportedVideoFormats = [
    'mp4',
    'mov',
    'mkv',
    'avi',
    'webm',
  ];

  // HLS Configuration
  static const int hlsSegmentDuration = 10; // seconds
  static const List<String> hlsQualities = ['360p', '480p', '720p', '1080p'];

  // UI Configuration
  static const double defaultPadding = 16.0;
  static const double defaultBorderRadius = 12.0;

  static void init() {
    // Initialize any required configurations
    // Example: Set up logging, initialize storage, etc.
  }
}
