"""Download commands for the CLI."""

from pathlib import Path

import click

from ytdl_app.download import DownloadOptions, Downloader
from ytdl_app.models import OutputFormat


def _create_progress_callback() -> callable:
    """Create a progress callback for download status."""

    def progress_hook(d: dict) -> None:
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "N/A")
            speed = d.get("_speed_str", "N/A")
            click.echo(f"\rDownloading: {percent} at {speed}", nl=False)
        elif d["status"] == "finished":
            click.echo("\nDownload complete, processing...")

    return progress_hook


@click.command()
@click.argument("url")
@click.option(
    "-o", "--output-dir",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Output directory for downloaded files.",
)
@click.option(
    "-f", "--format", "output_format",
    type=click.Choice(["mp4", "mp3"], case_sensitive=False),
    default="mp4",
    help="Output format: mp4 for video, mp3 for audio only.",
)
@click.option(
    "-c", "--cookies",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to cookies.txt file for authenticated downloads.",
)
def video(url: str, output_dir: Path, output_format: str, cookies: Path | None):
    """Download a single video from URL."""
    options = DownloadOptions(
        output_dir=output_dir,
        output_format=OutputFormat(output_format.lower()),
        cookies_file=cookies,
    )

    downloader = Downloader(options=options, progress_callback=_create_progress_callback())
    click.echo(f"Downloading video as {output_format.upper()}...")

    try:
        info = downloader.download(url)
        click.echo(f"Successfully downloaded: {info.get('title', 'Unknown')}")
    except Exception as e:
        raise click.ClickException(f"Download failed: {e}") from e


@click.command()
@click.argument("url")
@click.option(
    "-o", "--output-dir",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Output directory for downloaded files.",
)
@click.option(
    "-f", "--format", "output_format",
    type=click.Choice(["mp4", "mp3"], case_sensitive=False),
    default="mp4",
    help="Output format: mp4 for video, mp3 for audio only.",
)
@click.option(
    "-c", "--cookies",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to cookies.txt file for authenticated downloads.",
)
def playlist(url: str, output_dir: Path, output_format: str, cookies: Path | None):
    """Download an entire playlist from URL."""
    options = DownloadOptions(
        output_dir=output_dir,
        output_format=OutputFormat(output_format.lower()),
        cookies_file=cookies,
    )

    downloader = Downloader(options=options, progress_callback=_create_progress_callback())
    click.echo(f"Downloading playlist as {output_format.upper()}...")

    try:
        info = downloader.download_playlist(url)
        entries = info.get("entries", [])
        click.echo(f"Successfully downloaded: {info.get('title', 'Unknown')} ({len(entries)} items)")
    except Exception as e:
        raise click.ClickException(f"Download failed: {e}") from e


@click.command()
@click.argument("url")
def info(url: str):
    """Fetch and display video or playlist metadata without downloading."""
    downloader = Downloader()

    try:
        metadata = downloader.get_info(url)
        click.echo(f"Title: {metadata.get('title', 'N/A')}")

        if "entries" in metadata:
            click.echo(f"Type: Playlist ({len(metadata['entries'])} videos)")
            for i, entry in enumerate(metadata["entries"], 1):
                click.echo(f"  {i}. {entry.get('title', 'Unknown')}")
        else:
            click.echo("Type: Single Video")
            duration = metadata.get("duration", 0)
            if duration:
                minutes, seconds = divmod(duration, 60)
                click.echo(f"Duration: {int(minutes)}:{int(seconds):02d}")
            click.echo(f"Channel: {metadata.get('channel', 'N/A')}")
    except Exception as e:
        raise click.ClickException(f"Failed to fetch info: {e}") from e
