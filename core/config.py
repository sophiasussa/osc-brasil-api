from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    rate_limit_max_requests: int = Field(default=100, ge=1)
    rate_limit_window_seconds: float = Field(
        default=60,
        gt=0,
        allow_inf_nan=False,
    )
    rate_limit_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
