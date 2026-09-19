"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    All values are loaded from environment variables.
    See .env.example for the full list.
    """

    # Database
    database_url: str = "postgresql+asyncpg://career:career@localhost:5432/career_intel"

    # Auth
    secret_key: str = "change-me-to-a-different-random-string"
    access_token_expire_minutes: int = 15
    github_client_id: str = ""
    github_client_secret: str = ""

    # AI / LLM
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # File Storage
    storage_backend: str = "local"
    local_storage_path: str = "./data/uploads"

    # Application URLs
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
