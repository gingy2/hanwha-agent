''' 9/10
from app.models.base import Base
from app.models.document import Department, Document, DocumentVersion

__all__ = ['Base', 'Department', 'Document', 'DocumentVersion']
'''

# 9/11


from app.models.base import Base, TimestampMixin
from app.models.document import Document, DocumentVersion
from app.models.org import CLEARANCE, Department, User

__all__ = [
    "Base",
    "TimestampMixin",
    "Department",
    "User",
    "Document",
    "DocumentVersion",
    "CLEARANCE",
]