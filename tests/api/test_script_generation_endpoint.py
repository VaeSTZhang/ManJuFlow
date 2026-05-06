from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.ownership_repository import SQLiteOwnershipRepository  # noqa: E402
from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository  # noqa: E402
from app.main import app  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript, ScriptOutput  # noqa: E402
from app.schemas.script_generation import ShortDramaScriptOutput  # noqa: E402
from app.services.usage_ledger_service import (  # noqa: E402
    configure_usage_ledger_repository_for_testing,
    reset_usage_ledger_repository_for_testing,
)
from app.services.ownership_service import (  # noqa: E402
    configure_ownership_repository_for_testing,
    reset_ownership_repository_for_testing,
)


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "script_generation_endpoint_usage.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "script_generation_endpoint_ownership.sqlite")
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield usage_repository
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


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


def test_generate_from_source_idea_returns_short_drama_output(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
    client = TestClient(app)

    response = client.post("/api/scripts/generate-from-source", json=make_source_request())
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "idea"
    assert data["project_title"]
    assert data["episode_count"] == 3
    assert len(data["episodes"]) == 3


def make_fake_script_output() -> ScriptOutput:
    episodes = [
        EpisodeScript(
            episode_number=episode_number,
            title=f"第{episode_number}集：归来线索",
            summary=f"沈知远回到公司，发现第{episode_number}条虚构线索。",
            hook=f"旧硬盘里出现第{episode_number}条关键署名记录。",
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
        for episode_number in range(1, 4)
    ]
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
        episodes=episodes,
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


def test_generate_from_source_llm_mode_film_script_returns_short_drama_output(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_film_script_adaptation_llm",
        lambda input_data: ShortDramaScriptOutput(
            project_title="旧片场复仇夜",
            source_mode="film_script",
            logline="女演员回到废弃片场追查父亲失踪真相。",
            world_setting="废弃片场与旧电影工业交织。",
            characters=[],
            adaptation_notes=None,
            episode_count=3,
            episodes=[
                EpisodeScript(
                    episode_number=episode_number,
                    title=f"第{episode_number}集：片场线索",
                    summary=f"女演员发现第{episode_number}条片场旧案线索。",
                    hook=f"第{episode_number}集结尾，旧道具暴露新的真相。",
                    scenes=[],
                )
                for episode_number in range(1, 4)
            ],
            metadata={"generation_mode": "llm"},
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="film_script"),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "film_script"
    assert data["metadata"]["generation_mode"] == "llm"


def test_generate_from_source_returns_422_when_episode_contract_fails(
    monkeypatch,
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_film_script_adaptation_llm",
        lambda input_data: ShortDramaScriptOutput(
            project_title="旧片场复仇夜",
            source_mode="film_script",
            logline="女演员回到废弃片场追查父亲失踪真相。",
            world_setting="废弃片场与旧电影工业交织。",
            characters=[],
            adaptation_notes=None,
            episode_count=1,
            episodes=[
                EpisodeScript(
                    episode_number=1,
                    title="第1集：片场线索",
                    summary="女演员发现第一条片场旧案线索。",
                    hook="旧道具暴露新的真相。",
                    scenes=[],
                )
            ],
            metadata={"generation_mode": "llm"},
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(
            source_mode="film_script",
            source_text="安全虚构电影剧本片段。",
            target_episode_count=3,
            context_options={
                "request_id": "request_endpoint_contract_failed",
                "project_id": "project_endpoint_contract",
                "session_id": "session_endpoint_contract",
            },
        ),
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"]["error_code"] == "script_generation_contract_failed"
    assert "模型输出未满足目标集数要求" in data["detail"]["message"]
    assert "requested=3" in data["detail"]["reason"]
    assert "episode_count=1" in data["detail"]["reason"]
    assert "episodes=1" in data["detail"]["reason"]
    assert "source_text" not in str(data["detail"])
    assert "安全虚构电影剧本片段" not in str(data["detail"])

    stored = isolated_usage_ledger_repository.get_entry_by_request_id(
        "request_endpoint_contract_failed"
    )
    assert stored is not None
    assert stored.status == "failed"
    assert stored.operation == "film_adaptation"
    assert stored.source_mode == "film_script"
    assert stored.project_id == "project_endpoint_contract"
    assert stored.session_id == "session_endpoint_contract"
    assert stored.error_code == "script_generation_contract_failed"
    assert stored.metadata_json is not None
    assert "source_text" not in stored.metadata_json
    assert "安全虚构电影剧本片段" not in stored.metadata_json


def test_generate_from_source_llm_mode_novel_returns_short_drama_output(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_novel_adaptation_llm",
        lambda input_data: ShortDramaScriptOutput(
            project_title="旧书店日记",
            source_mode="novel",
            logline="年轻编剧追查母亲日记里的舞台事故。",
            world_setting="旧书店与废弃剧场交织。",
            characters=[],
            adaptation_notes=None,
            episode_count=3,
            episodes=[
                EpisodeScript(
                    episode_number=episode_number,
                    title=f"第{episode_number}集：书店线索",
                    summary=f"年轻编剧发现第{episode_number}条旧书店线索。",
                    hook=f"第{episode_number}集结尾，日记出现新的名字。",
                    scenes=[],
                )
                for episode_number in range(1, 4)
            ],
            metadata={"generation_mode": "llm"},
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="novel"),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["source_mode"] == "novel"
    assert data["metadata"]["generation_mode"] == "llm"


def test_generate_from_source_film_script_returns_expected_episode_count(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
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


def test_generate_from_source_novel_returns_expected_episode_count(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
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


def test_generate_from_source_accepts_ai_options(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
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


def test_generate_from_source_returns_context_options_metadata(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(
            context_options={
                "user_id": "user-001",
                "workspace_id": "workspace-001",
                "project_id": "project-001",
                "session_id": "session-001",
                "request_id": "request-001",
                "source_stage": "generated_script",
            },
        ),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["metadata"]["context_policy"] == "current_project_only"
    assert data["metadata"]["context"]["user_id"] == "user-001"
    assert data["metadata"]["context"]["workspace_id"] == "workspace-001"
    assert data["metadata"]["context"]["project_id"] == "project-001"
    assert data["metadata"]["context"]["session_id"] == "session-001"
    assert data["metadata"]["context"]["request_id"] == "request-001"
    assert data["metadata"]["context"]["source_stage"] == "generated_script"
    assert "source_text" not in data["metadata"]


def test_generate_from_source_rejects_assistant_rewrite_as_400(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="assistant_rewrite"),
    )
    data = response.json()

    assert response.status_code == 400
    assert "Assistant module" in data["detail"]


def test_generate_from_source_rejects_uploaded_document_as_400(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
    client = TestClient(app)

    response = client.post(
        "/api/scripts/generate-from-source",
        json=make_source_request(source_mode="uploaded_document"),
    )
    data = response.json()

    assert response.status_code == 400
    assert "Document Import" in data["detail"]


def test_existing_generate_script_endpoint_still_works(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
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
