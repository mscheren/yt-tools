"""Metadata extraction for videos (thumbnails, chapters, info)."""

from dataclasses import dataclass
from pathlib import Path

import yt_dlp


@dataclass
class Chapter:
    """A chapter/timestamp in a video."""

    title: str
    start_time: float
    end_time: float

    def format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS or MM:SS."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @property
    def duration(self) -> float:
        """Get chapter duration in seconds."""
        return self.end_time - self.start_time


@dataclass
class VideoInfo:
    """Extracted video metadata."""

    id: str
    title: str
    description: str
    duration: float
    uploader: str
    upload_date: str | None
    view_count: int | None
    thumbnail_url: str | None
    chapters: list[Chapter]
    formats: list[dict]

    @classmethod
    def from_yt_dlp(cls, info: dict) -> "VideoInfo":
        """Create from yt-dlp info dict."""
        chapters = []
        for ch in info.get("chapters") or []:
            chapters.append(
                Chapter(
                    title=ch.get("title", ""),
                    start_time=ch.get("start_time", 0),
                    end_time=ch.get("end_time", 0),
                )
            )

        return cls(
            id=info.get("id", ""),
            title=info.get("title", ""),
            description=info.get("description", ""),
            duration=info.get("duration", 0),
            uploader=info.get("uploader", ""),
            upload_date=info.get("upload_date"),
            view_count=info.get("view_count"),
            thumbnail_url=info.get("thumbnail"),
            chapters=chapters,
            formats=info.get("formats", []),
        )


def extract_metadata(url: str, cookies_file: Path | None = None) -> VideoInfo:
    """Extract full metadata from a video URL."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    if cookies_file and cookies_file.exists():
        opts["cookiefile"] = str(cookies_file)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return VideoInfo.from_yt_dlp(info)


def download_thumbnail(
    url: str, output_path: Path, cookies_file: Path | None = None
) -> Path | None:
    """Download the thumbnail for a video."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writethumbnail": True,
        "outtmpl": str(output_path.with_suffix("")),
    }

    if cookies_file and cookies_file.exists():
        opts["cookiefile"] = str(cookies_file)

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    # Find the downloaded thumbnail (extension varies)
    for ext in [".jpg", ".png", ".webp"]:
        thumb_path = output_path.with_suffix(ext)
        if thumb_path.exists():
            return thumb_path

    return None


def get_available_formats(url: str, cookies_file: Path | None = None) -> list[dict]:
    """Get list of available formats for a video."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    if cookies_file and cookies_file.exists():
        opts["cookiefile"] = str(cookies_file)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info.get("formats", []):
            formats.append(
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("resolution"),
                    "fps": f.get("fps"),
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "filesize": f.get("filesize"),
                }
            )
        return formats
