"""Tests for video editor with mocked moviepy."""

from pathlib import Path
from unittest.mock import patch

from ytdl_app.video import VideoEditor


class TestVideoEditor:
    """Tests for VideoEditor class with mocked moviepy."""

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_context_manager(self, mock_clip_class, mock_video_clip):
        """Editor should work as context manager."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            assert editor.clip is not None

        mock_video_clip.close.assert_called_once()

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_get_metadata(self, mock_clip_class, mock_video_clip):
        """Get metadata should return correct values."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            meta = editor.get_metadata()

        assert meta.duration == 10.0
        assert meta.fps == 30.0
        assert meta.width == 1920
        assert meta.height == 1080

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_trim(self, mock_clip_class, mock_video_clip):
        """Trim should call subclipped on clip."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            editor.trim(5.0, 10.0)

        mock_video_clip.subclipped.assert_called_with(5.0, 10.0)

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_adjust_volume(self, mock_clip_class, mock_video_clip):
        """Adjust volume should scale audio."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            editor.adjust_volume(0.5)

        mock_video_clip.with_volume_scaled.assert_called_with(0.5)

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_speed(self, mock_clip_class, mock_video_clip):
        """Speed should call with_speed_scaled."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            editor.speed(2.0)

        mock_video_clip.with_speed_scaled.assert_called_with(2.0)

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_reverse(self, mock_clip_class, mock_video_clip):
        """Reverse should call time_mirror."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            editor.reverse()

        mock_video_clip.time_mirror.assert_called_once()

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_loop(self, mock_clip_class, mock_video_clip):
        """Loop should call loop with n parameter."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            editor.loop(3)

        mock_video_clip.loop.assert_called_with(n=3)

    @patch("ytdl_app.video.editor.VideoFileClip")
    def test_method_chaining(self, mock_clip_class, mock_video_clip):
        """Methods should support chaining."""
        mock_clip_class.return_value = mock_video_clip

        with VideoEditor(Path("test.mp4")) as editor:
            result = editor.trim(0, 5).speed(2.0).reverse()

        assert result is editor
