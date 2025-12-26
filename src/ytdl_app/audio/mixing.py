"""Audio mixing operations (overlay, ducking, crossfade)."""

from pathlib import Path

import numpy as np
from pedalboard.io import AudioFile


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    """Load audio file and return (audio_data, sample_rate)."""
    with AudioFile(str(path)) as f:
        return f.read(f.frames), int(f.samplerate)


def resample_to_match(audio: np.ndarray, src_rate: int, target_rate: int) -> np.ndarray:
    """Resample audio to match target sample rate."""
    if src_rate == target_rate:
        return audio
    ratio = target_rate / src_rate
    new_length = int(audio.shape[-1] * ratio)
    indices = np.linspace(0, audio.shape[-1] - 1, new_length)
    if audio.ndim == 1:
        return np.interp(indices, np.arange(audio.shape[0]), audio)
    return np.array([np.interp(indices, np.arange(audio.shape[1]), ch) for ch in audio])


def overlay(
    base: np.ndarray, overlay_audio: np.ndarray, position: int = 0, volume: float = 1.0
) -> np.ndarray:
    """
    Overlay audio on top of base audio at a specific position.

    Args:
        base: Base audio array.
        overlay_audio: Audio to overlay.
        position: Sample position to start overlay.
        volume: Volume multiplier for overlay (0.0 to 1.0).
    """
    result = base.copy().astype(np.float64)
    overlay_scaled = overlay_audio * volume

    # Handle mono/stereo conversion
    if base.ndim == 2 and overlay_audio.ndim == 1:
        overlay_scaled = np.stack([overlay_scaled] * base.shape[0])
    elif base.ndim == 1 and overlay_audio.ndim == 2:
        overlay_scaled = np.mean(overlay_scaled, axis=0)

    end_pos = min(position + overlay_scaled.shape[-1], result.shape[-1])
    overlay_len = end_pos - position

    if result.ndim == 1:
        result[position:end_pos] += overlay_scaled[:overlay_len]
    else:
        result[:, position:end_pos] += overlay_scaled[:, :overlay_len]

    return np.clip(result, -1.0, 1.0)


def duck(
    main: np.ndarray,
    sidechain: np.ndarray,
    threshold: float = 0.1,
    ratio: float = 0.3,
    attack_ms: float = 10,
    release_ms: float = 100,
    sample_rate: int = 44100,
) -> np.ndarray:
    """
    Apply ducking effect (reduce main volume when sidechain is loud).

    Args:
        main: Main audio to duck.
        sidechain: Audio that triggers ducking.
        threshold: Level above which ducking activates.
        ratio: How much to reduce volume (0.0 = full duck, 1.0 = no duck).
        attack_ms: Attack time in milliseconds.
        release_ms: Release time in milliseconds.
    """
    attack_samples = int(attack_ms * sample_rate / 1000)
    release_samples = int(release_ms * sample_rate / 1000)

    # Get envelope from sidechain
    if sidechain.ndim == 2:
        envelope = np.max(np.abs(sidechain), axis=0)
    else:
        envelope = np.abs(sidechain)

    # Pad if needed
    if len(envelope) < main.shape[-1]:
        envelope = np.pad(envelope, (0, main.shape[-1] - len(envelope)))
    envelope = envelope[: main.shape[-1]]

    # Create gain reduction curve
    gain = np.ones_like(envelope)
    gain[envelope > threshold] = ratio

    # Smooth with attack/release
    smoothed = np.zeros_like(gain)
    smoothed[0] = gain[0]
    for i in range(1, len(gain)):
        if gain[i] < smoothed[i - 1]:
            coef = 1 - np.exp(-1 / attack_samples)
        else:
            coef = 1 - np.exp(-1 / release_samples)
        smoothed[i] = smoothed[i - 1] + coef * (gain[i] - smoothed[i - 1])

    if main.ndim == 2:
        return main * smoothed
    return main * smoothed


def crossfade(audio1: np.ndarray, audio2: np.ndarray, fade_samples: int) -> np.ndarray:
    """
    Crossfade between two audio clips.

    Args:
        audio1: First audio clip.
        audio2: Second audio clip.
        fade_samples: Number of samples for the crossfade.
    """
    # Create fade curves
    fade_out = np.linspace(1, 0, fade_samples)
    fade_in = np.linspace(0, 1, fade_samples)

    # Get overlap region from end of audio1 and start of audio2
    if audio1.ndim == 2:
        overlap1 = audio1[:, -fade_samples:] * fade_out
        overlap2 = audio2[:, :fade_samples] * fade_in
        crossfaded = overlap1 + overlap2
        return np.concatenate(
            [audio1[:, :-fade_samples], crossfaded, audio2[:, fade_samples:]], axis=1
        )
    else:
        overlap1 = audio1[-fade_samples:] * fade_out
        overlap2 = audio2[:fade_samples] * fade_in
        crossfaded = overlap1 + overlap2
        return np.concatenate(
            [audio1[:-fade_samples], crossfaded, audio2[fade_samples:]]
        )


def fade_in(audio: np.ndarray, duration_samples: int) -> np.ndarray:
    """Apply fade in effect."""
    fade = np.linspace(0, 1, duration_samples)
    result = audio.copy()
    if audio.ndim == 2:
        result[:, :duration_samples] *= fade
    else:
        result[:duration_samples] *= fade
    return result


def fade_out(audio: np.ndarray, duration_samples: int) -> np.ndarray:
    """Apply fade out effect."""
    fade = np.linspace(1, 0, duration_samples)
    result = audio.copy()
    if audio.ndim == 2:
        result[:, -duration_samples:] *= fade
    else:
        result[-duration_samples:] *= fade
    return result
