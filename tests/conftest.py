"""Shared test fixtures and configuration."""

from unittest.mock import MagicMock

import numpy as np
import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing."""
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Generate a simple sine wave
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    return audio, sample_rate


@pytest.fixture
def stereo_audio_data(sample_audio_data):
    """Generate stereo audio data."""
    mono, sample_rate = sample_audio_data
    stereo = np.stack([mono, mono])
    return stereo, sample_rate


@pytest.fixture
def mock_video_clip():
    """Create a mock VideoFileClip."""
    clip = MagicMock()
    clip.duration = 10.0
    clip.fps = 30.0
    clip.size = (1920, 1080)
    clip.audio = MagicMock()
    clip.subclipped.return_value = clip
    clip.with_volume_scaled.return_value = clip
    clip.loop.return_value = clip
    clip.time_mirror.return_value = clip
    clip.cropped.return_value = clip
    clip.resized.return_value = clip
    clip.rotated.return_value = clip
    clip.image_transform.return_value = clip
    clip.with_speed_scaled.return_value = clip
    return clip


@pytest.fixture
def mock_yt_dlp_info():
    """Sample yt-dlp info dictionary."""
    return {
        "id": "test123",
        "title": "Test Video",
        "description": "A test video",
        "duration": 120,
        "uploader": "Test Channel",
        "upload_date": "20240101",
        "view_count": 1000,
        "thumbnail": "https://example.com/thumb.jpg",
        "chapters": [
            {"title": "Intro", "start_time": 0, "end_time": 30},
            {"title": "Main", "start_time": 30, "end_time": 120},
        ],
        "formats": [
            {"format_id": "22", "ext": "mp4", "resolution": "720p"},
        ],
    }
