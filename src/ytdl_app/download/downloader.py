"""YouTube content downloader using yt-dlp."""

import time
from pathlib import Path
from typing import Callable

import yt_dlp

from .config import DownloadConfig


class DownloadError(Exception):
    """Exception raised when a download fails."""

    pass


class Downloader:
    """YouTube content downloader with retry support."""

    def __init__(
        self,
        config: DownloadConfig | None = None,
        progress_callback: Callable[[dict], None] | None = None,
    ):
        self.config = config or DownloadConfig()
        self.progress_callback = progress_callback

    def _build_opts(self, is_playlist: bool = False) -> dict:
        """Build yt-dlp options from config."""
        opts = self.config.to_ydl_opts(is_playlist)
        if self.progress_callback:
            opts["progress_hooks"] = [self.progress_callback]
        return opts

    def download(self, url: str) -> dict:
        """Download a single video with retry logic."""
        opts = self._build_opts(is_playlist=False)
        opts["noplaylist"] = True
        return self._download_with_retry(url, opts)

    def download_playlist(self, url: str) -> dict:
        """Download an entire playlist with retry logic."""
        opts = self._build_opts(is_playlist=True)
        return self._download_with_retry(url, opts)

    def _download_with_retry(self, url: str, opts: dict) -> dict:
        """Execute download with retry logic."""
        last_error = None

        for attempt in range(self.config.retries + 1):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=True)
            except yt_dlp.DownloadError as e:
                last_error = e
                if attempt < self.config.retries:
                    time.sleep(self.config.retry_sleep)
                    continue
                raise DownloadError(
                    f"Download failed after {attempt + 1} attempts: {e}"
                ) from e

        raise DownloadError(f"Download failed: {last_error}")

    def get_info(self, url: str) -> dict:
        """Fetch metadata without downloading."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
        }

        if self.config.cookies_file and self.config.cookies_file.exists():
            opts["cookiefile"] = str(self.config.cookies_file)

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def merge_formats(
        self, url: str, video_format_id: str, audio_format_id: str, output_path: Path
    ) -> Path:
        """Download and merge specific video and audio formats."""
        opts = {
            "format": f"{video_format_id}+{audio_format_id}",
            "outtmpl": str(output_path),
            "merge_output_format": self.config.output_format.value,
            "quiet": True,
            "no_warnings": True,
        }

        if self.config.cookies_file and self.config.cookies_file.exists():
            opts["cookiefile"] = str(self.config.cookies_file)

        if self.progress_callback:
            opts["progress_hooks"] = [self.progress_callback]

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        return output_path
