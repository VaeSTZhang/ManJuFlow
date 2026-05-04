from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript, ScriptOutput  # noqa: E402


def make_source_request(**overrides) -> dict:
    data = {
        "project_title": "三入口短剧测试",
        "source_mode": "idea",
        "idea_text": "雨夜里，女主收到一封来自十年前的信。",
        "source_text": "虚构来源文本。",
        "target_episode_count": 3,
        "genre": "悬疑短剧",
        "style": "强钩子、快节奏",
        "language": "zh",
    }
    data.update(overrides)
    return data


def test_generate_from_source_idea_returns_short_drama_output() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/generate-from-source", json=make_source_request())
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "idea"
    assert data["project_title"]
    assert data["episode_count"] == 3
    assert len(data["episodes"]) == 3


def make_fake_script_output() -> ScriptOutput:
    return ScriptOutput(
        project_title="测试短剧：归来之夜",
        logline="归来的编剧发现旧案与新项目窃取阴谋相连。",
        world_setting="现代都市影视公司。",
        characters=[
            CharacterProfile(
                name="沈知远",
                role="主角",
                age="32",
                personality="冷静、敏锐",
                arc="从自证清白到反击对手。",
            )
        ],
        episodes=[
            EpisodeScript(
                episode_number=1,
                title="第1集：归来",
                summary="沈知远回到公司。",
                hook="旧硬盘里出现关键署名记录。",
                scenes=[
                    SceneScript(
                        scene_number=1,
                        location="影视公司会议室",
                        time="夜晚",
                        description="沈知远与对手在会议室对峙。",
                        dialogues=[
                            DialogueLine(character="沈知远", line="这个故事，我三年前就写过。"),
                        ],
                        visual_notes="冷光会议室，投影屏压迫人物。",
                        emotion_curve="归来→对峙→钩子",
                    )
                ],
            )
        ],
    )


def test_generate_from_source_llm_mode_idea_returns_short_drama_output(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_script_with_llm",
        lambda idea_input, provider=None, model=None: make_fake_script_output(),
    )
    client = TestClient(app)

    response = client.post("/api/scripts/generate-from-source", json=make_source_request())
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "idea"
    assert data["project_title"] == "测试短剧：归来之夜"
    assert data["metadata"]["generation_mode"] == "llm"


def test_generate_from_source_llm_mode_film_script_returns_clear_not_implemented_error(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="film_script"),
    )
    data = response.json()

    assert response.status_code == 400
    assert "SCRIPT_GENERATION_MODE=llm is not implemented for source_mode='film_script' yet." in data["detail"]


def test_generate_from_source_film_script_returns_expected_episode_count() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(
            source_mode="film_script",
            source_text="虚构电影剧本片段。",
            target_episode_count=4,
        ),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "film_script"
    assert data["episode_count"] == 4
    assert len(data["episodes"]) == 4


def test_generate_from_source_novel_returns_expected_episode_count() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(
            source_mode="novel",
            source_text="虚构小说片段。",
            target_episode_count=4,
        ),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "novel"
    assert data["episode_count"] == 4
    assert len(data["episodes"]) == 4


def test_generate_from_source_accepts_ai_options() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(
            ai_options={
                "provider": "deepseek",
                "model": "deepseek-chat",
                "language": "zh",
                "purpose": "script_generation",
            },
        ),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "idea"
    assert data["episode_count"] == 3
    assert data["metadata"]["provider"] == "deepseek"
    assert data["metadata"]["model"] == "deepseek-chat"
    assert data["metadata"]["purpose"] == "script_generation"
    assert data["metadata"]["ai_options"]["provider"] == "deepseek"


def test_generate_from_source_rejects_assistant_rewrite_as_400() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="assistant_rewrite"),
    )
    data = response.json()

    assert response.status_code == 400
    assert "Assistant module" in data["detail"]


def test_generate_from_source_rejects_uploaded_document_as_400() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="uploaded_document"),
    )
    data = response.json()

    assert response.status_code == 400
    assert "Document Import" in data["detail"]


def test_existing_generate_script_endpoint_still_works() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate",
        json={
            "idea_text": "一个安全虚构的短剧灵感。",
            "script_type": "短剧",
            "genre": "都市",
            "episode_count": 2,
            "episode_duration": "3-5分钟",
            "target_platform": "短视频平台",
            "tone": "节奏快、反转强",
            "audience": "短剧观众",
            "style_requirements": "开头强冲突",
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data["episodes"]) == 2


def test_openapi_contains_generate_from_source_route() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")
    data = response.json()

    assert response.status_code == 200
    assert "/api/scripts/generate-from-source" in data["paths"]
