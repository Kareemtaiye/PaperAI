from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    sync_database_url: str

    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    gemini_api_key: str = ""
    resend_api_key: str = ""
    from_email: str = "noreply@send.kareemtaiye.com"
    app_name: str = "PaperAI"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
