from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, Secret, SecretStr
from functools import lru_cache

from app.models.base import EMBED_DIM

class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )

    app_mode:str=Field(default='mock',pattern=r'^(mock|live)$')
    anthropic_api_key:SecretStr | None=None
    llm_model:str='claude-haiku-4-5'
    max_tokens:int=Field(default=400, ge=1, le=8192)
    temperature:float=Field(default=0.0, ge=0.0, le=1.0)
    daily_call_limit:int=Field(default=200, ge=1)
    max_input_chars:int=Field(default=200, ge=1)
    database_url:str='sqlite:///./app.db'
    debug:bool=False
    allow_external_send:bool=False
    top_k:int=Field(default=3, ge=1, le=20)

    langfuse_enabled:bool=False
    langfuse_host:str='http://localhost:3000'
    langfuse_public_key:str|None=None
    langfuse_secret_key:SecretStr|None=None
    # --- Upstage ---
    upstage_api_key: SecretStr | None = None
    upstage_base_url: str = "https://api.upstage.ai/v1"
    upstage_parse_model: str = "document-parse"
    upstage_parse_ocr: str = "auto"  
    # --- embedding ---
    embed_provider:str=Field(default='local',pattern=r'^(local|upstage)')
    embed_model_dir:str='models/bge-m3'
    embed_dim:int=EMBED_DIM
    upstage_embed_model:str|None=None

    # live 모드인지 확인 -> settings.is_live => True/False 
    @property
    def is_live(self) -> bool:
        return self.app_mode == "live"

@lru_cache
def get_settings()->Settings:
    return Settings()

def mask(secret: str | None, keep: int = 8) -> str:
    if not secret:
        return "(없음)"
    return f"{secret[:keep]}...({len(secret)}자)"