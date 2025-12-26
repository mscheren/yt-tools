"""Video transformation operations."""

from dataclasses import dataclass
from enum import Enum

from moviepy import VideoClip


class RotationAngle(Enum):
    """Standard rotation angles."""

    CW_90 = 90
    CW_180 = 180
    CW_270 = 270
    CCW_90 = -90


@dataclass
class CropRegion:
    """Defines a crop region."""

    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1


def apply_speed(clip: VideoClip, factor: float) -> VideoClip:
    """
    Adjust playback speed.

    Args:
        clip: Input video clip.
        factor: Speed multiplier (0.5 = half speed, 2.0 = double speed).
    """
    return clip.with_speed_scaled(factor)


def apply_reverse(clip: VideoClip) -> VideoClip:
    """Reverse the video playback."""
    return clip.time_mirror()


def apply_loop(clip: VideoClip, n_loops: int) -> VideoClip:
    """
    Loop the video a specified number of times.

    Args:
        clip: Input video clip.
        n_loops: Number of times to loop.
    """
    return clip.loop(n=n_loops)


def apply_crop(clip: VideoClip, region: CropRegion) -> VideoClip:
    """
    Crop the video to a specific region.

    Args:
        clip: Input video clip.
        region: Crop region coordinates.
    """
    return clip.cropped(x1=region.x1, y1=region.y1, x2=region.x2, y2=region.y2)


def apply_resize(
    clip: VideoClip, width: int | None = None, height: int | None = None
) -> VideoClip:
    """
    Resize the video.

    Args:
        clip: Input video clip.
        width: Target width (maintains aspect ratio if height is None).
        height: Target height (maintains aspect ratio if width is None).
    """
    if width and height:
        return clip.resized((width, height))
    elif width:
        return clip.resized(width=width)
    elif height:
        return clip.resized(height=height)
    return clip


def apply_rotate(clip: VideoClip, angle: float | RotationAngle) -> VideoClip:
    """
    Rotate the video.

    Args:
        clip: Input video clip.
        angle: Rotation angle in degrees (positive = counter-clockwise).
    """
    if isinstance(angle, RotationAngle):
        angle = angle.value
    return clip.rotated(angle)


def apply_mirror(clip: VideoClip, horizontal: bool = True) -> VideoClip:
    """
    Mirror/flip the video.

    Args:
        clip: Input video clip.
        horizontal: If True, mirror horizontally. If False, mirror vertically.
    """
    if horizontal:
        return clip.fx("mirror_x")
    return clip.fx("mirror_y")
