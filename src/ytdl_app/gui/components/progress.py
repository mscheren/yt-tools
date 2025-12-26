"""Progress tracking components."""

import streamlit as st


class ProgressTracker:
    """Context manager for tracking progress in Streamlit."""

    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.description = description
        self.current_step = 0
        self._progress_bar = None
        self._status_text = None

    def __enter__(self) -> "ProgressTracker":
        self._status_text = st.empty()
        self._progress_bar = st.progress(0)
        self._update_display()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self._progress_bar.progress(1.0)
            self._status_text.success(f"{self.description} complete")
        else:
            self._status_text.error(f"{self.description} failed")

    def step(self, message: str | None = None) -> None:
        """Advance to the next step."""
        self.current_step += 1
        self._update_display(message)

    def _update_display(self, message: str | None = None) -> None:
        """Update the progress bar and status text."""
        progress = self.current_step / self.total_steps
        self._progress_bar.progress(progress)

        if message:
            self._status_text.text(f"{self.description}: {message}")
        else:
            self._status_text.text(
                f"{self.description}: Step {self.current_step}/{self.total_steps}"
            )
