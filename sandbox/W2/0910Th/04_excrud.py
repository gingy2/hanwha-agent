from sqlalchemy import and_, desc, func, or_, select

from demo_models import Department, Document, SessionLocal, reset_db, seed


def main()->None:
    reset_db()
    seed()

    with SessionLocal() as session:
        stmt=(select(Document.id, Department.name)
        .join(Department, Document.dept_id == Department.id)
        )
        print('문서별 ID&부서명:')
        for doc_id, dept_name in session.execute(stmt):
            print(f'{doc_id} | {dept_name}')

        stmt=(select(Document.id, Department.name)
        .join(Department, Document.dept_id == Department.id)
        .where(Department.name == '보안')
        )
        print('보안팀 문서별 ID&부서명:')
        for doc_id, dept_name in session.execute(stmt):
            print(f'{doc_id} | {dept_name}')


if __name__=='__main__':
    main()
