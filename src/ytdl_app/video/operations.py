"""Standalone video operations."""

from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips

from ytdl_app.models import VideoMetadata


def concatenate_videos(
    video_paths: list[Path],
    output_path: Path,
    transition: str | None = None,
) -> Path:
    """Concatenate multiple videos into one."""
    clips = [VideoFileClip(str(p)) for p in video_paths]

    try:
        method = "compose" if transition else "chain"
        final = concatenate_videoclips(clips, method=method)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(str(output_path), logger=None)
        return output_path
    finally:
        for clip in clips:
            clip.close()


def get_video_info(video_path: Path) -> VideoMetadata:
    """Get metadata about a video file."""
    with VideoFileClip(str(video_path)) as clip:
        return VideoMetadata(
            path=video_path,
            duration=clip.duration,
            fps=clip.fps,
            width=clip.size[0],
            height=clip.size[1],
            has_audio=clip.audio is not None,
        )
