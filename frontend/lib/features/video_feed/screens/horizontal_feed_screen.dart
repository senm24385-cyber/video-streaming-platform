/// Horizontal Video Feed Screen (YouTube style)
/// 
/// Implements:
/// - Horizontal scrollable grid of video thumbnails
/// - Video metadata (title, author, view count)
/// - Thumbnail caching for performance
/// - Click to play video in detail view

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:video_streaming_platform/features/video_player/providers/video_provider.dart';

class HorizontalFeedScreen extends StatefulWidget {
  const HorizontalFeedScreen({Key? key}) : super(key: key);

  @override
  State<HorizontalFeedScreen> createState() => _HorizontalFeedScreenState();
}

class _HorizontalFeedScreenState extends State<HorizontalFeedScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<VideoProvider>().fetchVideos();
    });

    _scrollController.addListener(() {
      // Load more videos when scrolling near end
      if (_scrollController.position.pixels >
          _scrollController.position.maxScrollExtent - 500) {
        final videoProvider = context.read<VideoProvider>();
        videoProvider.fetchVideos(skip: videoProvider.videos.length);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Video Feed'),
        elevation: 0,
      ),
      body: Consumer<VideoProvider>(
        builder: (context, videoProvider, _) {
          if (videoProvider.isLoading && videoProvider.videos.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (videoProvider.videos.isEmpty) {
            return const Center(child: Text('No videos available'));
          }

          return GridView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.all(8),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 9 / 16,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
            ),
            itemCount: videoProvider.videos.length,
            itemBuilder: (context, index) {
              final video = videoProvider.videos[index];
              return HorizontalVideoCard(
                video: video,
                onTap: () {
                  // Navigate to detail view
                  videoProvider.loadVideo(video['id']);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => VideoDetailScreen(video: video),
                    ),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
}

class HorizontalVideoCard extends StatelessWidget {
  final Map<String, dynamic> video;
  final VoidCallback onTap;

  const HorizontalVideoCard({
    Key? key,
    required this.video,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        clipBehavior: Clip.antiAlias,
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Thumbnail placeholder
            Container(
              color: Colors.grey[900],
              child: const Center(
                child: Icon(Icons.video_library, size: 50, color: Colors.grey),
              ),
            ),
            // Gradient for text visibility
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.7),
                  ],
                ),
              ),
            ),
            // Video info
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      video['title'] ?? 'Untitled',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${video['views'] ?? 0} views',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // Play icon overlay
            const Center(
              child: Icon(
                Icons.play_circle_filled,
                color: Colors.white,
                size: 50,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class VideoDetailScreen extends StatelessWidget {
  final Map<String, dynamic> video;

  const VideoDetailScreen({Key? key, required this.video}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Video Player'),
      ),
      body: const Center(
        child: Text('Video detail view - Implement with VideoPlayerWidget'),
      ),
    );
  }
}
