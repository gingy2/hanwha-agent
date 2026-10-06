from __future__ import annotations
import time                                          # 진행 상황을 다시 확인하기 전 잠깐 기다리기용 (_render_progress 에서 사용 예정)
import streamlit as st                               # 화면 구성
from core import api_client, router, session         # 백엔드 호출, 화면 이동, 로그인 사용자 정보
from core.api_client import ApiError                 # 백엔드 호출 실패 예외
from ui.badge import badge_html                      # 상태 배지(색 라벨) HTML (_render_progress 에서 사용 예정)
from ui.card import page_header                      # 화면 상단 제목·경로·설명
from ui.status import progress, steps                # 진행 막대, 단계 표시 (_render_progress 에서 사용 예정)

DEPTS = {'HR': '경영지원팀', 'HRGA': '인사총무', 'INFRA2': '인프라사업부 2팀', 'PMO': 'PMO', 'PU': '구매팀', 'SE': '보안팀'}   # 부서 ID → 화면 표시 이름
LEVELS = ['일반', '3급', '대외비']                     # 보안등급 선택지
ACCEPT = ['docx', 'pdf']                             # 업로드 허용 확장자

# 문서 업로드 화면 전체 그리기 (app.py 에서 호출)
def render()->None:
    page_header('문서 업로드', crumb='문서 관리>업로드',subtitle='DOCX, PDF를 파싱해 조항 단위와 표 단위로 나눠 저장.')   # 상단 제목·경로·설명
    if st.button('← 문서 관리'):                      # 뒤로 가기 버튼을 누르면
        router.go('documents')                       # 문서 관리 화면으로 이동
        st.rerun()                                   # 바로 다시 그려서 문서 관리 화면 표시
    job_id=st.session_state.get('upload_job')        # 진행 중인 업로드 작업 ID (없으면 None)
    # job_id가 유무에 따른 화면 분기
    if job_id:                                       # 업로드를 이미 보냈으면
        _render_progress(job_id)                     # 업로드 과정 나타내는 화면
    else:                                            # 아직이면
        _render_form()                               # 업로드 폼 페이지 화면

# 문서 등록 폼 화면 그리기
def _render_form() -> None:
    up = st.file_uploader('파일을 끌어다 놓으세요', type=ACCEPT)            # 파일 선택 (docx, pdf만)
    doc_id = st.text_input('문서번호', value='DOC-FI-009')                 # 문서번호 (실습용 기본값)
    title = st.text_input('문서명', value='법인카드 사용 지침')               # 문서명
    version = st.text_input('판 번호', value='v1.4')                       # 버전
    effective_from = st.text_input('시행일', value='2025-07-01')           # 시행일 (YYYY-MM-DD)
    dept_id = st.selectbox('소관 부서', options=list(DEPTS), format_func=DEPTS.get)   # 값은 부서 ID, 화면엔 부서 이름
    security_level = st.selectbox('보안등급', options=LEVELS)              # 보안등급 선택
    if st.button('등록', type='primary') and up is not None:              # 등록을 눌렀고 파일이 있으면
        try:
            res = api_client.upload_document(doc_id=doc_id, title=title, dept_id=dept_id, security_level=security_level, version=version, effective_from=effective_from, filename=up.name, content=up.getvalue(), emp_no=session.emp_no())   # 입력값 + 파일 내용(바이트)을 백엔드로 전송
        except ApiError as exc:                                          # 백엔드 오류면
            st.error(str(exc))                                           # 오류 표시
            return                                                       # 폼 화면에 그대로 머무름
        st.session_state['upload_job'] = res['job_id']                   # 백엔드가 준 작업 ID 저장
        st.rerun()                                                       # 화면 다시 그리기 → render 에서 진행 화면으로 분기
    st.caption('현행/만료를 고르는 일은 금주 버전 관리 챕터에서 진행할 예정입니다.')   # 안내 문구

# 1초에 한번씩 요청. 업로드 진행되는 화면 그릭. 업로드 완료되면 멈추기.
def _render_progress(job_id:str)->None:
    try:
        job = api_client.get_job(job_id, emp_no=session.emp_no())
    except ApiError as exc:
        st.error(str(exc))
        job = None
    if job is not None:
        st.markdown(badge_html(f"{job['status']} · {job['chunk_count']}청크"), unsafe_allow_html=True)
        steps(job['steps'])
        progress(job['progress'])
        if job['status'] == '완료':
            st.markdown(f"**{job['message']}**")
            st.caption('표 1개가 청크 1개로 저장됩니다.')
        if job['status'] not in ('완료', '실패'):
            time.sleep(1)
            st.rerun()
    if st.button('문서 하나 더 올리기'):
        st.session_state.pop('upload_job', None)
        st.rerun()