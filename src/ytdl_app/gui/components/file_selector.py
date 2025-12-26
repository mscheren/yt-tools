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

    col1, col2 = st.columns([4, 1])

    with col1:
        path_str = st.text_input(
            label,
            value=str(default),
            key=f"{key}_input",
            help=help_text,
        )

    current_path = Path(path_str)

    with col2:
        st.write("")  # Spacing
        if st.button("Home", key=f"{key}_home", use_container_width=True):
            current_path = Path.home()
            st.session_state[f"{key}_input"] = str(current_path)
            st.rerun()

    if current_path.exists() and current_path.is_dir():
        subdirs = sorted([d for d in current_path.iterdir() if d.is_dir()])
        if subdirs:
            options = ["(current directory)"] + [d.name for d in subdirs[:20]]
            selected = st.selectbox(
                "Quick navigate",
                options,
                key=f"{key}_nav",
                label_visibility="collapsed",
            )
            if selected != "(current directory)":
                new_path = current_path / selected
                st.session_state[f"{key}_input"] = str(new_path)
                st.rerun()

        # Show parent navigation
        if current_path != current_path.parent:
            if st.button("Go to parent directory", key=f"{key}_parent"):
                st.session_state[f"{key}_input"] = str(current_path.parent)
                st.rerun()

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
