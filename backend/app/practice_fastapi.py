from typing import Annotated
from fastapi import FastAPI, Query

app=FastAPI(
    title='사내 업무 에이전트 연습',
    version='0.1.0'
)
'''
# --- 사용자의 요청을 처리해 줄 URI 매핑 함수들 ---
# 요청 함수 GET /health
@app.get('/health')
def health()->dict:
    return {'status':'ok'}  # 리턴값이 요청에 응답해줄 데이터

# 쿼리 파라미터
# ex. 문서 목록을 조회하는 함수
@app.get('/documents')
def list_documents(
    dept:str|None=None,
    limit:int=20
)->dict:
    return {
        'dept':dept,
        'limit':limit
    }

# * 요청 범위 제한 *
# ex. 문서 목록 조회 시 범위 제한 부여
@app.get('/document-limited')
def list_documents_limited(
    dept:str|None=None,
    limit:Annotated[int,Query(ge=1,le=100)]=20
)->dict:
    return {
        'dept':dept,
        'limited':limit
    }

# * 고정 경로를 위에 배치 *
@app.get('/documents/latest')
def get_document2()->dict:
    return {
        'level':'latest',
        'title':f'latest 문서'
    }

# * 경로 변수 *
# ex. 특정 문서를 조회하는 함수
@app.get('/documents/{doc_id}')
def get_document(doc_id:str)->dict:
    return {
        'doc_id':doc_id,
        'title':f'{doc_id}번 문서'
    }

# ex. 타입 검증 - 레벨 조회
@app.get('/documents/{level}')
def get_document_level(level:str)->dict:
    return {
        'level':level,
        'title':f'{level} 권한 문서'
    }
'''

documents = [
    {
        "doc_id": "DOC-HR-014",
        "title": "2026년 휴가 운영 규정",
        "dept": "인사",
        "security_level": "일반",
        "file_format": "docx",
        "status": "active",
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

@app.get('/health')
def health()->dict:
    return {'status':'ok'}

# 문서 조회 
@app.get('/practice/documents')
def search_documents(
    dept:str|None=None,
    security_level:str|None=None,
    file_format:str|None=None,
    limit:Annotated[int,Query(ge=1,le=100)]=20
)->list[dict]:
    # 원본 복사
    result=documents.copy()
    # 부서 조건
    if dept is not None:
        result=[doc for doc in result if doc['dept']==dept]
    # 보안 등급 조건
    if security_level is not None:
        result=[doc for doc in result if doc['security_level']==security_level]
    # 파일 형식 조건
    if file_format is not None:
        result=[doc for doc in result if doc['file_format']==file_format]
    # limit 조건
    return result[:limit]

'''
# 인사 부서의 데이터 조회
@app.get('/practice/documents?dept=인사')
def get_dept_info(dept:'인사')->dict:
    return {"doc_id": doc_id,
            "title": title,
            "dept": dept,
            "security_level": level,
            "file_format": format,
            "status": status}

# 보안 등급 3급 데이터 조회                           
@app.get('/practice/documents?security_level=3급')
def get_secured_data()->dict:
    return {}

# pdf 문서 조회
@app.get('/practice/documents?file_format=pdf')
def get_pdf()->dict:
    return {}

# 인사 부서의 pdf 파일 조회
@app.get('/practice/documents?dept=인사&file_format=pdf')
def get_dept_pdf()->dict:
    return {}
'''