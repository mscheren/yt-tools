"""Tests for download archive."""

from ytdl_app.download import DownloadArchive


class TestDownloadArchive:
    """Tests for DownloadArchive class."""

    def test_add_entry(self, temp_dir):
        """Adding entry should write to file."""
        archive = DownloadArchive(temp_dir / "archive.txt")
        archive.add("youtube", "abc123", "Test Video")

        assert archive.contains("youtube", "abc123")
        assert len(archive) == 1

    def test_contains_not_found(self, temp_dir):
        """Contains should return False for missing entries."""
        archive = DownloadArchive(temp_dir / "archive.txt")
        assert not archive.contains("youtube", "nonexistent")

    def test_remove_entry(self, temp_dir):
        """Remove should delete entry from archive."""
        archive = DownloadArchive(temp_dir / "archive.txt")
        archive.add("youtube", "abc123")

        result = archive.remove("youtube", "abc123")
        assert result is True
        assert not archive.contains("youtube", "abc123")

    def test_persistence(self, temp_dir):
        """Archive should persist across instances."""
        archive_path = temp_dir / "archive.txt"
        archive1 = DownloadArchive(archive_path)
        archive1.add("youtube", "video1")

        archive2 = DownloadArchive(archive_path)
        assert archive2.contains("youtube", "video1")

    def test_list_entries(self, temp_dir):
        """List entries should return all entries."""
        archive = DownloadArchive(temp_dir / "archive.txt")
        archive.add("youtube", "vid1")
        archive.add("youtube", "vid2")

        entries = archive.list_entries()
        assert len(entries) == 2

    def test_clear(self, temp_dir):
        """Clear should remove all entries."""
        archive = DownloadArchive(temp_dir / "archive.txt")
        archive.add("youtube", "vid1")
        archive.clear()

        assert len(archive) == 0
