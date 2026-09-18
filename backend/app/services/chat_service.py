from __future__ import annotations
from pdb import run

import app.integrations.factory as factory

from pydantic import ValidationError

from app.core.guards import check_question
from app.core.logging import get_logger
from app.schemas.chat import AnswerOut, AskOut

log=get_logger(__name__)

# 첫 호출 1회 + 재시도 2회 = 3회
MAX_ATTEMPTS=3

# 폴백 답변 본문
FALLBACK_ANSWER='요청을 처리했지만 근거 확인 불가. 담당 부서에 문의 요망.'

# 질문자 (임시)
DEFAULT_USER={'name':'김민준','dept':'인프라사업부2팀'}

# 근거 문서 목록
NO_CONTEXTS:list[dict]=[]

# pydantic의 오류 목록을 모델에게 다시 한 문장으로 반환: 재시도 힌트
def _hint_from(errors:list[dict])->str:
    # errors: ValidationError가 반환하는 목록
    parts=[]
    for err in errors:
        where='.'.join(str(x) for x in err.get('loc',())) or '(최상위)'
        parts.append(f'{where}:{err.get('msg','')}')
    return '.'.join(parts)

# fallback: 
def _fallback(run_id:str, attempts:int)->AskOut:
    # 
    return AskOut(
        answer=FALLBACK_ANSWER,
        sources=[],
        enough_evidence=False,
        run_id=run_id,
        attempts=attempts,
        fallback_used=True
    )

# 본체: 질문 하나에 대답하기
def ask(*, question:str, run_id:str='RUN-000')->AskOut:
    # 1. 가드 호출-> 여기서 발생한 예외는 이 함수를 통과해 전역 핸들러까지 올라간다.
    q=check_question(question)

    # 2. 어댑터 한 개 가져오기
    llm=factory.get_llm()

    from app.integrations.llm_claude import _extract_json

    hint=''
    for attempt in range(1, MAX_ATTEMPTS+1):
        # 3. llm 호출
        # 프롬프트 준비
        prompt=q if not hint else f'{q}\n\n[직전 응답의 문제]{hint}\n출력 형식 지켜서 다시 답해주세요'
        # llm에 질문
        result=llm.answer(question=prompt, context=NO_CONTEXTS, user=DEFAULT_USER)

        try:
            data=_extract_json(result.text)
            AnswerOut.model_validate(data)  # 규격에 맞는지 검사
        except ValidationError as e:
            hint=_hint_from(e.errors(include_url=False))
            # log.warning(f'스키마 위반{attempt}/{MAX_ATTEMPTS}회:{hint}')
            log.warning('스키마 위반 %d/%d회:%s',attempt,MAX_ATTEMPTS,hint)
            continue

        # 통과 시 결과 반환
        return AskOut(**data, run_id=run_id, attempts=attempt, fallback_used=False)

    # 3번 다 시도했다. 로그 남기고 fallback 실행.
    log.warning('스키마 검증에 %d회 실패하여 폴백함.(run_id=%s)',MAX_ATTEMPTS,run_id)
    return _fallback(run_id, MAX_ATTEMPTS)