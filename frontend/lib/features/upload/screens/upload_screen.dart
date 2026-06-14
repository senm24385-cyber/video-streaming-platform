/// Video Upload Screen
/// 
/// Implements:
/// - File picker for video selection
/// - Chunked upload with progress tracking
/// - Pause/Resume functionality
/// - Upload status monitoring

import 'package:flutter/material.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({Key? key}) : super(key: key);

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String? _selectedFilePath;
  double _uploadProgress = 0.0;
  bool _isUploading = false;
  String _uploadStatus = 'Ready to upload';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upload Video'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // File selection area
            GestureDetector(
              onTap: _selectFile,
              child: Container(
                padding: const EdgeInsets.all(40),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.blue, width: 2),
                  borderRadius: BorderRadius.circular(12),
                  color: Colors.blue.withOpacity(0.05),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.cloud_upload, size: 60, color: Colors.blue),
                    const SizedBox(height: 16),
                    Text(
                      _selectedFilePath ?? 'Tap to select video',
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            // Video metadata form
            TextField(
              decoration: const InputDecoration(
                labelText: 'Video Title',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              decoration: const InputDecoration(
                labelText: 'Video Description',
                border: OutlineInputBorder(),
              ),
              maxLines: 4,
            ),
            const SizedBox(height: 24),
            // Upload progress
            if (_isUploading) ...
              [
                LinearProgressIndicator(
                  value: _uploadProgress,
                  minHeight: 8,
                ),
                const SizedBox(height: 12),
                Text(
                  '${(_uploadProgress * 100).toStringAsFixed(1)}%',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                Text(
                  _uploadStatus,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            const SizedBox(height: 24),
            // Upload button
            ElevatedButton(
              onPressed: _isUploading ? null : _uploadVideo,
              child: Text(_isUploading ? 'Uploading...' : 'Upload Video'),
            ),
          ],
        ),
      ),
    );
  }

  void _selectFile() {
    // TODO: Implement file picker
    setState(() {
      _selectedFilePath = 'video.mp4';
    });
  }

  void _uploadVideo() {
    // TODO: Implement chunked upload
    // This should:
    // 1. Split video into chunks (10MB each)
    // 2. Calculate MD5 hash of each chunk
    // 3. Call apiService.uploadChunk() for each chunk
    // 4. Update progress bar
    // 5. Handle upload completion and transcoding status

    setState(() {
      _isUploading = true;
      _uploadStatus = 'Starting upload...';
    });
  }
}
