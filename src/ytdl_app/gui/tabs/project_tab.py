"""Project management tab implementation."""

from pathlib import Path

import streamlit as st

from ytdl_app.gui.components import render_directory_selector, render_file_selector
from ytdl_app.project import ProjectConfig, ProjectManager


def _render_new_project_section():
    """Render the new project section."""
    st.subheader("Create New Project")

    project_name = st.text_input(
        "Project name",
        placeholder="My Video Project",
        key="new_project_name",
    )

    project_dir = render_directory_selector(
        "Project directory",
        key="new_project_dir",
        default=Path.cwd(),
        help_text="Where to save the project file",
    )

    file_format = st.radio(
        "Project format",
        ["JSON", "YAML"],
        horizontal=True,
        key="project_format",
    )

    if st.button("Create Project", key="create_project_btn", disabled=not project_name):
        try:
            manager = ProjectManager()
            manager.new_project(project_name)

            ext = "json" if file_format == "JSON" else "yaml"
            safe_name = project_name.lower().replace(" ", "_")
            save_path = project_dir / f"{safe_name}.{ext}"
            manager.save(save_path)

            st.session_state["current_project_path"] = save_path
            st.success(f"Created project: {save_path}")
        except Exception as e:
            st.error(f"Failed to create project: {e}")


def _render_load_project_section():
    """Render the load project section."""
    st.subheader("Load Project")

    project_dir = render_directory_selector(
        "Search directory",
        key="load_project_dir",
        default=Path.cwd(),
    )

    try:
        projects = ProjectManager.list_projects(project_dir)
        if projects:
            st.write(f"Found {len(projects)} project(s):")
            for path in projects:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(path.name)
                with col2:
                    if st.button("Load", key=f"load_{path.name}"):
                        try:
                            manager = ProjectManager()
                            config = manager.load(path)
                            st.session_state["current_project_path"] = path
                            st.session_state["current_project"] = config
                            st.success(f"Loaded: {config.name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Load failed: {e}")
        else:
            st.info("No project files found in this directory.")
    except Exception as e:
        st.error(f"Error scanning directory: {e}")


def _render_current_project_section():
    """Render the current project info section."""
    st.subheader("Current Project")

    current_path = st.session_state.get("current_project_path")

    if current_path:
        try:
            manager = ProjectManager()
            config = manager.load(current_path)

            st.write(f"**Name:** {config.name}")
            st.write(f"**Created:** {config.created_at.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Modified:** {config.modified_at.strftime('%Y-%m-%d %H:%M')}")

            if config.source_files:
                with st.expander(f"Source files ({len(config.source_files)})"):
                    for f in config.source_files:
                        st.text(str(f))

            if config.operations:
                with st.expander(f"Operations ({len(config.operations)})"):
                    for i, op in enumerate(config.operations, 1):
                        st.text(f"{i}. {op.op_type.value}: {op.params}")

            if config.metadata:
                with st.expander("Metadata"):
                    st.json(config.metadata)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Project", key="save_project_btn"):
                    try:
                        manager.save(current_path)
                        st.success("Project saved!")
                    except Exception as e:
                        st.error(f"Save failed: {e}")
            with col2:
                if st.button("Close Project", key="close_project_btn"):
                    st.session_state.pop("current_project_path", None)
                    st.session_state.pop("current_project", None)
                    st.rerun()

        except Exception as e:
            st.error(f"Error loading project: {e}")
    else:
        st.info("No project currently loaded. Create or load a project above.")


def _render_add_files_section():
    """Render section to add source files to project."""
    st.subheader("Add Source Files")

    current_path = st.session_state.get("current_project_path")
    if not current_path:
        st.info("Load a project first to add source files.")
        return

    source_dir = render_directory_selector(
        "Browse directory",
        key="add_files_dir",
        default=Path.cwd(),
    )

    selected_file = render_file_selector(
        "Select file to add",
        key="add_source_file",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".webm", ".mp3", ".wav", ".flac"],
        directory=source_dir,
    )

    if selected_file and st.button("Add to Project", key="add_file_btn"):
        try:
            manager = ProjectManager()
            config = manager.load(current_path)

            if selected_file not in config.source_files:
                config.source_files.append(selected_file)
                manager.project = config
                manager.save(current_path)
                st.success(f"Added: {selected_file.name}")
            else:
                st.warning("File already in project.")
        except Exception as e:
            st.error(f"Failed to add file: {e}")


def render_project_tab():
    """Render the project management tab content."""
    st.header("Project Management")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["New Project", "Load Project", "Current Project", "Add Files"]
    )

    with tab1:
        _render_new_project_section()

    with tab2:
        _render_load_project_section()

    with tab3:
        _render_current_project_section()

    with tab4:
        _render_add_files_section()
