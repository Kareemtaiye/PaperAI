from pydantic.v1 import BaseSettings
from pydantic_settings import SettingsConfigDict

ENV_FILE = ".env.test" if os.getenv("ENV") == "test" else ".env"


class Settings(BaseSettings):
    database_url: str
    env: str = "development"
    redis_cache_url: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.env.lower() in ("production", "prod")


settings = Settings()
