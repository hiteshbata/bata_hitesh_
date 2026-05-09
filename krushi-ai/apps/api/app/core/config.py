from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Krushi AI API"
    VERSION: str = "0.1.0"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # APIs
    GEMINI_API_KEY: str = ""
    META_WHATSAPP_TOKEN: str = ""
    META_WHATSAPP_PHONE_ID: str = ""
    META_WEBHOOK_VERIFY_TOKEN: str = ""
    AGROMONITORING_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
