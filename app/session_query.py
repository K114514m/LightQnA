"""Helpers for the persistent auth token carried in Streamlit query params."""

from __future__ import annotations

import streamlit as st


AUTH_SESSION_QUERY_PARAM = "auth_session"


def get_query_session_token() -> str | None:
    """Return the auth token from the current URL query params."""
    value = st.query_params.get(AUTH_SESSION_QUERY_PARAM)
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value else None


def set_query_session_token(token: str) -> None:
    """Persist the auth token in the current URL query params."""
    st.query_params[AUTH_SESSION_QUERY_PARAM] = token


def clear_query_session_token() -> None:
    """Remove the auth token from the current URL query params."""
    if AUTH_SESSION_QUERY_PARAM in st.query_params:
        del st.query_params[AUTH_SESSION_QUERY_PARAM]
