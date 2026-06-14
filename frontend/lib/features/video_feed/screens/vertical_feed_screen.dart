/// Vertical Video Feed Screen (TikTok/Reels style)
/// 
/// Implements:
/// - Vertical scrollable video feed (PageView)
/// - Full-screen video playback
/// - Video metadata overlay (title, author, like/comment buttons)
/// - Auto-play on scroll
/// - Video caching for smooth scrolling

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:video_streaming_platform/features/video_player/providers/video_provider.dart';

class VerticalFeedScreen extends StatefulWidget {
  const VerticalFeedScreen({Key? key}) : super(key: key);

  @override
  State<VerticalFeedScreen> createState() => _VerticalFeedScreenState();
}

class _VerticalFeedScreenState extends State<VerticalFeedScreen> {
  late PageController _pageController;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
    
    // Load initial videos
    Future.microtask(() {
      context.read<VideoProvider>().fetchVideos();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<VideoProvider>(
        builder: (context, videoProvider, _) {
          if (videoProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (videoProvider.videos.isEmpty) {
            return const Center(child: Text('No videos available'));
          }

          return PageView.builder(
            scrollDirection: Axis.vertical,
            controller: _pageController,
            onPageChanged: (index) {
              setState(() {
                _currentIndex = index;
              });
              
              // Load next video when approaching end of list
              if (index == videoProvider.videos.length - 2) {
                videoProvider.fetchVideos(
                  skip: videoProvider.videos.length,
                );
              }
            },
            itemCount: videoProvider.videos.length,
            itemBuilder: (context, index) {
              final video = videoProvider.videos[index];
              return VerticalVideoCard(
                video: video,
                isVisible: index == _currentIndex,
              );
            },
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }
}

class VerticalVideoCard extends StatefulWidget {
  final Map<String, dynamic> video;
  final bool isVisible;

  const VerticalVideoCard({
    Key? key,
    required this.video,
    required this.isVisible,
  }) : super(key: key);

  @override
  State<VerticalVideoCard> createState() => _VerticalVideoCardState();
}

class _VerticalVideoCardState extends State<VerticalVideoCard> {
  late VideoPlayerController _controller;
  bool _isMuted = false;
  bool _isLiked = false;
  int _likeCount = 0;

  @override
  void initState() {
    super.initState();
    _initializePlayer();
    _likeCount = widget.video['likes'] ?? 0;
  }

  void _initializePlayer() {
    /// Initialize video player with HLS playlist
    /// This demonstrates the integration between Flutter frontend
    /// and the FastAPI backend's HLS streaming endpoint
    
    final playlistUrl = widget.video['hls_playlist_url'] ??
        '/api/v1/stream/videos/${widget.video['id']}/playlist.m3u8';

    _controller = VideoPlayerController.network(playlistUrl)
      ..initialize().then((_) {
        setState(() {});
        if (widget.isVisible) {
          _controller.play();
        }
      });
  }

  @override
  void didUpdateWidget(VerticalVideoCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.isVisible && !oldWidget.isVisible) {
      _controller.play();
    } else if (!widget.isVisible && oldWidget.isVisible) {
      _controller.pause();
    }
  }

  void _toggleLike() {
    setState(() {
      _isLiked = !_isLiked;
      _likeCount += _isLiked ? 1 : -1;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Video player
        _controller.value.isInitialized
            ? VideoPlayer(_controller)
            : const Center(child: CircularProgressIndicator()),

        // Gradient overlay for text visibility
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.transparent,
                Colors.black.withOpacity(0.3),
              ],
            ),
          ),
        ),

        // Video metadata and controls
        Positioned(
          bottom: 20,
          left: 20,
          right: 80,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.video['title'] ?? 'Untitled',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Text(
                widget.video['description'] ?? '',
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),

        // Right-side action buttons
        Positioned(
          right: 15,
          bottom: 100,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              // Like button
              GestureDetector(
                onTap: _toggleLike,
                child: Column(
                  children: [
                    Icon(
                      _isLiked ? Icons.favorite : Icons.favorite_outline,
                      color: _isLiked ? Colors.red : Colors.white,
                      size: 30,
                    ),
                    const SizedBox(height: 5),
                    Text(
                      _likeCount.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              // Comment button
              Column(
                children: [
                  const Icon(Icons.chat_bubble_outline,
                      color: Colors.white, size: 30),
                  const SizedBox(height: 5),
                  Text(
                    widget.video['comments']?.toString() ?? '0',
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              // Mute button
              GestureDetector(
                onTap: () {
                  setState(() {
                    _isMuted = !_isMuted;
                    _controller.setVolume(_isMuted ? 0 : 1);
                  });
                },
                child: Icon(
                  _isMuted ? Icons.volume_off : Icons.volume_up,
                  color: Colors.white,
                  size: 30,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
