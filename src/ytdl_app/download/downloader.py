"""YouTube content downloader using yt-dlp."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import yt_dlp

from ytdl_app.models import OutputFormat


@dataclass
class DownloadOptions:
    """Configuration options for downloads."""

    output_dir: Path = field(default_factory=Path.cwd)
    output_format: OutputFormat = OutputFormat.MP4
    cookies_file: Path | None = None

    def get_output_template(self, is_playlist: bool = False) -> str:
        """Generate the output template string for yt-dlp."""
        base_dir = str(self.output_dir)
        if is_playlist:
            return f"{base_dir}/%(playlist)s/%(title)s.%(ext)s"
        return f"{base_dir}/%(title)s.%(ext)s"


class Downloader:
    """YouTube content downloader using yt-dlp."""

    _VIDEO_FORMAT = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b"
    _AUDIO_FORMAT = "ba[ext=m4a]/ba/b"

    def __init__(
        self,
        options: DownloadOptions | None = None,
        progress_callback: Callable[[dict], None] | None = None,
    ):
        self.options = options or DownloadOptions()
        self.progress_callback = progress_callback

    def _build_ydl_opts(self, is_playlist: bool = False) -> dict:
        """Build yt-dlp options dictionary."""
        opts = {
            "outtmpl": self.options.get_output_template(is_playlist),
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "quiet": True,
            "no_warnings": True,
        }

        if self.progress_callback:
            opts["progress_hooks"] = [self.progress_callback]

        if self.options.cookies_file and self.options.cookies_file.exists():
            opts["cookiefile"] = str(self.options.cookies_file)

        if self.options.output_format == OutputFormat.MP4:
            opts["format"] = self._VIDEO_FORMAT
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = self._AUDIO_FORMAT
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        return opts

    def download(self, url: str) -> dict:
        """Download a single video or audio from URL."""
        opts = self._build_ydl_opts(is_playlist=False)
        opts["noplaylist"] = True

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=True)

    def download_playlist(self, url: str) -> dict:
        """Download an entire playlist."""
        opts = self._build_ydl_opts(is_playlist=True)

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=True)

    def get_info(self, url: str) -> dict:
        """Fetch metadata without downloading."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
        }

        if self.options.cookies_file and self.options.cookies_file.exists():
            opts["cookiefile"] = str(self.options.cookies_file)

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
