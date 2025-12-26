"""Video editing tab implementation."""

from pathlib import Path

import streamlit as st

from ytdl_app.gui.components import render_directory_selector, render_file_selector
from ytdl_app.video import TextOverlayConfig, VideoEditor, get_video_info


def _render_trim_section(source_dir: Path):
    """Render the video trimming section."""
    st.subheader("Trim Video")

    selected_file = render_file_selector(
        "Select video to trim",
        key="trim_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        try:
            meta = get_video_info(selected_file)
            st.info(f"Duration: {meta.format_duration()} | Resolution: {meta.width}x{meta.height}")
        except Exception:
            pass

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.number_input("Start time (seconds)", min_value=0.0, key="trim_start")
        with col2:
            end_time = st.number_input("End time (seconds)", min_value=0.0, key="trim_end")

        output_name = st.text_input("Output filename", value="trimmed_video.mp4", key="trim_output")

        if st.button("Trim Video", key="trim_btn", disabled=end_time <= start_time):
            output_path = source_dir / output_name
            try:
                with st.spinner("Trimming video..."):
                    with VideoEditor(selected_file) as editor:
                        editor.trim(start_time, end_time).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Trim failed: {e}")


def _render_overlay_section(source_dir: Path):
    """Render the text overlay section."""
    st.subheader("Add Text Overlay")

    selected_file = render_file_selector(
        "Select video",
        key="overlay_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        overlay_text = st.text_input("Overlay text", key="overlay_text")

        col1, col2, col3 = st.columns(3)
        with col1:
            font_size = st.slider("Font size", 20, 100, 50, key="overlay_font_size")
        with col2:
            color = st.selectbox(
                "Color",
                ["white", "black", "red", "blue", "green", "yellow"],
                key="overlay_color",
            )
        with col3:
            position = st.selectbox(
                "Position",
                ["center", "top", "bottom"],
                key="overlay_position",
            )

        output_name = st.text_input(
            "Output filename", value="video_with_overlay.mp4", key="overlay_output"
        )

        if st.button("Add Overlay", key="overlay_btn", disabled=not overlay_text):
            config = TextOverlayConfig(
                text=overlay_text,
                font_size=font_size,
                color=color,
                position=position,
            )
            output_path = source_dir / output_name

            try:
                with st.spinner("Adding overlay..."):
                    with VideoEditor(selected_file) as editor:
                        editor.add_text_overlay(config).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Overlay failed: {e}")


def _render_info_section(source_dir: Path):
    """Render the video info section."""
    st.subheader("Video Information")

    selected_file = render_file_selector(
        "Select video",
        key="info_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file and st.button("Get Info", key="video_info_btn"):
        try:
            meta = get_video_info(selected_file)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Duration", meta.format_duration())
                st.metric("Resolution", f"{meta.width}x{meta.height}")
            with col2:
                st.metric("FPS", f"{meta.fps:.2f}")
                st.metric("Has Audio", "Yes" if meta.has_audio else "No")
        except Exception as e:
            st.error(f"Failed to read video: {e}")


def render_video_tab():
    """Render the video editing tab content."""
    st.header("Video Editing")

    source_dir = render_directory_selector(
        "Working Directory",
        key="video_source_dir",
        default=Path.cwd(),
        help_text="Directory containing your video files",
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs(["Trim", "Text Overlay", "Info"])

    with tab1:
        _render_trim_section(source_dir)

    with tab2:
        _render_overlay_section(source_dir)

    with tab3:
        _render_info_section(source_dir)
