from __future__ import annotations

from html import escape                                   # HTML 특수문자(<, & 등) 이스케이프 → 표에 안전하게 넣기

import streamlit as st                                    # 화면 구성

from core import api_client, session, router              # 백엔드 호출, 로그인 사용자 정보, 화면 이동
from ui.badge import badge_html                           # 상태 배지(색 라벨) HTML
from ui.metric import metrics                             # 지표 카드 한 줄
from ui.table import table                                # HTML 표 그리기


# 부서 선택지: 화면 표시 이름 → 백엔드 부서 ID (전체는 필터 없음 = None)
DEPTS: dict[str, str | None] = {
    "전체": None,
    "인사총무": "HRGA",
    "구매팀": "PU",
    "보안팀": "SE",
    "PMO": "PMO",
}

LEVELS = ["전체", "일반", "3급", "대외비"]                 # 보안등급 선택지

STATUSES = ["전체", "현행", "만료"]                        # 문서 상태 선택지

HEADERS = ["문서 ID", "문서명", "버전", "시행 ~ 만료", "상태", "부서", "등급", "검색 반영"]   # 표 머리글

ALIGNS = ["ag-nowrap", "", "", "ag-nowrap", "", "", "", "ag-nowrap"]   # 열별 CSS 클래스 (ag-nowrap: 줄바꿈 안 함)


# 맨 위 지표 카드 4개 (전체 / 현행 / 만료 / 재임베딩)
def _metrics_row() -> None:
    try:
        counts = api_client.stats(emp_no=session.emp_no())   # 로그인 사원 기준 문서 통계 요청
    except api_client.ApiError as exc:                     # 백엔드 오류면
        st.caption(f"지표를 불러오지 못했습니다: {exc}")      # 작은 안내만 띄우고
        return                                             # 화면의 나머지는 계속 그림

    metrics([
        {"label": "전체", "value": counts["total"], "delta": "문서 버전 기준"},            # 모든 버전 수
        {"label": "현행", "value": counts["current"], "delta": "지금 유효한 판",
         "tone": "ok"},                                                                   # 초록
        {"label": "만료", "value": counts["expired"], "delta": "지난 판",
         "tone": "no"},                                                                   # 빨강
        {"label": "재임베딩", "value": counts["reindexing"], "delta": "검색 내용에 다시 반영하는 중",
         "tone": "wait"},                                                                 # 노랑(대기)
    ])


# 필터 한 줄 (부서·보안등급·상태 선택 + 검색어) → 백엔드에 보낼 조건 dict 반환
def _filter_row() -> dict:
    left, middle, right, search = st.columns([1, 1, 1, 2])   # 4칸 (검색창만 2배 폭)

    with left:
        dept_name = st.selectbox("부서", list(DEPTS), key="f_dept")          # 부서 선택 (화면 이름)
    with middle:
        level = st.selectbox("보안등급", LEVELS, key="f_level")              # 보안등급 선택
    with right:
        status = st.selectbox("상태", STATUSES, key="f_status")             # 상태 선택
    with search:
        keyword = st.text_input("검색어", key="f_q", placeholder="문서명 또는 문서 ID")   # 검색어 입력

    return {
        "dept_id": DEPTS[dept_name],                                      # 화면 이름 → 부서 ID
        "security_level": None if level == "전체" else level,             # 전체면 조건 없음
        "status": None if status == "전체" else status,                   # 전체면 조건 없음
        "q": keyword or None,                                             # 빈 검색어면 조건 없음
    }


# 문서 목록 → 표 그리기
def _table(documents: list[dict]) -> None:
    rows = []                                                             # 표 행들
    for document in documents:                                            # 문서마다
        period = f"{document['effective_from']} ~ {document['expires_at'] or '현행'}"   # 시행일 ~ 만료일 (만료일 없으면 '현행')
        index_label = f"{document['index_status']} {document['index_progress']}%"      # 색인 상태 + 진행률 (예: 완료 100%)
        # 표 한 행 = 열 8개 (글자는 escape, 상태·색인은 배지 HTML)
        rows.append([
            escape(document["doc_id"]),                                   # 문서 ID
            escape(document["title"]),                                    # 문서명
            escape(document["version"]),                                  # 버전
            escape(period),                                               # 시행 ~ 만료
            badge_html(document["status"]),                               # 상태 배지 (현행/만료)
            escape(document["dept"]),                                     # 부서
            escape(document["security_level"]),                           # 보안등급
            badge_html(index_label),                                      # 색인 배지
        ])

    table(HEADERS, rows, align=ALIGNS)                                    # 머리글 + 행 + 열 정렬로 표 출력

# 화면 그리기 (랜더링)
def render() -> None:
    st.title("문서 관리")                                                  # 화면 제목
    st.caption("상태 필터가 「전체」라 지난 판까지 함께 보입니다. "
               "「현행」으로 좁히면 현재 유효한 최신본만 남습니다.")            # 사용 안내

    _metrics_row() # 지표 그리기 호출

    filters = _filter_row() # 필터 4개 그리기 호출

    if st.button("새 문서 업로드"):                                        # 업로드 버튼
        # st.info("업로드 화면은 다음 단계에서 만듭니다.")                    # 미구현 상태라 안내만 했었는데
        router.go('document_upload')                                     # 업로드 화면으로 이동 (app.py 의 페이지 키와 같아야 함)
        st.rerun()                                                       # 바로 다시 그려서 업로드 화면 표시

    with st.spinner("문서를 불러오는 중입니다..."):                          # 로딩 표시
        try:
            documents = api_client.list_documents(**filters, limit=100,
                                                  emp_no=session.emp_no())   # 필터 조건으로 문서 목록 요청 (최대 100건)
        except api_client.ApiError as exc:                                # 백엔드 오류면
            st.error(str(exc))                                            # 오류 표시
            return                                                        # 표는 그리지 않음

    if not documents:                                                     # 결과가 없으면
        st.info("조건에 맞는 문서가 없습니다. 필터를 바꿔 보세요.")             # 안내
        return

    st.caption(f"{len(documents)}건")                                     # 건수
    _table(documents)                                                     # 표 출력
