"""
시드를 적재한다. 몇 번을 돌려도 결과가 같아야 한다(멱등).
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.seed_data import DEPARTMENTS, DOCUMENTS, USERS
from app.db.session import session_scope
from app.models import Department, Document, DocumentVersion, User

# 4개 테이블의 행의 수를 반환하는 함수
def count_rows(session: Session) -> dict[str, int]:

    return {
        "departments": session.scalar(select(func.count()).select_from(Department)) or 0,
        "users": session.scalar(select(func.count()).select_from(User)) or 0,
        "documents": session.scalar(select(func.count()).select_from(Document)) or 0,
        "versions": session.scalar(select(func.count()).select_from(DocumentVersion)) or 0,
    }

# 비어있을 때만 데이터를 적재하는 함수
def seed_all(session: Session | None = None) -> dict[str, int]:
    
    if session is not None: # 세션이 있으면 해당 세션을 _seed 적재
        return _seed(session)
    with session_scope() as s: # 세션이 없으면 세션을 만들어서 _seed 적재
        return _seed(s)

# 실제로 적재 처리하는 함수 (별도 분리)
def _seed(session: Session) -> dict[str, int]:

    # 실제로 적재된 게 있는지 확인: 있으면 갯수 세서 반환
    if session.scalar(select(func.count()).select_from(Document)):
        return count_rows(session)

    # 실제로 적재된 게 없으면 add_all
    session.add_all(Department(**row) for row in DEPARTMENTS) # 부서
    session.add_all(User(**row) for row in USERS) # 사용자
    session.flush()

    # 문서 적재
    for doc in DOCUMENTS:

        # dict에서 version들만 출력?제외? // 빼낸다는게 없앤다는 말이야 뭐야
        fields = {k: v for k, v in doc.items() if k != "versions"}
        # 문서 저장
        session.add(Document(**fields))
        session.flush()
        # 문서 버전 저장
        session.add_all(
            DocumentVersion(doc_id=doc["id"], **ver) for ver in doc["versions"]
        )
    session.flush()

    # 전체 몇 개 적재됐는지 count해서 반환
    return count_rows(session)
