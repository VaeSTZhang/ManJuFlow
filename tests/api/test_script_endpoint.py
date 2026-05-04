from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app


def make_generate_request(**overrides) -> dict:
    data = {
        "idea_text": "一个被裁员的中年男人发现公司老板用 AI 伪造财报",
        "script_type": "短剧",
        "genre": "都市悬疑",
        "episode_count": 1,
        "episode_duration": "3-5分钟",
        "target_platform": "短视频平台",
        "tone": "节奏快、反转强",
        "audience": "短剧观众",
        "style_requirements": "开头强冲突，结尾反转",
    }
    data.update(overrides)
    return data


def test_generate_script_endpoint_episode_count_one_returns_one_episode() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/generate", json=make_generate_request(episode_count=1))
    data = response.json()

    assert response.status_code == 200
    assert len(data["episodes"]) == 1
    assert data["episodes"][0]["episode_number"] == 1


def test_generate_script_endpoint_episode_count_four_returns_four_episodes() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/generate", json=make_generate_request(episode_count=4))
    data = response.json()

    assert response.status_code == 200
    assert len(data["episodes"]) == 4
    assert [episode["episode_number"] for episode in data["episodes"]] == [1, 2, 3, 4]
    assert all(episode["scenes"] for episode in data["episodes"])


def test_generate_script_endpoint_preserves_script_output_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/generate", json=make_generate_request(episode_count=2))
    data = response.json()

    assert response.status_code == 200
    assert data["project_title"]
    assert data["logline"]
    assert data["world_setting"]
    assert data["characters"]
    assert len(data["episodes"]) == 2


def test_generate_script_endpoint_rejects_idea_text_over_limit() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/generate", json=make_generate_request(idea_text="a" * 5001))
    data = response.json()

    assert response.status_code == 400
    assert "IDEA_TEXT_TOO_LONG" in data["detail"]
    assert "5,000" in data["detail"]
    assert "5,001" in data["detail"]


def test_generate_script_endpoint_rejects_extra_requirements_over_limit() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate",
        json=make_generate_request(style_requirements="a" * 2001),
    )
    data = response.json()

    assert response.status_code == 400
    assert "EXTRA_REQUIREMENTS_TOO_LONG" in data["detail"]
