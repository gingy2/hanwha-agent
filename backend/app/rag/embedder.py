# 임베딩 진입점
from __future__ import annotations
from collections.abc import Callable
from app.integrations.factory import get_embedder

# 청크 텍스트 목록을 벡터 목록으로 변환해주는 함수
def embed_documents(
        texts:list[str],
        *,
        batch:int=50,
        on_progress:Callable[[int,int],None]|None=None,
)->list[list[float]]:
    embedder=get_embedder()
    out:list[list[float]]=[]
    total=len(texts)
    for i in range(0, total, batch):
        out.extend(embedder.embed_documents(texts[i:i+batch]))
        if on_progress is not None:
            on_progress(min(i+batch, total),total)
    return out                                    # 반복이 다 끝난 뒤 반환 (안쪽에 있으면 첫 묶음만 반환됨)

# 질문 한 문장을 벡터로 변환하는 함수
def embed_query(text:str)->list[float]:
    return get_embedder().embed_query(text)

# DB(document_versions.embed_model)에 남길 모델 이름: 예) local/bge-m3, upstage/embedding-passage
def model_label()->str:
    from pathlib import Path
    from app.core.config import get_settings
    s=get_settings()
    if s.embed_provider=='upstage':
        return f'upstage/{s.upstage_embed_model or "-"}'
    return f'local/{Path(s.embed_model_dir).name}'

# 현재 사용중인 어댑터가 만들어주는 벡터 길이
def embed_dim()->int:
    return int(getattr(get_embedder(),'dim',0))