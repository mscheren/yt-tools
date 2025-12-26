"""Audio effect configurations and presets."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pedalboard import (
    Chorus,
    Compressor,
    Delay,
    Distortion,
    Gain,
    HighpassFilter,
    Limiter,
    LowpassFilter,
    Pedalboard,
    Reverb,
)


class EffectPreset(Enum):
    """Predefined effect chain presets."""

    RADIO = "radio"
    PODCAST = "podcast"
    REVERB_LIGHT = "reverb_light"
    REVERB_HEAVY = "reverb_heavy"
    WARM = "warm"


@dataclass
class EffectChain:
    """Configuration for a chain of audio effects."""

    gain_db: float | None = None
    highpass_hz: float | None = None
    lowpass_hz: float | None = None
    compressor: bool = False
    compressor_threshold_db: float = -20.0
    compressor_ratio: float = 4.0
    reverb: bool = False
    reverb_room_size: float = 0.5
    reverb_wet_level: float = 0.3
    delay: bool = False
    delay_seconds: float = 0.3
    delay_feedback: float = 0.3
    chorus: bool = False
    distortion: bool = False
    distortion_drive_db: float = 10.0
    limiter: bool = False
    limiter_threshold_db: float = -1.0

    def build(self) -> Pedalboard:
        """Build a Pedalboard from this configuration."""
        effects: list[Any] = []

        if self.gain_db is not None:
            effects.append(Gain(gain_db=self.gain_db))

        if self.highpass_hz is not None:
            effects.append(HighpassFilter(cutoff_frequency_hz=self.highpass_hz))

        if self.lowpass_hz is not None:
            effects.append(LowpassFilter(cutoff_frequency_hz=self.lowpass_hz))

        if self.compressor:
            effects.append(
                Compressor(
                    threshold_db=self.compressor_threshold_db,
                    ratio=self.compressor_ratio,
                )
            )

        if self.distortion:
            effects.append(Distortion(drive_db=self.distortion_drive_db))

        if self.chorus:
            effects.append(Chorus())

        if self.delay:
            effects.append(
                Delay(delay_seconds=self.delay_seconds, feedback=self.delay_feedback)
            )

        if self.reverb:
            effects.append(
                Reverb(room_size=self.reverb_room_size, wet_level=self.reverb_wet_level)
            )

        if self.limiter:
            effects.append(Limiter(threshold_db=self.limiter_threshold_db))

        return Pedalboard(effects)

    @classmethod
    def from_preset(cls, preset: EffectPreset) -> "EffectChain":
        """Create an effect chain from a preset."""
        presets = {
            EffectPreset.RADIO: cls(
                highpass_hz=300, lowpass_hz=5000, compressor=True, limiter=True
            ),
            EffectPreset.PODCAST: cls(
                highpass_hz=80, compressor=True, compressor_threshold_db=-18, limiter=True
            ),
            EffectPreset.REVERB_LIGHT: cls(
                reverb=True, reverb_room_size=0.3, reverb_wet_level=0.15
            ),
            EffectPreset.REVERB_HEAVY: cls(
                reverb=True, reverb_room_size=0.9, reverb_wet_level=0.6
            ),
            EffectPreset.WARM: cls(
                lowpass_hz=8000, gain_db=2, compressor=True
            ),
        }
        return presets[preset]
