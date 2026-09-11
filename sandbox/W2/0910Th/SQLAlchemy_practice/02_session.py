from contextlib import contextmanager
from typing import final # commit, rollback 자동 처리 위해 import
from sqlalchemy import create_engine, event, text # 엔진, 연결 이벤트, sql 실행 도구 등
from sqlalchemy.orm import sessionmaker

# 엔진 생성
engine=create_engine(
    'sqlite:///./sandbox/w2/0910Th/SQLAlchemy_practice.db',
    connect_args={'check_same_thread':False},
    pool_pre_ping=True,
)

# 새 SQLite 연결이 생길 때마다 외래키 검사 실행
@event.listens_for(engine,'connect')
def enable_sqlite_foreign_keys(dbapi_connection,_connection_record)->None:
    cursor=dbapi_connection.cursor()            # sqlite3 연결의 커서 가져오기
    cursor.execute('PRAGMA foreign_keys=ON')   # 이 연결에서 외래키 제약 조건 검사 활성화
    cursor.close()

# 요청이나 작업마다 새 session을 만들 공장 준비
SessionLocal=sessionmaker(bind=engine, expire_on_commit=False)

# 세션의 시작, 성공, 실패, 종료 규칙 한 곳에 모으기
@contextmanager
def session_scope():
    session=SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def main()->None:
    # session을 통해서 실제 DB에 접속
    with session_scope() as session:
        result=session.execute(text('SELECT 1')).scalar_one()
        print('select 결과:',result)

# VSCode에서 이 파일을 직접 run할 때만 실행되도록 설정
if __name__=='__main__':
    main()