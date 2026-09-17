from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header

from app.core.exceptions import AuthFailed
from app.schemas.auth import LoginIn, UserOut
from app.services import auth_service

# 인증 관련 요청
router = APIRouter(prefix="/auth", tags=["auth"])

# 로그인 요청
@router.post("/login", response_model=UserOut)  # 응답 데이터 타입 UserOut
def login(body: LoginIn) -> dict:  # 사용자가 요청한 데이터는 LoginIn 타입으로 취합
    return auth_service.authenticate(body.emp_no, body.password)

# 사용자 정보 요청 : x_emp_no는 JWT 토큰으로 변경 예정
@router.get("/me", response_model=UserOut)
def me(x_emp_no: Annotated[str | None, Header()] = None) -> dict:  # 헤더로 넘어오는 인증키(사번으로 임시 사용)
    if x_emp_no is None:
        raise AuthFailed("로그인이 필요합니다.")
    return auth_service.get_me(x_emp_no)
