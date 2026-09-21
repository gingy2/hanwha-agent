# 샘플 근거 청크. 실제 파싱/임베딩 파이프라인이 생기기 전까지 검색 단계를 검증하기 위한 대용 데이터.
# 내용은 tests/golden/chat_golden.json 의 기대 답변과 일치하도록 맞췄다.
from __future__ import annotations

CHUNKS: list[dict] = [
    {
        "doc_id": "DOC-HR-014", "version": "v2.0", "locator": "표지 · p.1",
        "text": "국내출장 여비 규정 v2.0. 이 규정은 2025년 7월 1일부터 시행하는 현행 판이다.",
    },
    {
        "doc_id": "DOC-HR-014", "version": "v2.0", "locator": "제5조(출장 신청) · p.3",
        "text": "국내출장은 출발 3일 전까지 출장신청서를 작성하여 소속 팀장의 승인을 받아야 한다.",
    },
    {
        "doc_id": "DOC-HR-014", "version": "v2.0", "locator": "제12조(숙박비) · p.6",
        "text": "국내출장 숙박비는 1박 70,000원 이내에서 영수증에 따라 실비로 정산한다.",
    },
    {
        "doc_id": "DOC-HR-014", "version": "v2.0", "locator": "제18조(정산) · p.9",
        "text": "출장자는 출장 종료 후 7일 이내에 출장비 정산서와 영수증을 제출하여 정산해야 한다.",
    },
    {
        "doc_id": "DOC-SE-003", "version": "v2.2", "locator": "표지 · p.1",
        "text": "정보보안 지침 v2.2. 이 문서는 대외비이며 열람 권한이 있는 임직원만 볼 수 있다.",
    },
    {
        "doc_id": "DOC-SE-003", "version": "v2.2", "locator": "제12조(반출 통제) · p.14",
        "text": "대외비 문서와 저장매체는 보안팀장의 사전 승인 없이 사외로 반출할 수 없다.",
    },
]
