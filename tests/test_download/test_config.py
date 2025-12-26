"""Tests for download configuration."""

from pathlib import Path

from ytdl_app.download import DownloadConfig
from ytdl_app.models import OutputFormat, VideoResolution


class TestDownloadConfig:
    """Tests for DownloadConfig dataclass."""

    def test_default_values(self):
        """Default config should have sensible values."""
        config = DownloadConfig()
        assert config.output_format == OutputFormat.MP4
        assert config.resolution == VideoResolution.BEST
        assert config.retries == 3

    def test_output_template_single(self):
        """Single video template should not include playlist."""
        config = DownloadConfig(output_dir=Path("/tmp"))
        template = config.get_output_template(is_playlist=False)
        assert "%(title)s" in template
        assert "%(playlist)s" not in template

    def test_output_template_playlist(self):
        """Playlist template should include playlist folder."""
        config = DownloadConfig(output_dir=Path("/tmp"))
        template = config.get_output_template(is_playlist=True)
        assert "%(playlist)s" in template

    def test_format_string_video(self):
        """Video format string should prefer mp4."""
        config = DownloadConfig(output_format=OutputFormat.MP4)
        fmt = config.get_format_string()
        assert "mp4" in fmt

    def test_format_string_audio(self):
        """Audio format string should select best audio."""
        config = DownloadConfig(output_format=OutputFormat.MP3)
        fmt = config.get_format_string()
        assert "ba" in fmt  # best audio

    def test_format_string_with_resolution(self):
        """Format string should include height limit."""
        config = DownloadConfig(resolution=VideoResolution.R_720P)
        fmt = config.get_format_string()
        assert "720" in fmt

    def test_to_ydl_opts_includes_retries(self):
        """YDL options should include retry settings."""
        config = DownloadConfig(retries=5)
        opts = config.to_ydl_opts()
        assert opts["retries"] == 5

    def test_to_ydl_opts_audio_postprocessor(self):
        """Audio format should include extraction postprocessor."""
        config = DownloadConfig(output_format=OutputFormat.MP3)
        opts = config.to_ydl_opts()
        assert "postprocessors" in opts
        assert opts["postprocessors"][0]["key"] == "FFmpegExtractAudio"
