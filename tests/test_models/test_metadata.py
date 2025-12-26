"""Tests for metadata dataclasses."""

from pathlib import Path

import pytest

from ytdl_app.models import AudioMetadata, VideoMetadata


class TestVideoMetadata:
    """Tests for VideoMetadata dataclass."""

    def test_size_property(self):
        """Size should return (width, height) tuple."""
        meta = VideoMetadata(
            path=Path("test.mp4"),
            duration=60.0,
            fps=30.0,
            width=1920,
            height=1080,
            has_audio=True,
        )
        assert meta.size == (1920, 1080)

    def test_aspect_ratio(self):
        """Aspect ratio should be calculated correctly."""
        meta = VideoMetadata(
            path=Path("test.mp4"),
            duration=60.0,
            fps=30.0,
            width=1920,
            height=1080,
            has_audio=True,
        )
        assert abs(meta.aspect_ratio - 16 / 9) < 0.01

    def test_format_duration_short(self):
        """Short durations should format as MM:SS."""
        meta = VideoMetadata(
            path=Path("test.mp4"),
            duration=125.0,
            fps=30.0,
            width=1920,
            height=1080,
            has_audio=True,
        )
        assert meta.format_duration() == "2:05"

    def test_format_duration_long(self):
        """Long durations should format as HH:MM:SS."""
        meta = VideoMetadata(
            path=Path("test.mp4"),
            duration=3725.0,
            fps=30.0,
            width=1920,
            height=1080,
            has_audio=True,
        )
        assert meta.format_duration() == "1:02:05"


class TestAudioMetadata:
    """Tests for AudioMetadata dataclass."""

    def test_format_duration(self):
        """Duration should format correctly."""
        meta = AudioMetadata(
            path=Path("test.mp3"),
            duration=185.0,
            sample_rate=44100,
            channels=2,
        )
        assert meta.format_duration() == "3:05"

    def test_frozen(self):
        """AudioMetadata should be immutable."""
        meta = AudioMetadata(
            path=Path("test.mp3"),
            duration=60.0,
            sample_rate=44100,
            channels=2,
        )
        with pytest.raises(Exception):
            meta.duration = 120.0
