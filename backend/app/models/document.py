from __future__ import annotations

from datetime import date                                                 # 날짜 컬럼 타입
from sqlalchemy import ForeignKey, String, UniqueConstraint, Text         # 외래키, 길이 제한 문자열, 복합 유일 제약, 긴 문자열
from sqlalchemy.orm import Mapped, mapped_column, relationship            # 컬럼 타입 표시, 컬럼 정의, 테이블 간 관계
from app.models.base import Base, TimestampMixin, EMBED_DIM               # 모델 부모, 생성·수정 시각 컬럼, 임베딩 차원 수
from pgvector.sqlalchemy import Vector                                    # PostgreSQL 벡터 컬럼 타입 (pgvector)

''' 9/10 목 코드
class Department(Base, TimestampMixin):
    __tablename__='departments'
    id:Mapped[str]=mapped_column(String(20),primary_key=True)
    name:Mapped[str]=mapped_column(String(100),unique=True)
    documents:Mapped[list['Document']]=relationship(back_populates='department')

class Document(Base, TimestampMixin):
    __tablename__='documents'
    id:Mapped[str]=mapped_column(String(30),primary_key=True)
    title:Mapped[str]=mapped_column(String(200),index=True)
    dept_id:Mapped[str]=mapped_column(ForeignKey('departments.id'),index=True)
    security_level:Mapped[str]=mapped_column(String(20),default='일반',index=True)
    # 연관된 ORM 객체를 양방향으로 탐색할 관계 만듦
    department:Mapped[str]=relationship(back_populates='documents')
    versions:Mapped[list['DocumentVersion']]=relationship(back_populates='document',cascade='all,delete-orphan')

class DocumentVersion(Base, TimestampMixin):
    __tablename__='document_versions'
    __table_args__=(UniqueConstraint('doc_id','version',name='uq_document_version'),)
    id:Mapped[int]=mapped_column(primary_key=True, autoincrement=True)
    doc_id:Mapped[str]=mapped_column(ForeignKey('documents.id'),index=True)
    version:Mapped[str]=mapped_column(String(20))
    status:Mapped[str]=mapped_column(String(20),default='현행',index=True)
    effective_date:Mapped[date|None]
    file_path:Mapped[str]=mapped_column(String(500))
    page_count:Mapped[int]=mapped_column(default=0)
    document:Mapped[Document]=relationship(back_populates='versions')
'''

# 9/11 금
# 문서 모델
class Document(Base, TimestampMixin):
    __tablename__ = "documents"                                           # 테이블 이름

    id: Mapped[str] = mapped_column(String(20), primary_key=True)         # 문서번호 (예: DOC-HR-014) = 기본키
    title: Mapped[str] = mapped_column(String(200))                       # 문서명
    dept_id: Mapped[str] = mapped_column(ForeignKey("departments.id"), index=True)   # 소관 부서 (부서 테이블 참조)

    security_level: Mapped[str] = mapped_column(String(10), index=True)   # 보안등급 (일반 / 3급 / 대외비) → 권한 필터에 쓰여 인덱스

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))  # 담당자 (사용자 테이블 참조, 없을 수 있음)

    dept: Mapped["Department"] = relationship(back_populates="documents")    # 문서.dept → 부서 객체
    owner: Mapped["User | None"] = relationship(back_populates="documents")  # 문서.owner → 담당자 객체
    versions: Mapped[list["DocumentVersion"]] = relationship(             # 문서.versions → 이 문서의 모든 버전
        back_populates="document",                                        # 반대쪽: DocumentVersion.document
        order_by="DocumentVersion.version",                               # 버전 순으로 정렬해서 가져옴
    )

    # 현행중(시행중)인 버전 반환
    @property
    def current(self) -> "DocumentVersion | None":
        for v in self.versions:                                           # 버전마다
            if v.status == "현행":                                        # 현행이면
                return v                                                  # 그 버전 반환
        return None                                                       # 현행 버전이 없으면 None

# 문서 버전 모델
class DocumentVersion(Base, TimestampMixin):
    __tablename__ = "document_versions"                                   # 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True)                     # 자동 증가 번호 = 기본키
    doc_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)   # 어느 문서의 버전인지
    version: Mapped[str] = mapped_column(String(10))                      # 판 번호 (예: v2.0)
    status: Mapped[str] = mapped_column(String(10))                       # 현행 / 만료

    effective_from: Mapped[date]                                          # 시행일 (필수)
    expires_at: Mapped[date | None]                                       # 만료일 (현행이면 None)

    # 파일 자체는 디스크에 두고 DB에는 경로만 저장
    file_path: Mapped[str | None] = mapped_column(String(300))            # 원본 파일 경로
    file_format: Mapped[str] = mapped_column(String(10))                  # 확장자 (docx, pdf, hwpx ...)

    # 색인 관련 (추후 파싱/임베딩에 사용될 필드)
    chunk_count: Mapped[int] = mapped_column(default=0)                   # 저장된 청크 수
    embed_model: Mapped[str | None] = mapped_column(String(50))           # 임베딩에 쓴 모델 이름 (예: bge-m3)
    index_status: Mapped[str] = mapped_column(String(10), default="대기")  # 색인 상태 (대기 / 진행 / 완료 / 재임베딩 ...)
    index_progress: Mapped[int] = mapped_column(default=0)                # 색인 진행률 (0~100 %)
    indexed_at: Mapped[date | None]                                       # 색인 완료일

    document: Mapped["Document"] = relationship(back_populates="versions")    # 버전.document → 문서 객체
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="version", cascade="all, delete-orphan")   # 버전.chunks → 청크들 (버전 삭제 시 청크도 함께 삭제)

    __table_args__ = (UniqueConstraint("doc_id", "version", name="uq_doc_version"),)   # 같은 문서에 같은 판 번호는 하나만

    # 화면에 '시행~만료'칸에 그대로 들어갈 문자열 반환
    @property
    def period(self) -> str:
        if self.expires_at is None:                                       # 만료일이 없으면 (현행)
            return f"{self.effective_from} ~"                             # '2025-07-01 ~'
        return f"{self.effective_from} ~ {self.expires_at}"               # '2024-01-01 ~ 2025-06-30'

    # 검색 결과에 내보내도 되는지 판단하는 기능: 현행이며 색인이 완료된 경우에만 반환
    @property
    def is_searchable(self) -> bool:
        return self.status == "현행" and self.index_status == "완료"       # 둘 다 만족해야 검색 대상

# 청크 한 조각 저장할 수 있는 모델
class Chunk(Base):
    __tablename__ = "chunks"                                              # 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True)                     # 자동 증가 번호 = 기본키
    version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id"), index=True)   # 어느 문서 버전의 청크인지
    ord: Mapped[int] = mapped_column(default=0)       # 문서 안에서의 순서
    kind: Mapped[str] = mapped_column(String(16))     # '조항' | '표'
    locator: Mapped[str] = mapped_column(String(200)) # '제14조(숙박비) - 별표1'
    text: Mapped[str] = mapped_column(Text)           # 내용. 표는 마크다운으로 처리

    embedding:Mapped[list[float]|None]=mapped_column(Vector(EMBED_DIM),nullable=True)   # 임베딩 벡터 (EMBED_DIM 차원, 아직 안 만들었으면 NULL)

    version: Mapped["DocumentVersion"] = relationship(back_populates="chunks")   # 청크.version → 문서 버전 객체
