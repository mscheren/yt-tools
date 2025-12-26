"""Subtitle handling for videos."""

from dataclasses import dataclass
from pathlib import Path

from moviepy import CompositeVideoClip, TextClip, VideoClip


@dataclass
class SubtitleEntry:
    """A single subtitle entry."""

    start_time: float
    end_time: float
    text: str

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


def parse_srt(srt_path: Path) -> list[SubtitleEntry]:
    """Parse an SRT subtitle file."""
    entries = []
    content = srt_path.read_text(encoding="utf-8")
    blocks = content.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            time_line = lines[1]
            text = "\n".join(lines[2:])

            start_str, end_str = time_line.split(" --> ")
            start_time = _parse_srt_time(start_str.strip())
            end_time = _parse_srt_time(end_str.strip())

            entries.append(SubtitleEntry(start_time, end_time, text))

    return entries


def _parse_srt_time(time_str: str) -> float:
    """Parse SRT timestamp to seconds."""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def add_subtitles(
    clip: VideoClip,
    subtitles: list[SubtitleEntry],
    font_size: int = 24,
    color: str = "white",
    bg_color: str = "black",
    position: str = "bottom",
) -> VideoClip:
    """Add subtitles to a video clip."""
    subtitle_clips = []

    for entry in subtitles:
        txt_clip = (
            TextClip(
                text=entry.text,
                font_size=font_size,
                color=color,
                bg_color=bg_color,
            )
            .with_position(("center", position))
            .with_start(entry.start_time)
            .with_duration(entry.duration)
        )
        subtitle_clips.append(txt_clip)

    return CompositeVideoClip([clip] + subtitle_clips)


def add_subtitles_from_file(
    clip: VideoClip,
    srt_path: Path,
    font_size: int = 24,
    color: str = "white",
) -> VideoClip:
    """Add subtitles from an SRT file."""
    subtitles = parse_srt(srt_path)
    return add_subtitles(clip, subtitles, font_size, color)
