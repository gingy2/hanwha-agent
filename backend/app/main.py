from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from h11 import Request
from app.api.v1.documents import router as documents_router
from app.core.config import Settings
from app.core.exceptions import AgentError
from app.core.logging import setup_logging

# lifespan 함수 정의
@asynccontextmanager
async def lifespan(app:FastAPI):
    setup_logging()
    yield

app=FastAPI(
    title='사내 AI 에이전트',
    version='0.1.0',
    lifespan=lifespan
)

# 서버 상태 확인용 API
@app.get('/health')
def health()->dict:
    return{'status':'ok'}

# 라우터 연결
app.include_router(
    documents_router,
    prefix='/api/v1'
)

@app.exception_handler(AgentError)
async def handle_agent_error(
    request:Request,
    exc:AgentError
)->JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'code':exc.code,
            'message':str(exc),
            'detail':None
        }
    )

# -------------------------------------------------------
def get_settings()->Settings:
    return Settings()

@app.get('/example')
def example(
    settings:Settings=Depends(get_settings) # FastAPI에게 요청 처리시 '이 함수가 필요하다'고 등록
):
    return {}

# -------------------------------------------------------
SettingsDep=Annotated[Settings,Depends(get_settings)]

def list_doc(
        settings:SettingsDep    # 의존성 주입 처리 됨
):
    pass