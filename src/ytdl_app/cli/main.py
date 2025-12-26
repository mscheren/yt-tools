"""CLI entry point and command group registration."""

import click

from .audio_cmd import audio_info, effects, normalize_audio, trim_audio
from .download_cmd import info, playlist, video
from .video_cmd import concat, overlay, trim, video_info


@click.group()
@click.version_option(package_name="ytdl-app")
def cli():
    """YouTube downloader and media editor."""
    pass


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


if __name__ == "__main__":
    cli()
