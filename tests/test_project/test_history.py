"""Tests for edit history (undo/redo)."""

from ytdl_app.project import EditHistory


class TestEditHistory:
    """Tests for EditHistory class."""

    def test_push_and_undo(self):
        """Push should allow undo to previous state."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        history.push("state2", "Edit 1")

        result = history.undo()
        assert result == "state1"

    def test_undo_empty(self):
        """Undo on empty history should return None."""
        history = EditHistory[str]()
        assert history.undo() is None

    def test_undo_single(self):
        """Undo with single state should return None."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        assert history.undo() is None

    def test_redo(self):
        """Redo should restore undone state."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        history.push("state2", "Edit 1")

        history.undo()
        result = history.redo()

        assert result == "state2"

    def test_redo_empty(self):
        """Redo without undo should return None."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        assert history.redo() is None

    def test_new_push_clears_redo(self):
        """New push after undo should clear redo stack."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        history.push("state2", "Edit 1")
        history.undo()
        history.push("state3", "New edit")

        assert history.redo() is None

    def test_can_undo(self):
        """Can undo should report correctly."""
        history = EditHistory[str]()
        assert not history.can_undo()

        history.push("state1", "Initial")
        assert not history.can_undo()

        history.push("state2", "Edit")
        assert history.can_undo()

    def test_can_redo(self):
        """Can redo should report correctly."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        history.push("state2", "Edit")

        assert not history.can_redo()
        history.undo()
        assert history.can_redo()

    def test_max_history(self):
        """History should respect max size."""
        history = EditHistory[int](max_history=3)

        for i in range(5):
            history.push(i, f"State {i}")

        assert history.undo_count == 2  # max_history - 1

    def test_descriptions(self):
        """Descriptions should be retrievable."""
        history = EditHistory[str]()
        history.push("state1", "First edit")
        history.push("state2", "Second edit")

        assert history.get_undo_description() == "Second edit"
        history.undo()
        assert history.get_redo_description() == "Second edit"

    def test_clear(self):
        """Clear should empty both stacks."""
        history = EditHistory[str]()
        history.push("state1", "Initial")
        history.push("state2", "Edit")
        history.undo()

        history.clear()

        assert not history.can_undo()
        assert not history.can_redo()
