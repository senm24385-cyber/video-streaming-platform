/// Stateful Video Player Widget
/// 
/// Implements:
/// - HLS video playback with Chewie player
/// - Adaptive bitrate switching
/// - Playback controls (play, pause, seek, fullscreen)
/// - Buffering indicators
/// - Quality selection UI

import 'package:flutter/material.dart';
import 'package:chewie/chewie.dart';
import 'package:video_player/video_player.dart';

class VideoPlayerWidget extends StatefulWidget {
  /// HLS playlist URL from backend
  final String playlistUrl;
  
  /// Callback when quality changes
  final Function(String)? onQualityChanged;
  
  /// Available quality options
  final List<String> qualities;

  const VideoPlayerWidget({
    Key? key,
    required this.playlistUrl,
    this.onQualityChanged,
    this.qualities = const ['360p', '480p', '720p', '1080p'],
  }) : super(key: key);

  @override
  State<VideoPlayerWidget> createState() => _VideoPlayerWidgetState();
}

class _VideoPlayerWidgetState extends State<VideoPlayerWidget> {
  late VideoPlayerController _videoPlayerController;
  late ChewieController _chewieController;
  String _selectedQuality = '720p';
  bool _showQualityMenu = false;

  @override
  void initState() {
    super.initState();
    _initializePlayer();
  }

  void _initializePlayer() {
    /// Initialize video player with HLS URL
    /// 
    /// HLS (HTTP Live Streaming) is an adaptive bitrate streaming protocol.
    /// The video_player plugin automatically:
    /// - Downloads the master playlist (m3u8)
    /// - Parses variant playlists for each quality
    /// - Implements adaptive bitrate selection
    /// - Downloads segments based on available bandwidth
    
    _videoPlayerController = VideoPlayerController.network(
      widget.playlistUrl,
      httpHeaders: {
        'User-Agent': 'VideoStreamingPlatform/1.0',
      },
    );

    _chewieController = ChewieController(
      videoPlayerController: _videoPlayerController,
      autoPlay: true,
      looping: false,
      allowPlaybackSpeedChanging: true,
      allowMuting: true,
      progressIndicatorDelay: const Duration(milliseconds: 500),
      hideControlsTimer: const Duration(seconds: 3),
      showControlsOnInitialize: true,
      customControls: _buildCustomControls(),
    );
  }

  Widget _buildCustomControls() {
    /// Custom video player controls with quality selector
    return Stack(
      children: [
        // Default Chewie controls
        const Chewie(),
        // Quality selector button
        Positioned(
          top: 10,
          right: 10,
          child: GestureDetector(
            onTap: () {
              setState(() {
                _showQualityMenu = !_showQualityMenu;
              });
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(5),
              ),
              child: Text(
                _selectedQuality,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ),
        ),
        // Quality menu dropdown
        if (_showQualityMenu)
          Positioned(
            top: 50,
            right: 10,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(5),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: widget.qualities.map((quality) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        _selectedQuality = quality;
                        _showQualityMenu = false;
                      });
                      widget.onQualityChanged?.call(quality);
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(10),
                      child: Text(
                        quality,
                        style: TextStyle(
                          color: _selectedQuality == quality
                              ? Colors.blue
                              : Colors.white,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
      ],
    );
  }

  @override
  void dispose() {
    _videoPlayerController.dispose();
    _chewieController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Chewie(
      controller: _chewieController,
    );
  }
}
