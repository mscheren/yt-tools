"""Tests for audio mixing operations."""

import numpy as np

from ytdl_app.audio.mixing import (
    crossfade,
    fade_in,
    fade_out,
    overlay,
    resample_to_match,
)


class TestOverlay:
    """Tests for audio overlay function."""

    def test_overlay_at_start(self, sample_audio_data):
        """Overlay at position 0 should mix at beginning."""
        base, sr = sample_audio_data
        overlay_audio = np.ones(1000, dtype=np.float32) * 0.5

        result = overlay(base, overlay_audio, position=0, volume=1.0)

        assert result.shape == base.shape
        # First samples should be mixed
        assert not np.allclose(result[:1000], base[:1000])

    def test_overlay_with_volume(self, sample_audio_data):
        """Volume parameter should scale overlay."""
        base, sr = sample_audio_data
        overlay_audio = np.ones(1000, dtype=np.float32)

        result_full = overlay(base, overlay_audio, position=0, volume=1.0)
        result_half = overlay(base, overlay_audio, position=0, volume=0.5)

        # Half volume should have less difference from base
        diff_full = np.sum(np.abs(result_full[:1000] - base[:1000]))
        diff_half = np.sum(np.abs(result_half[:1000] - base[:1000]))
        assert diff_half < diff_full


class TestCrossfade:
    """Tests for crossfade function."""

    def test_crossfade_length(self, sample_audio_data):
        """Crossfade should produce correct output length."""
        audio1, sr = sample_audio_data
        audio2 = audio1.copy()
        fade_samples = 1000

        result = crossfade(audio1, audio2, fade_samples)

        expected_length = len(audio1) + len(audio2) - fade_samples
        assert len(result) == expected_length

    def test_crossfade_stereo(self, stereo_audio_data):
        """Crossfade should work with stereo audio."""
        audio1, sr = stereo_audio_data
        audio2 = audio1.copy()

        result = crossfade(audio1, audio2, 1000)
        assert result.ndim == 2
        assert result.shape[0] == 2


class TestFades:
    """Tests for fade in/out functions."""

    def test_fade_in_starts_silent(self, sample_audio_data):
        """Fade in should start at zero."""
        audio, sr = sample_audio_data
        result = fade_in(audio, 1000)

        assert result[0] == 0.0
        assert result[999] != 0.0

    def test_fade_out_ends_silent(self, sample_audio_data):
        """Fade out should end at zero."""
        audio, sr = sample_audio_data
        result = fade_out(audio, 1000)

        assert result[-1] == 0.0


class TestResample:
    """Tests for resampling function."""

    def test_resample_same_rate(self, sample_audio_data):
        """Same rate should return unchanged audio."""
        audio, sr = sample_audio_data
        result = resample_to_match(audio, sr, sr)

        np.testing.assert_array_equal(result, audio)

    def test_resample_upsample(self, sample_audio_data):
        """Upsampling should increase length."""
        audio, sr = sample_audio_data
        result = resample_to_match(audio, sr, sr * 2)

        assert len(result) == len(audio) * 2

    def test_resample_downsample(self, sample_audio_data):
        """Downsampling should decrease length."""
        audio, sr = sample_audio_data
        result = resample_to_match(audio, sr, sr // 2)

        assert len(result) == len(audio) // 2
