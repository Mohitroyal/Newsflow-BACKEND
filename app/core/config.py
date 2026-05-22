from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BeforeValidator, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

import json

def parse_cors(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str):
        if v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                pass
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    FRONTEND_URL: str = "https://newscraft-ai.vercel.app"
    BACKEND_URL: str = "https://mohitroyal-newsflow-backend.hf.space"
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NewsCraft AI"
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    CORS_ORIGINS: Annotated[List[str], BeforeValidator(parse_cors)] = []

    # Database
    DATABASE_URL: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "newscraft-clippings"
    
    # xAI Grok
    GROK_API_KEY: str
    
    # Stripe
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_ENTERPRISE_PRICE_ID: Optional[str] = None
    
    # Redis & Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None

settings = Settings()
