"""Output format enums and codec configurations."""

from enum import Enum


class OutputFormat(Enum):
    """Supported output formats for downloads."""

    MP4 = "mp4"
    MP3 = "mp3"
    MKV = "mkv"
    WEBM = "webm"
    AVI = "avi"
    MOV = "mov"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"

    @property
    def is_audio_only(self) -> bool:
        """Check if format is audio-only."""
        return self in (self.MP3, self.WAV, self.FLAC, self.AAC, self.OGG)

    @property
    def is_video(self) -> bool:
        """Check if format is a video container."""
        return self in (self.MP4, self.MKV, self.WEBM, self.AVI, self.MOV)


class VideoCodec(Enum):
    """Supported video codecs."""

    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"


class AudioCodec(Enum):
    """Supported audio codecs."""

    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
    FLAC = "flac"
    VORBIS = "libvorbis"
    PCM = "pcm_s16le"


class VideoResolution(Enum):
    """Common video resolutions."""

    R_360P = "360"
    R_480P = "480"
    R_720P = "720"
    R_1080P = "1080"
    R_1440P = "1440"
    R_2160P = "2160"
    BEST = "best"

    @property
    def height(self) -> int | None:
        """Get the height in pixels."""
        if self == self.BEST:
            return None
        return int(self.value)


class DownloadStatus(Enum):
    """Status of a download item."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
