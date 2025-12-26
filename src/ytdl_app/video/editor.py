"""Video editor class for editing operations."""

from pathlib import Path

from moviepy import CompositeVideoClip, TextClip, VideoFileClip

from ytdl_app.models import VideoMetadata

from .effects import (
    ColorGrading,
    apply_blur,
    apply_color_grading,
    apply_grayscale,
    apply_sepia,
)
from .overlay import TextOverlayConfig
from .transforms import (
    CropRegion,
    RotationAngle,
    apply_crop,
    apply_resize,
    apply_rotate,
    apply_speed,
)


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

    # Basic operations
    def trim(self, start: float, end: float) -> "VideoEditor":
        """Trim the video to a specific time range."""
        self._clip = self.clip.subclipped(start, end)
        return self

    def adjust_volume(self, factor: float) -> "VideoEditor":
        """Adjust the audio volume (1.0 = original)."""
        if self.clip.audio is not None:
            self._clip = self.clip.with_volume_scaled(factor)
        return self

    # Transformations
    def speed(self, factor: float) -> "VideoEditor":
        """Adjust playback speed (2.0 = double speed, 0.5 = half speed)."""
        self._clip = apply_speed(self.clip, factor)
        return self

    def reverse(self) -> "VideoEditor":
        """Reverse video playback."""
        self._clip = self.clip.time_mirror()
        return self

    def loop(self, n_loops: int) -> "VideoEditor":
        """Loop the video n times."""
        self._clip = self.clip.loop(n=n_loops)
        return self

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> "VideoEditor":
        """Crop to region (x1, y1) to (x2, y2)."""
        self._clip = apply_crop(self.clip, CropRegion(x1, y1, x2, y2))
        return self

    def resize(
        self, width: int | None = None, height: int | None = None
    ) -> "VideoEditor":
        """Resize video. Maintains aspect ratio if only one dimension given."""
        self._clip = apply_resize(self.clip, width, height)
        return self

    def rotate(self, angle: float | RotationAngle) -> "VideoEditor":
        """Rotate video by angle in degrees."""
        self._clip = apply_rotate(self.clip, angle)
        return self

    # Effects
    def color_grade(self, grading: ColorGrading) -> "VideoEditor":
        """Apply color grading adjustments."""
        self._clip = apply_color_grading(self.clip, grading)
        return self

    def grayscale(self) -> "VideoEditor":
        """Convert to grayscale."""
        self._clip = apply_grayscale(self.clip)
        return self

    def blur(self, kernel_size: int = 5) -> "VideoEditor":
        """Apply blur effect."""
        self._clip = apply_blur(self.clip, kernel_size)
        return self

    def sepia(self) -> "VideoEditor":
        """Apply sepia tone."""
        self._clip = apply_sepia(self.clip)
        return self

    # Overlays
    def add_text_overlay(self, config: TextOverlayConfig) -> "VideoEditor":
        """Add a text overlay to the video."""
        duration = config.duration or (self.clip.duration - config.start_time)
        txt_clip = (
            TextClip(text=config.text, font_size=config.font_size, color=config.color)
            .with_position(config.position)
            .with_start(config.start_time)
            .with_duration(duration)
        )
        self._clip = CompositeVideoClip([self.clip, txt_clip])
        return self

    # Export
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
