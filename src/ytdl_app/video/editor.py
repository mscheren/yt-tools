"""Video editor class for editing operations."""

from pathlib import Path

from moviepy import CompositeVideoClip, TextClip, VideoFileClip

from ytdl_app.models import VideoMetadata

from .overlay import TextOverlayConfig


class VideoEditor:
    """Video editing operations using moviepy."""

    def __init__(self, input_path: Path):
        self.input_path = Path(input_path)
        self._clip: VideoFileClip | None = None

    def __enter__(self) -> "VideoEditor":
        self._clip = VideoFileClip(str(self.input_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Release video resources."""
        if self._clip is not None:
            self._clip.close()
            self._clip = None

    @property
    def clip(self) -> VideoFileClip:
        """Get the current clip."""
        if self._clip is None:
            raise RuntimeError("Video not loaded. Use context manager or load().")
        return self._clip

    def load(self) -> "VideoEditor":
        """Load the video file."""
        self._clip = VideoFileClip(str(self.input_path))
        return self

    def get_metadata(self) -> VideoMetadata:
        """Get metadata about the loaded video."""
        return VideoMetadata(
            path=self.input_path,
            duration=self.clip.duration,
            fps=self.clip.fps,
            width=self.clip.size[0],
            height=self.clip.size[1],
            has_audio=self.clip.audio is not None,
        )

    def trim(self, start: float, end: float) -> "VideoEditor":
        """Trim the video to a specific time range."""
        self._clip = self.clip.subclipped(start, end)
        return self

    def adjust_volume(self, factor: float) -> "VideoEditor":
        """Adjust the audio volume (1.0 = original)."""
        if self.clip.audio is not None:
            self._clip = self.clip.with_volume_scaled(factor)
        return self

    def add_text_overlay(self, config: TextOverlayConfig) -> "VideoEditor":
        """Add a text overlay to the video."""
        duration = config.duration or (self.clip.duration - config.start_time)

        txt_clip = (
            TextClip(
                text=config.text,
                font_size=config.font_size,
                color=config.color,
            )
            .with_position(config.position)
            .with_start(config.start_time)
            .with_duration(duration)
        )

        self._clip = CompositeVideoClip([self.clip, txt_clip])
        return self

    def export(
        self,
        output_path: Path,
        codec: str = "libx264",
        audio_codec: str = "aac",
        fps: int | None = None,
    ) -> Path:
        """Export the edited video."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        write_kwargs = {"codec": codec, "audio_codec": audio_codec, "logger": None}
        if fps:
            write_kwargs["fps"] = fps

        self.clip.write_videofile(str(output_path), **write_kwargs)
        return output_path
