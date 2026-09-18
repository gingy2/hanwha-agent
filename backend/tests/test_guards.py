import pytest

from app.core.config import get_settings
from app.core.exceptions import GuardTripped, RateLimited
from app.core.guards import check_daily_limit, check_model, check_question

def test_check_q_passed_n_strips()->None:
    assert check_question('제주도 출장 숙박비 한도 얼마?')=='제주도 출장 숙박비 한도 얼마?'

def test_check_question_rejects_blank()->None:
    with pytest.raises(GuardTripped):
        check_question('')

def test_check_question_rejects_too_long()->None:
        limit=get_settings().max_input_chars
        with pytest.raises(GuardTripped):
            check_question('가'*(limit+1))

def test_check_question_rejects_unknown_model()->None:
        with pytest.raises(GuardTripped):
            check_question('claude-opus-5')
        assert check_model(get_settings().llm_model)==get_settings().llm_model

def test_check_daily_limit_raises_when_exhausted()->None:
     limit=get_settings().daily_call_limit
     check_daily_limit(limit-1)
     with pytest.raises(RateLimited):
          check_daily_limit(limit)