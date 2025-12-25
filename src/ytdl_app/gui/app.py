"""Streamlit GUI for the YouTube downloader."""

from pathlib import Path

import streamlit as st

from ytdl_app.core import DownloadOptions, Downloader, OutputFormat


def init_session_state():
    """Initialize session state variables."""
    if "download_status" not in st.session_state:
        st.session_state.download_status = None
    if "download_message" not in st.session_state:
        st.session_state.download_message = ""


def render_sidebar() -> tuple[Path, OutputFormat, Path | None]:
    """Render sidebar with download options."""
    st.sidebar.header("Download Options")

    output_dir = st.sidebar.text_input(
        "Output Directory",
        value=str(Path.cwd()),
        help="Directory where files will be saved",
    )

    format_choice = st.sidebar.radio(
        "Output Format",
        options=["MP4 (Video)", "MP3 (Audio)"],
        help="Choose video or audio-only download",
    )
    output_format = OutputFormat.MP4 if "MP4" in format_choice else OutputFormat.MP3

    cookies_path = st.sidebar.text_input(
        "Cookies File (optional)",
        value="",
        help="Path to cookies.txt for authenticated downloads",
    )
    cookies_file = Path(cookies_path) if cookies_path else None

    return Path(output_dir), output_format, cookies_file


def perform_download(url: str, is_playlist: bool, options: DownloadOptions) -> tuple[bool, str]:
    """
    Execute the download operation.

    Returns:
        Tuple of (success, message).
    """
    try:
        downloader = Downloader(options=options)

        if is_playlist:
            info = downloader.download_playlist(url)
            title = info.get("title", "Unknown Playlist")
            count = len(info.get("entries", []))
            return True, f"Downloaded playlist: {title} ({count} items)"
        else:
            info = downloader.download(url)
            title = info.get("title", "Unknown")
            return True, f"Downloaded: {title}"
    except Exception as e:
        return False, f"Download failed: {e}"


def render_main_content(output_dir: Path, output_format: OutputFormat, cookies_file: Path | None):
    """Render the main content area."""
    st.header("Download YouTube Content")

    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=... or playlist URL",
    )

    download_type = st.radio(
        "Download Type",
        options=["Single Video", "Playlist"],
        horizontal=True,
    )
    is_playlist = download_type == "Playlist"

    if st.button("Download", type="primary", disabled=not url):
        options = DownloadOptions(
            output_dir=output_dir,
            output_format=output_format,
            cookies_file=cookies_file,
        )

        with st.spinner("Downloading..."):
            success, message = perform_download(url, is_playlist, options)

        if success:
            st.success(message)
        else:
            st.error(message)

    # Info section
    st.divider()
    render_info_section()


def render_info_section():
    """Render the video info lookup section."""
    st.subheader("Lookup Video Info")

    info_url = st.text_input(
        "URL for info lookup",
        placeholder="Enter URL to fetch metadata",
        key="info_url",
    )

    if st.button("Fetch Info", disabled=not info_url):
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


def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(
        page_title="YouTube Downloader",
        page_icon="▶",
        layout="centered",
    )

    init_session_state()

    st.title("YouTube Downloader")

    output_dir, output_format, cookies_file = render_sidebar()
    render_main_content(output_dir, output_format, cookies_file)


if __name__ == "__main__":
    main()
