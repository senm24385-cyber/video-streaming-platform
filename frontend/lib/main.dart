/// Video Streaming Platform - Flutter App
/// 
/// Main entry point for the video streaming application.
/// This app implements:
/// - Vertical scrollable video feed (TikTok/Reels style)
/// - Horizontal scrollable video feed (YouTube style)
/// - Video player with adaptive bitrate (HLS)
/// - Video upload with progress tracking
/// - User authentication and profiles

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:video_streaming_platform/core/config/app_config.dart';
import 'package:video_streaming_platform/core/routes/app_router.dart';
import 'package:video_streaming_platform/core/services/api_service.dart';
import 'package:video_streaming_platform/features/video_player/providers/video_provider.dart';

void main() {
  // Initialize app configuration
  AppConfig.init();
  
  runApp(const VideoStreamingApp());
}

class VideoStreamingApp extends StatelessWidget {
  const VideoStreamingApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // API Service (singleton)
        Provider<ApiService>(
          create: (_) => ApiService(),
        ),
        // Video Provider for state management
        ChangeNotifierProvider(
          create: (context) => VideoProvider(
            apiService: context.read<ApiService>(),
          ),
        ),
      ],
      child: MaterialApp(
        title: 'Video Streaming Platform',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
          brightness: Brightness.dark,
        ),
        home: const HomeScreen(),
        routes: AppRouter.routes,
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const VerticalFeedScreen(),
    const HorizontalFeedScreen(),
    const UploadScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.vertical_split),
            label: 'Shorts',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.horizontal_split),
            label: 'Feed',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.cloud_upload),
            label: 'Upload',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

// Placeholder screens - implemented in respective feature modules
class VerticalFeedScreen extends StatelessWidget {
  const VerticalFeedScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Vertical Feed - See lib/features/video_feed/')),
    );
  }
}

class HorizontalFeedScreen extends StatelessWidget {
  const HorizontalFeedScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Horizontal Feed - See lib/features/video_feed/')),
    );
  }
}

class UploadScreen extends StatelessWidget {
  const UploadScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Upload - See lib/features/upload/')),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Profile - See lib/features/profile/')),
    );
  }
}
