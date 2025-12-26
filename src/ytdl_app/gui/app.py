"""Main Streamlit application entry point."""

import streamlit as st

from .state import init_session_state
from .tabs import render_audio_tab, render_download_tab, render_video_tab


def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(
        page_title="Media Tools",
        page_icon="▶",
        layout="wide",
    )

    init_session_state()

    st.title("Media Tools")
    st.caption("Download, edit video, and process audio")

    tab_download, tab_video, tab_audio = st.tabs(
        ["Download", "Video Editing", "Audio Editing"]
    )

    with tab_download:
        render_download_tab()

    with tab_video:
        render_video_tab()

    with tab_audio:
        render_audio_tab()


if __name__ == "__main__":
    main()
