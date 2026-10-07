from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

# 임베딩 벡터 차원 수 (bge-m3 = 1024). 바꾸면 chunks.embedding 컬럼도 마이그레이션 필요
EMBED_DIM = 1024

# 모든 모델의 부모
class Base(DeclarativeBase):
    pass

# DB 테이블 또는 공통 기반 클래스 정의
class TimestampMixin:
    created_at:Mapped[datetime]=mapped_column(default=datetime.utcnow)
    updated_at:Mapped[datetime]=mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

