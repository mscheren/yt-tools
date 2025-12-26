"""Tests for format enums."""

from ytdl_app.models import DownloadStatus, OutputFormat, VideoResolution


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_audio_only_formats(self):
        """Audio-only formats should be identified correctly."""
        assert OutputFormat.MP3.is_audio_only
        assert OutputFormat.WAV.is_audio_only
        assert OutputFormat.FLAC.is_audio_only
        assert not OutputFormat.MP4.is_audio_only
        assert not OutputFormat.MKV.is_audio_only

    def test_video_formats(self):
        """Video formats should be identified correctly."""
        assert OutputFormat.MP4.is_video
        assert OutputFormat.MKV.is_video
        assert OutputFormat.WEBM.is_video
        assert not OutputFormat.MP3.is_video
        assert not OutputFormat.WAV.is_video


class TestVideoResolution:
    """Tests for VideoResolution enum."""

    def test_height_values(self):
        """Resolution heights should be correct."""
        assert VideoResolution.R_720P.height == 720
        assert VideoResolution.R_1080P.height == 1080
        assert VideoResolution.R_2160P.height == 2160

    def test_best_has_no_height(self):
        """BEST resolution should return None for height."""
        assert VideoResolution.BEST.height is None


class TestDownloadStatus:
    """Tests for DownloadStatus enum."""

    def test_all_statuses_exist(self):
        """All expected statuses should exist."""
        assert DownloadStatus.PENDING.value == "pending"
        assert DownloadStatus.DOWNLOADING.value == "downloading"
        assert DownloadStatus.COMPLETED.value == "completed"
        assert DownloadStatus.FAILED.value == "failed"
        assert DownloadStatus.PAUSED.value == "paused"
        assert DownloadStatus.CANCELLED.value == "cancelled"
