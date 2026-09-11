"""
서비스: 사용자 요청에 대한 로직을 처리하는 곳.
DB 정보가 필요하면 repository를 호출.
트랜잭션을 여닫는 위치가 여기.
"""
from __future__ import annotations

from datetime import date

from pytest import Session

from app.core.exceptions import NotFound, ValidationFailed
from app.db.session import session_scope    # session DB 접속 통로
from app.models.document import Document, DocumentVersion   # 데이터 넣는 가방
from app.repositories import document_repo  # repository DB 접속시 필요

# 사용자에게 전달할 데이터를 예쁘게(?) 만들어주는 함수
def _to_out(version: DocumentVersion, document: Document) -> dict:
   
    return {
        "doc_id": document.id,
        "title": document.title,
        "dept": document.dept.name,
        "version": version.version,
        "security_level": document.security_level,
        "file_format": version.file_format,
        "status": version.status,
        "effective_from": version.effective_from,
        "expires_at": version.expires_at,
        "index_status": version.index_status,
        "index_progress": version.index_progress,
    }

# 문서 목록 조회
def list_documents(
    *,
    dept_id: str | None = None,
    security_level: str | None = None,
    status: str | None = None,
    q: str | None = None,
    limit: int = 50,
) -> list[dict]:

    # session 만들어 repository 호출해 결과 받기
    with session_scope() as s:
        
        # repository(document_repo)의 문서 목록 함수 호출
        rows = document_repo.list_documents(
            s,
            dept_id=dept_id,
            security_level=security_level,
            status=status,
            q=q,
            limit=limit,
        )
        # 위 _to_out의 rows에 있는 문서 버전과 문서 자체를 전달해서 예쁘게 만들어 리스트로 전달
        return [_to_out(version, document) for version, document in rows]

# 문서 1개 조회: 문서 ID값 외부에서 전달해주면 해당 문서 1개 조회해서 반환해줌
def get_document(*, doc_id: str) -> dict:

    # 세션 생성해서 문서 1개 조회
    with session_scope() as s:
        document = document_repo.get_document(s, doc_id)
        if document is None:
            raise NotFound(f"문서를 찾을 수 없습니다: {doc_id}")
        current = document.current
        if current is None:
            raise NotFound(f"현행 버전이 없습니다: {doc_id}")
        return _to_out(current, document)

# 문서 등록(저장) 처리
def create_document(
    *,
    doc_id: str,
    title: str,
    dept_id: str,
    security_level: str,
    version: str,
    effective_from: date,
    file_path: str,
    file_format: str,
    owner_id: int | None = None,
) -> dict:

    with session_scope() as s:
        document = document_repo.get_document(s, doc_id)
        created = document is None
        if document is None:
            document = Document(
                id=doc_id,
                title=title,
                dept_id=dept_id,
                security_level=security_level,
                owner_id=owner_id,
            )
            s.add(document)
            s.flush()
        elif any(v.version == version for v in document.versions):
            raise ValidationFailed(
                f"{doc_id} 의 {version} 은(는) 이미 등록되어 있습니다. "
                "판 번호를 올려 다시 올려 주세요."
            )

        document_repo.add_version(
            s,
            document,
            version=version,
            status="현행",
            effective_from=effective_from,
            expires_at=None,
            file_path=file_path,
            file_format=file_format,
            index_status="대기",     
        )
        return {
            "doc_id": document.id,
            "title": document.title,
            "version": version,
            "file_format": file_format,
            "file_path": file_path,
            "created": created,
        }
