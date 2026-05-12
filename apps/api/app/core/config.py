from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./clipspark.db"
    redis_url: str = "redis://localhost:6379/0"

    dashscope_api_key: str = ""
    bailian_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    bailian_text_model: str = "qwen-plus"
    bailian_vision_model: str = "qwen-vl-plus"
    bailian_embedding_model: str = "text-embedding-v4"

    storage_driver: str = "local"
    local_storage_root: str = "../../storage"
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def storage_root_path(self) -> Path:
        root = Path(self.local_storage_root)
        if not root.is_absolute():
            root = Path(__file__).resolve().parents[4] / root
        return root.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
