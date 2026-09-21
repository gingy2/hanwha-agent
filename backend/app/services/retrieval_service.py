from __future__ import annotations

import re

from langfuse.decorators import langfuse_context, observe

from app.core.config import get_settings
from app.db.seed_chunks import CHUNKS
from app.db.seed_data import DOCUMENTS

# 보안등급 서열: 사용자 등급 이상인 문서만 열람 가능
CLEARANCE_RANK = {"일반": 0, "3급": 1, "대외비": 2}

# 질문과 청크가 이 비율보다 덜 겹치면 근거로 쓰지 않는다
MIN_SCORE = 0.2


# 문서 번호 -> (제목, 보안등급, 현행 버전)
def _doc_index() -> dict[str, dict]:
    index = {}
    for doc in DOCUMENTS:
        current = next((v["version"] for v in doc["versions"] if v["status"] == "현행"), None)
        index[doc["id"]] = {
            "title": doc["title"],
            "security_level": doc["security_level"],
            "current_version": current,
        }
    return index


# 한국어는 띄어쓰기로 자르면 조사 때문에 겹침이 안 잡혀서 글자 2개씩 묶어서 비교한다
def _bigrams(text: str) -> set[str]:
    compact = re.sub(r"[^0-9A-Za-z가-힣]", "", text)
    return {compact[i : i + 2] for i in range(len(compact) - 1)}


# 질문 글자쌍 중 청크에도 있는 비율 (0~1)
def _score(question_grams: set[str], chunk_text: str) -> float:
    if not question_grams:
        return 0.0
    return len(question_grams & _bigrams(chunk_text)) / len(question_grams)


# 질문에 맞는 근거 청크를 top_k개 찾아 ClaudeLLM._context_block 이 읽는 형태로 반환
@observe(name="retrieve-documents", capture_input=False, capture_output=False)
def retrieve(question: str, *, user: dict, top_k: int | None = None) -> list[dict]:
    top_k = top_k or get_settings().top_k
    user_rank = CLEARANCE_RANK.get(user.get("clearance", "일반"), 0)
    docs = _doc_index()
    question_grams = _bigrams(question)

    scored = []
    for chunk in CHUNKS:
        doc = docs.get(chunk["doc_id"])
        # 현행 버전이고 열람 권한이 있는 문서만 후보
        if doc is None or chunk["version"] != doc["current_version"]:
            continue
        if CLEARANCE_RANK[doc["security_level"]] > user_rank:
            continue
        score = _score(question_grams, f'{chunk["locator"]} {chunk["text"]}')
        if score >= MIN_SCORE:
            scored.append((score, chunk, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    contexts = [
        {
            "doc_id": chunk["doc_id"],
            "title": doc["title"],
            "version": chunk["version"],
            "locator": chunk["locator"],
            "score": score,
            "quote": chunk["text"],
        }
        for score, chunk, doc in scored[:top_k]
    ]

    langfuse_context.update_current_observation(
        input=question,
        output=[
            {"doc_id": c["doc_id"], "locator": c["locator"], "score": round(c["score"], 2)}
            for c in contexts
        ],
        metadata={"top_k": top_k, "clearance": user.get("clearance"), "candidates": len(CHUNKS)},
    )
    return contexts
