"""Live vs. offline mode indicator banner."""

import streamlit as st


def render_mode_banner():
    """Display a banner showing whether the app is in live or offline mode."""
    mode = st.session_state.get("mode", "offline")
    if mode == "live":
        st.caption("Live mode — queries use the Anthropic API")
    else:
        st.info(
            "Running in demo mode — showing cached results. "
            "Add ANTHROPIC_API_KEY to .env for live queries."
        )
