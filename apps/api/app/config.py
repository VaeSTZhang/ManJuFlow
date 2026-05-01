from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "ManJuFlow"
    app_env: str = "development"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    script_generation_mode: str = "mock"
    storyboard_generation_mode: str = "mock"
    image_prompt_generation_mode: str = "mock"

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
