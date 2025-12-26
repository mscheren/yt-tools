"""YouTube downloading functionality."""

from .archive import DownloadArchive
from .config import DownloadConfig
from .downloader import Downloader, DownloadError
from .item import DownloadItem
from .metadata import (
    Chapter,
    VideoInfo,
    download_thumbnail,
    extract_metadata,
    get_available_formats,
)
from .queue import DownloadQueue

__all__ = [
    "Chapter",
    "DownloadArchive",
    "DownloadConfig",
    "DownloadError",
    "DownloadItem",
    "DownloadQueue",
    "Downloader",
    "VideoInfo",
    "download_thumbnail",
    "extract_metadata",
    "get_available_formats",
]
