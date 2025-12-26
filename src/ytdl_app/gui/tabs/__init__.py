"""GUI tab implementations."""

from .audio_tab import render_audio_tab
from .download_tab import render_download_tab
from .project_tab import render_project_tab
from .video_tab import render_video_tab

__all__ = [
    "render_audio_tab",
    "render_download_tab",
    "render_project_tab",
    "render_video_tab",
]
