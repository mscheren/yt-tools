"""Tests for project manager."""

from pathlib import Path

import pytest

from ytdl_app.project import ProjectConfig, ProjectManager


class TestProjectManager:
    """Tests for ProjectManager class."""

    def test_new_project(self):
        """New project should create empty config."""
        manager = ProjectManager()
        project = manager.new_project("Test Project")

        assert project.name == "Test Project"
        assert len(project.operations) == 0

    def test_save_load_json(self, temp_dir):
        """Project should save and load from JSON."""
        manager = ProjectManager()
        project = manager.new_project("Test", [Path("video.mp4")])

        save_path = temp_dir / "project.json"
        manager.save(save_path)

        # Load in new manager
        manager2 = ProjectManager()
        loaded = manager2.load(save_path)

        assert loaded.name == "Test"
        assert len(loaded.source_files) == 1

    def test_save_load_yaml(self, temp_dir):
        """Project should save and load from YAML."""
        manager = ProjectManager()
        manager.new_project("Test YAML")

        save_path = temp_dir / "project.yaml"
        manager.save(save_path)

        manager2 = ProjectManager()
        loaded = manager2.load(save_path)

        assert loaded.name == "Test YAML"

    def test_unsupported_format(self, temp_dir):
        """Unsupported format should raise error."""
        manager = ProjectManager()
        manager.new_project("Test")

        with pytest.raises(ValueError):
            manager.save(temp_dir / "project.txt")

    def test_list_projects(self, temp_dir):
        """List projects should find project files."""
        manager = ProjectManager()
        manager.new_project("Project 1")
        manager.save(temp_dir / "p1.json")

        manager.new_project("Project 2")
        manager.save(temp_dir / "p2.yaml")

        projects = ProjectManager.list_projects(temp_dir)
        assert len(projects) == 2


class TestProjectConfig:
    """Tests for ProjectConfig dataclass."""

    def test_add_operation(self):
        """Adding operation should update modified_at."""
        from ytdl_app.project import EditOperation, OperationType

        config = ProjectConfig(name="Test")
        original_time = config.modified_at

        op = EditOperation(OperationType.TRIM, {"start": 0, "end": 10})
        config.add_operation(op)

        assert len(config.operations) == 1
        assert config.modified_at >= original_time

    def test_serialization_roundtrip(self):
        """Config should survive serialization roundtrip."""
        config = ProjectConfig(
            name="Test",
            source_files=[Path("video.mp4")],
            metadata={"quality": "high"},
        )

        data = config.to_dict()
        restored = ProjectConfig.from_dict(data)

        assert restored.name == config.name
        assert len(restored.source_files) == 1
        assert restored.metadata["quality"] == "high"
