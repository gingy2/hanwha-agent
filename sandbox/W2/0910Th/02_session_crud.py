from demo_models import Department, Document, SessionLocal, reset_db

def main()->None:
    reset_db()  # 원활한 테스트를 위한 DB 초기화

    # 세션 공장에서 session 하나 생성
    with SessionLocal() as session:
        # add로 추가. 객체를 저장 대상으로 등록해라-> 아직 DB에 반영 전
        hr = Department(id='HR', name='인사')
        session.add(hr)
        print('added:', session.new)

        # flush로 등록 내용을 SQL로 전송-> 아직 commit 전
        session.flush()
        print('flushed:', session.new)
        print('DB에서 조회는 가능:', session.get(Department,'HR'))

        # add_all: 여러 건을 한번에 등록
        session.add_all([
            Document(id='DOC-HR-012',title='출장 여비 규정',dept_id='HR',page_count=18),
            Document(id='DOC-HR-013',title='재택 근무 지침',dept_id='HR',page_count=9),
        ])

        # commit으로 데이터 등록 확정
        session.commit()
        print('successfully committed')

    with SessionLocal() as session:
        # get: 기본키로 한 건 조회
        document=session.get(Document,'DOC-HR-012')
        print('get:',document,'/ 없는 ID:',session.get(Document,'DOC-HR-999'))

        # 업뎃X -> 객체의 속성만 변경
        document.page_count=20
        print('updated-dirty:',session.dirty)
        session.commit()
        print('committed - page_count:', session.get(Document,'DOC-HR-012'))

    with SessionLocal() as session:
        # rollback: 확정 전에 되돌리면 아무 일도 없던 것처럼 되돌아감
        session.add(Document(id='DOC-TMP-001',title='Oopsy',dept_id=HR))
        session.flush() # 쿼리문 나감-> 조회시 조회됨 // 이게 무슨 어릴때 난 어렸지 같은;
        print('before rollback:',session.get(Document,'DOC-TMP-001'))
        session.rollback()  # 되돌리기
        print('after rollback:',session.get(Document,'DOC-TMP-001'))

        # delete: 삭제도 객체단위
        doc=session.get(Document,'DOC-HR-013')
        session.delete(doc)
        session.commit()
        print('after deletion:',session.get(Document,'DOC-HR-013'))

if __name__=='__main__':
    main()

'''
D:\hanwha-agent\sandbox\W2\0910Th> python -m 02_session_crud
'''