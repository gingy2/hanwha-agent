from __future__ import annotations
from datetime import datetime
from sqlalchemy import Float,ForeignKey,Integer,String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

# UsageLog는 LLM 한번 호출할 때마다의 사용량과 원가를 저장할 테이블(모델)
class UsageLog(Base,TimestampMixin):
    __tablename__='usage_logs'
    id:Mapped[int]=mapped_column(primary_key=True)
    run_id:Mapped[str]=mapped_column(String(32),ForeignKey('runs.id'),nullable=False)
    model:Mapped[str]=mapped_column(String(64))
    input_tok:Mapped[int]=mapped_column(Integer,default=0)
    cache_tok:Mapped[int]=mapped_column(Integer,default=0)
    output_tok:Mapped[int]=mapped_column(Integer,default=0)
    cost_krw:Mapped[float]=mapped_column(Float,default=0.0)
    occured_at:Mapped[datetime]=mapped_column(default=datetime.now)
