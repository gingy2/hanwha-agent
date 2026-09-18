# 모델로 메시지를 보내기 전에 검증하는 기능
from __future__ import annotations

from app.core.config import get_settings
from app.core.exceptions import GuardTripped, RateLimited

# 질문의 최소 길이 지정
MIN_QUESTION_LEN=2

# 사용할 수 있는 LLM 모델 목록 (추후 .env에 모델을 바꾸면 여기도 변경하면 됨) 걍 .env꺼 불러와도 됨
ALLOWED_MODELS={'claude-haiku-4-5'}

# 사용자 질문 검사 함수: 검사 후 정리된 문자열로 반환
def check_question(text:str)->str:
    # text: 사용자가 보낸 질문 원문
    settings=get_settings()
    q=(text or "").strip()
    if len(q)<MIN_QUESTION_LEN:
        raise GuardTripped('질문을 더 길게 해주세요.')
    if len(q)>settings.max_input_chars:
        raise GuardTripped(f'현재 {len(q)}자. {settings.max_input_chars}자 이내로 질문을 줄여주세요.')
    return q

# LLM 모델 체크
def check_model(model:str)->str:
    # model: 호출하려는 모델 이름
    if model not in ALLOWED_MODELS:
        raise GuardTripped(f'{model}은 허용되지 않은 모델임')
    return model # 통과한 모델 이름 반환

# 오늘 사용한 호출 수가 상한을 넘었는지 확인하는 함수
def check_daily_limit(used_today:int)->None:
    # used_today: 오늘 이미 사용한 호출 수
    settings=get_settings()
    if used_today >= settings.daily_call_limit:
        raise RateLimited(
            f'오늘 호출 한도({settings.daily_call_limit}회)를 모두 소진함'
        )