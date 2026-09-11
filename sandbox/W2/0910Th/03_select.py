from sqlalchemy import and_, desc, func, or_, select

from demo_models import Document, SessionLocal, reset_db, seed

def main()->None:
    reset_db()
    seed()      # sample data

    with SessionLocal() as session:
        stmt=select(Document)   #select * from documents
        print('전체:',len(session.scalars(stmt).all()),'건')

        print('만들어진 SQL문')
        print(select(Document.id, Document.title).where(Document.dept_id=='HRGA'))

        # where 조건은 비교연산자 사용
        stmt=select(Document).where(Document.dept_id=='HRGA')
        print('인사총무:',[d.id for d in session.scalars(stmt)])

        # 조건이 여러개-> 이어서 작성 == and 효과
        stmt=select(Document).where(Document.dept_id=='HRGA').where(Document.page_count>=10)
        # 조건이 여러개-> and_, or_로 묶기
        stmt=select(Document).where(and_(Document.dept_id=='HRGA').where(Document.page_count>=10))
        stmt=select(Document).where(or_(Document.dept_id=='HRGA').where(Document.page_count>=10))

        # in_, like, is_ (None)
        print('in:',[d.id from d in session.scalars(select(Document).where(Document.dept_id.in_(['SE','PMO'])))])
        print('in:',[d.id from d in session.scalars(select(Document).where(Document.title.like('%규정%')))])

        # order_by, limit: 정렬, 개수 제한
        stmt=select(Document).order_by(desc(Document.page_count)).limit(3)
        print('최다 쪽수 Top 3', [(d.id, d.page_count) for d in session.scalars(stmt)])

        # 집계함수: func 하위 기능 such as count(), sum(), avg(), ...
        total=session.scalar(select(func.count()).select_from(Document))
        page=session.scalar(select(func.sum(Document.page_count)))
        print('전체 건수:', total)
        print('전체 쪽수:', page)

if __name__=='__main__':
    main()

'''
D:\hanwha-agent\sandbox\W2\0910Th> python -m 02_session_crud
'''