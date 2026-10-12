from functools import lru_cache

from openai import OpenAI

from app.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService

# Built on first request and reused. Tests swap them out with app.dependency_overrides.


@lru_cache
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=get_settings().openai_api_key)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(get_openai_client(), get_settings().embedding_model)


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService(get_openai_client(), get_settings().llm_model)
