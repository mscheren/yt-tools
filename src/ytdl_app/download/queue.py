"""Download queue management."""

import json
import threading
from pathlib import Path
from queue import Queue
from typing import Callable

from ytdl_app.models import DownloadStatus

from .item import DownloadItem


class DownloadQueue:
    """Manages a queue of downloads with persistence."""

    def __init__(self, queue_file: Path | None = None):
        self._items: dict[str, DownloadItem] = {}
        self._queue: Queue[str] = Queue()
        self._lock = threading.Lock()
        self._paused = False
        self._queue_file = queue_file
        self._on_progress: Callable[[DownloadItem], None] | None = None

        if queue_file and queue_file.exists():
            self._load()

    def add(self, url: str, title: str = "") -> DownloadItem:
        """Add a URL to the download queue."""
        with self._lock:
            item = DownloadItem(url=url, title=title)
            self._items[item.id] = item
            self._queue.put(item.id)
            self._save()
            return item

    def add_batch(self, urls: list[str]) -> list[DownloadItem]:
        """Add multiple URLs to the queue."""
        items = []
        with self._lock:
            for url in urls:
                item = DownloadItem(url=url)
                self._items[item.id] = item
                self._queue.put(item.id)
                items.append(item)
            self._save()
        return items

    def get_next(self) -> DownloadItem | None:
        """Get the next pending item from the queue."""
        if self._paused:
            return None
        try:
            item_id = self._queue.get_nowait()
            item = self._items.get(item_id)
            if item and item.status == DownloadStatus.PENDING:
                return item
            return self.get_next()
        except Exception:
            return None

    def update_progress(self, item_id: str, progress: float) -> None:
        """Update download progress."""
        with self._lock:
            if item_id in self._items:
                self._items[item_id].progress = progress
                if self._on_progress:
                    self._on_progress(self._items[item_id])

    def update_status(
        self, item_id: str, status: DownloadStatus, error: str | None = None
    ) -> None:
        """Update the status of a download item."""
        with self._lock:
            if item_id in self._items:
                item = self._items[item_id]
                if status == DownloadStatus.DOWNLOADING:
                    item.mark_started()
                elif status == DownloadStatus.COMPLETED:
                    item.mark_completed()
                elif status == DownloadStatus.FAILED:
                    item.mark_failed(error or "Unknown error")
                else:
                    item.status = status
                self._save()

    def pause(self, item_id: str | None = None) -> None:
        """Pause a specific item or the entire queue."""
        with self._lock:
            if item_id and item_id in self._items:
                self._items[item_id].status = DownloadStatus.PAUSED
            else:
                self._paused = True
            self._save()

    def resume(self, item_id: str | None = None) -> None:
        """Resume a specific item or the entire queue."""
        with self._lock:
            if item_id and item_id in self._items:
                item = self._items[item_id]
                if item.status == DownloadStatus.PAUSED:
                    item.status = DownloadStatus.PENDING
                    self._queue.put(item_id)
            else:
                self._paused = False
            self._save()

    def cancel(self, item_id: str) -> bool:
        """Cancel a download item."""
        with self._lock:
            if item_id in self._items:
                self._items[item_id].status = DownloadStatus.CANCELLED
                self._save()
                return True
            return False

    def retry(self, item_id: str) -> bool:
        """Retry a failed download."""
        with self._lock:
            if item_id in self._items:
                item = self._items[item_id]
                if item.status == DownloadStatus.FAILED:
                    item.status = DownloadStatus.PENDING
                    item.error = None
                    item.retries += 1
                    self._queue.put(item_id)
                    self._save()
                    return True
            return False

    def get_all(self) -> list[DownloadItem]:
        """Get all download items."""
        return list(self._items.values())

    def get_by_status(self, status: DownloadStatus) -> list[DownloadItem]:
        """Get items by status."""
        return [item for item in self._items.values() if item.status == status]

    def clear_completed(self) -> int:
        """Remove completed and cancelled items."""
        with self._lock:
            to_remove = [
                id
                for id, item in self._items.items()
                if item.status in (DownloadStatus.COMPLETED, DownloadStatus.CANCELLED)
            ]
            for id in to_remove:
                del self._items[id]
            self._save()
            return len(to_remove)

    def set_progress_callback(self, callback: Callable[[DownloadItem], None]) -> None:
        """Set a callback for progress updates."""
        self._on_progress = callback

    def _save(self) -> None:
        """Save queue state to file."""
        if not self._queue_file:
            return
        self._queue_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"items": [item.to_dict() for item in self._items.values()]}
        self._queue_file.write_text(json.dumps(data, indent=2))

    def _load(self) -> None:
        """Load queue state from file."""
        if not self._queue_file or not self._queue_file.exists():
            return
        try:
            data = json.loads(self._queue_file.read_text())
            for item_data in data.get("items", []):
                item = DownloadItem.from_dict(item_data)
                self._items[item.id] = item
                if item.status == DownloadStatus.PENDING:
                    self._queue.put(item.id)
        except (json.JSONDecodeError, KeyError):
            pass

    def __len__(self) -> int:
        return len(self._items)
