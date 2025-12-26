"""Tests for download queue."""

from ytdl_app.download import DownloadQueue
from ytdl_app.models import DownloadStatus


class TestDownloadQueue:
    """Tests for DownloadQueue class."""

    def test_add_item(self):
        """Adding item should create a pending download."""
        queue = DownloadQueue()
        item = queue.add("https://example.com/video")

        assert item.url == "https://example.com/video"
        assert item.status == DownloadStatus.PENDING
        assert len(queue) == 1

    def test_add_batch(self):
        """Adding batch should create multiple items."""
        queue = DownloadQueue()
        urls = ["https://example.com/1", "https://example.com/2"]
        items = queue.add_batch(urls)

        assert len(items) == 2
        assert len(queue) == 2

    def test_get_next(self):
        """Get next should return pending item."""
        queue = DownloadQueue()
        queue.add("https://example.com/video")

        item = queue.get_next()
        assert item is not None
        assert item.status == DownloadStatus.PENDING

    def test_get_next_empty(self):
        """Get next on empty queue should return None."""
        queue = DownloadQueue()
        assert queue.get_next() is None

    def test_pause_resume(self):
        """Pause and resume should work correctly."""
        queue = DownloadQueue()
        item = queue.add("https://example.com/video")

        queue.pause(item.id)
        assert queue._items[item.id].status == DownloadStatus.PAUSED

        queue.resume(item.id)
        assert queue._items[item.id].status == DownloadStatus.PENDING

    def test_cancel(self):
        """Cancel should mark item as cancelled."""
        queue = DownloadQueue()
        item = queue.add("https://example.com/video")

        result = queue.cancel(item.id)
        assert result is True
        assert queue._items[item.id].status == DownloadStatus.CANCELLED

    def test_retry_failed(self):
        """Retry should reset failed item to pending."""
        queue = DownloadQueue()
        item = queue.add("https://example.com/video")
        queue.update_status(item.id, DownloadStatus.FAILED, "Error")

        result = queue.retry(item.id)
        assert result is True
        assert queue._items[item.id].status == DownloadStatus.PENDING
        assert queue._items[item.id].retries == 1

    def test_clear_completed(self):
        """Clear completed should remove finished items."""
        queue = DownloadQueue()
        item1 = queue.add("https://example.com/1")
        item2 = queue.add("https://example.com/2")

        queue.update_status(item1.id, DownloadStatus.COMPLETED)

        removed = queue.clear_completed()
        assert removed == 1
        assert len(queue) == 1

    def test_persistence(self, temp_dir):
        """Queue should persist to file."""
        queue_file = temp_dir / "queue.json"
        queue = DownloadQueue(queue_file=queue_file)
        queue.add("https://example.com/video")

        # Load in new instance
        queue2 = DownloadQueue(queue_file=queue_file)
        assert len(queue2) == 1

    def test_get_by_status(self):
        """Should filter items by status."""
        queue = DownloadQueue()
        item1 = queue.add("https://example.com/1")
        item2 = queue.add("https://example.com/2")
        queue.update_status(item1.id, DownloadStatus.COMPLETED)

        completed = queue.get_by_status(DownloadStatus.COMPLETED)
        pending = queue.get_by_status(DownloadStatus.PENDING)

        assert len(completed) == 1
        assert len(pending) == 1
