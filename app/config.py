"""Configuración central de la app. Carga desde variables de entorno / .env.

Toda la app importa `settings` desde aquí. Cero valores hardcodeados.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- LLM (capa agnóstica, OpenAI-compatible vía OpenRouter) ---
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="LLM_BASE_URL"
    )
    llm_model: str = Field(default="google/gemini-2.5-flash", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")

    # --- Tools ---
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    # --- DB ---
    database_url: str = Field(
        default="postgresql+psycopg2://ddagent:changeme@localhost:5432/duediligence",
        alias="DATABASE_URL",
    )

    # --- App ---
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")


@lru_cache
def get_settings() -> Settings:
    """Singleton cacheado. Usar `get_settings()` en vez de instanciar Settings."""
    return Settings()


settings = get_settings()
