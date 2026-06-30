"""Shared Streamlit presentation helpers for LightQnA."""

from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components


def apply_apple_style() -> None:
    """Apply the LightQnA visual system to Streamlit widgets."""
    st.markdown(
        """
        <style>
        /* ── Token system: readable clinical workspace ── */
        :root {
            --bg:            #f3f6fa;
            --surface:       #ffffff;
            --surface-solid: #ffffff;
            --surface-soft:  #f8fafc;
            --border:        #d7e0ea;
            --border-strong: #aeb9c7;
            --text:          #172033;
            --muted:         #4b5565;
            --hint:          #7c8798;

            --accent:        #0f766e;
            --accent-hover:  #115e59;
            --accent-light:  #e6f4f1;
            --accent-border: #9ed5cd;

            --user-bg:       #eef6ff;
            --user-border:   #bfd7f0;
            --assistant-bg:  #ffffff;

            --shadow-sm:     0 1px 2px rgba(23, 32, 51, 0.06);
            --shadow-md:     0 8px 24px rgba(23, 32, 51, 0.08);
            --shadow-lg:     0 18px 48px rgba(23, 32, 51, 0.12);
            --radius:        10px;

            /* [FIX 3] 统一字号 token，避免魔法数字散落 */
            --text-xs:   0.72rem;   /* kicker、sidebar meta */
            --text-sm:   0.82rem;   /* sidebar title、expander header */
            --text-base: 1rem;      /* subtitle、正文 */
            --text-lg:   0.9rem;    /* button */
            --text-notice: 0.88rem; /* auth notice body */

            /* [FIX 5] form / auth 容器宽度 token，避免散落的 640px/720px */
            --form-max-w:      640px;
            --auth-block-max-w: 720px;
        }

        /* ── Page background ── */
        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(15, 118, 110, 0.08), transparent 32rem),
                linear-gradient(180deg, #f8fafc 0%, var(--bg) 48%, #eef3f8 100%);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                         "Segoe UI", system-ui, sans-serif;
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
        }

        /* ── Topbar ── */
        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.92);
            backdrop-filter: saturate(180%) blur(20px);
            -webkit-backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 1px solid var(--border);
        }

        /* ── Hide Streamlit chrome ── */
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu, footer { display: none; }

        /* ── Content column ── */
        .block-container {
            max-width: 1100px;
            padding-top: 2.5rem;
            padding-bottom: 6rem;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--border);
            box-shadow: 8px 0 28px rgba(23, 32, 51, 0.04);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding: 1.2rem 1rem;
        }

        /* ── Typography resets ── */
        /* [FIX 7] 补全 h2/h3，避免样式系统不完整 */
        h1, h2, h3 {
            color: var(--text);
            letter-spacing: 0;
        }
        h1 { font-weight: 750; }
        h2 { font-weight: 600; font-size: 1.4rem; }
        h3 { font-weight: 600; font-size: 1.1rem; }
        p, li, label, span {
            color: inherit;
        }

        /* ════════════════════════════════════════
           Hero blocks
           ════════════════════════════════════════ */
        .apple-hero {
            margin: 0 0 1.4rem 0;
            padding: 1.4rem 1.6rem;
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            border-radius: var(--radius);
            background: linear-gradient(135deg, #ffffff 0%, #f6fbfa 100%);
            box-shadow: var(--shadow-md);
        }

        .apple-auth-hero {
            max-width: var(--form-max-w);
            margin: 5rem auto 1.6rem auto;
            text-align: center;
        }

        .apple-kicker {
            margin: 0 0 0.4rem 0;
            color: var(--accent);
            font-size: var(--text-xs);
            font-weight: 700;
            letter-spacing: 0.10em;
            text-transform: uppercase;
        }

        .apple-title {
            margin: 0;
            color: var(--text);
            font-size: clamp(1.8rem, 3.5vw, 2.8rem);
            line-height: 1.08;
            font-weight: 750;
            letter-spacing: 0;
        }

        .apple-subtitle {
            margin: 0.65rem 0 0 0;
            color: var(--muted);
            font-size: var(--text-base);
            line-height: 1.65;
        }

        .apple-auth-hero .apple-subtitle {
            max-width: 560px;
            margin-left: auto;
            margin-right: auto;
        }

        /* ════════════════════════════════════════
           Sidebar cards
           ════════════════════════════════════════ */
        .apple-sidebar-card {
            margin: 0.5rem 0 1rem 0;
            padding: 0.75rem 0.85rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface-soft);
            box-shadow: var(--shadow-sm);
        }

        .apple-sidebar-title {
            margin: 0;
            color: var(--text);
            font-size: var(--text-sm);
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        /* [FIX 10] sidebar meta 改用 <ul> 语义标签对应的样式 */
        .apple-sidebar-meta {
            margin: 0.2rem 0 0 0;
            padding: 0;
            list-style: none;
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.55;
        }

        .apple-sidebar-meta li + li {
            margin-top: 0.15rem;
        }

        .apple-sidebar-section-label {
            margin: 1rem 0 0.45rem 0;
            color: var(--hint);
            font-size: var(--text-xs);
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .apple-conversation-active {
            width: 100%;
            margin: 0.25rem 0;
            padding: 0.58rem 0.72rem;
            border: 1px solid var(--accent-border);
            border-radius: 8px;
            background: var(--accent-light);
            color: var(--accent-hover);
            font-size: 0.86rem;
            font-weight: 700;
            line-height: 1.35;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* ════════════════════════════════════════
           Forms
           ════════════════════════════════════════ */
        /* [FIX 2] 去除冗余的 max-width，只保留 min() 写法 */
        [data-testid="stForm"] {
            width: min(100%, var(--form-max-w));
            margin: 0 auto;
            padding: 1.5rem 1.6rem;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: var(--surface);
            box-shadow: var(--shadow-md);
        }

        /* ── Inputs ── */
        /* [FIX 1] 尽可能减少 !important，仅在确实需要覆盖 Streamlit 内联样式时保留 */
        [data-testid="stTextInput"],
        [data-testid="stPasswordInput"] {
            width: 100%;
        }

        [data-testid="stTextInput"] > div,
        [data-testid="stPasswordInput"] > div {
            width: 100%;
        }

        [data-testid="stPasswordInput"] div[data-baseweb="input"] {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 3.4rem;
            align-items: stretch;
            width: 100%;
        }

        [data-testid="stPasswordInput"] div[data-baseweb="input"] input {
            grid-column: 1;
            min-width: 0;
        }

        [data-testid="stPasswordInput"] div[data-baseweb="input"] button {
            grid-column: 2;
            width: 3.4rem;
            min-width: 3.4rem;
            border-radius: 0 8px 8px 0;
        }

        /* 仅对 Streamlit 强制覆盖的属性保留 !important */
        [data-testid="stTextInput"] input,
        [data-testid="stPasswordInput"] input,
        [data-baseweb="select"] > div,
        textarea {
            width: 100% !important;
            min-width: 0 !important;
            min-height: 2.75rem !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 8px !important;
            background: var(--surface-solid) !important;
            color: var(--text) !important;
            font-size: 0.96rem !important;
            transition: border-color 120ms ease, box-shadow 120ms ease;
        }

        [data-testid="stPasswordInput"] input {
            border-radius: 8px 0 0 8px !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stPasswordInput"] input:focus,
        textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14) !important;
            outline: none !important;
        }

        /* ════════════════════════════════════════
           Buttons
           ════════════════════════════════════════ */
        .stButton > button,
        [data-testid="stFormSubmitButton"] button {
            min-height: 2.4rem;
            padding: 0 1.25rem;
            border: 1px solid var(--accent-hover) !important;
            border-radius: 999px !important;
            background: var(--accent) !important;
            color: #ffffff !important;
            font-size: var(--text-lg);
            font-weight: 600;
            letter-spacing: 0;
            box-shadow: var(--shadow-sm);
            transition: background 130ms ease, transform 120ms ease, box-shadow 120ms ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background: var(--accent-hover) !important;
            color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }

        .stButton > button:active,
        [data-testid="stFormSubmitButton"] button:active {
            transform: translateY(0);
            box-shadow: var(--shadow-sm);
        }

        /* Sidebar buttons — ghost style */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            min-height: 2.2rem;
            justify-content: flex-start;
            text-align: left;
            background: #ffffff !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            box-shadow: none !important;
            font-weight: 600;
        }

        [data-testid="stSidebar"] .stButton > button p {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: var(--accent-light) !important;
            color: var(--accent-hover) !important;
            border-color: var(--accent-border) !important;
            transform: none;
            box-shadow: none !important;
        }

        /* ════════════════════════════════════════
           Sidebar image
           ════════════════════════════════════════ */
        [data-testid="stSidebar"] [data-testid="stImage"] {
            overflow: hidden;
            border-radius: 8px;
            border: 1px solid var(--border-strong);
            background: #ffffff;
        }

        /* ════════════════════════════════════════
           Chat messages
           ════════════════════════════════════════ */
        [data-testid="stChatMessage"] {
            margin: 0.6rem 0;
            padding: 0.95rem 1rem;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: var(--assistant-bg);
            box-shadow: var(--shadow-sm);
            color: var(--text);
        }

        /*
         * [FIX 8] :has() 降级方案
         * 先用通用样式兜底，再用 :has() 做细化覆盖。
         * 不支持 :has() 的浏览器两种气泡都显示为 var(--surface)，
         * 体验可接受；支持 :has() 的浏览器享受精细区分。
         */
        /* User bubble — very light gray tint */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: var(--user-bg);
            border-color: var(--user-border);
        }

        /* Assistant bubble — white */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: var(--assistant-bg);
            border-color: var(--border);
        }

        /* ── Chat input bar ── */
        [data-testid="stChatInput"] {
            border-top: 0 !important;
            background: transparent !important;
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
            padding: 0.85rem 1rem 1.1rem 1rem;
        }
        

        [data-testid="stChatInput"] > div {
            width: min(100%, 760px);
            margin: 0 auto;
            background: transparent !important;
        }

        [data-testid="stChatInput"] textarea {
            min-height: 2.8rem !important;
            border-radius: 999px !important;
            background: var(--surface-solid) !important;
            border: 1px solid var(--border-strong) !important;
            box-shadow: 0 10px 30px rgba(23, 32, 51, 0.10) !important;
            padding: 0.78rem 3.25rem 0.78rem 1.05rem !important;
        }

        /* ════════════════════════════════════════
           Expanders / alerts / misc
           ════════════════════════════════════════ */
        .streamlit-expanderHeader {
            border-radius: 6px;
            color: var(--text);
            font-weight: 600;
            font-size: var(--text-sm);
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid var(--border-strong);
        }

        .stCheckbox label { color: var(--text); }

        [data-testid="stCaptionContainer"] { color: var(--muted); }

        /* ── Selectbox ── */
        [data-baseweb="select"] > div {
            background: #ffffff !important;
        }

        [data-baseweb="select"] [data-baseweb="popover"] {
            border: 1px solid var(--border-strong) !important;
            border-radius: 8px !important;
        }

        /* ════════════════════════════════════════
           Responsive
           ════════════════════════════════════════ */
        /* [FIX 4] 补充中间断点，单一 760px 断点在平板上表现差 */
        @media (max-width: 1024px) {
            .block-container { max-width: 900px; }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 2rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            /* [FIX 2] 移动端 stForm 只需调整 padding，宽度由 min() 自动处理 */
            [data-testid="stForm"] {
                padding: 1rem 1.1rem;
            }
            .apple-hero { padding: 1rem 1.1rem; }
            .apple-auth-hero { margin-top: 2.5rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_auth_page_style() -> None:
    """Hide the sidebar and tighten the centered auth layout."""
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        :root {
            --auth-mouse-x: 50vw;
            --auth-mouse-y: 34vh;
        }

        html,
        body,
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(
                    circle 26rem at var(--auth-mouse-x) var(--auth-mouse-y),
                    rgba(15, 118, 110, 0.22),
                    rgba(15, 118, 110, 0.08) 34%,
                    transparent 70%
                ),
                radial-gradient(
                    circle 34rem at calc(100% - var(--auth-mouse-x)) calc(100% - var(--auth-mouse-y)),
                    rgba(59, 130, 246, 0.12),
                    transparent 66%
                ),
                linear-gradient(
                    135deg,
                    #f8fafc 0%,
                    #eef8f6 48%,
                    #f3f6fa 100%
                );
        }

        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.44), rgba(255, 255, 255, 0.08)),
                repeating-linear-gradient(
                    105deg,
                    rgba(15, 118, 110, 0.035) 0,
                    rgba(15, 118, 110, 0.035) 1px,
                    transparent 1px,
                    transparent 22px
                );
            opacity: 0.68;
            animation: auth-bg-drift 16s ease-in-out infinite alternate;
        }

        [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(circle 18rem at 18% 24%, rgba(255, 255, 255, 0.42), transparent 72%),
                radial-gradient(circle 18rem at 84% 72%, rgba(15, 118, 110, 0.10), transparent 70%);
            mix-blend-mode: screen;
            opacity: 0.72;
            animation: auth-glow-breathe 10s ease-in-out infinite alternate;
        }

        @keyframes auth-bg-drift {
            from {
                transform: translate3d(-0.8rem, -0.5rem, 0);
                background-position: 0 0, 0 0;
            }
            to {
                transform: translate3d(0.8rem, 0.5rem, 0);
                background-position: 0 0, 1.5rem 1rem;
            }
        }

        @keyframes auth-glow-breathe {
            from { opacity: 0.48; transform: scale(1); }
            to { opacity: 0.78; transform: scale(1.025); }
        }

        @media (prefers-reduced-motion: reduce) {
            [data-testid="stAppViewContainer"]::before,
            [data-testid="stAppViewContainer"]::after {
                animation: none;
            }
        }

        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.72);
            border-bottom: 0;
            backdrop-filter: saturate(180%) blur(26px);
            -webkit-backdrop-filter: saturate(180%) blur(26px);
        }

        .block-container {
            max-width: 900px;
            padding-top: 4rem;
        }

        /* 登录页外层只保留一条方形边框，清掉 Streamlit 生成的重复层 */
        div[data-testid="stAppViewBlockContainer"] > div[data-testid="stVerticalBlockBorderWrapper"]:has(.apple-auth-hero) {
            width: min(100%, var(--auth-block-max-w));
            margin: 0 auto;
            padding: 1.5rem 1.6rem;
            border: 1px solid var(--border) !important;
            border-radius: 18px !important;
            background: transparent !important;
            box-shadow: var(--shadow-lg) !important;
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
        }

        div[data-testid="stAppViewBlockContainer"] > div[data-testid="stVerticalBlockBorderWrapper"]:has(.apple-auth-hero) > div:first-child {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stAppViewBlockContainer"] > div[data-testid="stVerticalBlockBorderWrapper"]:has(.apple-auth-hero) > div:first-child > div:first-child {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        div[data-testid="stAppViewBlockContainer"]
            > div[data-testid="stVerticalBlockBorderWrapper"]:has(.apple-auth-hero)
            div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        .apple-auth-hero {
            margin: 0 auto 1.35rem auto;
        }

        [data-testid="stRadio"] {
            width: 100%;
            margin: 0 auto 0.75rem auto;
            padding: 0.25rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: #ffffff;
            box-shadow: var(--shadow-sm);
        }

        [data-testid="stRadio"] > label {
            display: none;
        }

        [data-testid="stRadio"] div[role="radiogroup"] {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.25rem;
        }

        [data-testid="stRadio"] label {
            min-height: 2.35rem;
            margin: 0 !important;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            justify-content: center;
            color: var(--muted);
            font-weight: 600;
        }

        /* [FIX 8] :has() 先正常声明，不支持的浏览器自动跳过这条规则 */
        [data-testid="stRadio"] label:has(input:checked) {
            background: var(--accent);
            color: #ffffff;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        }

        [data-testid="stRadio"] label:has(input:checked) * {
            color: #ffffff !important;
        }

        [data-testid="stRadio"] input {
            accent-color: var(--accent) !important;
        }

        .apple-auth-notice {
            width: 100%;
            margin: 0 auto 0.9rem auto;
            padding: 0.9rem 1rem;
            border-radius: var(--radius);
            border: 1px solid #bbf7d0;
            background: #ecfdf5;
            color: #14532d;
        }

        .apple-auth-notice-title {
            margin: 0;
            font-weight: 700;
            font-size: var(--text-base);
        }

        .apple-auth-notice-body {
            margin: 0.22rem 0 0 0;
            color: #166534;
            font-size: var(--text-notice);
            line-height: 1.45;
        }

        /*
         * [FIX 6] 认证页 stForm 重置：合并冗余声明为简写
         * 原来的 5 行独立属性全部归为一行 all-reset 写法
         */
        [data-testid="stForm"] {
            all: unset;
            display: block;
            width: 100%;
        }

        /* auth 页输入框：无边框 + 毛玻璃风格 */
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] input,
        div[data-testid="stVerticalBlockBorderWrapper"] textarea {
            border: 1px solid var(--border-strong) !important;
            background: #ffffff !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
            [data-testid="stPasswordInput"]
            div[data-baseweb="input"] {
            border: 0 !important;
            border-radius: 8px !important;
            background: transparent !important;
            box-shadow: none !important;
            overflow: visible;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
            [data-testid="stPasswordInput"]
            div[data-baseweb="input"] input {
            border: 1px solid var(--border-strong) !important;
            border-right: 0 !important;
            border-radius: 8px 0 0 8px !important;
            background: #ffffff !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] input:focus,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPasswordInput"] input:focus,
        div[data-testid="stVerticalBlockBorderWrapper"] textarea:focus {
            border: 1px solid var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
            [data-testid="stPasswordInput"]
            div[data-baseweb="input"] button {
            border: 1px solid var(--border-strong) !important;
            border-radius: 0 8px 8px 0 !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="textInputRootElement"] {
            border: 1px solid var(--border-strong) !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            box-shadow: var(--shadow-sm) !important;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="textInputRootElement"] input {
            border: 0 !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="base-input"] {
            background: #ffffff !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] button[aria-label*="password"] {
            width: 3.2rem;
            min-width: 3.2rem;
            border: 0 !important;
            border-left: 1px solid var(--border) !important;
            border-radius: 0 !important;
            background: var(--surface-soft) !important;
            color: var(--text) !important;
        }

        @media (max-width: 760px) {
            .block-container { padding-top: 2.2rem; }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                padding: 1rem 1.1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
        (() => {
            try {
                const parentWindow = window.parent;
                const root = parentWindow.document.documentElement;

                if (
                    parentWindow.__lightQnaAuthPointerBackgroundDocument
                    === parentWindow.document
                ) {
                    return;
                }
                parentWindow.__lightQnaAuthPointerBackgroundDocument = parentWindow.document;

                let pendingFrame = null;
                let pointerX = parentWindow.innerWidth * 0.5;
                let pointerY = parentWindow.innerHeight * 0.34;

                const writePosition = () => {
                    pendingFrame = null;
                    root.style.setProperty("--auth-mouse-x", `${pointerX}px`);
                    root.style.setProperty("--auth-mouse-y", `${pointerY}px`);
                };

                const handlePointerMove = (event) => {
                    pointerX = event.clientX;
                    pointerY = event.clientY;
                    if (!pendingFrame) {
                        pendingFrame = parentWindow.requestAnimationFrame(writePosition);
                    }
                };

                const handlePointerLeave = () => {
                    pointerX = parentWindow.innerWidth * 0.5;
                    pointerY = parentWindow.innerHeight * 0.34;
                    if (!pendingFrame) {
                        pendingFrame = parentWindow.requestAnimationFrame(writePosition);
                    }
                };

                parentWindow.addEventListener("pointermove", handlePointerMove, { passive: true });
                parentWindow.document.addEventListener("pointermove", handlePointerMove, { passive: true });
                parentWindow.document.body.addEventListener("pointermove", handlePointerMove, { passive: true });
                parentWindow.document.addEventListener("mousemove", handlePointerMove, { passive: true });
                parentWindow.document.body.addEventListener("mousemove", handlePointerMove, { passive: true });
                parentWindow.document.addEventListener("pointerleave", handlePointerLeave, { passive: true });

                const appContainer = parentWindow.document.querySelector(
                    '[data-testid="stAppViewContainer"]'
                );
                if (appContainer) {
                    appContainer.addEventListener("pointermove", handlePointerMove, { passive: true });
                    appContainer.addEventListener("mousemove", handlePointerMove, { passive: true });
                }
                writePosition();
            } catch (error) {
                // Streamlit may sandbox components differently across versions.
                // The CSS-only drift animation remains active if pointer tracking is unavailable.
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def render_page_hero(
    title: str,
    subtitle: str,
    kicker: str = "LightQnA",
) -> None:
    """Render a top-of-page hero block in the main content area.

    Args:
        title:    Primary heading text displayed large.
        subtitle: Descriptive sentence shown beneath the title.
        kicker:   Small all-caps label above the title (default: "LightQnA").
    """
    st.markdown(
        f"""
        <div class="apple-hero">
            <p class="apple-kicker">{html.escape(kicker)}</p>
            <h1 class="apple-title">{html.escape(title)}</h1>
            <p class="apple-subtitle">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth_hero(
    title: str,
    subtitle: str,
    kicker: str = "LightQnA",
) -> None:
    """Render the centered hero shown on login / register pages.

    Args:
        title:    Primary heading text.
        subtitle: Supporting description beneath the title.
        kicker:   Small all-caps label above the title (default: "LightQnA").
    """
    st.markdown(
        f"""
        <div class="apple-auth-hero">
            <p class="apple-kicker">{html.escape(kicker)}</p>
            <h1 class="apple-title">{html.escape(title)}</h1>
            <p class="apple-subtitle">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth_notice(title: str, body: str) -> None:
    """Render a prominent auth-page status notice (e.g. success / info banner).

    Args:
        title: Bold notice heading.
        body:  Supporting detail text.
    """
    st.markdown(
        f"""
        <div class="apple-auth-notice">
            <p class="apple-auth-notice-title">{html.escape(title)}</p>
            <p class="apple-auth-notice-body">{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_card(title: str, lines: list[str]) -> None:
    """Render a compact info card inside the sidebar.

    Args:
        title: Bold card heading.
        lines: Each string becomes a separate list item in the card body.
               Using <ul>/<li> for proper semantics rather than <br>-joined text.
    """
    # [FIX 9] 使用 <ul>/<li> 替代 <br> 拼接，语义正确、易于屏幕阅读器解析
    items_html = "".join(f"<li>{html.escape(line)}</li>" for line in lines)
    st.markdown(
        f"""
        <div class="apple-sidebar-card">
            <p class="apple-sidebar-title">{html.escape(title)}</p>
            <ul class="apple-sidebar-meta">{items_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
