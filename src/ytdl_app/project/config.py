"""Project configuration dataclasses."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class OperationType(Enum):
    """Types of edit operations."""

    TRIM = "trim"
    SPEED = "speed"
    CROP = "crop"
    RESIZE = "resize"
    ROTATE = "rotate"
    COLOR_GRADE = "color_grade"
    FILTER = "filter"
    OVERLAY = "overlay"
    AUDIO_EFFECT = "audio_effect"
    AUDIO_MIX = "audio_mix"
    CONCATENATE = "concatenate"


@dataclass
class EditOperation:
    """A single edit operation with parameters."""

    operation_type: OperationType
    params: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "type": self.operation_type.value,
            "params": self.params,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EditOperation":
        """Deserialize from dictionary."""
        return cls(
            operation_type=OperationType(data["type"]),
            params=data["params"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class ProjectConfig:
    """Project configuration with all settings and operations."""

    name: str
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    source_files: list[Path] = field(default_factory=list)
    output_dir: Path = field(default_factory=Path.cwd)
    operations: list[EditOperation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_operation(self, op: EditOperation) -> None:
        """Add an operation to the project."""
        self.operations.append(op)
        self.modified_at = datetime.now()

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "source_files": [str(p) for p in self.source_files],
            "output_dir": str(self.output_dir),
            "operations": [op.to_dict() for op in self.operations],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectConfig":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            source_files=[Path(p) for p in data.get("source_files", [])],
            output_dir=Path(data.get("output_dir", ".")),
            operations=[
                EditOperation.from_dict(op) for op in data.get("operations", [])
            ],
            metadata=data.get("metadata", {}),
        )
