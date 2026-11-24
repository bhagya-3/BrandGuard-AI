
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "BrandGuard AI"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./brandguard.db"
    AUTO_CREATE_TABLES: bool = True
    STORAGE_BACKEND: str = "local"
    FILE_STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 20
    REDIS_URL: str = "redis://localhost:6379/0"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    SLACK_WEBHOOK_URL: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    ENTRA_CLIENT_ID: str = ""
    ENTRA_CLIENT_SECRET: str = ""
    ENTRA_TENANT_ID: str = ""
    ENTRA_REDIRECT_URI: str = ""

    JWT_SECRET_KEY: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    FRONTEND_ORIGIN: str = "http://localhost:5173,http://127.0.0.1:5173"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "brandguard-files"
    MINIO_SECURE: bool = False

    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_SECRET_KEY: str = ""
    SUPABASE_BUCKET: str = "brandguard-files"

    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_ACCOUNT_NAME: str = ""
    AZURE_STORAGE_ACCOUNT_KEY: str = ""
    AZURE_STORAGE_CONTAINER: str = "brandguard-files"

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4.1-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
