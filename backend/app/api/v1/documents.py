from fastapi import APIRouter, Query
from typing import Annotated

from backend.app.core.exceptions import NotFound
from backend.app.schemas.document import DocumentOut
# from backend.app.core.config import Settings
# from app.api.v1.deps import SettingsDep

# 문서 API를 모아두는 라우터
router=APIRouter(
    prefix='/documents',
    tags=['documents']
)

# DB 사용 전 임시 데이터 추가 (추후 삭제 예정)
_DOCS:list[dict] = [
    {
        "doc_id": "DOC-HR-014",
        "title": "2026년 휴가 운영 규정",
        "dept": "인사",
        "security_level": "일반",
        "file_format": "docx",
        "status": "active",
        "secret_note": "담당자 메모 - 개정 예고", # 이런 식으로 DB에는 넣어놓고 꺼내보는건 선택사항임
    },
    {
        "doc_id": "DOC-HR-021",
        "title": "복리후생 운영 지침",
        "dept": "인사",
        "security_level": "일반",
        "file_format": "pdf",
        "status": "active",
    },
    {
        "doc_id": "DOC-SE-011",
        "title": "정보보안 관리 규정",
        "dept": "보안",
        "security_level": "3급",
        "file_format": "pdf",
        "status": "active",
    },
    {
        "doc_id": "DOC-PU-007",
        "title": "구매 계약 업무 지침",
        "dept": "구매",
        "security_level": "대외비",
        "file_format": "docx",
        "status": "active",
    },
]

# 문서 목록 요청
@router.get('',response_model=list[DocumentOut])
def list_documents(
#     settings:Settings   # 의존성 주입: 별칭으로 처리
    dept:str|None=None,
    security_level:str|None=None,
    file_format:str|None=None,
    limit:Annotated[int,Query(ge=1,le=100)]=20
)->list[dict]:
    result=_DOCS.copy()

    if dept is not None:
        result=[doc for doc in result if doc['dept']==dept]

    if security_level is not None:
        result=[doc for doc in result if doc['security_level']==security_level]

    if file_format is not None:
        result=[doc for doc in result if doc['file_format']==file_format]

    return result[:limit]

# 문서 1개 조회: ...8000/documents/문서id값
# @router.get('/{doc_id}')
# def get_document(doc_id:str)->dict:
#     for doc in documents:
#         if doc['doc_id']==doc_id:
#             return doc
#     return {
#         'doc_id':doc_id,
#         'message': '문서를 찾지 못했음'
#     }
@router.get('/{doc_id}',response_model=DocumentOut)
def get_document(doc_id:str)->dict:
    for doc in _DOCS:
        if doc['doc_id']==doc_id:
            return doc
    raise NotFound(f'{doc_id} 문서를 찾지 못했음')

# 예외 테스트
@router.get('/find')
def find_doc():
    raise NotFound('문서 못찾음')