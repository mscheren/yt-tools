"""Video effects and color grading."""

from dataclasses import dataclass

import numpy as np
from moviepy import VideoClip


@dataclass
class ColorGrading:
    """Color grading parameters."""

    brightness: float = 0.0  # -1.0 to 1.0
    contrast: float = 1.0  # 0.0 to 2.0
    saturation: float = 1.0  # 0.0 to 2.0
    gamma: float = 1.0  # 0.1 to 3.0


def _adjust_brightness(frame: np.ndarray, value: float) -> np.ndarray:
    """Adjust frame brightness."""
    return np.clip(frame + value * 255, 0, 255).astype(np.uint8)


def _adjust_contrast(frame: np.ndarray, value: float) -> np.ndarray:
    """Adjust frame contrast."""
    mean = np.mean(frame)
    return np.clip((frame - mean) * value + mean, 0, 255).astype(np.uint8)


def _adjust_saturation(frame: np.ndarray, value: float) -> np.ndarray:
    """Adjust frame saturation."""
    gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
    gray = np.stack([gray] * 3, axis=-1)
    return np.clip(gray + (frame - gray) * value, 0, 255).astype(np.uint8)


def _adjust_gamma(frame: np.ndarray, value: float) -> np.ndarray:
    """Adjust frame gamma."""
    normalized = frame / 255.0
    corrected = np.power(normalized, 1.0 / value)
    return (corrected * 255).astype(np.uint8)


def apply_color_grading(clip: VideoClip, grading: ColorGrading) -> VideoClip:
    """Apply color grading to video."""

    def process_frame(frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float64)

        if grading.brightness != 0:
            result = _adjust_brightness(result, grading.brightness)

        if grading.contrast != 1.0:
            result = _adjust_contrast(result, grading.contrast)

        if grading.saturation != 1.0:
            result = _adjust_saturation(result, grading.saturation)

        if grading.gamma != 1.0:
            result = _adjust_gamma(result, grading.gamma)

        return result.astype(np.uint8)

    return clip.image_transform(process_frame)


def apply_grayscale(clip: VideoClip) -> VideoClip:
    """Convert video to grayscale."""

    def to_grayscale(frame: np.ndarray) -> np.ndarray:
        gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
        return np.stack([gray] * 3, axis=-1).astype(np.uint8)

    return clip.image_transform(to_grayscale)


def apply_blur(clip: VideoClip, kernel_size: int = 5) -> VideoClip:
    """Apply box blur to video."""
    from scipy.ndimage import uniform_filter

    def blur_frame(frame: np.ndarray) -> np.ndarray:
        return uniform_filter(frame, size=(kernel_size, kernel_size, 1)).astype(
            np.uint8
        )

    return clip.image_transform(blur_frame)


def apply_edge_detection(clip: VideoClip) -> VideoClip:
    """Apply edge detection filter."""
    from scipy.ndimage import sobel

    def detect_edges(frame: np.ndarray) -> np.ndarray:
        gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
        edges_x = sobel(gray, axis=0)
        edges_y = sobel(gray, axis=1)
        edges = np.hypot(edges_x, edges_y)
        edges = (edges / edges.max() * 255).astype(np.uint8)
        return np.stack([edges] * 3, axis=-1)

    return clip.image_transform(detect_edges)


def apply_invert(clip: VideoClip) -> VideoClip:
    """Invert video colors."""

    def invert_frame(frame: np.ndarray) -> np.ndarray:
        return 255 - frame

    return clip.image_transform(invert_frame)


def apply_sepia(clip: VideoClip) -> VideoClip:
    """Apply sepia tone filter."""

    def sepia_frame(frame: np.ndarray) -> np.ndarray:
        sepia_matrix = np.array(
            [
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131],
            ]
        )
        result = np.dot(frame[..., :3], sepia_matrix.T)
        return np.clip(result, 0, 255).astype(np.uint8)

    return clip.image_transform(sepia_frame)
