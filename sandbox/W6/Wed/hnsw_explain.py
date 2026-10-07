from __future__ import annotations

import sys
import time
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[3]                   # sandbox/W6/Wed → 프로젝트 루트
sys.path.insert(0, str(ROOT / "backend"))                    # 어디서 실행해도 `from app...` 가 되게

REPEAT=10
TOP_K=5
WIDTH=88

PICK=text('SELECT embedding::text FROM chunks '              # 끝에 공백: 다음 문자열과 붙을 때 'chunksWHERE' 가 되지 않게
          'WHERE embedding IS NOT NULL ORDER BY id LIMIT 1')
SEARCH=('SELECT id FROM chunks WHERE embedding IS NOT NULL '   # 끝에 공백: 'NULLORDER' 방지
        'ORDER BY embedding <=> CAST(:q AS vector) LIMIT :k')
NOISE=('Sort Key', 'Sort Method', 'Buffers', 'Planning', 'Execution')

def average_ms(session, qvec:str)->float:
    started=time.perf_counter()
    for _ in range(REPEAT):
        session.execute(text(SEARCH), {'q':qvec, 'k':TOP_K}).all()
    return (time.perf_counter()-started)/REPEAT*1000

def show_plan(session, qvec: str, *, seqscan: str) -> None:
    print(f"\n[ enable_seqscan = {seqscan} ]")
    session.execute(text(f"SET enable_seqscan = {seqscan}"))
    rows = session.execute(text("EXPLAIN ANALYZE " + SEARCH),
                           {"q": qvec, "k": TOP_K}).all()
    for (line,) in rows:
        if line.strip().startswith(NOISE):  
            continue
        print(line[:WIDTH] + (" ..." if len(line) > WIDTH else ""))

def main() -> None:
    try:
        from app.db.session import session_scope
        with session_scope() as s:
            qvec = s.execute(PICK).scalar()
            if qvec is None:
                print("벡터가 든 청크가 한 줄도 없습니다. 문서 한 건 올린 뒤 다시 돌리세요.")
                return
            print(f"같은 질의 {REPEAT}회 평균 : {average_ms(s, qvec):.1f} ms")
            show_plan(s, qvec, seqscan="off")  
            show_plan(s, qvec, seqscan="on")   
            print("\n계획은 바뀌었다. 시간은 이 규모에서 바뀌지 않는다.")
    except Exception as exc:
        print(f"DB 에 붙지 못했습니다: {type(exc).__name__} — docker compose up -d 로 "
              "postgres 를 먼저 띄운 뒤 다시 돌리세요.")
        print(f"  (실제 오류: {str(exc).splitlines()[0][:200]})")   # 연결 문제가 아닐 수도 있으니 원문도 보여 줌

if __name__ == "__main__":
    main()