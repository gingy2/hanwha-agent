from __future__ import annotations

import html
import pathlib
import sys

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from core import router, session
from ui.theme import inject_css
from views import login as login_view
from views import documents as documents_view

st.set_page_config(
    page_title="사내 업무 에이전트",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

NAV: list[tuple[str, str | None]] = [
    ("AI 업무 도우미", None),
    ("문서 관리", "documents"),
    ("승인함", None),
    ("운영 대시보드", None),
]


def render_sidebar() -> None:
    st.sidebar.markdown(
        '<div class="ag-brand"><div class="ag-brand-name">사내 업무 에이전트</div></div>',
        unsafe_allow_html=True,
    )

    user = session.current_user()
    if user is not None:
        st.sidebar.markdown(
            '<div class="ag-user"><div>'
            f'<div class="ag-user-name">{html.escape(user["name"])}</div>'
            f'<div class="ag-user-role">{html.escape(user["dept"])}</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button("로그아웃", key="nav_logout"):
            session.logout()
            st.rerun()

    for label, page_key in NAV:
        if st.sidebar.button(label, key=f"nav_{label}"):
            if page_key is None:
                st.sidebar.info("아직 만들지 않은 화면입니다.")
            else:
                st.session_state["page"] = page_key


def main() -> None:
    session.init_state()

    if not session.is_authenticated():
        login_view.render()
        return

    render_sidebar()

    page = router.current_page()
    if page == "documents":
        documents_view.render()
    else:
        st.info("아직 만들지 않은 화면입니다.")


main()
