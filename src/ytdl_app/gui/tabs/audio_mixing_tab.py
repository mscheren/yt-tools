"""Audio mixing sub-tab for overlay, ducking, and crossfade."""

from pathlib import Path

import streamlit as st

from ytdl_app.audio import AudioEditor
from ytdl_app.audio.editor import get_audio_info
from ytdl_app.gui.components import render_file_selector


def _render_overlay_section(source_dir: Path):
    """Render the audio overlay section."""
    st.subheader("Audio Overlay")
    st.write("Mix a secondary audio track over the base audio.")

    base_file = render_file_selector(
        "Base audio file",
        key="overlay_base_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    overlay_file = render_file_selector(
        "Overlay audio file",
        key="overlay_track_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if base_file and overlay_file:
        col1, col2 = st.columns(2)
        with col1:
            position = st.number_input(
                "Start position (seconds)",
                min_value=0.0,
                value=0.0,
                key="overlay_position",
                help="Where to start the overlay in the base audio",
            )
        with col2:
            volume = st.slider(
                "Overlay volume",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                key="overlay_volume",
            )

        output_name = st.text_input(
            "Output filename", value="mixed_audio.wav", key="overlay_output"
        )

        if st.button("Mix Audio", key="overlay_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Mixing audio..."):
                    with AudioEditor(base_file) as editor:
                        editor.overlay(overlay_file, position=position, volume=volume)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Overlay failed: {e}")


def _render_ducking_section(source_dir: Path):
    """Render the audio ducking section."""
    st.subheader("Audio Ducking")
    st.write("Lower background music when speech is detected.")

    music_file = render_file_selector(
        "Background music",
        key="duck_music_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    speech_file = render_file_selector(
        "Speech/voiceover",
        key="duck_speech_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if music_file and speech_file:
        col1, col2 = st.columns(2)
        with col1:
            duck_level = st.slider(
                "Duck level",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                key="duck_level",
                help="Volume level for music during speech (0.3 = 30%)",
            )
        with col2:
            threshold = st.slider(
                "Detection threshold",
                min_value=-60.0,
                max_value=-20.0,
                value=-40.0,
                key="duck_threshold",
                help="dB threshold for speech detection",
            )

        output_name = st.text_input(
            "Output filename", value="ducked_audio.wav", key="duck_output"
        )

        if st.button("Apply Ducking", key="duck_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Applying ducking..."):
                    with AudioEditor(music_file) as editor:
                        editor.duck(
                            speech_file, duck_level=duck_level, threshold=threshold
                        )
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Ducking failed: {e}")


def _render_crossfade_section(source_dir: Path):
    """Render the crossfade section."""
    st.subheader("Crossfade")
    st.write("Smoothly transition between two audio files.")

    audio1_file = render_file_selector(
        "First audio file",
        key="xfade_audio1_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    audio2_file = render_file_selector(
        "Second audio file",
        key="xfade_audio2_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if audio1_file and audio2_file:
        try:
            meta1 = get_audio_info(audio1_file)
            meta2 = get_audio_info(audio2_file)
            max_fade = min(meta1.duration, meta2.duration) / 2
        except Exception:
            max_fade = 5.0

        fade_duration = st.slider(
            "Crossfade duration (seconds)",
            min_value=0.1,
            max_value=float(max_fade),
            value=min(1.0, float(max_fade)),
            key="xfade_duration",
        )

        output_name = st.text_input(
            "Output filename", value="crossfaded_audio.wav", key="xfade_output"
        )

        if st.button("Apply Crossfade", key="xfade_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Applying crossfade..."):
                    with AudioEditor(audio1_file) as editor:
                        editor.crossfade(audio2_file, fade_duration)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Crossfade failed: {e}")


def _render_fades_section(source_dir: Path):
    """Render the fade in/out section."""
    st.subheader("Fade In/Out")

    selected_file = render_file_selector(
        "Select audio file",
        key="fade_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file:
        col1, col2 = st.columns(2)
        with col1:
            fade_in = st.number_input(
                "Fade in duration (seconds)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                key="fade_in_dur",
            )
        with col2:
            fade_out = st.number_input(
                "Fade out duration (seconds)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                key="fade_out_dur",
            )

        output_name = st.text_input(
            "Output filename", value="faded_audio.wav", key="fade_output"
        )

        if st.button("Apply Fades", key="fade_btn", disabled=fade_in == 0 and fade_out == 0):
            output_path = source_dir / output_name
            try:
                with st.spinner("Applying fades..."):
                    with AudioEditor(selected_file) as editor:
                        if fade_in > 0:
                            editor.fade_in(fade_in)
                        if fade_out > 0:
                            editor.fade_out(fade_out)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Fades failed: {e}")


def render_audio_mixing(source_dir: Path):
    """Render all audio mixing sections."""
    tab1, tab2, tab3, tab4 = st.tabs(["Overlay", "Ducking", "Crossfade", "Fades"])

    with tab1:
        _render_overlay_section(source_dir)
    with tab2:
        _render_ducking_section(source_dir)
    with tab3:
        _render_crossfade_section(source_dir)
    with tab4:
        _render_fades_section(source_dir)
