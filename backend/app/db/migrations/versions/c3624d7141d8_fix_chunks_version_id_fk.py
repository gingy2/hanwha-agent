"""fix chunks version_id fk

Revision ID: c3624d7141d8
Revises: 497b49a32beb
Create Date: 2026-10-06 11:23:24.135674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3624d7141d8'
down_revision: Union[str, Sequence[str], None] = '497b49a32beb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # chunks.version_id가 documents.id(문자열)를 잘못 참조하던 것을 document_versions.id(정수)로 수정
    with op.batch_alter_table('chunks') as batch_op:
        batch_op.drop_constraint('chunks_version_id_fkey', type_='foreignkey')
        batch_op.alter_column(
            'version_id',
            existing_type=sa.String(length=20),
            type_=sa.Integer(),
            existing_nullable=False,
            postgresql_using='version_id::integer',
        )
        batch_op.create_foreign_key('chunks_version_id_fkey', 'document_versions', ['version_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('chunks') as batch_op:
        batch_op.drop_constraint('chunks_version_id_fkey', type_='foreignkey')
        batch_op.alter_column(
            'version_id',
            existing_type=sa.Integer(),
            type_=sa.String(length=20),
            existing_nullable=False,
        )
        batch_op.create_foreign_key('chunks_version_id_fkey', 'documents', ['version_id'], ['id'])
