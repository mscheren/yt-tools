"""Download item dataclass."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ytdl_app.models import DownloadStatus


@dataclass
class DownloadItem:
    """A single download item in the queue."""

    url: str
    id: str = ""
    title: str = ""
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error: str | None = None
    output_path: Path | None = None
    added_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retries: int = 0

    def __post_init__(self):
        if not self.id:
            self.id = f"{hash(self.url)}_{int(time.time() * 1000)}"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "url": self.url,
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "progress": self.progress,
            "error": self.error,
            "output_path": str(self.output_path) if self.output_path else None,
            "added_at": self.added_at.isoformat(),
            "retries": self.retries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DownloadItem":
        """Create from dictionary."""
        return cls(
            url=data["url"],
            id=data.get("id", ""),
            title=data.get("title", ""),
            status=DownloadStatus(data.get("status", "pending")),
            progress=data.get("progress", 0.0),
            error=data.get("error"),
            output_path=Path(data["output_path"]) if data.get("output_path") else None,
            added_at=(
                datetime.fromisoformat(data["added_at"])
                if data.get("added_at")
                else datetime.now()
            ),
            retries=data.get("retries", 0),
        )

    def mark_started(self) -> None:
        """Mark the download as started."""
        self.status = DownloadStatus.DOWNLOADING
        self.started_at = datetime.now()

    def mark_completed(self, output_path: Path | None = None) -> None:
        """Mark the download as completed."""
        self.status = DownloadStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 100.0
        if output_path:
            self.output_path = output_path

    def mark_failed(self, error: str) -> None:
        """Mark the download as failed."""
        self.status = DownloadStatus.FAILED
        self.error = error
