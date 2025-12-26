"""Audio editing tab implementation."""

from pathlib import Path

import streamlit as st

from ytdl_app.audio import AudioEditor, EffectChain, EffectPreset
from ytdl_app.audio.editor import get_audio_info
from ytdl_app.gui.components import render_directory_selector, render_file_selector


def _render_effects_section(source_dir: Path):
    """Render the audio effects section."""
    st.subheader("Apply Effects")

    selected_file = render_file_selector(
        "Select audio file",
        key="effects_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file:
        try:
            meta = get_audio_info(selected_file)
            st.info(f"Duration: {meta.format_duration()} | {meta.sample_rate}Hz | {meta.channels}ch")
        except Exception:
            pass

        st.write("**Preset or Custom Effects**")

        use_preset = st.checkbox("Use preset", value=True, key="use_preset")

        if use_preset:
            preset_name = st.selectbox(
                "Select preset",
                [p.value for p in EffectPreset],
                format_func=lambda x: x.replace("_", " ").title(),
                key="preset_select",
            )
            chain = EffectChain.from_preset(EffectPreset(preset_name))
        else:
            col1, col2 = st.columns(2)

            with col1:
                gain_db = st.slider("Gain (dB)", -20.0, 20.0, 0.0, key="gain_slider")
                highpass = st.slider("Highpass (Hz)", 0, 500, 0, key="highpass_slider")
                lowpass = st.slider("Lowpass (Hz)", 1000, 20000, 20000, key="lowpass_slider")

            with col2:
                use_compressor = st.checkbox("Compressor", key="use_compressor")
                use_reverb = st.checkbox("Reverb", key="use_reverb")
                use_limiter = st.checkbox("Limiter", key="use_limiter")

            chain = EffectChain(
                gain_db=gain_db if gain_db != 0 else None,
                highpass_hz=highpass if highpass > 0 else None,
                lowpass_hz=lowpass if lowpass < 20000 else None,
                compressor=use_compressor,
                reverb=use_reverb,
                limiter=use_limiter,
            )

        normalize = st.checkbox("Normalize output", value=True, key="normalize_output")
        output_name = st.text_input("Output filename", value="processed_audio.wav", key="fx_output")

        if st.button("Apply Effects", key="apply_effects_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Processing audio..."):
                    with AudioEditor(selected_file) as editor:
                        editor.apply_effects(chain)
                        if normalize:
                            editor.normalize()
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Processing failed: {e}")


def _render_trim_section(source_dir: Path):
    """Render the audio trimming section."""
    st.subheader("Trim Audio")

    selected_file = render_file_selector(
        "Select audio file",
        key="trim_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file:
        try:
            meta = get_audio_info(selected_file)
            st.info(f"Duration: {meta.format_duration()}")
        except Exception:
            pass

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.number_input("Start time (seconds)", min_value=0.0, key="audio_trim_start")
        with col2:
            end_time = st.number_input("End time (seconds)", min_value=0.0, key="audio_trim_end")

        output_name = st.text_input("Output filename", value="trimmed_audio.wav", key="audio_trim_output")

        if st.button("Trim Audio", key="audio_trim_btn", disabled=end_time <= start_time):
            output_path = source_dir / output_name
            try:
                with st.spinner("Trimming audio..."):
                    with AudioEditor(selected_file) as editor:
                        editor.trim(start_time, end_time).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Trim failed: {e}")


def _render_info_section(source_dir: Path):
    """Render the audio info section."""
    st.subheader("Audio Information")

    selected_file = render_file_selector(
        "Select audio file",
        key="info_audio_select",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        directory=source_dir,
    )

    if selected_file and st.button("Get Info", key="audio_info_btn"):
        try:
            meta = get_audio_info(selected_file)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Duration", meta.format_duration())
                st.metric("Sample Rate", f"{meta.sample_rate} Hz")
            with col2:
                st.metric("Channels", meta.channels)
        except Exception as e:
            st.error(f"Failed to read audio: {e}")


def render_audio_tab():
    """Render the audio editing tab content."""
    st.header("Audio Editing")

    source_dir = render_directory_selector(
        "Working Directory",
        key="audio_source_dir",
        default=Path.cwd(),
        help_text="Directory containing your audio files",
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs(["Effects", "Trim", "Info"])

    with tab1:
        _render_effects_section(source_dir)

    with tab2:
        _render_trim_section(source_dir)

    with tab3:
        _render_info_section(source_dir)
