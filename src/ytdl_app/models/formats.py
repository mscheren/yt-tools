"""Output format enums and codec configurations."""

from enum import Enum


class OutputFormat(Enum):
    """Supported output formats for downloads."""

    MP4 = "mp4"
    MP3 = "mp3"


class VideoCodec(Enum):
    """Supported video codecs."""

    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"


class AudioCodec(Enum):
    """Supported audio codecs."""

    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
