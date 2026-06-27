from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DevDocs AI"
    environment: str = "development"
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-large"
    fallback_embedding_dimensions: int = 3072

    database_url: str = "sqlite:///./devdocs.db"
    chroma_host: str | None = None
    chroma_port: int = 8000
    chroma_persist_dir: str = "./.chroma"
    chroma_collection: str = "devdocs_chunks"

    crawl_max_pages: int = 40
    crawl_timeout_seconds: float = 15.0
    chunk_size: int = 800
    chunk_overlap: int = 150
    retrieval_top_k: int = 5
    retrieval_pool_k: int = 20

    tavily_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())

    @property
    def chroma_is_remote(self) -> bool:
        return bool(self.chroma_host)

    def ensure_local_dirs(self) -> None:
        Path(self.chroma_persist_dir).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_local_dirs()
    return settings
