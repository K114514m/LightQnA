"""Streamlit UI for the LightRAG-backed medical QA workflow."""

from __future__ import annotations

import html
import logging
import os
from pathlib import Path

import streamlit as st

from app.auth_service import revoke_auth_session
from app.conversation_store import (
    add_message,
    create_conversation,
    delete_conversation,
    get_or_create_default_conversation,
    list_conversations,
    list_messages,
    recent_history,
    rename_conversation,
)
from app.i18n import DEFAULT_LANGUAGE, LANGUAGES, normalize_language, t
from app.lightrag_adapter import (
    finalize_lightrag,
    initialize_lightrag,
    query_lightrag,
    run_async,
)
from app.logging_setup import setup_logging
from app.session_query import clear_query_session_token, get_query_session_token
from app.ui_theme import apply_apple_style, render_page_hero

setup_logging()
logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


async def _ask_lightrag(question: str, history: list[dict[str, str]]) -> str:
    rag = await initialize_lightrag()
    try:
        return await query_lightrag(rag, question, conversation_history=history)
    finally:
        await finalize_lightrag(rag)


def ask_lightrag(question: str, history: list[dict[str, str]]) -> str:
    """Sync wrapper used by Streamlit event handlers."""
    return run_async(_ask_lightrag(question, history))


def _conversation_label(
    conversation_id: int, labels: dict[int, str], lang: str
) -> str:
    return labels.get(conversation_id, t(lang, "conversation"))


def main(is_admin: bool, usname: str, user_id: int) -> None:
    """Streamlit 主界面入口；由 ``login.py`` 在用户登录成功后调用。"""
    apply_apple_style()
    if "lang" not in st.session_state:
        st.session_state.lang = DEFAULT_LANGUAGE
    else:
        st.session_state.lang = normalize_language(st.session_state.lang)
    lang = st.session_state.lang
    render_page_hero(
        t(lang, "app_title"),
        t(lang, "app_subtitle"),
    )
    active_key = f"active_conversation_id_{user_id}"
    rename_key = f"rename_conversation_id_{user_id}"
    delete_key = f"delete_conversation_id_{user_id}"

    with st.sidebar:
        # Streamlit 1.32 supports use_column_width for images.
        logo_path = PROJECT_ROOT / "assets" / "img" / "logo.jpg"
        if os.path.exists(logo_path):
            col1, _ = st.columns([0.6, 0.6])
            with col1:
                st.image(str(logo_path), use_column_width=True)

        lang = st.selectbox(
            t(lang, "language_label"),
            options=list(LANGUAGES.keys()),
            format_func=lambda code: LANGUAGES[code],
            key="lang",
        )

        if st.button(t(lang, "new_chat"), use_container_width=True):
            conversation = create_conversation(user_id)
            st.session_state[active_key] = conversation.id
            st.rerun()

        conversations = list_conversations(user_id)
        if not conversations:
            conversations = [get_or_create_default_conversation(user_id)]

        conversation_ids = [c.id for c in conversations]
        if st.session_state.get(active_key) not in conversation_ids:
            st.session_state[active_key] = conversation_ids[0]
        if st.session_state.get(rename_key) not in conversation_ids:
            st.session_state[rename_key] = None
        if st.session_state.get(delete_key) not in conversation_ids:
            st.session_state[delete_key] = None

        labels = {c.id: c.title for c in conversations}
        st.markdown(
            f'<p class="apple-sidebar-section-label">{html.escape(t(lang, "select_chat"))}</p>',
            unsafe_allow_html=True,
        )
        for conversation in conversations:
            label = _conversation_label(conversation.id, labels, lang)
            if st.session_state.get(rename_key) == conversation.id:
                input_key = f"rename_input_{user_id}_{conversation.id}"
                if input_key not in st.session_state:
                    st.session_state[input_key] = conversation.title

                st.text_input(
                    t(lang, "rename_conversation"),
                    key=input_key,
                    label_visibility="collapsed",
                )
                save_col, cancel_col = st.columns([0.58, 0.42])
                with save_col:
                    if st.button(
                        t(lang, "save"),
                        key=f"rename_save_{user_id}_{conversation.id}",
                        use_container_width=True,
                    ):
                        rename_conversation(
                            user_id,
                            conversation.id,
                            str(st.session_state[input_key]),
                        )
                        st.session_state[rename_key] = None
                        st.rerun()
                with cancel_col:
                    if st.button(
                        t(lang, "cancel"),
                        key=f"rename_cancel_{user_id}_{conversation.id}",
                        use_container_width=True,
                    ):
                        st.session_state[rename_key] = None
                        st.rerun()
                continue

            if st.session_state.get(delete_key) == conversation.id:
                st.markdown(
                    f'<div class="apple-conversation-active">{html.escape(label)}</div>',
                    unsafe_allow_html=True,
                )
                confirm_col, cancel_col = st.columns([0.58, 0.42])
                with confirm_col:
                    if st.button(
                        t(lang, "delete_confirm"),
                        key=f"delete_confirm_{user_id}_{conversation.id}",
                        use_container_width=True,
                    ):
                        delete_conversation(user_id, conversation.id)
                        st.session_state[delete_key] = None
                        if st.session_state.get(active_key) == conversation.id:
                            st.session_state[active_key] = None
                        st.rerun()
                with cancel_col:
                    if st.button(
                        t(lang, "cancel"),
                        key=f"delete_cancel_{user_id}_{conversation.id}",
                        use_container_width=True,
                    ):
                        st.session_state[delete_key] = None
                        st.rerun()
                continue

            label_col, rename_col, delete_col = st.columns([0.58, 0.21, 0.21])
            with label_col:
                if conversation.id == st.session_state[active_key]:
                    st.markdown(
                        f'<div class="apple-conversation-active">{html.escape(label)}</div>',
                        unsafe_allow_html=True,
                    )
                elif st.button(
                    label,
                    key=f"conversation_button_{user_id}_{conversation.id}",
                    use_container_width=True,
                ):
                    st.session_state[active_key] = conversation.id
                    st.rerun()

            with rename_col:
                if st.button(
                    "✎",
                    key=f"rename_start_{user_id}_{conversation.id}",
                    help=t(lang, "rename"),
                    use_container_width=True,
                ):
                    st.session_state[f"rename_input_{user_id}_{conversation.id}"] = (
                        conversation.title
                    )
                    st.session_state[rename_key] = conversation.id
                    st.rerun()

            with delete_col:
                if st.button(
                    "✕",
                    key=f"delete_start_{user_id}_{conversation.id}",
                    help=t(lang, "delete"),
                    use_container_width=True,
                ):
                    st.session_state[delete_key] = conversation.id
                    st.session_state[rename_key] = None
                    st.rerun()

        active_conversation_id = int(st.session_state[active_key])

        if is_admin:
            if st.button(t(lang, "neo4j_button"), use_container_width=True):
                st.markdown(
                    f"[{t(lang, 'click_open_neo4j')}](http://127.0.0.1:7474/)",
                    unsafe_allow_html=True,
                )

        st.divider()
        if st.button(t(lang, "logout"), use_container_width=True):
            revoke_auth_session(get_query_session_token())
            clear_query_session_token()
            for key in ("logged_in", "admin", "usname", "user_id"):
                st.session_state[key] = (False if key == "logged_in" else
                                         False if key == "admin" else
                                         "" if key == "usname" else None)
            st.rerun()

    # ── 消息历史 ──
    current_messages = list_messages(active_conversation_id)

    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── 输入框 & 推理 ──
    if query := st.chat_input(
        t(lang, "chat_placeholder"), key=f"chat_input_{active_conversation_id}"
    ):
        history = recent_history(active_conversation_id, limit=10)
        add_message(active_conversation_id, "user", query)
        current_messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        response_placeholder = st.empty()
        response_placeholder.text(t(lang, "querying"))

        try:
            answer = ask_lightrag(query, history)
        except Exception:
            logger.exception("LightRAG 查询失败")
            answer = t(lang, "query_failed")

        response_placeholder.empty()

        with st.chat_message("assistant"):
            st.markdown(answer)

        current_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )
        add_message(
            active_conversation_id,
            "assistant",
            answer,
        )
