"""Streamlit UI for the LightRAG-backed medical QA workflow."""

from __future__ import annotations

import logging
import os
from typing import Dict, List

import streamlit as st

from config import settings
from lightrag_adapter import (
    finalize_lightrag,
    initialize_lightrag,
    query_lightrag,
    run_async,
    runtime_summary,
)
from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def _conversation_history(messages: List[Dict[str, str]]) -> list[dict[str, str]]:
    """Return recent chat history in LightRAG's expected shape."""
    history: list[dict[str, str]] = []
    for message in messages[-10:]:
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and content:
            history.append({"role": role, "content": content})
    return history


async def _ask_lightrag(question: str, history: list[dict[str, str]]) -> str:
    rag = await initialize_lightrag()
    try:
        return await query_lightrag(rag, question, conversation_history=history)
    finally:
        await finalize_lightrag(rag)


def ask_lightrag(question: str, history: list[dict[str, str]]) -> str:
    """Sync wrapper used by Streamlit event handlers."""
    return run_async(_ask_lightrag(question, history))


def _debug_payload() -> dict[str, str]:
    return {
        "ent": "LightRAG 全链路模式：未使用独立 BERT NER；实体和关系由 LightRAG 在索引阶段抽取。",
        "yitu": f"LightRAG query mode={settings.LIGHTRAG_QUERY_MODE}；未使用固定 16 类意图路由。",
        "prompt": runtime_summary(),
    }


def main(is_admin: bool, usname: str) -> None:
    """Streamlit 主界面入口；由 ``login.py`` 在用户登录成功后调用。"""
    st.title("医疗智能问答机器人")

    with st.sidebar:
        col1, _ = st.columns([0.6, 0.6])
        with col1:
            st.image(os.path.join("img", "logo.jpg"), use_column_width=True)

        st.caption(
            f"""<p align="left">欢迎您，{'管理员' if is_admin else '用户'}{usname}！当前版本：{1.1}</p>""",
            unsafe_allow_html=True,
        )
        st.caption(f"LightRAG LLM: {settings.LIGHTRAG_LLM_MODEL}")
        st.caption(f"检索模式: {settings.LIGHTRAG_QUERY_MODE}")

        if "chat_windows" not in st.session_state:
            st.session_state.chat_windows = [[]]
            st.session_state.messages = [[]]

        if st.button("新建对话窗口"):
            st.session_state.chat_windows.append([])
            st.session_state.messages.append([])

        window_options = [f"对话窗口 {i + 1}" for i in range(len(st.session_state.chat_windows))]
        selected_window = st.selectbox("请选择对话窗口:", window_options)
        active_window_index = int(selected_window.split()[1]) - 1

        show_ent = show_int = show_prompt = False
        if is_admin:
            show_ent = st.sidebar.checkbox("显示实体抽取模式")
            show_int = st.sidebar.checkbox("显示检索路由模式")
            show_prompt = st.sidebar.checkbox("显示 LightRAG 配置")
            if st.button("打开 Neo4j 图谱"):
                st.markdown("[点击这里打开 Neo4j](http://127.0.0.1:7474/)", unsafe_allow_html=True)

        if st.button("返回登录"):
            st.session_state.logged_in = False
            st.session_state.admin = False
            st.rerun()

    current_messages = st.session_state.messages[active_window_index]

    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if show_ent:
                    with st.expander("实体抽取模式"):
                        st.write(message.get("ent", "未使用独立 BERT NER。"))
                if show_int:
                    with st.expander("检索路由模式"):
                        st.write(message.get("yitu", f"LightRAG query mode={settings.LIGHTRAG_QUERY_MODE}"))
                if show_prompt:
                    with st.expander("LightRAG 配置"):
                        st.write(message.get("prompt", runtime_summary()))

    if query := st.chat_input("Ask me anything!", key=f"chat_input_{active_window_index}"):
        history = _conversation_history(current_messages)
        current_messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        response_placeholder = st.empty()
        response_placeholder.text("正在查询 LightRAG 知识库...")

        debug_payload = _debug_payload()
        try:
            answer = ask_lightrag(query, history)
        except Exception as exc:
            logger.exception("LightRAG 查询失败")
            answer = (
                "LightRAG 查询失败。请确认已安装 lightrag-hku，Neo4j Bolt 服务、"
                "Ollama LLM 和 embedding 模型都已启动并完成索引构建。"
            )
            debug_payload["prompt"] = f"{runtime_summary()}\nerror={exc}"

        response_placeholder.empty()
        with st.chat_message("assistant"):
            st.markdown(answer)
            if show_ent:
                with st.expander("实体抽取模式"):
                    st.write(debug_payload["ent"])
            if show_int:
                with st.expander("检索路由模式"):
                    st.write(debug_payload["yitu"])
            if show_prompt:
                with st.expander("LightRAG 配置"):
                    st.write(debug_payload["prompt"])

        current_messages.append(
            {
                "role": "assistant",
                "content": answer,
                "yitu": debug_payload["yitu"],
                "prompt": debug_payload["prompt"],
                "ent": debug_payload["ent"],
            }
        )

    st.session_state.messages[active_window_index] = current_messages
