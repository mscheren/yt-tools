"""File and directory selection components."""

from pathlib import Path

import streamlit as st


def render_directory_selector(
    label: str,
    key: str,
    default: Path | None = None,
    help_text: str | None = None,
) -> Path:
    """
    Render a directory selector with path input and quick navigation.

    Args:
        label: Label for the selector.
        key: Unique key for the widget.
        default: Default directory path.
        help_text: Optional help text.

    Returns:
        Selected directory path.
    """
    default = default or Path.cwd()
    input_key = f"{key}_input"

    # Initialize session state before widget creation
    if input_key not in st.session_state:
        st.session_state[input_key] = str(default)

    # Handle pending navigation (set by callbacks)
    pending_key = f"{key}_pending_path"
    if pending_key in st.session_state:
        st.session_state[input_key] = st.session_state[pending_key]
        del st.session_state[pending_key]

    col1, col2 = st.columns([4, 1])

    with col1:
        path_str = st.text_input(
            label,
            key=input_key,
            help=help_text,
        )

    current_path = Path(path_str)

    def go_home():
        st.session_state[pending_key] = str(Path.home())

    def go_parent():
        st.session_state[pending_key] = str(Path(path_str).parent)

    with col2:
        st.write("")  # Spacing
        st.button("Home", key=f"{key}_home", use_container_width=True, on_click=go_home)

    if current_path.exists() and current_path.is_dir():
        subdirs = sorted([d for d in current_path.iterdir() if d.is_dir()])
        if subdirs:
            options = ["(current directory)"] + [d.name for d in subdirs[:20]]

            def on_nav_change():
                selected = st.session_state[f"{key}_nav"]
                if selected != "(current directory)":
                    new_path = current_path / selected
                    st.session_state[pending_key] = str(new_path)

            st.selectbox(
                "Quick navigate",
                options,
                key=f"{key}_nav",
                label_visibility="collapsed",
                on_change=on_nav_change,
            )

        # Show parent navigation
        if current_path != current_path.parent:
            st.button("Go to parent directory", key=f"{key}_parent", on_click=go_parent)

        return current_path

    st.warning("Directory does not exist")
    return default


def render_file_selector(
    label: str,
    key: str,
    extensions: list[str] | None = None,
    directory: Path | None = None,
) -> Path | None:
    """
    Render a file selector with filtering by extension.

    Args:
        label: Label for the selector.
        key: Unique key for the widget.
        extensions: List of allowed extensions (e.g., [".mp4", ".avi"]).
        directory: Directory to browse.

    Returns:
        Selected file path or None.
    """
    directory = directory or Path.cwd()

    if not directory.exists():
        st.warning(f"Directory not found: {directory}")
        return None

    files = []
    for f in directory.iterdir():
        if f.is_file():
            if extensions is None or f.suffix.lower() in extensions:
                files.append(f)

    files = sorted(files, key=lambda x: x.name.lower())

    if not files:
        ext_str = ", ".join(extensions) if extensions else "any"
        st.info(f"No files found ({ext_str})")
        return None

    options = {f.name: f for f in files}
    selected_name = st.selectbox(label, list(options.keys()), key=key)

    return options.get(selected_name)
