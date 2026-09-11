from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

# 모든 모델의 부모
class Base(DeclarativeBase):
    pass

# DB 테이블 또는 공통 기반 클래스 정의
class TimestampMixin:
    created_at:Mapped[datetime]=mapped_column(default=datetime.utcnow)
    updated_at:Mapped[datetime]=mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

