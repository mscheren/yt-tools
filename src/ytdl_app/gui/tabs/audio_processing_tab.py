"""Audio processing sub-tab for noise removal and extraction."""

from pathlib import Path

import streamlit as st

from ytdl_app.audio import AudioEditor
from ytdl_app.audio.processing import extract_audio_from_video
from ytdl_app.gui.components import render_file_selector


def _render_noise_removal_section(source_dir: Path):
    """Render the noise removal section."""
    st.subheader("Noise Removal")

    selected_file = render_file_selector(
        "Select audio file",
        key="noise_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file:
        method = st.radio(
            "Noise removal method",
            ["Noise Gate", "Spectral"],
            key="noise_method",
            horizontal=True,
            help="Noise gate is faster; Spectral is more thorough",
        )

        if method == "Noise Gate":
            col1, col2 = st.columns(2)
            with col1:
                threshold = st.slider(
                    "Threshold (dB)",
                    min_value=-60.0,
                    max_value=-20.0,
                    value=-40.0,
                    key="gate_threshold",
                )
            with col2:
                ratio = st.slider(
                    "Ratio",
                    min_value=1.0,
                    max_value=20.0,
                    value=10.0,
                    key="gate_ratio",
                )
        else:
            reduction = st.slider(
                "Reduction strength",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                key="spectral_reduction",
            )

        output_name = st.text_input(
            "Output filename", value="denoised_audio.wav", key="noise_output"
        )

        if st.button("Remove Noise", key="noise_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Removing noise..."):
                    with AudioEditor(selected_file) as editor:
                        if method == "Noise Gate":
                            editor.remove_noise(
                                method="gate", threshold=threshold, ratio=ratio
                            )
                        else:
                            editor.remove_noise(method="spectral", reduction=reduction)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Noise removal failed: {e}")


def _render_extract_section(source_dir: Path):
    """Render the audio extraction from video section."""
    st.subheader("Extract Audio from Video")

    selected_file = render_file_selector(
        "Select video file",
        key="extract_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        output_format = st.selectbox(
            "Output format",
            ["WAV", "MP3", "FLAC"],
            key="extract_format",
        )

        ext = output_format.lower()
        default_name = f"{selected_file.stem}_audio.{ext}"
        output_name = st.text_input(
            "Output filename", value=default_name, key="extract_output"
        )

        if st.button("Extract Audio", key="extract_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Extracting audio..."):
                    extract_audio_from_video(selected_file, output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Extraction failed: {e}")


def _render_normalize_section(source_dir: Path):
    """Render the audio normalization section."""
    st.subheader("Normalize Audio")

    selected_file = render_file_selector(
        "Select audio file",
        key="normalize_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file:
        target_db = st.slider(
            "Target level (dB)",
            min_value=-20.0,
            max_value=0.0,
            value=-3.0,
            key="normalize_target",
            help="Target peak level in dB",
        )

        output_name = st.text_input(
            "Output filename", value="normalized_audio.wav", key="normalize_output"
        )

        if st.button("Normalize Audio", key="normalize_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Normalizing audio..."):
                    with AudioEditor(selected_file) as editor:
                        editor.normalize(target_db=target_db)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Normalization failed: {e}")


def _render_volume_section(source_dir: Path):
    """Render the volume adjustment section."""
    st.subheader("Adjust Volume")

    selected_file = render_file_selector(
        "Select audio file",
        key="volume_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file:
        volume_db = st.slider(
            "Volume adjustment (dB)",
            min_value=-20.0,
            max_value=20.0,
            value=0.0,
            key="volume_db",
            help="Positive = louder, Negative = quieter",
        )

        output_name = st.text_input(
            "Output filename", value="volume_adjusted.wav", key="volume_output"
        )

        if st.button("Adjust Volume", key="volume_btn", disabled=volume_db == 0):
            output_path = source_dir / output_name
            try:
                with st.spinner("Adjusting volume..."):
                    with AudioEditor(selected_file) as editor:
                        editor.adjust_volume(volume_db)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Volume adjustment failed: {e}")


def render_audio_processing(source_dir: Path):
    """Render all audio processing sections."""
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Noise Removal", "Extract from Video", "Normalize", "Volume"]
    )

    with tab1:
        _render_noise_removal_section(source_dir)
    with tab2:
        _render_extract_section(source_dir)
    with tab3:
        _render_normalize_section(source_dir)
    with tab4:
        _render_volume_section(source_dir)
