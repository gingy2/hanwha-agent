from __future__ import annotations

from html import escape

import streamlit as st

from core import api_client, session
from ui.badge import badge_html
from ui.metric import metrics
from ui.table import table


DEPTS: dict[str, str | None] = {
    "전체": None,
    "인사총무": "HRGA",
    "구매팀": "PU",
    "보안팀": "SE",
    "PMO": "PMO",
}

LEVELS = ["전체", "일반", "3급", "대외비"]

STATUSES = ["전체", "현행", "만료"]

HEADERS = ["문서 ID", "문서명", "버전", "시행 ~ 만료", "상태", "부서", "등급", "색인"]

ALIGNS = ["ag-nowrap", "", "", "ag-nowrap", "", "", "", "ag-nowrap"]


def _metrics_row() -> None:
    try:
        counts = api_client.stats(emp_no=session.emp_no())
    except api_client.ApiError as exc:
        st.caption(f"지표를 불러오지 못했습니다: {exc}")
        return

    metrics([
        {"label": "전체", "value": counts["total"], "delta": "문서 버전 기준"},
        {"label": "현행", "value": counts["current"], "delta": "지금 유효한 판",
         "tone": "ok"},
        {"label": "만료", "value": counts["expired"], "delta": "지난 판",
         "tone": "no"},
        {"label": "재임베딩", "value": counts["reindexing"], "delta": "색인을 다시 만드는 중",
         "tone": "wait"},
    ])


def _filter_row() -> dict:
    left, middle, right, search = st.columns([1, 1, 1, 2])

    with left:
        dept_name = st.selectbox("부서", list(DEPTS), key="f_dept")
    with middle:
        level = st.selectbox("보안등급", LEVELS, key="f_level")
    with right:
        status = st.selectbox("상태", STATUSES, key="f_status")
    with search:
        keyword = st.text_input("검색어", key="f_q", placeholder="문서명 또는 문서 ID")

    return {
        "dept_id": DEPTS[dept_name],
        "security_level": None if level == "전체" else level,
        "status": None if status == "전체" else status,
        "q": keyword or None,
    }


def _table(documents: list[dict]) -> None:
    rows = []
    for document in documents:
        period = f"{document['effective_from']} ~ {document['expires_at'] or '현행'}"
        index_label = f"{document['index_status']} {document['index_progress']}%"
        rows.append([
            escape(document["doc_id"]),
            escape(document["title"]),
            escape(document["version"]),
            escape(period),
            badge_html(document["status"]),
            escape(document["dept"]),
            escape(document["security_level"]),
            badge_html(index_label),
        ])

    table(HEADERS, rows, align=ALIGNS)


def render() -> None:
    st.title("문서 관리")
    st.caption("상태 필터가 「전체」라 지난 판까지 함께 보입니다. "
               "「현행」으로 좁히면 현재 유효한 최신본만 남습니다.")

    _metrics_row()

    filters = _filter_row()

    if st.button("새 문서 업로드"):
        st.info("업로드 화면은 다음 단계에서 만듭니다.")

    with st.spinner("문서를 불러오는 중입니다..."):
        try:
            documents = api_client.list_documents(**filters, limit=100,
                                                  emp_no=session.emp_no())
        except api_client.ApiError as exc:
            st.error(str(exc))
            return

    if not documents:
        st.info("조건에 맞는 문서가 없습니다. 필터를 바꿔 보세요.")
        return

    st.caption(f"{len(documents)}건")
    _table(documents)
