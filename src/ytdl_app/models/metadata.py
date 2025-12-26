"""Metadata dataclasses for video and audio files."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoMetadata:
    """Metadata about a video file."""

    path: Path
    duration: float
    fps: float
    width: int
    height: int
    has_audio: bool

    @property
    def size(self) -> tuple[int, int]:
        """Return video dimensions as (width, height) tuple."""
        return (self.width, self.height)

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio."""
        return self.width / self.height if self.height > 0 else 0.0

    def format_duration(self) -> str:
        """Format duration as MM:SS or HH:MM:SS."""
        total_seconds = int(self.duration)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


@dataclass(frozen=True)
class AudioMetadata:
    """Metadata about an audio file."""

    path: Path
    duration: float
    sample_rate: int
    channels: int

    def format_duration(self) -> str:
        """Format duration as MM:SS or HH:MM:SS."""
        total_seconds = int(self.duration)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
