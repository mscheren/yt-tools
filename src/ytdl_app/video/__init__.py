"""Video editing functionality."""

from .editor import VideoEditor
from .operations import concatenate_videos, get_video_info
from .overlay import TextOverlayConfig

__all__ = [
    "TextOverlayConfig",
    "VideoEditor",
    "concatenate_videos",
    "get_video_info",
]
