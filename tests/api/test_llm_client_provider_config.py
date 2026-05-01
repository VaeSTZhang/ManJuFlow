from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings
from app.services.llm_client import LLMClient


LLM_ENV_NAMES = [
    "LLM_PROVIDER",
    "LLM_BASE_URL",
    "LLM_MODEL",
    "LLM_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "DEEPSEEK_API_KEY",
    "MIMO_BASE_URL",
    "MIMO_MODEL",
    "MIMO_API_KEY",
]


@pytest.fixture(autouse=True)
def clean_llm_env(monkeypatch):
    for name in LLM_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_llm_client_uses_default_provider_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "default")
    monkeypatch.setenv("LLM_BASE_URL", "https://legacy.example.com/")
    monkeypatch.setenv("LLM_MODEL", "legacy-model")
    monkeypatch.setenv("LLM_API_KEY", "legacy-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://legacy.example.com"
    assert client.model == "legacy-model"
    assert client.api_key == "legacy-key"


def test_llm_client_empty_provider_uses_default_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "")
    monkeypatch.setenv("LLM_BASE_URL", "https://legacy.example.com")
    monkeypatch.setenv("LLM_MODEL", "legacy-model")
    monkeypatch.setenv("LLM_API_KEY", "legacy-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://legacy.example.com"
    assert client.model == "legacy-model"
    assert client.api_key == "legacy-key"


def test_llm_client_uses_deepseek_provider_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.deepseek.com"
    assert client.model == "deepseek-chat"
    assert client.api_key == "deepseek-key"


def test_llm_client_uses_mimo_provider_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "mimo")
    monkeypatch.setenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/")
    monkeypatch.setenv("MIMO_MODEL", "mimo-v2.5-pro")
    monkeypatch.setenv("MIMO_API_KEY", "mimo-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.xiaomimimo.com"
    assert client.model == "mimo-v2.5-pro"
    assert client.api_key == "mimo-key"


def test_llm_client_rejects_invalid_provider(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "unknown")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="LLM_PROVIDER only supports"):
        LLMClient()


def test_llm_client_rejects_missing_provider_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "mimo")
    monkeypatch.setenv("MIMO_BASE_URL", "https://api.xiaomimimo.com")
    monkeypatch.setenv("MIMO_MODEL", "mimo-v2.5-pro")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="MIMO_API_KEY"):
        LLMClient()


def test_llm_client_strips_trailing_slash_from_base_url(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com///")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.deepseek.com"
