from __future__ import annotations

import html
import pathlib
import sys

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from core import router, session
from ui.theme import inject_css
from views import chat as chat_view
from views import login as login_view
from views import documents as documents_view

st.set_page_config(
    page_title="사내 업무 에이전트",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS 적용
inject_css()

# 메뉴 목록
NAV: list[tuple[str, str | None]] = [
    ("AI 업무 도우미", "chat"),
    ("문서 관리", "documents"),
    ("승인함", None),
    ("운영 대시보드", None),
]

# 사이드바
def render_sidebar() -> None:
    st.sidebar.markdown(
        '<div class="ag-brand"><div class="ag-brand-name">사내 업무 에이전트</div></div>',
        unsafe_allow_html=True,
    )

    # 사용자 추가
    user = session.current_user()
    # 로그인 했으면
    if user is not None:
        # 사용자 이름과 부서명 화면에 띄우기
        st.sidebar.markdown(
            '<div class="ag-user">'
            f'<div class="ag-avatar">{html.escape(user["name"][:1])}</div>'
            f'<div class="ag-user-name">{html.escape(user["name"])}</div>'
            f'<div class="ag-user-role">{html.escape(user["dept"])}</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )
        # 로그아웃 버튼
        if st.sidebar.button("로그아웃", key="nav_logout"):
            session.logout()
            st.rerun()

    # 메뉴 버튼 그리기
    for label, page_key in NAV:
        if st.sidebar.button(label, key=f"nav_{label}"):
            if page_key is None:
                st.sidebar.info("아직 만들지 않은 화면입니다.")
            else:
                # 메뉴 클릭 시 화면 키값을 상태에 추가-> 화면 이동 처리ㄴ
                st.session_state["page"] = page_key

# 수정
def main() -> None:
    # 상태값 초기화
    session.init_state()

    # 로그인 상태 확인
    if not session.is_authenticated(): # 비로그인 상태면
        login_view.render()            # 로그인 창 보여주기
        return

    # 사이드바 랜더
    render_sidebar()

    # 현재 페이지 키 가져오기
    page = router.current_page()
    # 현재 페이지 키 값이 documents면
    if page=='chat':
        chat_view.render()
    elif page == "documents":
        documents_view.render()
    else:
        st.info("아직 만들지 않은 화면입니다.")


main()
