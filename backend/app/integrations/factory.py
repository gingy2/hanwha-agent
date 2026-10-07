# mock / live 분기의 유일한 지점
from __future__ import annotations
from functools import lru_cache
from app.core.config import get_settings
from app.core.exceptions import ModeNotAvailable
from app.integrations.ports import EmbedderPort, LLMPort

# reusable Claude adapter
@lru_cache
def _live_llm()->LLMPort:
    # live모드일 때만 import해서 ClaudeLLM 생성
    from app.integrations.llm_claude import ClaudeLLM
    return ClaudeLLM()

# 지금 설정에 맞는 LLM어댑터를 돌려주는 함수
def get_llm()->LLMPort:
    settings=get_settings()
    if not settings.is_live: 
        raise ModeNotAvailable(
            '테스트용 mock 어댑터는 만들지 않았음'
            '.env의 APP_MODE를 live로 두고 터미널에서 부르삼'
        )
    return _live_llm()

# 로컬 임베딩 어댑터를 하나 만들어두고 재사용
@lru_cache
def _local_embedder()->EmbedderPort:
    from app.integrations.local_embed import LocalEmbedder

    return LocalEmbedder()

# 상용 임베딩 어댑터를 하나 만들어두고, 재사용 
@lru_cache
def _upstage_embedder() -> EmbedderPort:
    from app.integrations.upstage import UpstageEmbedder 

    return UpstageEmbedder() 

# 현재 설정에 맞는 임베딩 어댑터 반환하는 함수
def get_embedder()->EmbedderPort:
    provider=get_settings().embed_provider
    if provider=='upstage':
        return _upstage_embedder()
    return _local_embedder()
