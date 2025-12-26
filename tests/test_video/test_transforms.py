"""Tests for video transforms."""


from ytdl_app.video.transforms import (
    CropRegion,
    RotationAngle,
    apply_crop,
    apply_loop,
    apply_resize,
    apply_reverse,
    apply_rotate,
    apply_speed,
)


class TestCropRegion:
    """Tests for CropRegion dataclass."""

    def test_width_height(self):
        """Width and height should be calculated correctly."""
        region = CropRegion(x1=100, y1=50, x2=500, y2=350)
        assert region.width == 400
        assert region.height == 300


class TestRotationAngle:
    """Tests for RotationAngle enum."""

    def test_values(self):
        """Rotation angles should have correct values."""
        assert RotationAngle.CW_90.value == 90
        assert RotationAngle.CW_180.value == 180
        assert RotationAngle.CCW_90.value == -90


class TestTransformFunctions:
    """Tests for transform functions."""

    def test_apply_speed(self, mock_video_clip):
        """Apply speed should call with_speed_scaled."""
        apply_speed(mock_video_clip, 2.0)
        mock_video_clip.with_speed_scaled.assert_called_with(2.0)

    def test_apply_reverse(self, mock_video_clip):
        """Apply reverse should call time_mirror."""
        apply_reverse(mock_video_clip)
        mock_video_clip.time_mirror.assert_called_once()

    def test_apply_loop(self, mock_video_clip):
        """Apply loop should call loop with n."""
        apply_loop(mock_video_clip, 3)
        mock_video_clip.loop.assert_called_with(n=3)

    def test_apply_crop(self, mock_video_clip):
        """Apply crop should call cropped with region."""
        region = CropRegion(0, 0, 100, 100)
        apply_crop(mock_video_clip, region)
        mock_video_clip.cropped.assert_called_with(x1=0, y1=0, x2=100, y2=100)

    def test_apply_resize_width_only(self, mock_video_clip):
        """Resize with width only should maintain aspect ratio."""
        apply_resize(mock_video_clip, width=1280)
        mock_video_clip.resized.assert_called_with(width=1280)

    def test_apply_resize_both(self, mock_video_clip):
        """Resize with both dimensions should use tuple."""
        apply_resize(mock_video_clip, width=1280, height=720)
        mock_video_clip.resized.assert_called_with((1280, 720))

    def test_apply_rotate_angle(self, mock_video_clip):
        """Apply rotate should accept numeric angle."""
        apply_rotate(mock_video_clip, 45.0)
        mock_video_clip.rotated.assert_called_with(45.0)

    def test_apply_rotate_enum(self, mock_video_clip):
        """Apply rotate should accept RotationAngle enum."""
        apply_rotate(mock_video_clip, RotationAngle.CW_90)
        mock_video_clip.rotated.assert_called_with(90)
