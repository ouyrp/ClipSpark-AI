from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./clipspark.db"
    redis_url: str = "redis://localhost:6379/0"

    ai_provider: str = "gemini"

    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_text_model: str = "gemini-2.5-flash-lite"
    gemini_vision_model: str = "gemini-2.5-flash"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_text_model: str = "openrouter/free"
    openrouter_vision_model: str = "openrouter/free"

    ollama_api_key: str = "ollama"
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_text_model: str = "qwen2.5:7b"
    ollama_vision_model: str = "qwen2.5vl:7b"

    dashscope_api_key: str = ""
    bailian_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    bailian_text_model: str = "qwen-plus"
    bailian_vision_model: str = "qwen-vl-plus"
    bailian_embedding_model: str = "text-embedding-v4"
    bailian_asr_model: str = "paraformer-v2"
    asr_public_base_url: str = ""

    storage_driver: str = "local"
    local_storage_root: str = "../../storage"
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def storage_root_path(self) -> Path:
        root = Path(self.local_storage_root)
        if not root.is_absolute():
            root = Path.cwd() / root
        return root.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
