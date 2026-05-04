from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings
from app.services.llm_client import LLMClient


LLM_ENV_NAMES = [
    "DEFAULT_LLM_PROVIDER",
    "DEFAULT_SCRIPT_MODEL",
    "LLM_REQUEST_TIMEOUT_SECONDS",
    "ASSISTANT_GENERATION_MODE",
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
    "KIMI_BASE_URL",
    "KIMI_MODEL",
    "KIMI_API_KEY",
    "MINIMAX_BASE_URL",
    "MINIMAX_MODEL",
    "MINIMAX_API_KEY",
]


@pytest.fixture(autouse=True)
def clean_llm_env(monkeypatch):
    for name in LLM_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_exposes_dramora_default_llm_fields() -> None:
    settings = get_settings()

    assert settings.default_llm_provider == "deepseek"
    assert settings.default_script_model == "deepseek-chat"
    assert settings.llm_request_timeout_seconds > 0
    assert settings.assistant_generation_mode == "mock"


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
    assert client.temperature == 0.7
    assert client.timeout == 60.0


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
    assert client.temperature == 0.7
    assert client.timeout == 60.0


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
    assert client.temperature == 0.7
    assert client.timeout == 60.0


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
    assert client.temperature == 0.7
    assert client.timeout == 60.0


def test_llm_client_uses_kimi_provider_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("KIMI_BASE_URL", "https://api.moonshot.cn/")
    monkeypatch.setenv("KIMI_MODEL", "moonshot-v1-8k")
    monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.moonshot.cn"
    assert client.model == "moonshot-v1-8k"
    assert client.api_key == "kimi-key"
    assert client.temperature == 1.0
    assert client.timeout == 120.0


def test_llm_client_uses_minimax_provider_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "minimax")
    monkeypatch.setenv("MINIMAX_BASE_URL", "https://api.minimax.io/")
    monkeypatch.setenv("MINIMAX_MODEL", "MiniMax-M2.7")
    monkeypatch.setenv("MINIMAX_API_KEY", "minimax-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.minimax.io"
    assert client.model == "MiniMax-M2.7"
    assert client.api_key == "minimax-key"
    assert client.temperature == 0.7
    assert client.timeout == 60.0


def test_llm_client_explicit_provider_overrides_settings_provider(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.setenv("KIMI_BASE_URL", "https://api.moonshot.cn")
    monkeypatch.setenv("KIMI_MODEL", "kimi-k2.5")
    monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
    get_settings.cache_clear()

    client = LLMClient(provider="kimi")

    assert client.provider == "kimi"
    assert client.base_url == "https://api.moonshot.cn"
    assert client.model == "kimi-k2.5"
    assert client.api_key == "kimi-key"
    assert client.temperature == 1.0
    assert client.timeout == 120.0


def test_llm_client_explicit_minimax_provider_uses_minimax_config(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.setenv("MINIMAX_BASE_URL", "https://api.minimaxi.com")
    monkeypatch.setenv("MINIMAX_MODEL", "MiniMax-M2.7")
    monkeypatch.setenv("MINIMAX_API_KEY", "minimax-key")
    get_settings.cache_clear()

    client = LLMClient(provider="minimax")

    assert client.provider == "minimax"
    assert client.base_url == "https://api.minimaxi.com"
    assert client.model == "MiniMax-M2.7"
    assert client.api_key == "minimax-key"
    assert client.temperature == 0.7
    assert client.timeout == 60.0


def test_llm_client_explicit_model_overrides_provider_default_model(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("KIMI_BASE_URL", "https://api.moonshot.cn")
    monkeypatch.setenv("KIMI_MODEL", "kimi-k2.5")
    monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
    get_settings.cache_clear()

    client = LLMClient(model="kimi-k2.6")

    assert client.provider == "kimi"
    assert client.model == "kimi-k2.6"
    assert client.temperature == 1.0
    assert client.timeout == 120.0


def test_llm_client_explicit_timeout_overrides_provider_default(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("KIMI_BASE_URL", "https://api.moonshot.cn")
    monkeypatch.setenv("KIMI_MODEL", "moonshot-v1-8k")
    monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
    get_settings.cache_clear()

    client = LLMClient(timeout=30.0)

    assert client.timeout == 30.0
    assert client.temperature == 1.0


def test_llm_client_rejects_invalid_provider(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "unknown")
    get_settings.cache_clear()

    with pytest.raises(ValueError) as exc_info:
        LLMClient()

    message = str(exc_info.value)
    assert "default" in message
    assert "deepseek" in message
    assert "mimo" in message
    assert "kimi" in message
    assert "minimax" in message


def test_llm_client_rejects_invalid_explicit_provider() -> None:
    with pytest.raises(ValueError) as exc_info:
        LLMClient(provider="unknown")

    message = str(exc_info.value)
    assert "unknown" in message
    assert "default" in message
    assert "deepseek" in message
    assert "mimo" in message
    assert "kimi" in message
    assert "minimax" in message


def test_llm_client_rejects_missing_provider_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "mimo")
    monkeypatch.setenv("MIMO_BASE_URL", "https://api.xiaomimimo.com")
    monkeypatch.setenv("MIMO_MODEL", "mimo-v2.5-pro")
    monkeypatch.setenv("MIMO_API_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="MIMO_API_KEY"):
        LLMClient()


def test_llm_client_rejects_missing_kimi_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("KIMI_BASE_URL", "https://api.moonshot.cn")
    monkeypatch.setenv("KIMI_MODEL", "moonshot-v1-8k")
    monkeypatch.setenv("KIMI_API_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="KIMI_API_KEY"):
        LLMClient()


def test_llm_client_rejects_missing_minimax_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "minimax")
    monkeypatch.setenv("MINIMAX_BASE_URL", "https://api.minimax.io")
    monkeypatch.setenv("MINIMAX_MODEL", "MiniMax-M2.7")
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="MINIMAX_API_KEY"):
        LLMClient()


def test_llm_client_strips_trailing_slash_from_base_url(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com///")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.deepseek.com"


def test_llm_client_strips_trailing_slash_from_kimi_base_url(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("KIMI_BASE_URL", "https://api.moonshot.cn///")
    monkeypatch.setenv("KIMI_MODEL", "moonshot-v1-8k")
    monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.moonshot.cn"


def test_llm_client_strips_trailing_slash_from_minimax_base_url(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "minimax")
    monkeypatch.setenv("MINIMAX_BASE_URL", "https://api.minimax.io///")
    monkeypatch.setenv("MINIMAX_MODEL", "MiniMax-M2.7")
    monkeypatch.setenv("MINIMAX_API_KEY", "minimax-key")
    get_settings.cache_clear()

    client = LLMClient()

    assert client.base_url == "https://api.minimax.io"
