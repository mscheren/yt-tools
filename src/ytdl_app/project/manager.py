"""Project file management (save/load)."""

import json
from pathlib import Path

import yaml

from .config import ProjectConfig


class ProjectManager:
    """Handles saving and loading project files."""

    SUPPORTED_FORMATS = {".json", ".yaml", ".yml"}

    def __init__(self, project: ProjectConfig | None = None):
        self.project = project or ProjectConfig(name="Untitled")

    def save(self, path: Path) -> Path:
        """
        Save project to file.

        Args:
            path: Output file path (.json or .yaml/.yml).

        Returns:
            Path to saved file.
        """
        path = Path(path)
        suffix = path.suffix.lower()

        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}. Use .json or .yaml")

        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.project.to_dict()

        if suffix == ".json":
            path.write_text(json.dumps(data, indent=2))
        else:
            path.write_text(yaml.dump(data, default_flow_style=False))

        return path

    def load(self, path: Path) -> ProjectConfig:
        """
        Load project from file.

        Args:
            path: Path to project file.

        Returns:
            Loaded ProjectConfig.
        """
        path = Path(path)
        suffix = path.suffix.lower()

        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")

        content = path.read_text()

        if suffix == ".json":
            data = json.loads(content)
        else:
            data = yaml.safe_load(content)

        self.project = ProjectConfig.from_dict(data)
        return self.project

    def new_project(
        self, name: str, source_files: list[Path] | None = None
    ) -> ProjectConfig:
        """Create a new project."""
        self.project = ProjectConfig(
            name=name,
            source_files=source_files or [],
        )
        return self.project

    @staticmethod
    def list_projects(directory: Path) -> list[Path]:
        """List all project files in a directory."""
        projects = []
        for ext in ProjectManager.SUPPORTED_FORMATS:
            projects.extend(directory.glob(f"*{ext}"))
        return sorted(projects)
