"""Audio editor class for processing audio files."""

from pathlib import Path

import numpy as np
from pedalboard.io import AudioFile

from ytdl_app.models import AudioMetadata

from .effects import EffectChain


class AudioEditor:
    """Audio editing operations using pedalboard."""

    def __init__(self, input_path: Path):
        self.input_path = Path(input_path)
        self._audio: np.ndarray | None = None
        self._sample_rate: int | None = None

    def __enter__(self) -> "AudioEditor":
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._audio = None
        self._sample_rate = None

    def load(self) -> "AudioEditor":
        """Load the audio file into memory."""
        with AudioFile(str(self.input_path)) as f:
            self._audio = f.read(f.frames)
            self._sample_rate = int(f.samplerate)
        return self

    @property
    def audio(self) -> np.ndarray:
        """Get the audio data."""
        if self._audio is None:
            raise RuntimeError("Audio not loaded. Use context manager or load().")
        return self._audio

    @property
    def sample_rate(self) -> int:
        """Get the sample rate."""
        if self._sample_rate is None:
            raise RuntimeError("Audio not loaded. Use context manager or load().")
        return self._sample_rate

    def get_metadata(self) -> AudioMetadata:
        """Get metadata about the loaded audio."""
        channels = 1 if self.audio.ndim == 1 else self.audio.shape[0]
        frames = self.audio.shape[-1]
        duration = frames / self.sample_rate

        return AudioMetadata(
            path=self.input_path,
            duration=duration,
            sample_rate=self.sample_rate,
            channels=channels,
        )

    def apply_effects(self, chain: EffectChain) -> "AudioEditor":
        """Apply an effect chain to the audio."""
        board = chain.build()
        self._audio = board(self.audio, self.sample_rate)
        return self

    def trim(self, start: float, end: float) -> "AudioEditor":
        """Trim the audio to a specific time range in seconds."""
        start_sample = int(start * self.sample_rate)
        end_sample = int(end * self.sample_rate)

        if self.audio.ndim == 1:
            self._audio = self.audio[start_sample:end_sample]
        else:
            self._audio = self.audio[:, start_sample:end_sample]

        return self

    def normalize(self, target_db: float = -1.0) -> "AudioEditor":
        """Normalize audio to a target peak level in dB."""
        peak = np.max(np.abs(self.audio))
        if peak > 0:
            target_linear = 10 ** (target_db / 20)
            self._audio = self.audio * (target_linear / peak)
        return self

    def export(self, output_path: Path, format: str = "wav") -> Path:
        """Export the processed audio to a file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        channels = 1 if self.audio.ndim == 1 else self.audio.shape[0]

        with AudioFile(
            str(output_path), "w", samplerate=self.sample_rate, num_channels=channels
        ) as f:
            f.write(self.audio)

        return output_path


def get_audio_info(audio_path: Path) -> AudioMetadata:
    """Get metadata about an audio file."""
    with AudioFile(str(audio_path)) as f:
        duration = f.frames / f.samplerate
        return AudioMetadata(
            path=audio_path,
            duration=duration,
            sample_rate=int(f.samplerate),
            channels=f.num_channels,
        )
