"""Download configuration options."""

from dataclasses import dataclass, field
from pathlib import Path

from ytdl_app.models import OutputFormat, VideoResolution


@dataclass
class DownloadConfig:
    """Comprehensive configuration for downloads."""

    # Output settings
    output_dir: Path = field(default_factory=Path.cwd)
    output_format: OutputFormat = OutputFormat.MP4
    output_template: str | None = None

    # Quality settings
    resolution: VideoResolution = VideoResolution.BEST
    max_filesize: int | None = None  # In bytes
    prefer_free_formats: bool = False

    # Audio settings
    audio_quality: int = 192  # kbps for audio extraction
    extract_audio: bool = False

    # Authentication
    cookies_file: Path | None = None

    # Behavior
    download_archive: Path | None = None
    write_thumbnail: bool = False
    write_info_json: bool = False
    embed_thumbnail: bool = False
    embed_chapters: bool = True

    # Retry settings
    retries: int = 3
    retry_sleep: float = 5.0

    # Rate limiting
    rate_limit: str | None = None  # e.g., "1M" for 1MB/s

    def get_output_template(self, is_playlist: bool = False) -> str:
        """Generate the output template string for yt-dlp."""
        if self.output_template:
            return str(self.output_dir / self.output_template)

        base_dir = str(self.output_dir)
        if is_playlist:
            return f"{base_dir}/%(playlist)s/%(title)s.%(ext)s"
        return f"{base_dir}/%(title)s.%(ext)s"

    def get_format_string(self) -> str:
        """Build the format selection string for yt-dlp."""
        if self.output_format.is_audio_only or self.extract_audio:
            return "ba[ext=m4a]/ba/b"

        height = self.resolution.height
        if height:
            return f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]/b[height<={height}][ext=mp4]/bv*+ba/b"
        return "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b"

    def to_ydl_opts(self, is_playlist: bool = False) -> dict:
        """Convert config to yt-dlp options dictionary."""
        opts = {
            "outtmpl": self.get_output_template(is_playlist),
            "format": self.get_format_string(),
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "quiet": True,
            "no_warnings": True,
            "retries": self.retries,
            "fragment_retries": self.retries,
        }

        if not self.output_format.is_audio_only:
            opts["merge_output_format"] = self.output_format.value

        if self.cookies_file and self.cookies_file.exists():
            opts["cookiefile"] = str(self.cookies_file)

        if self.download_archive:
            opts["download_archive"] = str(self.download_archive)

        if self.max_filesize:
            opts["max_filesize"] = self.max_filesize

        if self.rate_limit:
            opts["ratelimit"] = self.rate_limit

        if self.write_thumbnail:
            opts["writethumbnail"] = True

        if self.write_info_json:
            opts["writeinfojson"] = True

        if self.embed_chapters:
            opts["embed_chapters"] = True

        # Audio extraction postprocessor
        if self.output_format.is_audio_only or self.extract_audio:
            codec_map = {
                OutputFormat.MP3: "mp3",
                OutputFormat.WAV: "wav",
                OutputFormat.FLAC: "flac",
                OutputFormat.AAC: "aac",
                OutputFormat.OGG: "vorbis",
            }
            codec = codec_map.get(self.output_format, "mp3")
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": codec,
                    "preferredquality": str(self.audio_quality),
                }
            ]
            if self.embed_thumbnail:
                opts["postprocessors"].append({"key": "EmbedThumbnail"})

        return opts
