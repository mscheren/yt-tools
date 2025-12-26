"""Text overlay configuration for video editing."""

from dataclasses import dataclass


@dataclass
class TextOverlayConfig:
    """Configuration for text overlay on video."""

    text: str
    font_size: int = 50
    color: str = "white"
    position: str | tuple[int, int] = "center"
    start_time: float = 0.0
    duration: float | None = None
