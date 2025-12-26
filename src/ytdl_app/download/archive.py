"""Download archive for tracking downloaded videos."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ArchiveEntry:
    """An entry in the download archive."""

    extractor: str
    video_id: str
    title: str | None = None
    downloaded_at: datetime | None = None

    def to_line(self) -> str:
        """Convert to archive file line format."""
        return f"{self.extractor} {self.video_id}"

    @classmethod
    def from_line(cls, line: str) -> "ArchiveEntry":
        """Parse from archive file line."""
        parts = line.strip().split(" ", 1)
        if len(parts) >= 2:
            return cls(extractor=parts[0], video_id=parts[1])
        return cls(extractor="youtube", video_id=parts[0])


class DownloadArchive:
    """Manages the download archive file."""

    def __init__(self, archive_path: Path):
        self.path = Path(archive_path)
        self._entries: set[str] | None = None

    def _load_entries(self) -> set[str]:
        """Load archive entries from file."""
        if self._entries is not None:
            return self._entries

        self._entries = set()
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    self._entries.add(line)
        return self._entries

    def contains(self, extractor: str, video_id: str) -> bool:
        """Check if a video is in the archive."""
        entries = self._load_entries()
        return f"{extractor} {video_id}" in entries

    def add(self, extractor: str, video_id: str, title: str | None = None) -> None:
        """Add a video to the archive."""
        entries = self._load_entries()
        entry_line = f"{extractor} {video_id}"

        if entry_line not in entries:
            entries.add(entry_line)
            self.path.parent.mkdir(parents=True, exist_ok=True)

            with self.path.open("a") as f:
                if title:
                    f.write(f"# {title} - {datetime.now().isoformat()}\n")
                f.write(f"{entry_line}\n")

    def remove(self, extractor: str, video_id: str) -> bool:
        """Remove a video from the archive."""
        entries = self._load_entries()
        entry_line = f"{extractor} {video_id}"

        if entry_line in entries:
            entries.remove(entry_line)
            self._save()
            return True
        return False

    def _save(self) -> None:
        """Save all entries back to file."""
        if self._entries is None:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            for entry in sorted(self._entries):
                f.write(f"{entry}\n")

    def list_entries(self) -> list[ArchiveEntry]:
        """Get all archive entries."""
        entries = self._load_entries()
        return [ArchiveEntry.from_line(line) for line in entries]

    def clear(self) -> None:
        """Clear all entries from the archive."""
        self._entries = set()
        if self.path.exists():
            self.path.unlink()

    def __len__(self) -> int:
        """Get the number of archived videos."""
        return len(self._load_entries())
