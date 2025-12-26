"""Tests for audio effects."""

from ytdl_app.audio import EffectChain, EffectPreset


class TestEffectChain:
    """Tests for EffectChain class."""

    def test_empty_chain(self):
        """Empty chain should produce empty pedalboard."""
        chain = EffectChain()
        board = chain.build()
        assert len(board) == 0

    def test_gain_only(self):
        """Chain with gain should have one effect."""
        chain = EffectChain(gain_db=6.0)
        board = chain.build()
        assert len(board) == 1

    def test_multiple_effects(self):
        """Chain with multiple effects should include all."""
        chain = EffectChain(
            gain_db=3.0,
            highpass_hz=80,
            compressor=True,
            reverb=True,
        )
        board = chain.build()
        assert len(board) == 4

    def test_preset_podcast(self):
        """Podcast preset should have correct settings."""
        chain = EffectChain.from_preset(EffectPreset.PODCAST)
        assert chain.highpass_hz == 80
        assert chain.compressor is True
        assert chain.limiter is True

    def test_preset_radio(self):
        """Radio preset should have bandpass filter."""
        chain = EffectChain.from_preset(EffectPreset.RADIO)
        assert chain.highpass_hz == 300
        assert chain.lowpass_hz == 5000

    def test_preset_reverb_light(self):
        """Reverb light should have small room size."""
        chain = EffectChain.from_preset(EffectPreset.REVERB_LIGHT)
        assert chain.reverb is True
        assert chain.reverb_room_size == 0.3

    def test_preset_reverb_heavy(self):
        """Reverb heavy should have large room size."""
        chain = EffectChain.from_preset(EffectPreset.REVERB_HEAVY)
        assert chain.reverb_room_size == 0.9


class TestEffectPreset:
    """Tests for EffectPreset enum."""

    def test_all_presets_exist(self):
        """All expected presets should exist."""
        presets = [p.value for p in EffectPreset]
        assert "podcast" in presets
        assert "radio" in presets
        assert "reverb_light" in presets
        assert "warm" in presets
