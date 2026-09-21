# Claude 어댑터 
from __future__ import annotations
import json
import re
import time
from pathlib import Path

from langfuse.decorators import langfuse_context, observe

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.integrations.ports import LLMResult

# 로거 생성
log = get_logger(__name__)

# 프롬프트 파일의 위치
PROMPTS = Path(__file__).resolve().parent.parent / 'prompts'  # app/prompts
# 요금: USD/mTok - 모델 변경 시 여기만 수정하면 됨
PRICING = {'input': 1.0, 'cache_write': 1.25, 'cache_read': 0.1, 'output': 5.0}
USD_KRW = 1400.0

# 호출 한번의 비용을 원화로 어림잡아 계산해주는 함수
def estimate_cost_krw(input_tok: int, output_tok: int) -> float:
    usd = input_tok / 1000000 * PRICING['input'] + output_tok / 1000000 * PRICING['output']
    return round(usd * USD_KRW, 1)

# 프롬프트 파일을 하나 읽어서 문자열로 리턴해주는 함수
def _load_prompt(name:str)->str:
    path=PROMPTS/name
    return path.read_text(encoding="utf-8") if path.exists() else ""

# 근거 문서 목록을 모델이 읽을 문자열 한 덩어리로 변환해서 리턴하는 함수
def _context_block(contexts:list[dict])->str:
    # contexts: 근거 항목 목록
    lines=[]
    for i, c in enumerate(contexts, 1):
        lines.append(
            f"[근거{i}] {c.get('doc_id')} {c.get('title')} {c.get('version')} · {c.get('locator')} "
            f"(유사도 {c.get('score', 0):.2f})\n{c.get('quote') or c.get('text') or ''}"
        )
    return "\n\n".join(lines) if lines else "(근거 문서 없음)"

# Claude Messages API 어댑터
class ClaudeLLM:
    name='claude'

    # SDK와 키를 확인하고 클라이언트 만들기
    def __init__(self) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exec:
            raise ExternalServiceError('anthropic 패키지가 설치되어있지 않음') from exec

        settings=get_settings()
        key=settings.anthropic_api_key  # SecretStr | None 값이 비어있을 수도 있다.
        if key is None:
            raise ExternalServiceError('Anthropic api key가 비어있음')
        self._client=Anthropic(api_key=key.get_secret_value())
        self._model=settings.llm_model

    # 공통으로 사용하는 호출 함수: Messages API를 한번 호출하고, 본문, 토큰, 걸린 시간을 반환.
    # Langfuse에는 generation(모델 호출 한 건)으로 기록된다.
    @observe(name='claude-messages', as_type='generation', capture_input=False, capture_output=False)
    def _call(self, system:str, user_text:str)-> tuple[str,dict,int]:
        # system: 시스템 프롬프트 한 덩어리
        # user_text: 사용자 메세지 본문
        max_tokens=get_settings().max_tokens

        langfuse_context.update_current_observation(
            model=self._model,
            model_parameters={'max_tokens': max_tokens},
            input=[
                {'role':'system','content':system},
                {'role':'user','content':user_text},
            ],
        )

        started=time.perf_counter() # 시간차이 구하는 기능

        try:
            response=self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=[{'role':'user','content':user_text}],
            )
        except Exception as exc:
            log.exception('Claude 호출 실패')
            langfuse_context.update_current_observation(
                level='ERROR',
                status_message=f'{type(exc).__name__}: {exc}',
            )
            raise ExternalServiceError(f'Claude 호출 실패했음:{exc}') from exc

        # * 응답 받은 내용중 필요한 부분만 추출해서 규격 맞춰 출력 *
        # 응답 텍스트 꺼내기
        text=''.join(b.text for b in response.content if getattr(b, 'type', '')=='text')
        usg=response.usage # 사용량 정보 꺼내기
        usage={
            'input':getattr(usg,'input_tokens',0) or 0,
            'cache_read':getattr(usg,'cache_read_input_tokens',0) or 0,
            'cache_write':getattr(usg,'cache_creation_input_tokens',0) or 0,
            'output':getattr(usg,'output_tokens',0) or 0
        }
        # 걸린 시간 계산
        elapsed = int((time.perf_counter() - started) * 1000)

        langfuse_context.update_current_observation(
            output=text,
            usage_details={
                'input': usage['input'],
                'output': usage['output'],
                'cache_read_input_tokens': usage['cache_read'],
                'cache_creation_input_tokens': usage['cache_write'],
            },
        )

        # 결과 리턴
        return text, usage, elapsed
    
    # 근거 문서를 싣고 질문에 답하는 함수: ports.py의 LLMPort 메소드 구현체
    def answer(self, *, question:str, context:list[dict], user:dict)->LLMResult:
        # question: 사용자 질문
        # context: 근거 문서 목록
        # user: 사용자 (질문자)
        system=_load_prompt('answer_system.md')
        prompt=(
            f'## 사용자\n{user.get('name')}-{user.get('dept')}\n\n'
            f'## 근거 문서\n{_context_block(context)}\n\n'
            f'## 질문\n{question}\n\n'
        )
        text, usage, ms = self._call(system, prompt) # 위 _call 함수 불러서 데이터 반환 받기
        total_in=usage['input']+usage['cache_read']+usage['cache_write']
        return LLMResult(
            text=text,
            model=self._model,
            input_tok=total_in,
            cache_tok=usage['cache_read'],
            output_tok=usage['output'],
            cost_krw=estimate_cost_krw(total_in, usage['output']),
            latency_ms=ms
        )

# 모델이 코드펜스로 감싸서 보낸 경우, 원활한 파싱을 위한 전처리 함수
def _extract_json(text:str)->dict:
    # 정규 표현식으로 원하는 부분만 추출
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = fenced.group(1) if fenced else text

    # 펜스가 없으면 앞뒤에 설명 문장이 붙어있을 수 있다. 첫 {와 마지막 } 사이만 남긴다.
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        log.warning("응답 JSON 파싱 실패")
        return {}