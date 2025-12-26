"""Session state management for Streamlit."""

import streamlit as st


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "current_tab": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
