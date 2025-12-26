"""Project management commands for the CLI."""

from pathlib import Path

import click

from ytdl_app.project import ProjectManager


@click.command("project-new")
@click.argument("name")
@click.option(
    "-o", "--output", type=click.Path(path_type=Path), help="Project file path."
)
@click.option(
    "-s", "--source", multiple=True, type=click.Path(exists=True, path_type=Path)
)
def project_new(name: str, output: Path | None, source: tuple[Path, ...]):
    """Create a new project file."""
    manager = ProjectManager()
    project = manager.new_project(name, list(source) if source else None)

    if output:
        saved_path = manager.save(output)
        click.echo(f"Created project: {saved_path}")
    else:
        click.echo(f"Created project '{name}' with {len(source)} source files")


@click.command("project-info")
@click.argument("project_file", type=click.Path(exists=True, path_type=Path))
def project_info(project_file: Path):
    """Display information about a project file."""
    manager = ProjectManager()
    project = manager.load(project_file)

    click.echo(f"Name: {project.name}")
    click.echo(f"Version: {project.version}")
    click.echo(f"Created: {project.created_at}")
    click.echo(f"Modified: {project.modified_at}")
    click.echo(f"Source files: {len(project.source_files)}")
    click.echo(f"Operations: {len(project.operations)}")

    if project.source_files:
        click.echo("\nSource files:")
        for f in project.source_files[:10]:
            click.echo(f"  - {f}")
        if len(project.source_files) > 10:
            click.echo(f"  ... and {len(project.source_files) - 10} more")


@click.command("project-list")
@click.argument("directory", type=click.Path(exists=True, path_type=Path), default=".")
def project_list(directory: Path):
    """List project files in a directory."""
    projects = ProjectManager.list_projects(directory)

    if not projects:
        click.echo("No project files found.")
        return

    click.echo(f"Found {len(projects)} project(s):")
    for p in projects:
        click.echo(f"  {p.name}")
