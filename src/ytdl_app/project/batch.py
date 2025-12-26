"""Batch processing for applying operations to multiple files."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

from .config import ProjectConfig


class JobStatus(Enum):
    """Status of a batch job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """A single job in a batch process."""

    input_file: Path
    output_file: Path
    status: JobStatus = JobStatus.PENDING
    error: str | None = None
    progress: float = 0.0


@dataclass
class BatchProcessor:
    """Process multiple files with consistent settings."""

    project: ProjectConfig
    jobs: list[BatchJob] = field(default_factory=list)
    _on_progress: Callable[[BatchJob], None] | None = None

    def add_files(
        self, input_files: list[Path], output_dir: Path, suffix: str = ""
    ) -> None:
        """
        Add files to the batch queue.

        Args:
            input_files: List of input files to process.
            output_dir: Directory for output files.
            suffix: Suffix to add to output filenames.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for input_file in input_files:
            stem = input_file.stem + suffix
            output_file = output_dir / f"{stem}{input_file.suffix}"
            self.jobs.append(BatchJob(input_file=input_file, output_file=output_file))

    def set_progress_callback(self, callback: Callable[[BatchJob], None]) -> None:
        """Set callback for progress updates."""
        self._on_progress = callback

    def process(self, processor: Callable[[Path, Path, ProjectConfig], None]) -> dict:
        """
        Process all jobs using the provided processor function.

        Args:
            processor: Function that takes (input_path, output_path, config).

        Returns:
            Summary dict with counts of completed/failed jobs.
        """
        completed = 0
        failed = 0

        for job in self.jobs:
            if job.status == JobStatus.CANCELLED:
                continue

            job.status = JobStatus.RUNNING
            if self._on_progress:
                self._on_progress(job)

            try:
                processor(job.input_file, job.output_file, self.project)
                job.status = JobStatus.COMPLETED
                job.progress = 100.0
                completed += 1
            except Exception as e:
                job.status = JobStatus.FAILED
                job.error = str(e)
                failed += 1

            if self._on_progress:
                self._on_progress(job)

        return {"completed": completed, "failed": failed, "total": len(self.jobs)}

    def cancel_all(self) -> None:
        """Cancel all pending jobs."""
        for job in self.jobs:
            if job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED

    def get_pending(self) -> list[BatchJob]:
        """Get all pending jobs."""
        return [j for j in self.jobs if j.status == JobStatus.PENDING]

    def get_completed(self) -> list[BatchJob]:
        """Get all completed jobs."""
        return [j for j in self.jobs if j.status == JobStatus.COMPLETED]

    def get_failed(self) -> list[BatchJob]:
        """Get all failed jobs."""
        return [j for j in self.jobs if j.status == JobStatus.FAILED]

    def clear(self) -> None:
        """Clear all jobs."""
        self.jobs.clear()
