from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings
from app.repositories.ownership_repository import SQLiteOwnershipRepository
from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository
from app.schemas.context import ContextOptions
from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript, ScriptOutput
from app.schemas.script_generation import AIRequestOptions, ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation.generator import (
    generate_idea_short_drama_script_llm,
    generate_short_drama_script,
    generate_short_drama_script_mock,
)
from app.services.script_generation.validation import ScriptGenerationContractError
from app.services.usage_ledger_service import (
    configure_usage_ledger_repository_for_testing,
    reset_usage_ledger_repository_for_testing,
)
from app.services.ownership_service import (
    configure_ownership_repository_for_testing,
    get_ownership_repository,
    reset_ownership_repository_for_testing,
)


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "script_generation_usage_test.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "script_generation_ownership_test.sqlite")
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield usage_repository
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


def make_fake_script_output() -> ScriptOutput:
    episodes = [
        EpisodeScript(
            episode_number=episode_number,
            title=f"第{episode_number}集：归来线索",
            summary=f"沈知远回到公司，发现第{episode_number}条新线索。",
            hook=f"第{episode_number}集结尾，旧硬盘里出现新的署名记录。",
            scenes=[
                SceneScript(
                    scene_number=1,
                    location="影视公司会议室",
                    time="夜晚",
                    description="沈知远推门进入会议室，许竞的项目提案正投在大屏上。",
                    dialogues=[
                        DialogueLine(character="沈知远", line="这个故事的第一版，三年前就写在我的电脑里。"),
                        DialogueLine(character="许竞", line="证据呢？没有证据，就别打扰大家开会。"),
                    ],
                    visual_notes="会议室冷光，投影屏形成强压迫感。",
                    emotion_curve="克制入场→正面对峙→证据钩子",
                )
            ],
        )
        for episode_number in range(1, 4)
    ]
    return ScriptOutput(
        project_title="测试短剧：归来之夜",
        logline="被误解离开的编剧归来，发现旧案背后藏着新项目窃取阴谋。",
        world_setting="现代都市影视公司，职场权力与创作署名冲突交织。",
        characters=[
            CharacterProfile(
                name="沈知远",
                role="主角，归来的短剧编剧",
                age="32",
                personality="冷静、敏锐、压抑怒意",
                arc="从被动自证到主动揭开陷害真相。",
            ),
            CharacterProfile(
                name="许竞",
                role="对手，准备窃取新项目的制作人",
                age="35",
                personality="圆滑、强势、擅长操控舆论",
                arc="从掌控公司话语权到被证据反噬。",
            ),
        ],
        episodes=episodes,
    )


def test_generate_short_drama_script_mock_for_idea_returns_short_drama_output():
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        genre="悬疑短剧",
        style="强钩子、快节奏",
        language="zh",
    )

    output = generate_short_drama_script_mock(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "idea"
    assert output.episode_count == 3
    assert len(output.episodes) == 3
    assert output.metadata["bridge_from"] == "ScriptOutput"


def test_generate_short_drama_script_mock_mode_returns_short_drama_output(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        genre="悬疑短剧",
        style="强钩子、快节奏",
        language="zh",
    )

    output = generate_short_drama_script(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "idea"
    assert output.episode_count == 3


def test_generate_short_drama_script_llm_mode_idea_returns_short_drama_output(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")

    captured = {}

    def fake_generate_script_with_llm(idea_input, provider=None, model=None):
        captured["idea_text"] = idea_input.idea_text
        captured["provider"] = provider
        captured["model"] = model
        return make_fake_script_output()

    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_script_with_llm",
        fake_generate_script_with_llm,
    )

    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="script_generation",
        ),
    )

    output = generate_short_drama_script(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "idea"
    assert output.project_title == "测试短剧：归来之夜"
    assert output.episode_count == 3
    assert output.metadata["generation_mode"] == "llm"
    assert output.metadata["provider"] == "deepseek"
    assert output.metadata["model"] == "deepseek-chat"
    assert output.metadata["purpose"] == "script_generation"
    assert captured == {
        "idea_text": "雨夜里，女主收到一封来自十年前的信。",
        "provider": "deepseek",
        "model": "deepseek-chat",
    }


def test_generate_idea_short_drama_script_llm_requires_idea_text(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    input_data = ShortDramaGenerationInput(source_mode="idea")

    with pytest.raises(ValueError, match="requires idea_text"):
        generate_idea_short_drama_script_llm(input_data)


def test_generate_short_drama_script_llm_mode_film_script_dispatches_to_film_llm(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    captured = {}

    def fake_generate_film_script_adaptation_llm(input_data):
        captured["source_mode"] = input_data.source_mode
        return ShortDramaScriptOutput(
            project_title="旧片场复仇夜",
            source_mode="film_script",
            logline="女演员回到废弃片场追查父亲失踪真相。",
            world_setting="废弃片场与旧电影工业交织。",
            characters=[],
            adaptation_notes=None,
            episode_count=1,
            episodes=[EpisodeScript(
                episode_number=1,
                title="第1集：片场归来",
                summary="女演员回到废弃片场。",
                hook="旧摄影机突然亮起。",
                scenes=[],
            )],
            metadata={"generation_mode": "llm"},
        )

    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_film_script_adaptation_llm",
        fake_generate_film_script_adaptation_llm,
    )
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="虚构电影剧本片段。",
    )

    output = generate_short_drama_script(input_data)

    assert output.source_mode == "film_script"
    assert output.metadata["generation_mode"] == "llm"
    assert captured == {"source_mode": "film_script"}


def test_generate_short_drama_script_llm_mode_novel_dispatches_to_novel_llm(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    captured = {}

    def fake_generate_novel_adaptation_llm(input_data):
        captured["source_mode"] = input_data.source_mode
        return ShortDramaScriptOutput(
            project_title="旧书店日记",
            source_mode="novel",
            logline="年轻编剧追查母亲日记里的舞台事故。",
            world_setting="旧书店与废弃剧场交织。",
            characters=[],
            adaptation_notes=None,
            episode_count=1,
            episodes=[EpisodeScript(
                episode_number=1,
                title="第1集：旧书店",
                summary="年轻编剧回到旧书店。",
                hook="旧日记写着她的名字。",
                scenes=[],
            )],
            metadata={"generation_mode": "llm"},
        )

    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_novel_adaptation_llm",
        fake_generate_novel_adaptation_llm,
    )
    input_data = ShortDramaGenerationInput(
        source_mode="novel",
        source_text="虚构小说片段。",
    )

    output = generate_short_drama_script(input_data)

    assert output.source_mode == "novel"
    assert output.metadata["generation_mode"] == "llm"
    assert captured == {"source_mode": "novel"}


def test_generate_short_drama_script_rejects_invalid_generation_mode(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "unsupported")
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
    )

    with pytest.raises(ValueError, match="SCRIPT_GENERATION_MODE only supports"):
        generate_short_drama_script(input_data)


def test_generate_short_drama_script_mock_idea_records_ai_options_metadata():
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        genre="悬疑短剧",
        style="强钩子、快节奏",
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="script_generation",
        ),
    )

    output = generate_short_drama_script_mock(input_data)

    assert output.metadata["ai_options"]["provider"] == "deepseek"
    assert output.metadata["ai_options"]["model"] == "deepseek-chat"
    assert output.metadata["ai_options"]["purpose"] == "script_generation"
    assert output.metadata["provider"] == "deepseek"
    assert output.metadata["model"] == "deepseek-chat"
    assert output.metadata["purpose"] == "script_generation"
    assert output.metadata["context_policy"] == "current_project_only"


def test_generate_short_drama_script_mock_records_context_options_metadata():
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        context_options=ContextOptions(
            user_id="user-001",
            workspace_id="workspace-001",
            project_id="project-001",
            session_id="session-001",
            request_id="request-001",
            source_stage="generated_script",
        ),
    )

    output = generate_short_drama_script_mock(input_data)

    assert output.metadata["context_policy"] == "current_project_only"
    assert output.metadata["context"]["user_id"] == "user-001"
    assert output.metadata["context"]["workspace_id"] == "workspace-001"
    assert output.metadata["context"]["project_id"] == "project-001"
    assert output.metadata["context"]["session_id"] == "session-001"
    assert output.metadata["context"]["request_id"] == "request-001"
    assert output.metadata["context"]["source_stage"] == "generated_script"
    assert "source_text" not in output.metadata


def test_generate_short_drama_script_mock_idea_attaches_usage_ledger_metadata():
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        genre="悬疑短剧",
        style="强钩子、快节奏",
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="script_generation",
        ),
        context_options=ContextOptions(
            user_id="user-usage-001",
            workspace_id="workspace-usage-001",
            project_id="project-usage-001",
            session_id="session-usage-001",
            request_id="request-usage-001",
            source_stage="generated_script",
        ),
    )

    output = generate_short_drama_script_mock(input_data)
    usage_ledger = output.metadata["usage_ledger"]

    assert usage_ledger["operation"] == "script_generation"
    assert usage_ledger["status"] == "success"
    assert usage_ledger["context"]["project_id"] == "project-usage-001"
    assert usage_ledger["context"]["session_id"] == "session-usage-001"
    assert usage_ledger["provider"] == "deepseek"
    assert usage_ledger["model"] == "deepseek-chat"
    assert usage_ledger["purpose"] == "script_generation"
    assert usage_ledger["source_mode"] == "idea"
    assert usage_ledger["source_stage"] == "generated_script"
    assert usage_ledger["request_id"] == "request-usage-001"


def test_generate_short_drama_script_mock_idea_persists_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="script_generation",
        ),
        context_options=ContextOptions(
            user_id="user-usage-idea",
            workspace_id="workspace-usage",
            project_id="project-usage-idea",
            session_id="session-usage-idea",
            request_id="request-usage-idea",
            source_stage="generated_script",
        ),
    )

    generate_short_drama_script_mock(input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request-usage-idea")

    assert stored is not None
    assert stored.operation == "script_generation"
    assert stored.status == "success"
    assert stored.source_mode == "idea"
    assert stored.user_id == "user-usage-idea"
    assert stored.workspace_id == "workspace-usage"
    assert stored.project_id == "project-usage-idea"
    assert stored.session_id == "session-usage-idea"
    assert stored.provider == "deepseek"
    assert stored.model == "deepseek-chat"
    assert stored.purpose == "script_generation"
    assert stored.input_character_count == len("雨夜里，女主收到一封来自十年前的信。")
    assert stored.output_character_count is not None
    assert stored.output_character_count > 0
    assert stored.metadata_json is not None
    assert "source_text" not in stored.metadata_json
    assert "idea_text" not in stored.metadata_json
    assert "沈知远" not in stored.metadata_json
    assert "第1集：归来线索" not in stored.metadata_json


def test_generate_short_drama_script_mock_idea_creates_project_and_session_ownership() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        context_options=ContextOptions(
            user_id="user-ownership-idea",
            workspace_id="workspace-ownership",
            project_id="project-ownership-idea",
            session_id="session-ownership-idea",
            request_id="request-ownership-idea",
            source_stage="generated_script",
        ),
    )

    output = generate_short_drama_script_mock(input_data)
    repository = get_ownership_repository()
    project = repository.get_project("project-ownership-idea")
    session = repository.get_session("session-ownership-idea")

    assert project is not None
    assert project.workspace_id == "workspace-ownership"
    assert project.owner_user_id == "user-ownership-idea"
    assert project.source_mode == "idea"
    assert session is not None
    assert session.project_id == "project-ownership-idea"
    assert session.user_id == "user-ownership-idea"
    assert output.metadata["ownership"]["project_id"] == "project-ownership-idea"
    assert output.metadata["ownership"]["session_id"] == "session-ownership-idea"
    assert "雨夜里，女主收到一封来自十年前的信。" not in (project.metadata_json or "")


def test_generate_short_drama_script_usage_ledger_does_not_include_source_or_output_body():
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="雨夜里，女主收到一封来自十年前的信。",
        target_episode_count=3,
        context_options=ContextOptions(request_id="request-safe-usage"),
    )

    output = generate_short_drama_script_mock(input_data)
    usage_ledger_text = str(output.metadata["usage_ledger"])

    assert "source_text" not in usage_ledger_text
    assert "idea_text" not in usage_ledger_text
    assert "沈知远" not in usage_ledger_text
    assert "第1集：归来线索" not in usage_ledger_text
    assert "雨夜里，女主收到一封来自十年前的信。" not in usage_ledger_text


def test_generate_short_drama_script_mock_for_film_script_dispatches_to_film_mock():
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        project_title="旧片场改编测试",
        source_text="虚构电影剧本片段。",
        target_episode_count=4,
    )

    output = generate_short_drama_script_mock(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "film_script"
    assert output.episode_count == 4
    assert len(output.episodes) == 4
    assert output.metadata["usage_ledger"]["operation"] == "film_adaptation"


def test_generate_short_drama_script_mock_for_film_script_persists_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        project_title="旧片场改编测试",
        source_text="虚构电影剧本片段。",
        target_episode_count=4,
        context_options=ContextOptions(request_id="request-usage-film"),
    )

    generate_short_drama_script_mock(input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request-usage-film")

    assert stored is not None
    assert stored.operation == "film_adaptation"
    assert stored.status == "success"
    assert stored.source_mode == "film_script"
    assert stored.input_character_count == len("虚构电影剧本片段。")
    assert stored.metadata_json is not None
    assert "虚构电影剧本片段" not in stored.metadata_json


def test_generate_short_drama_script_mock_for_film_script_creates_ownership() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        project_title="旧片场改编测试",
        source_text="虚构电影剧本片段。",
        target_episode_count=4,
        context_options=ContextOptions(
            project_id="project-ownership-film",
            session_id="session-ownership-film",
        ),
    )

    output = generate_short_drama_script_mock(input_data)
    repository = get_ownership_repository()
    project = repository.get_project("project-ownership-film")
    session = repository.get_session("session-ownership-film")

    assert project is not None
    assert project.source_mode == "film_script"
    assert session is not None
    assert session.project_id == "project-ownership-film"
    assert output.metadata["ownership"]["project_id"] == "project-ownership-film"


def test_generate_short_drama_script_mock_for_novel_dispatches_to_novel_mock():
    input_data = ShortDramaGenerationInput(
        source_mode="novel",
        project_title="旧书店改编测试",
        source_text="虚构小说片段。",
        target_episode_count=4,
    )

    output = generate_short_drama_script_mock(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "novel"
    assert output.episode_count == 4
    assert len(output.episodes) == 4
    assert output.metadata["usage_ledger"]["operation"] == "novel_adaptation"


def test_generate_short_drama_script_mock_for_novel_persists_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="novel",
        project_title="旧书店改编测试",
        source_text="虚构小说片段。",
        target_episode_count=4,
        context_options=ContextOptions(request_id="request-usage-novel"),
    )

    generate_short_drama_script_mock(input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request-usage-novel")

    assert stored is not None
    assert stored.operation == "novel_adaptation"
    assert stored.status == "success"
    assert stored.source_mode == "novel"
    assert stored.input_character_count == len("虚构小说片段。")
    assert stored.metadata_json is not None
    assert "虚构小说片段" not in stored.metadata_json


def test_generate_short_drama_script_mock_for_novel_creates_ownership() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="novel",
        project_title="旧书店改编测试",
        source_text="虚构小说片段。",
        target_episode_count=4,
        context_options=ContextOptions(
            project_id="project-ownership-novel",
            session_id="session-ownership-novel",
        ),
    )

    output = generate_short_drama_script_mock(input_data)
    repository = get_ownership_repository()
    project = repository.get_project("project-ownership-novel")
    session = repository.get_session("session-ownership-novel")

    assert project is not None
    assert project.source_mode == "novel"
    assert session is not None
    assert session.project_id == "project-ownership-novel"
    assert output.metadata["ownership"]["session_id"] == "session-ownership-novel"


def test_generate_short_drama_script_mock_rejects_assistant_rewrite_source_mode():
    input_data = ShortDramaGenerationInput(
        source_mode="assistant_rewrite",
        source_text="虚构改写文本。",
    )

    with pytest.raises(NotImplementedError, match="Assistant module"):
        generate_short_drama_script_mock(input_data)


def test_generate_short_drama_script_mock_rejects_uploaded_document_source_mode():
    input_data = ShortDramaGenerationInput(
        source_mode="uploaded_document",
        source_text="虚构上传文本。",
    )

    with pytest.raises(NotImplementedError, match="Document Import"):
        generate_short_drama_script_mock(input_data)


def test_generate_short_drama_script_contract_failure_persists_failed_usage_ledger(
    monkeypatch,
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")

    def fake_generate_film_script_adaptation_llm(input_data):
        return ShortDramaScriptOutput(
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
        )

    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_film_script_adaptation_llm",
        fake_generate_film_script_adaptation_llm,
    )
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="安全虚构电影剧本片段。",
        target_episode_count=3,
        context_options=ContextOptions(
            request_id="request-usage-contract-failed",
            project_id="project-contract-test",
            session_id="session-contract-test",
        ),
    )

    with pytest.raises(ScriptGenerationContractError):
        generate_short_drama_script(input_data)

    stored = isolated_usage_ledger_repository.get_entry_by_request_id(
        "request-usage-contract-failed"
    )

    assert stored is not None
    assert stored.operation == "film_adaptation"
    assert stored.status == "failed"
    assert stored.source_mode == "film_script"
    assert stored.project_id == "project-contract-test"
    assert stored.session_id == "session-contract-test"
    assert stored.error_code == "script_generation_contract_failed"
    assert stored.error_message_safe is not None
    assert "requested=3" in stored.error_message_safe
    stored_text = str(stored)
    assert "source_text" not in stored_text
    assert "安全虚构电影剧本片段" not in stored_text


def test_generate_short_drama_script_mock_idea_requires_idea_text():
    input_data = ShortDramaGenerationInput(source_mode="idea")

    with pytest.raises(ValueError, match="requires idea_text"):
        generate_short_drama_script_mock(input_data)
