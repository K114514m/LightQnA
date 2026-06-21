"""Streamlit 登录 / 注册入口。

启动方式::

    streamlit run login.py

登录成功后会调用 :func:`webui.main` 进入主界面。
"""

from __future__ import annotations

import streamlit as st

from auth_service import authenticate_user, create_user, get_user_by_username, init_auth_store
from webui import main

init_auth_store()

# 初始化会话状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin' not in st.session_state:
    st.session_state.admin = False
if 'usname' not in st.session_state:
    st.session_state.usname = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None


def login_page() -> None:
    """渲染登录表单并校验。"""
    with st.form("login_form"):
        st.title("登录")
        username = st.text_input("用户名", value="")
        password = st.text_input("密码", value="", type="password")
        submit = st.form_submit_button("登录")

        if submit:
            user = authenticate_user(username, password)
            if user:
                st.success("登录成功！")
                st.session_state.logged_in = True
                st.session_state.admin = user.is_admin
                st.session_state.usname = user.username
                st.session_state.user_id = user.id
                st.rerun()
            else:
                st.error("用户名或密码错误，请重新输入。")


def register_page() -> None:
    """渲染注册表单并写入凭证文件。"""
    with st.form("register_form"):
        st.title("注册")
        new_username = st.text_input("设置用户名", value="")
        new_password = st.text_input("设置密码", value="", type="password")
        is_admin = False
        register_submit = st.form_submit_button("注册")

        if register_submit:
            if get_user_by_username(new_username):
                st.error("用户名已存在，请使用其他用户名。")
            else:
                try:
                    user = create_user(new_username, new_password, is_admin=is_admin)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.success(f"用户 {user.username} 注册成功！请登录。")
                    st.rerun()


if __name__ == "__main__":
    if not st.session_state.logged_in:
        # 显示注册和登录选项
        st.sidebar.title("导航")
        app_mode = st.sidebar.selectbox("选择操作", ["登录", "注册"])
        if app_mode == "登录":
            login_page()
        elif app_mode == "注册":
            register_page()
    else:
        if st.session_state.user_id is None:
            st.session_state.logged_in = False
            st.session_state.admin = False
            st.session_state.usname = ""
            st.rerun()
        main(st.session_state.admin, st.session_state.usname, int(st.session_state.user_id))
