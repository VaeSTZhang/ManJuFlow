from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript
from app.schemas.context import ContextOptions
from app.schemas.script_generation import (
    AdaptationNotes,
    AIRequestOptions,
    ShortDramaGenerationInput,
    ShortDramaScriptOutput,
)


def make_character() -> CharacterProfile:
    return CharacterProfile(
        name="林棠",
        role="女主角，年轻编剧",
        age="26",
        personality="敏感、执拗、观察力强",
        arc="从逃避父亲旧案到主动追查真相。",
    )


def make_episode() -> EpisodeScript:
    return EpisodeScript(
        episode_number=1,
        title="旧剧本重现",
        summary="林棠在旧电影院发现父亲遗留剧本，意识到剧本与现实有关。",
        hook="放映机自动启动，银幕里出现父亲年轻时的影像。",
        scenes=[
            SceneScript(
                scene_number=1,
                location="旧电影院售票厅",
                time="雨夜",
                description="林棠抱着纸箱回到废弃电影院，准备烧掉父亲遗稿。",
                dialogues=[
                    DialogueLine(character="林棠", line="这些故事该结束了。"),
                ],
                visual_notes="雨水打在玻璃门上，售票厅只亮着一盏冷白灯。",
                emotion_curve="压抑、抗拒、惊疑。",
            )
        ],
    )


def test_short_drama_generation_input_defaults_to_idea_source_mode() -> None:
    input_data = ShortDramaGenerationInput(idea_text="一个编剧在旧电影院发现父亲遗稿。")

    assert input_data.source_mode == "idea"
    assert input_data.target_episode_count == 1
    assert input_data.genre == "短剧"
    assert input_data.language == "zh"


def test_short_drama_generation_input_idea_mode_can_use_idea_text() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        project_title="旧电影院",
        idea_text="一个编剧在旧电影院发现父亲遗稿。",
        target_episode_count=4,
    )

    assert input_data.source_mode == "idea"
    assert input_data.idea_text is not None
    assert input_data.target_episode_count == 4


def test_short_drama_generation_input_film_script_mode_can_use_source_text() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="【电影片段】女主回到废弃片场，发现父亲失踪线索。",
        target_episode_count=12,
    )

    assert input_data.source_mode == "film_script"
    assert input_data.source_text is not None
    assert input_data.target_episode_count == 12


def test_short_drama_generation_input_novel_mode_can_use_source_text() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="novel",
        source_text="雨停后的清晨，沈南星在旧书店发现一本日记。",
        key_relationships="女主与母亲的旧案关系",
    )

    assert input_data.source_mode == "novel"
    assert input_data.source_text is not None
    assert input_data.key_relationships == "女主与母亲的旧案关系"


def test_short_drama_generation_input_rejects_target_episode_count_below_minimum() -> None:
    with pytest.raises(ValidationError):
        ShortDramaGenerationInput(target_episode_count=0, idea_text="测试灵感")


def test_short_drama_generation_input_rejects_target_episode_count_above_maximum() -> None:
    with pytest.raises(ValidationError):
        ShortDramaGenerationInput(target_episode_count=101, idea_text="测试灵感")


def test_short_drama_generation_input_metadata_default_is_independent_dict() -> None:
    first_input = ShortDramaGenerationInput(idea_text="项目 A")
    second_input = ShortDramaGenerationInput(idea_text="项目 B")

    first_input.metadata["source"] = "test"

    assert second_input.metadata == {}


def test_short_drama_generation_input_can_omit_ai_options() -> None:
    input_data = ShortDramaGenerationInput(idea_text="一个编剧在旧电影院发现父亲遗稿。")

    assert input_data.ai_options is None


def test_short_drama_generation_input_accepts_ai_options_provider_and_model() -> None:
    input_data = ShortDramaGenerationInput(
        idea_text="一个编剧在旧电影院发现父亲遗稿。",
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="script_generation",
        ),
    )

    assert input_data.ai_options is not None
    assert input_data.ai_options.provider == "deepseek"
    assert input_data.ai_options.model == "deepseek-chat"
    assert input_data.ai_options.language == "zh"


def test_ai_request_options_rejects_temperature_out_of_range() -> None:
    with pytest.raises(ValidationError):
        AIRequestOptions(temperature=2.1)


@pytest.mark.parametrize("purpose", ["script_generation", "film_adaptation", "novel_adaptation"])
def test_ai_request_options_supports_script_creation_purposes(purpose: str) -> None:
    options = AIRequestOptions(purpose=purpose)

    assert options.purpose == purpose


def test_short_drama_generation_input_model_dump_contains_ai_options() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="虚构电影剧本片段。",
        ai_options=AIRequestOptions(
            provider="mimo",
            model="mimo-v2.5-pro",
            purpose="film_adaptation",
            temperature=0.7,
            max_tokens=1200,
        ),
    )

    dumped = input_data.model_dump()

    assert dumped["ai_options"]["provider"] == "mimo"
    assert dumped["ai_options"]["model"] == "mimo-v2.5-pro"
    assert dumped["ai_options"]["purpose"] == "film_adaptation"


def test_short_drama_generation_input_accepts_context_options() -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="虚构电影剧本片段。",
        context_options=ContextOptions(
            user_id="user-001",
            workspace_id="workspace-001",
            project_id="project-001",
            session_id="session-001",
            request_id="request-001",
            source_stage="draft",
        ),
    )

    assert input_data.context_options is not None
    assert input_data.context_options.project_id == "project-001"
    assert input_data.context_options.context_policy == "current_project_only"


def test_short_drama_generation_input_can_omit_context_options() -> None:
    input_data = ShortDramaGenerationInput(idea_text="一个编剧在旧电影院发现父亲遗稿。")

    assert input_data.context_options is None


def test_adaptation_notes_list_defaults_are_independent() -> None:
    first_notes = AdaptationNotes(source_mode="film_script")
    second_notes = AdaptationNotes(source_mode="film_script")

    first_notes.preserved_elements.append("父亲失踪主线")
    first_notes.short_drama_hooks.append("每集结尾出现新线索")

    assert second_notes.preserved_elements == []
    assert second_notes.short_drama_hooks == []
    assert second_notes.changed_elements == []
    assert second_notes.risk_notes == []


def test_short_drama_script_output_reuses_existing_character_and_episode_types() -> None:
    character = make_character()
    episode = make_episode()

    output = ShortDramaScriptOutput(
        project_title="旧电影院",
        source_mode="idea",
        logline="年轻编剧在旧电影院发现父亲遗留剧本，并被卷入旧案真相。",
        world_setting="现代都市，围绕废弃电影院和旧剧本展开。",
        characters=[character],
        episode_count=1,
        episodes=[episode],
    )

    assert isinstance(output.characters[0], CharacterProfile)
    assert isinstance(output.episodes[0], EpisodeScript)
    assert output.episodes[0].scenes[0].dialogues[0].character == "林棠"


def test_short_drama_script_output_model_dump_contains_core_fields() -> None:
    output = ShortDramaScriptOutput(
        project_title="旧电影院",
        source_mode="novel",
        logline="女主从一本日记追查母亲旧案。",
        world_setting="旧书店与城市剧场交织的悬疑世界。",
        characters=[make_character()],
        adaptation_notes=AdaptationNotes(
            source_mode="novel",
            adaptation_strategy="保留母女关系主线，增强每集结尾钩子。",
            preserved_elements=["母亲旧案", "旧日记"],
            changed_elements=["压缩旁支人物"],
            short_drama_hooks=["每集揭开一页日记"],
            risk_notes=["需确认小说改编授权"],
        ),
        episode_count=1,
        episodes=[make_episode()],
        metadata={"source": "schema_test"},
    )

    dumped = output.model_dump()

    assert dumped["source_mode"] == "novel"
    assert dumped["episode_count"] == 1
    assert len(dumped["episodes"]) == 1
    assert dumped["adaptation_notes"]["preserved_elements"] == ["母亲旧案", "旧日记"]


def test_short_drama_generation_input_rejects_invalid_source_mode() -> None:
    with pytest.raises(ValidationError):
        ShortDramaGenerationInput(source_mode="comic", source_text="测试文本")
