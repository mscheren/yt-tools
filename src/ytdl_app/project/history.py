"""Undo/redo history for edit operations."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class HistoryEntry(Generic[T]):
    """A single entry in the history stack."""

    state: T
    description: str


class EditHistory(Generic[T]):
    """Manages undo/redo history for editing operations."""

    def __init__(self, max_history: int = 50):
        self._undo_stack: list[HistoryEntry[T]] = []
        self._redo_stack: list[HistoryEntry[T]] = []
        self._max_history = max_history

    def push(self, state: T, description: str = "") -> None:
        """
        Push a new state onto the history stack.

        Args:
            state: The state to save (should be a copy/snapshot).
            description: Description of the operation.
        """
        self._undo_stack.append(HistoryEntry(state=state, description=description))
        self._redo_stack.clear()

        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def undo(self) -> T | None:
        """
        Undo the last operation.

        Returns:
            The previous state, or None if nothing to undo.
        """
        if len(self._undo_stack) <= 1:
            return None

        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return self._undo_stack[-1].state if self._undo_stack else None

    def redo(self) -> T | None:
        """
        Redo the last undone operation.

        Returns:
            The redone state, or None if nothing to redo.
        """
        if not self._redo_stack:
            return None

        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        return entry.state

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 1

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def get_undo_description(self) -> str | None:
        """Get description of the operation that would be undone."""
        if len(self._undo_stack) > 1:
            return self._undo_stack[-1].description
        return None

    def get_redo_description(self) -> str | None:
        """Get description of the operation that would be redone."""
        if self._redo_stack:
            return self._redo_stack[-1].description
        return None

    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    @property
    def undo_count(self) -> int:
        """Number of available undo steps."""
        return max(0, len(self._undo_stack) - 1)

    @property
    def redo_count(self) -> int:
        """Number of available redo steps."""
        return len(self._redo_stack)
