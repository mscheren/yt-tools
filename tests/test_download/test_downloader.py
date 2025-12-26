"""Tests for downloader with mocked yt-dlp."""

from unittest.mock import MagicMock, patch

import pytest

from ytdl_app.download import DownloadConfig, Downloader, DownloadError


class TestDownloader:
    """Tests for Downloader class with mocked yt-dlp."""

    @patch("ytdl_app.download.downloader.yt_dlp.YoutubeDL")
    def test_download_single_video(self, mock_ydl_class, mock_yt_dlp_info):
        """Download should call yt-dlp with correct options."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = mock_yt_dlp_info
        mock_ydl_class.return_value = mock_ydl

        downloader = Downloader()
        result = downloader.download("https://youtube.com/watch?v=test")

        assert result["title"] == "Test Video"
        mock_ydl.extract_info.assert_called_once()

    @patch("ytdl_app.download.downloader.yt_dlp.YoutubeDL")
    def test_download_playlist(self, mock_ydl_class, mock_yt_dlp_info):
        """Playlist download should work correctly."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_yt_dlp_info["entries"] = [{"title": "Video 1"}, {"title": "Video 2"}]
        mock_ydl.extract_info.return_value = mock_yt_dlp_info
        mock_ydl_class.return_value = mock_ydl

        downloader = Downloader()
        result = downloader.download_playlist("https://youtube.com/playlist?list=test")

        assert "entries" in result
        assert len(result["entries"]) == 2

    @patch("ytdl_app.download.downloader.yt_dlp.YoutubeDL")
    def test_get_info_no_download(self, mock_ydl_class, mock_yt_dlp_info):
        """Get info should not trigger download."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = mock_yt_dlp_info
        mock_ydl_class.return_value = mock_ydl

        downloader = Downloader()
        result = downloader.get_info("https://youtube.com/watch?v=test")

        mock_ydl.extract_info.assert_called_with(
            "https://youtube.com/watch?v=test", download=False
        )

    @patch("ytdl_app.download.downloader.yt_dlp.YoutubeDL")
    @patch("ytdl_app.download.downloader.time.sleep")
    def test_retry_on_failure(self, mock_sleep, mock_ydl_class):
        """Download should retry on failure."""
        import yt_dlp

        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.side_effect = yt_dlp.DownloadError("Network error")
        mock_ydl_class.return_value = mock_ydl

        config = DownloadConfig(retries=2, retry_sleep=0.1)
        downloader = Downloader(config=config)

        with pytest.raises(DownloadError):
            downloader.download("https://youtube.com/watch?v=test")

        # Should have tried 3 times (initial + 2 retries)
        assert mock_ydl.extract_info.call_count == 3

    def test_progress_callback(self):
        """Progress callback should be set in options."""
        callback = MagicMock()
        config = DownloadConfig()
        downloader = Downloader(config=config, progress_callback=callback)

        opts = downloader._build_opts()
        assert "progress_hooks" in opts
        assert callback in opts["progress_hooks"]
