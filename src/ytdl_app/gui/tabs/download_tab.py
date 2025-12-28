"""Download tab implementation."""

from pathlib import Path

import streamlit as st

from ytdl_app.download import DownloadConfig, Downloader
from ytdl_app.gui.components import render_directory_selector
from ytdl_app.models import OutputFormat, VideoResolution


class DownloadProgressUI:
    """Manages download progress display in Streamlit."""

    def __init__(self):
        self.status_container = st.empty()
        self.progress_bar = st.progress(0.0)
        self.details_container = st.empty()
        self._current_title = ""

    def create_callback(self):
        """Create a yt-dlp progress callback that updates the UI."""

        def callback(d: dict) -> None:
            status = d.get("status", "")

            if status == "downloading":
                # Extract progress info
                percent_str = d.get("_percent_str", "0%").strip()
                speed_str = d.get("_speed_str", "N/A")
                eta_str = d.get("_eta_str", "N/A")
                filename = d.get("filename", "")

                # Parse percentage for progress bar
                try:
                    percent = float(percent_str.replace("%", "")) / 100.0
                    self.progress_bar.progress(min(percent, 1.0))
                except (ValueError, TypeError):
                    pass

                # Update status text
                title = d.get("info_dict", {}).get("title", Path(filename).stem)
                if title != self._current_title:
                    self._current_title = title
                    self.status_container.info(f"Downloading: **{title}**")

                # Show details
                self.details_container.text(
                    f"Progress: {percent_str} | Speed: {speed_str} | ETA: {eta_str}"
                )

            elif status == "finished":
                self.progress_bar.progress(1.0)
                self.details_container.text("Processing and converting...")

            elif status == "error":
                self.details_container.error("Download error occurred")

        return callback

    def complete(self, message: str):
        """Mark download as complete."""
        self.progress_bar.progress(1.0)
        self.status_container.success(message)
        self.details_container.empty()

    def error(self, message: str):
        """Mark download as failed."""
        self.status_container.error(message)
        self.details_container.empty()


def _perform_download(
    url: str, is_playlist: bool, config: DownloadConfig, progress_ui: DownloadProgressUI
) -> tuple[bool, str]:
    """Execute download and return (success, message)."""
    try:
        downloader = Downloader(
            config=config, progress_callback=progress_ui.create_callback()
        )

        if is_playlist:
            info = downloader.download_playlist(url)
            title = info.get("title", "Unknown Playlist")
            entries = info.get("entries", [])
            # Count actual downloads (some may be None if filtered)
            count = sum(1 for e in entries if e is not None)
            return True, f"Downloaded playlist: {title} ({count} items)"
        else:
            info = downloader.download(url)
            return True, f"Downloaded: {info.get('title', 'Unknown')}"
    except Exception as e:
        return False, f"Download failed: {e}"


def _fetch_playlist_info(url: str) -> dict | None:
    """Fetch playlist metadata without downloading."""
    try:
        downloader = Downloader()
        return downloader.get_info(url)
    except Exception:
        return None


def _render_playlist_selector():
    """Render playlist video selection UI."""
    playlist_info = st.session_state.get("playlist_info")

    if not playlist_info:
        return None

    entries = playlist_info.get("entries", [])
    if not entries:
        st.warning("No videos found in playlist")
        return None

    st.subheader(f"Playlist: {playlist_info.get('title', 'Unknown')}")
    st.write(f"**{len(entries)} videos available**")

    # Select all / Deselect all buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Select All", key="select_all_btn"):
            for i in range(len(entries)):
                st.session_state[f"playlist_item_{i}"] = True
            st.rerun()
    with col2:
        if st.button("Deselect All", key="deselect_all_btn"):
            for i in range(len(entries)):
                st.session_state[f"playlist_item_{i}"] = False
            st.rerun()

    # Initialize selection state if not present
    for i in range(len(entries)):
        if f"playlist_item_{i}" not in st.session_state:
            st.session_state[f"playlist_item_{i}"] = True

    # Display videos with checkboxes
    selected_indices = []
    with st.container(height=300):
        for i, entry in enumerate(entries):
            if entry is None:
                continue

            title = entry.get("title", f"Video {i + 1}")
            duration = entry.get("duration", 0)
            duration_str = ""
            if duration:
                mins, secs = divmod(int(duration), 60)
                duration_str = f" ({mins}:{secs:02d})"

            is_selected = st.checkbox(
                f"{i + 1}. {title}{duration_str}",
                key=f"playlist_item_{i}",
            )
            if is_selected:
                selected_indices.append(i + 1)  # 1-indexed for yt-dlp

    # Show selection count
    st.write(f"**Selected: {len(selected_indices)} / {len(entries)} videos**")

    return selected_indices


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
        if output_format == OutputFormat.MP4:
            resolution_choice = st.selectbox(
                "Resolution",
                ["Best Available", "1080p", "720p", "480p", "360p"],
                key="download_resolution",
            )
            resolution_map = {
                "Best Available": VideoResolution.BEST,
                "1080p": VideoResolution.R_1080P,
                "720p": VideoResolution.R_720P,
                "480p": VideoResolution.R_480P,
                "360p": VideoResolution.R_360P,
            }
            resolution = resolution_map[resolution_choice]
        else:
            resolution = VideoResolution.BEST

    # Advanced options in expander
    with st.expander("Advanced Options"):
        col3, col4 = st.columns(2)
        with col3:
            cookies_file = st.file_uploader(
                "Cookies file (optional)",
                type=["txt"],
                key="cookies_upload",
                help="Upload cookies.txt for authenticated downloads",
            )
            max_retries = st.number_input(
                "Max retries", min_value=1, max_value=10, value=3, key="max_retries"
            )
        with col4:
            embed_thumbnail = st.checkbox(
                "Embed thumbnail", value=True, key="embed_thumbnail"
            )
            embed_metadata = st.checkbox(
                "Embed metadata", value=True, key="embed_metadata"
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

    # Playlist selection workflow
    selected_items = None
    if is_playlist and url:
        # Check if URL changed - clear old playlist info
        if st.session_state.get("playlist_url") != url:
            st.session_state["playlist_info"] = None
            st.session_state["playlist_url"] = url
            # Clear old selection states
            for key in list(st.session_state.keys()):
                if key.startswith("playlist_item_"):
                    del st.session_state[key]

        col_fetch, col_clear = st.columns([1, 1])
        with col_fetch:
            if st.button("Fetch Playlist", key="fetch_playlist_btn"):
                with st.spinner("Fetching playlist info..."):
                    info = _fetch_playlist_info(url)
                    if info and "entries" in info:
                        st.session_state["playlist_info"] = info
                        st.rerun()
                    else:
                        st.error("Failed to fetch playlist or URL is not a playlist")

        with col_clear:
            if st.session_state.get("playlist_info"):
                if st.button("Clear Selection", key="clear_playlist_btn"):
                    st.session_state["playlist_info"] = None
                    st.rerun()

        # Render playlist selector if we have playlist info
        selected_items = _render_playlist_selector()

    # Build playlist_items string if we have selections
    playlist_items_str = None
    if selected_items:
        playlist_items_str = ",".join(str(i) for i in selected_items)

    # Determine if download is possible
    can_download = bool(url)
    if is_playlist and st.session_state.get("playlist_info"):
        can_download = bool(selected_items)

    download_label = "Download"
    if is_playlist and selected_items:
        download_label = f"Download {len(selected_items)} Videos"

    if st.button(download_label, type="primary", disabled=not can_download, key="download_btn"):
        config = DownloadConfig(
            output_dir=output_dir,
            output_format=output_format,
            resolution=resolution,
            cookies_file=cookies_path,
            retries=max_retries,
            embed_thumbnail=embed_thumbnail,
            write_info_json=embed_metadata,
            playlist_items=playlist_items_str,
        )

        # Create progress UI
        progress_ui = DownloadProgressUI()
        success, message = _perform_download(url, is_playlist, config, progress_ui)

        if success:
            progress_ui.complete(message)
        else:
            progress_ui.error(message)

    st.divider()
    _render_info_section()
