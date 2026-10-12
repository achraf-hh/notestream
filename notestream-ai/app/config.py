from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # OpenAI. min_length rejects the empty string docker compose passes when the key is unset.
    openai_api_key: str = Field(min_length=1)

    # Models
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Load settings on first use, so importing the app doesn't require OPENAI_API_KEY."""
    return Settings()
