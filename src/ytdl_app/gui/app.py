"""Main Streamlit application entry point."""

import streamlit as st

from ytdl_app.gui.state import init_session_state
from ytdl_app.gui.tabs import (
    render_audio_tab,
    render_download_tab,
    render_project_tab,
    render_video_tab,
)


def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(
        page_title="YT Media Tools",
        page_icon="▶",
        layout="wide",
    )

    init_session_state()

    st.title("YT Media Tools")
    st.caption("Download, edit video, and process audio")

    tab_download, tab_video, tab_audio, tab_project = st.tabs(
        ["Download", "Video Editing", "Audio Editing", "Projects"]
    )

    with tab_download:
        render_download_tab()

    with tab_video:
        render_video_tab()

    with tab_audio:
        render_audio_tab()

    with tab_project:
        render_project_tab()


if __name__ == "__main__":
    main()
