from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


# 2026.09.11 금요일 - 어제의 코드를 수정함. 근데 뭐가 뭔지 모르겠음

# 만든 엔진을 URL별로 담아두는 상자
_ENGINES:dict[str, Engine]={}

# 엔진 하나 만들어 주는 함수
def get_engine(url:str|None=None)->Engine:

    resolved=url or get_settings().database_url
    if resolved in _ENGINES:
        return _ENGINES[resolved]

    # SQLite 설정 추가
    connect_args:dict[str, object]={}
    is_sqlite=resolved.startswith('sqlite')
    if is_sqlite:
        connect_args['check_same_thread']=False

    # 엔진 생성
    engine=create_engine(resolved, connect_args=connect_args)

    # SQLite 설정 추가
    if is_sqlite:
        @event.listens_for(engine,'connect')
        def _enable_sqlite_foreign_keys(dbapi_connection, connection_record)->None:
            cursor=dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()

    _ENGINES[resolved]=engine
    return engine


# 세션 공장 생성
def get_sessionmaker(engine:Engine | None=None)-> sessionmaker[Session]:
    return sessionmaker(bind=engine or get_engine(), expire_on_commit=False)


'''
2026.09.10 목요일 코드

# DB 경로: 환경변수 참고. 없으면 app.db 사용
DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///./app.db')

# 엔진 생성
def build_engine() -> Engine:
    
    options: dict = {"pool_pre_ping": True} # 연결 확인 옵션

    if DATABASE_URL.startswith("sqlite"):   # sqlite라면
        options["connect_args"] = {"check_same_thread": False} # 스레드 체크 옵션 추가

    db_engine = create_engine(DATABASE_URL, **options) # 엔진 생성: 옵션 풀어서 주기

    if DATABASE_URL.startswith("sqlite"):
        # sqlite라면 외래키 검사 설정 추가
        @event.listens_for(db_engine, "connect")
        def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return db_engine

# 세션 공장 생성: 어플리케이션 전체에서 하나만 만들면 됨
engine=build_engine()
SessionLocal=sessionmaker(bind=engine, expire_on_commit=False)
'''

# 편의 함수
@contextmanager
def session_scope():
    session=get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def main()->None:
    engine=get_engine()
    print('DB_URL:',engine.url)
    print('DB 종류:',engine.dialect.name)

    with session_scope() as session:
        print('select 결과:', session.execute(text('SELECT 1')).scalar_one())

# VSCode에 이 파일을 직접 실행할 때만 작동되도록 설정. (main이 뭐길래?)
if __name__=='__main__':
    main()