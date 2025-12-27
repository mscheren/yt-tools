"""CLI entry point and command group registration."""

import subprocess
import sys
from pathlib import Path

import click

from .audio_cmd import audio_info, effects, normalize_audio, trim_audio
from .download_cmd import info, playlist, video
from .project_cmd import project_info, project_list, project_new
from .video_cmd import concat, overlay, trim, video_info


@click.group()
@click.version_option(package_name="ytdl-app")
def cli():
    """YouTube downloader and media editor."""
    pass


@click.command()
@click.option("--port", "-p", default=8501, help="Port to run on")
def gui(port: int):
    """Launch the Streamlit web GUI."""
    app_path = Path(__file__).parent.parent / "gui" / "app.py"

    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)]

    click.echo(f"Starting GUI on http://localhost:{port}")
    subprocess.run(cmd)


# Download commands
cli.add_command(video)
cli.add_command(playlist)
cli.add_command(info)

# Video editing commands
cli.add_command(trim)
cli.add_command(concat)
cli.add_command(overlay)
cli.add_command(video_info)

# Audio editing commands
cli.add_command(trim_audio)
cli.add_command(effects)
cli.add_command(audio_info)
cli.add_command(normalize_audio)

# Project management commands
cli.add_command(project_new)
cli.add_command(project_info)
cli.add_command(project_list)

# GUI
cli.add_command(gui)


if __name__ == "__main__":
    cli()
