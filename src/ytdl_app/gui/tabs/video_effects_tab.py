"""Video effects sub-tab for color grading and filters."""

from pathlib import Path

import streamlit as st

from ytdl_app.gui.components import render_file_selector
from ytdl_app.video import ColorGrading, VideoEditor


def _render_color_grading_section(source_dir: Path):
    """Render the color grading section."""
    st.subheader("Color Grading")

    selected_file = render_file_selector(
        "Select video",
        key="grading_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        st.write("**Adjust color parameters:**")

        col1, col2 = st.columns(2)
        with col1:
            brightness = st.slider(
                "Brightness",
                min_value=-1.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                key="grading_brightness",
            )
            contrast = st.slider(
                "Contrast",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.05,
                key="grading_contrast",
            )

        with col2:
            saturation = st.slider(
                "Saturation",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.05,
                key="grading_saturation",
            )
            gamma = st.slider(
                "Gamma",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.05,
                key="grading_gamma",
            )

        output_name = st.text_input(
            "Output filename", value="color_graded.mp4", key="grading_output"
        )

        if st.button("Apply Color Grading", key="grading_btn"):
            grading = ColorGrading(
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                gamma=gamma,
            )
            output_path = source_dir / output_name
            try:
                with st.spinner("Applying color grading..."):
                    with VideoEditor(selected_file) as editor:
                        editor.color_grade(grading).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Color grading failed: {e}")


def _render_filters_section(source_dir: Path):
    """Render the filters section."""
    st.subheader("Video Filters")

    selected_file = render_file_selector(
        "Select video",
        key="filter_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        filter_type = st.selectbox(
            "Filter type",
            ["Grayscale", "Sepia", "Blur"],
            key="filter_select",
        )

        if filter_type == "Blur":
            blur_radius = st.slider(
                "Blur radius", min_value=1, max_value=20, value=5, key="blur_radius"
            )

        output_name = st.text_input(
            "Output filename", value="filtered_video.mp4", key="filter_output"
        )

        if st.button("Apply Filter", key="filter_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Applying filter..."):
                    with VideoEditor(selected_file) as editor:
                        if filter_type == "Grayscale":
                            editor.apply_filter("grayscale")
                        elif filter_type == "Sepia":
                            editor.apply_filter("sepia")
                        else:
                            editor.apply_filter("blur", radius=blur_radius)
                        editor.export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Filter failed: {e}")


def _render_reverse_section(source_dir: Path):
    """Render the reverse video section."""
    st.subheader("Reverse Video")

    selected_file = render_file_selector(
        "Select video",
        key="reverse_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        output_name = st.text_input(
            "Output filename", value="reversed_video.mp4", key="reverse_output"
        )

        if st.button("Reverse Video", key="reverse_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Reversing video..."):
                    with VideoEditor(selected_file) as editor:
                        editor.reverse().export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Reverse failed: {e}")


def _render_loop_section(source_dir: Path):
    """Render the loop video section."""
    st.subheader("Loop Video")

    selected_file = render_file_selector(
        "Select video",
        key="loop_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        loop_count = st.number_input(
            "Number of loops", min_value=2, max_value=10, value=2, key="loop_count"
        )

        output_name = st.text_input(
            "Output filename", value="looped_video.mp4", key="loop_output"
        )

        if st.button("Loop Video", key="loop_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Creating looped video..."):
                    with VideoEditor(selected_file) as editor:
                        editor.loop(loop_count).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Loop failed: {e}")


def render_video_effects(source_dir: Path):
    """Render all video effects sections."""
    tab1, tab2, tab3, tab4 = st.tabs(["Color Grading", "Filters", "Reverse", "Loop"])

    with tab1:
        _render_color_grading_section(source_dir)
    with tab2:
        _render_filters_section(source_dir)
    with tab3:
        _render_reverse_section(source_dir)
    with tab4:
        _render_loop_section(source_dir)
