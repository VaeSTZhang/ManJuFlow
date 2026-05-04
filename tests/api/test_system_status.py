from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402


def test_system_status_llm_enabled_uses_default_provider_key(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", "Dramora")
    monkeypatch.setenv("SCRIPT_GENERATION_MODE", "llm")
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy-deepseek-key")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()

    client = TestClient(app)
    response = client.get("/api/system/status")
    data = response.json()

    assert response.status_code == 200
    assert data["app_name"] == "Dramora"
    assert data["script_generation_mode"] == "llm"
    assert data["llm_enabled"] is True
    assert "dummy-deepseek-key" not in str(data)

    get_settings.cache_clear()
