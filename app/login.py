"""Streamlit 登录 / 注册入口。

启动方式::

    streamlit run app/login.py

登录成功后会调用 :func:`app.webui.main` 进入主界面。
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.auth_service import (
    authenticate_user,
    create_auth_session,
    create_user,
    get_user_by_session_token,
    get_user_by_username,
    init_auth_store,
)
from app.i18n import DEFAULT_LANGUAGE, LANGUAGES, normalize_language, t
from app.session_query import clear_query_session_token, get_query_session_token, set_query_session_token
from app.ui_theme import apply_apple_style, apply_auth_page_style, render_auth_hero, render_auth_notice
from app.webui import main

st.set_page_config(
    page_title="LightQnA",
    layout="wide",
    initial_sidebar_state="auto",
)

apply_apple_style()
init_auth_store()

# ── 会话状态初始化 ──
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "admin" not in st.session_state:
    st.session_state.admin = False
if "usname" not in st.session_state:
    st.session_state.usname = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "lang" not in st.session_state:
    st.session_state.lang = DEFAULT_LANGUAGE
else:
    st.session_state.lang = normalize_language(st.session_state.lang)
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
elif st.session_state.auth_mode in ("登录", "Log in", "ログイン"):
    st.session_state.auth_mode = "login"
elif st.session_state.auth_mode in ("注册", "Register", "登録"):
    st.session_state.auth_mode = "register"
if "auth_notice" not in st.session_state:
    st.session_state.auth_notice = None
if "pending_auth_mode" not in st.session_state:
    st.session_state.pending_auth_mode = None


def set_logged_in_user(user) -> None:
    """Copy authenticated user details into Streamlit session state."""
    st.session_state.logged_in = True
    st.session_state.admin = user.is_admin
    st.session_state.usname = user.username
    st.session_state.user_id = user.id


def restore_login_from_query_token() -> None:
    """Restore Streamlit session state after a browser refresh."""
    if st.session_state.logged_in:
        return

    token = get_query_session_token()
    if not token:
        return

    user = get_user_by_session_token(token)
    if user:
        set_logged_in_user(user)
    else:
        clear_query_session_token()


def translated_auth_error(lang: str, error: ValueError) -> str:
    """Translate known auth validation errors from auth_service."""
    error_key = {
        "用户名不能为空": "username_empty",
        "密码不能为空": "password_empty",
        "用户名已存在": "username_exists",
        "用户不存在": "user_not_found",
    }.get(str(error))
    if error_key:
        return t(lang, error_key)
    return str(error)


def auth_page() -> None:
    """Render the centered login/register experience."""
    apply_auth_page_style()

    with st.container(border=True):
        lang = st.selectbox(
            t(st.session_state.lang, "language_label"),
            options=list(LANGUAGES.keys()),
            format_func=lambda code: LANGUAGES[code],
            key="lang",
        )
        render_auth_hero(t(lang, "app_title"), t(lang, "auth_subtitle"))

        if st.session_state.pending_auth_mode:
            st.session_state.auth_mode = st.session_state.pending_auth_mode
            st.session_state.pending_auth_mode = None

        auth_mode = st.radio(
            "Authentication mode",
            ["login", "register"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode",
            format_func=lambda mode: t(lang, mode),
        )

        if st.session_state.auth_notice:
            render_auth_notice(
                t(lang, "register_notice_title"),
                t(lang, "register_notice_body", notice=st.session_state.auth_notice),
            )
            st.session_state.auth_notice = None

        with st.form("auth_form"):
            if auth_mode == "login":
                st.markdown(f"### {t(lang, 'login')}")
                st.caption(t(lang, "auth_caption_login"))
                submit_label = t(lang, "login")
            else:
                st.markdown(f"### {t(lang, 'register')}")
                st.caption(t(lang, "auth_caption_register"))
                submit_label = t(lang, "register")

            username = st.text_input(t(lang, "username"), value="")
            password = st.text_input(t(lang, "password"), value="", type="password")
            submit = st.form_submit_button(submit_label, use_container_width=True)

            if submit:
                if auth_mode == "login":
                    user = authenticate_user(username, password)
                    if user:
                        st.success(t(lang, "login_success"))
                        token = create_auth_session(user.id)
                        set_query_session_token(token)
                        set_logged_in_user(user)
                        st.rerun()
                    else:
                        st.error(t(lang, "username_or_password_wrong"))
                elif get_user_by_username(username):
                    st.error(t(lang, "username_exists"))
                else:
                    try:
                        user = create_user(username, password, is_admin=False)
                    except ValueError as exc:
                        st.error(translated_auth_error(lang, exc))
                    else:
                        st.session_state.pending_auth_mode = "login"
                        st.session_state.auth_notice = t(
                            lang, "register_success", username=user.username
                        )
                        st.rerun()


# ── 路由：Streamlit 直接执行模块顶层，无需 __main__ 判断 ──
restore_login_from_query_token()

if not st.session_state.logged_in:
    auth_page()
else:
    # 会话安全检查：user_id 缺失则强制重新登录
    if st.session_state.user_id is None:
        st.session_state.logged_in = False
        st.session_state.admin = False
        st.session_state.usname = ""
        clear_query_session_token()
        st.rerun()
    else:
        main(
            st.session_state.admin,
            st.session_state.usname,
            int(st.session_state.user_id),
        )
