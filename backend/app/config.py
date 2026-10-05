"""Configuración de la app, leída del archivo .env de la raíz del repo."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> subimos dos niveles hasta la raíz del repo
ROOT_DIR = Path(__file__).resolve().parents[2]



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-120b"
    default_provider: str = "groq"

    # Frontend
    cors_origins: str = "http://localhost:5173"


settings = Settings()