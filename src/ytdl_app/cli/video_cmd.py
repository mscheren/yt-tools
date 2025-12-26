"""Video editing commands for the CLI."""

from pathlib import Path

import click

from ytdl_app.video import TextOverlayConfig, VideoEditor, concatenate_videos, get_video_info


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option("--start", type=float, required=True, help="Start time in seconds.")
@click.option("--end", type=float, required=True, help="End time in seconds.")
def trim(input_file: Path, output_file: Path, start: float, end: float):
    """Trim a video to a specific time range."""
    click.echo(f"Trimming {input_file.name} from {start}s to {end}s...")

    try:
        with VideoEditor(input_file) as editor:
            editor.trim(start, end).export(output_file)
        click.echo(f"Saved to {output_file}")
    except Exception as e:
        raise click.ClickException(f"Trim failed: {e}") from e


@click.command()
@click.argument("output_file", type=click.Path(path_type=Path))
@click.argument("input_files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--transition", is_flag=True, help="Use compose transition between clips.")
def concat(output_file: Path, input_files: tuple[Path, ...], transition: bool):
    """Concatenate multiple videos into one."""
    if len(input_files) < 2:
        raise click.ClickException("At least two input files required.")

    click.echo(f"Concatenating {len(input_files)} videos...")

    try:
        concatenate_videos(
            list(input_files),
            output_file,
            transition="compose" if transition else None,
        )
        click.echo(f"Saved to {output_file}")
    except Exception as e:
        raise click.ClickException(f"Concatenation failed: {e}") from e


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option("--text", required=True, help="Text to overlay.")
@click.option("--font-size", default=50, help="Font size for the text.")
@click.option("--color", default="white", help="Text color.")
@click.option("--position", default="center", help="Position: center, top, bottom.")
def overlay(
    input_file: Path,
    output_file: Path,
    text: str,
    font_size: int,
    color: str,
    position: str,
):
    """Add a text overlay to a video."""
    click.echo(f"Adding text overlay to {input_file.name}...")

    config = TextOverlayConfig(
        text=text,
        font_size=font_size,
        color=color,
        position=position,
    )

    try:
        with VideoEditor(input_file) as editor:
            editor.add_text_overlay(config).export(output_file)
        click.echo(f"Saved to {output_file}")
    except Exception as e:
        raise click.ClickException(f"Overlay failed: {e}") from e


@click.command("video-info")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def video_info(input_file: Path):
    """Display information about a video file."""
    try:
        meta = get_video_info(input_file)
        click.echo(f"File: {meta.path.name}")
        click.echo(f"Duration: {meta.format_duration()}")
        click.echo(f"Resolution: {meta.width}x{meta.height}")
        click.echo(f"FPS: {meta.fps:.2f}")
        click.echo(f"Has Audio: {'Yes' if meta.has_audio else 'No'}")
    except Exception as e:
        raise click.ClickException(f"Failed to read video: {e}") from e
