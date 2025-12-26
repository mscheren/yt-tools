"""Download tab implementation."""

from pathlib import Path

import streamlit as st

from ytdl_app.download import Downloader, DownloadOptions
from ytdl_app.gui.components import render_directory_selector
from ytdl_app.models import OutputFormat


def _perform_download(
    url: str, is_playlist: bool, options: DownloadOptions
) -> tuple[bool, str]:
    """Execute download and return (success, message)."""
    try:
        downloader = Downloader(options=options)

        if is_playlist:
            info = downloader.download_playlist(url)
            title = info.get("title", "Unknown Playlist")
            count = len(info.get("entries", []))
            return True, f"Downloaded playlist: {title} ({count} items)"
        else:
            info = downloader.download(url)
            return True, f"Downloaded: {info.get('title', 'Unknown')}"
    except Exception as e:
        return False, f"Download failed: {e}"


def _render_info_section():
    """Render the video info lookup section."""
    st.subheader("Lookup Video Info")

    info_url = st.text_input(
        "URL for info lookup",
        placeholder="Enter URL to fetch metadata",
        key="info_url",
    )

    if st.button("Fetch Info", disabled=not info_url, key="fetch_info_btn"):
        try:
            downloader = Downloader()
            with st.spinner("Fetching metadata..."):
                metadata = downloader.get_info(info_url)

            st.write(f"**Title:** {metadata.get('title', 'N/A')}")

            if "entries" in metadata:
                st.write(f"**Type:** Playlist ({len(metadata['entries'])} videos)")
                with st.expander("Show playlist contents"):
                    for i, entry in enumerate(metadata["entries"], 1):
                        st.write(f"{i}. {entry.get('title', 'Unknown')}")
            else:
                st.write("**Type:** Single Video")
                duration = metadata.get("duration", 0)
                if duration:
                    minutes, seconds = divmod(duration, 60)
                    st.write(f"**Duration:** {int(minutes)}:{int(seconds):02d}")
                st.write(f"**Channel:** {metadata.get('channel', 'N/A')}")
        except Exception as e:
            st.error(f"Failed to fetch info: {e}")


def render_download_tab():
    """Render the download tab content."""
    st.header("Download YouTube Content")

    # Output directory selector
    output_dir = render_directory_selector(
        "Output Directory",
        key="download_output_dir",
        default=Path.cwd(),
        help_text="Directory where downloaded files will be saved",
    )

    # Format selection
    col1, col2 = st.columns(2)

    with col1:
        format_choice = st.radio(
            "Output Format",
            options=["MP4 (Video)", "MP3 (Audio)"],
            horizontal=True,
            key="download_format",
        )
        output_format = OutputFormat.MP4 if "MP4" in format_choice else OutputFormat.MP3

    with col2:
        cookies_file = st.file_uploader(
            "Cookies file (optional)",
            type=["txt"],
            key="cookies_upload",
            help="Upload cookies.txt for authenticated downloads",
        )

    cookies_path = None
    if cookies_file:
        temp_path = Path("/tmp") / "cookies.txt"
        temp_path.write_bytes(cookies_file.read())
        cookies_path = temp_path

    st.divider()

    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=... or playlist URL",
        key="download_url",
    )

    download_type = st.radio(
        "Download Type",
        options=["Single Video", "Playlist"],
        horizontal=True,
        key="download_type",
    )
    is_playlist = download_type == "Playlist"

    if st.button("Download", type="primary", disabled=not url, key="download_btn"):
        options = DownloadOptions(
            output_dir=output_dir,
            output_format=output_format,
            cookies_file=cookies_path,
        )

        with st.spinner("Downloading..."):
            success, message = _perform_download(url, is_playlist, options)

        if success:
            st.success(message)
        else:
            st.error(message)

    st.divider()
    _render_info_section()
