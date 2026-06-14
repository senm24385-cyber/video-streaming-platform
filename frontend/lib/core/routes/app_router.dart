/// Application routing configuration

import 'package:flutter/material.dart';

class AppRouter {
  static const String home = '/';
  static const String videoPlayer = '/video-player';
  static const String upload = '/upload';
  static const String profile = '/profile';

  static Map<String, WidgetBuilder> get routes {
    return {
      home: (context) => const Scaffold(),
      videoPlayer: (context) => const Scaffold(),
      upload: (context) => const Scaffold(),
      profile: (context) => const Scaffold(),
    };
  }
}
