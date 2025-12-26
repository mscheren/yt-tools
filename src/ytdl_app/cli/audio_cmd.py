"""Audio editing commands for the CLI."""

from pathlib import Path

import click

from ytdl_app.audio import AudioEditor, EffectChain, EffectPreset
from ytdl_app.audio.editor import get_audio_info


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option("--start", type=float, required=True, help="Start time in seconds.")
@click.option("--end", type=float, required=True, help="End time in seconds.")
def trim_audio(input_file: Path, output_file: Path, start: float, end: float):
    """Trim an audio file to a specific time range."""
    click.echo(f"Trimming {input_file.name} from {start}s to {end}s...")

    try:
        with AudioEditor(input_file) as editor:
            editor.trim(start, end).export(output_file)
        click.echo(f"Saved to {output_file}")
    except Exception as e:
        raise click.ClickException(f"Trim failed: {e}") from e


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--preset",
    type=click.Choice([p.value for p in EffectPreset]),
    help="Apply a preset.",
)
@click.option("--gain", type=float, help="Gain adjustment in dB.")
@click.option("--highpass", type=float, help="Highpass filter cutoff in Hz.")
@click.option("--lowpass", type=float, help="Lowpass filter cutoff in Hz.")
@click.option("--compress", is_flag=True, help="Apply compression.")
@click.option("--reverb", is_flag=True, help="Apply reverb.")
@click.option("--normalize", is_flag=True, help="Normalize audio levels.")
def effects(
    input_file: Path,
    output_file: Path,
    preset: str | None,
    gain: float | None,
    highpass: float | None,
    lowpass: float | None,
    compress: bool,
    reverb: bool,
    normalize: bool,
):
    """Apply audio effects to a file."""
    click.echo(f"Processing {input_file.name}...")

    try:
        if preset:
            chain = EffectChain.from_preset(EffectPreset(preset))
        else:
            chain = EffectChain(
                gain_db=gain,
                highpass_hz=highpass,
                lowpass_hz=lowpass,
                compressor=compress,
                reverb=reverb,
            )

        with AudioEditor(input_file) as editor:
            editor.apply_effects(chain)
            if normalize:
                editor.normalize()
            editor.export(output_file)

        click.echo(f"Saved to {output_file}")
    except Exception as e:
        raise click.ClickException(f"Processing failed: {e}") from e


@click.command("audio-info")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def audio_info(input_file: Path):
    """Display information about an audio file."""
    try:
        meta = get_audio_info(input_file)
        click.echo(f"File: {meta.path.name}")
        click.echo(f"Duration: {meta.format_duration()}")
        click.echo(f"Sample Rate: {meta.sample_rate} Hz")
        click.echo(f"Channels: {meta.channels}")
    except Exception as e:
        raise click.ClickException(f"Failed to read audio: {e}") from e


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option("--target-db", type=float, default=-1.0, help="Target peak level in dB.")
def normalize_audio(input_file: Path, output_file: Path, target_db: float):
    """Normalize audio to a target peak level."""
    click.echo(f"Normalizing {input_file.name} to {target_db} dB...")

    try:
        with AudioEditor(input_file) as editor:
            editor.normalize(target_db).export(output_file)
        click.echo(f"Saved to {output_file}")
    except Exception as e:
        raise click.ClickException(f"Normalization failed: {e}") from e
