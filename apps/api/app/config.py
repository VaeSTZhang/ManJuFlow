from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "Dramora"
    app_env: str = "local"
    default_llm_provider: str = "deepseek"
    default_script_model: str = "deepseek-chat"
    llm_request_timeout_seconds: int = 60
    llm_provider: str = "default"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    deepseek_base_url: str = ""
    deepseek_model: str = ""
    deepseek_api_key: str = ""
    mimo_base_url: str = ""
    mimo_model: str = ""
    mimo_api_key: str = ""
    kimi_base_url: str = ""
    kimi_model: str = ""
    kimi_api_key: str = ""
    minimax_base_url: str = ""
    minimax_model: str = ""
    minimax_api_key: str = ""
    script_generation_mode: str = "mock"
    storyboard_generation_mode: str = "mock"
    image_prompt_generation_mode: str = "mock"
    assistant_generation_mode: str = "mock"

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
