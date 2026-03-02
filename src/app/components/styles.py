"""Shared CSS styles for the Streamlit portal."""

import streamlit as st

CUSTOM_CSS = """
<style>
/* Purple buttons */
.stButton > button {
    background-color: #6A0572;
    color: white;
    border: 1px solid #6A0572;
}
.stButton > button:hover {
    background-color: #540460;
    color: white;
    border: 1px solid #540460;
}
.stButton > button:active,
.stButton > button:focus {
    background-color: #6A0572;
    color: white;
    border: 1px solid #6A0572;
}

/* Purple download buttons */
.stDownloadButton > button {
    background-color: #6A0572;
    color: white;
    border: 1px solid #6A0572;
}
.stDownloadButton > button:hover {
    background-color: #540460;
    color: white;
    border: 1px solid #540460;
}
.stDownloadButton > button:active,
.stDownloadButton > button:focus {
    background-color: #6A0572;
    color: white;
    border: 1px solid #6A0572;
}

/* Teal expander headers with white text */
[data-testid="stExpander"] summary {
    background-color: #21918C;
    color: white !important;
    border-radius: 6px;
    padding: 8px 14px;
}
[data-testid="stExpander"] summary:hover {
    background-color: #1a7a76;
    color: white !important;
}
[data-testid="stExpander"] summary * {
    color: white !important;
}

/* Hide Streamlit deploy button */
[data-testid="stAppDeployButton"] {
    display: none !important;
}

/* Sidebar — dark-blue background with white text (CSS-only, not via config) */
section[data-testid="stSidebar"] > div:first-child {
    background-color: #1B2A4A;
}
section[data-testid="stSidebar"] {
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
</style>
"""


def inject_custom_css() -> None:
    """Inject custom CSS (buttons, sidebar text)."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Keep backward-compatible alias
inject_button_css = inject_custom_css
