# Langfuse 관측(트레이싱) 설정: 앱 시작/종료 시 한 번씩만 부르면 된다.
from __future__ import annotations

from langfuse.decorators import langfuse_context

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


def configure_langfuse() -> None:
    settings = get_settings()
    langfuse_context.configure(
        public_key=settings.langfuse_public_key,
        secret_key=(
            settings.langfuse_secret_key.get_secret_value()
            if settings.langfuse_secret_key is not None
            else None
        ),
        host=settings.langfuse_host,
        enabled=settings.langfuse_enabled,
    )
    if settings.langfuse_enabled:
        log.info("Langfuse tracing 활성화 (host=%s)", settings.langfuse_host)


def flush_langfuse() -> None:
    # 프로세스가 끝나기 전에 큐에 쌓인 트레이스를 마저 전송한다.
    langfuse_context.flush()
