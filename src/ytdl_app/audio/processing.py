"""Audio processing operations (noise removal, extraction)."""

from pathlib import Path

import numpy as np
from pedalboard import HighpassFilter, LowpassFilter, NoiseGate, Pedalboard
from pedalboard.io import AudioFile


def remove_noise_gate(
    audio: np.ndarray,
    sample_rate: int,
    threshold_db: float = -40,
    attack_ms: float = 1,
    release_ms: float = 100,
) -> np.ndarray:
    """
    Remove background noise using a noise gate.

    Args:
        audio: Input audio array.
        sample_rate: Sample rate in Hz.
        threshold_db: Gate threshold in dB.
        attack_ms: Attack time in ms.
        release_ms: Release time in ms.
    """
    board = Pedalboard(
        [
            NoiseGate(
                threshold_db=threshold_db, attack_ms=attack_ms, release_ms=release_ms
            )
        ]
    )
    return board(audio, sample_rate)


def remove_noise_spectral(
    audio: np.ndarray, sample_rate: int, noise_reduce: float = 0.5
) -> np.ndarray:
    """
    Simple spectral noise reduction using frequency filtering.

    Args:
        audio: Input audio array.
        sample_rate: Sample rate in Hz.
        noise_reduce: Reduction strength (0.0 to 1.0).
    """
    # Apply bandpass filter to remove very low and very high frequencies
    board = Pedalboard(
        [
            HighpassFilter(cutoff_frequency_hz=80),
            LowpassFilter(cutoff_frequency_hz=min(15000, sample_rate // 2 - 100)),
        ]
    )
    return board(audio, sample_rate)


def extract_audio_from_video(
    video_path: Path, output_path: Path, format: str = "wav"
) -> Path:
    """
    Extract audio track from a video file.

    Args:
        video_path: Path to video file.
        output_path: Path for output audio file.
        format: Output format (wav, mp3, flac).
    """
    from moviepy import VideoFileClip

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with VideoFileClip(str(video_path)) as video:
        if video.audio is None:
            raise ValueError("Video has no audio track")
        video.audio.write_audiofile(str(output_path), logger=None)

    return output_path


def convert_audio(
    input_path: Path, output_path: Path, target_sample_rate: int | None = None
) -> Path:
    """
    Convert audio file to different format with optional resampling.

    Args:
        input_path: Input audio file.
        output_path: Output audio file (format determined by extension).
        target_sample_rate: Optional target sample rate.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with AudioFile(str(input_path)) as f:
        audio = f.read(f.frames)
        sample_rate = int(f.samplerate)
        channels = f.num_channels

    if target_sample_rate and target_sample_rate != sample_rate:
        from .mixing import resample_to_match

        audio = resample_to_match(audio, sample_rate, target_sample_rate)
        sample_rate = target_sample_rate

    with AudioFile(
        str(output_path), "w", samplerate=sample_rate, num_channels=channels
    ) as f:
        f.write(audio)

    return output_path


def split_audio(
    audio: np.ndarray, sample_rate: int, segment_duration: float
) -> list[np.ndarray]:
    """
    Split audio into segments of specified duration.

    Args:
        audio: Input audio array.
        sample_rate: Sample rate in Hz.
        segment_duration: Duration of each segment in seconds.

    Returns:
        List of audio segments.
    """
    segment_samples = int(segment_duration * sample_rate)
    segments = []

    total_samples = audio.shape[-1]
    for start in range(0, total_samples, segment_samples):
        end = min(start + segment_samples, total_samples)
        if audio.ndim == 2:
            segments.append(audio[:, start:end])
        else:
            segments.append(audio[start:end])

    return segments


def concatenate_audio(segments: list[np.ndarray]) -> np.ndarray:
    """Concatenate multiple audio segments."""
    if not segments:
        raise ValueError("No segments to concatenate")

    axis = 1 if segments[0].ndim == 2 else 0
    return np.concatenate(segments, axis=axis)
