"""Video transforms sub-tab for speed, crop, resize, rotate."""

from pathlib import Path

import streamlit as st

from ytdl_app.gui.components import render_file_selector
from ytdl_app.video import CropRegion, RotationAngle, VideoEditor, get_video_info


def _render_speed_section(source_dir: Path):
    """Render the speed adjustment section."""
    st.subheader("Adjust Speed")

    selected_file = render_file_selector(
        "Select video",
        key="speed_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        speed_factor = st.slider(
            "Speed factor",
            min_value=0.25,
            max_value=4.0,
            value=1.0,
            step=0.25,
            key="speed_factor",
            help="1.0 = normal, 2.0 = double speed, 0.5 = half speed",
        )

        output_name = st.text_input(
            "Output filename", value="speed_adjusted.mp4", key="speed_output"
        )

        if st.button("Apply Speed Change", key="speed_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Adjusting speed..."):
                    with VideoEditor(selected_file) as editor:
                        editor.speed(speed_factor).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Speed adjustment failed: {e}")


def _render_crop_section(source_dir: Path):
    """Render the crop section."""
    st.subheader("Crop Video")

    selected_file = render_file_selector(
        "Select video",
        key="crop_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        try:
            meta = get_video_info(selected_file)
            st.info(f"Original size: {meta.width}x{meta.height}")
            max_w, max_h = meta.width, meta.height
        except Exception:
            max_w, max_h = 1920, 1080

        col1, col2 = st.columns(2)
        with col1:
            x1 = st.number_input("Left (x1)", min_value=0, max_value=max_w, key="crop_x1")
            y1 = st.number_input("Top (y1)", min_value=0, max_value=max_h, key="crop_y1")
        with col2:
            x2 = st.number_input(
                "Right (x2)", min_value=0, max_value=max_w, value=max_w, key="crop_x2"
            )
            y2 = st.number_input(
                "Bottom (y2)", min_value=0, max_value=max_h, value=max_h, key="crop_y2"
            )

        output_name = st.text_input(
            "Output filename", value="cropped_video.mp4", key="crop_output"
        )

        valid_crop = x2 > x1 and y2 > y1
        if st.button("Crop Video", key="crop_btn", disabled=not valid_crop):
            region = CropRegion(x1=x1, y1=y1, x2=x2, y2=y2)
            output_path = source_dir / output_name
            try:
                with st.spinner("Cropping video..."):
                    with VideoEditor(selected_file) as editor:
                        editor.crop(region).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Crop failed: {e}")


def _render_resize_section(source_dir: Path):
    """Render the resize section."""
    st.subheader("Resize Video")

    selected_file = render_file_selector(
        "Select video",
        key="resize_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        preset = st.selectbox(
            "Resolution preset",
            ["Custom", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"],
            key="resize_preset",
        )

        if preset == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                width = st.number_input("Width", min_value=1, value=1280, key="resize_w")
            with col2:
                height = st.number_input("Height", min_value=1, value=720, key="resize_h")
        elif "1080p" in preset:
            width, height = 1920, 1080
        elif "720p" in preset:
            width, height = 1280, 720
        else:
            width, height = 854, 480

        output_name = st.text_input(
            "Output filename", value="resized_video.mp4", key="resize_output"
        )

        if st.button("Resize Video", key="resize_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Resizing video..."):
                    with VideoEditor(selected_file) as editor:
                        editor.resize(width=width, height=height).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Resize failed: {e}")


def _render_rotate_section(source_dir: Path):
    """Render the rotate section."""
    st.subheader("Rotate Video")

    selected_file = render_file_selector(
        "Select video",
        key="rotate_video_select",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm"],
        directory=source_dir,
    )

    if selected_file:
        rotation = st.selectbox(
            "Rotation",
            ["90° Clockwise", "180°", "90° Counter-clockwise", "Custom"],
            key="rotate_select",
        )

        if rotation == "Custom":
            angle = st.number_input("Custom angle", value=0.0, key="rotate_custom")
        elif rotation == "90° Clockwise":
            angle = RotationAngle.CW_90
        elif rotation == "180°":
            angle = RotationAngle.CW_180
        else:
            angle = RotationAngle.CCW_90

        output_name = st.text_input(
            "Output filename", value="rotated_video.mp4", key="rotate_output"
        )

        if st.button("Rotate Video", key="rotate_btn"):
            output_path = source_dir / output_name
            try:
                with st.spinner("Rotating video..."):
                    with VideoEditor(selected_file) as editor:
                        editor.rotate(angle).export(output_path)
                st.success(f"Saved to {output_path}")
            except Exception as e:
                st.error(f"Rotate failed: {e}")


def render_video_transforms(source_dir: Path):
    """Render all transform sections."""
    tab1, tab2, tab3, tab4 = st.tabs(["Speed", "Crop", "Resize", "Rotate"])

    with tab1:
        _render_speed_section(source_dir)
    with tab2:
        _render_crop_section(source_dir)
    with tab3:
        _render_resize_section(source_dir)
    with tab4:
        _render_rotate_section(source_dir)
