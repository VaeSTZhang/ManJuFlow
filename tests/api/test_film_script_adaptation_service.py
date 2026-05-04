from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript
from app.schemas.script_generation import (
    AIRequestOptions,
    AdaptationNotes,
    ShortDramaGenerationInput,
    ShortDramaScriptOutput,
)
from app.services.script_generation import (  # noqa: E402
    generate_film_script_adaptation_llm,
    generate_film_script_adaptation_mock,
    load_film_script_prompt_template,
)


def make_film_input(**overrides) -> ShortDramaGenerationInput:
    data = {
        "project_title": "旧片场最后一镜",
        "source_mode": "film_script",
        "source_text": "虚构电影剧本片段：女主回到废弃片场，发现父亲未完成的最后一镜。",
        "target_episode_count": 4,
        "adaptation_goal": "改成强钩子、快节奏短剧。",
        "key_plot_must_keep": "父亲遗作、废弃片场、制片人隐藏旧案。",
    }
    data.update(overrides)
    return ShortDramaGenerationInput(**data)


def make_fake_film_output_json() -> str:
    output = ShortDramaScriptOutput(
        project_title="旧片场复仇夜",
        source_mode="film_script",
        logline="女演员回到废弃片场追查父亲失踪真相，却发现制片人正利用遗作掩盖旧案。",
        world_setting="现代都市边缘的废弃片场，旧电影工业和家族悬疑交织。",
        characters=[
            CharacterProfile(
                name="许映",
                role="女主角，回到片场的演员",
                age="29",
                personality="敏感、倔强、行动果断",
                arc="从逃避父亲遗作到主动追查旧案。",
            ),
            CharacterProfile(
                name="周祁",
                role="制片人，旧案知情人",
                age="35",
                personality="圆滑、克制、藏有秘密",
                arc="从阻止许映开机到被迫面对真相。",
            ),
        ],
        adaptation_notes=AdaptationNotes(
            source_mode="film_script",
            adaptation_strategy="压缩电影长铺垫，以废弃片场和父亲遗作为短剧主线。",
            preserved_elements=["废弃片场", "父亲遗作", "制片人隐藏旧案"],
            changed_elements=["提前反派压迫", "合并支线人物"],
            short_drama_hooks=["每集一个道具线索", "每集结尾反转"],
            risk_notes=["输入为虚构片段，后续需人工确认完整改编方向。"],
        ),
        episode_count=1,
        episodes=[
            EpisodeScript(
                episode_number=1,
                title="第1集：最后一镜",
                summary="许映回到废弃片场，发现父亲遗作的关键道具被人重新摆好。",
                hook="旧摄影机突然亮起，画面里出现周祁当年的身影。",
                scenes=[
                    SceneScript(
                        scene_number=1,
                        location="废弃片场主棚",
                        time="午夜",
                        description="许映进入主棚，与阻止她开机的周祁正面对峙。",
                        dialogues=[
                            DialogueLine(character="许映", line="这台摄影机，为什么还会自己亮起来？"),
                            DialogueLine(character="周祁", line="你不该回来，更不该碰你父亲的东西。"),
                        ],
                        visual_notes="旧摄影机做前景，周祁从暗处走出。",
                        emotion_curve="试探→对峙→反转",
                    )
                ],
            )
        ],
        metadata={"source": "fake-film-llm"},
    )

    return output.model_dump_json()


class FakeFilmLLMClient:
    calls: list[dict[str, str | None]] = []

    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        self.provider = provider
        self.model = model
        self.calls.append({"provider": provider, "model": model})

    def chat(self, messages: list[dict[str, str]]) -> str:
        assert "film_script_to_short_drama_v1" in messages[0]["content"]
        assert "source_text" in messages[1]["content"]
        return make_fake_film_output_json()


def test_load_film_script_prompt_template_reads_prompt() -> None:
    prompt = load_film_script_prompt_template()

    assert "film_script" in prompt
    assert "ShortDramaScriptOutput" in prompt


def test_generate_film_script_adaptation_mock_returns_short_drama_output() -> None:
    output = generate_film_script_adaptation_mock(make_film_input())

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.project_title == "旧片场最后一镜"


def test_generate_film_script_adaptation_mock_uses_film_source_mode() -> None:
    output = generate_film_script_adaptation_mock(make_film_input())

    assert output.source_mode == "film_script"


def test_generate_film_script_adaptation_mock_matches_target_episode_count() -> None:
    output = generate_film_script_adaptation_mock(make_film_input(target_episode_count=6))

    assert output.episode_count == 6
    assert len(output.episodes) == 6


def test_generate_film_script_adaptation_mock_episode_numbers_increment() -> None:
    output = generate_film_script_adaptation_mock(make_film_input(target_episode_count=4))

    assert [episode.episode_number for episode in output.episodes] == [1, 2, 3, 4]


def test_generate_film_script_adaptation_mock_each_episode_has_scene_and_dialogues() -> None:
    output = generate_film_script_adaptation_mock(make_film_input(target_episode_count=3))

    for episode in output.episodes:
        assert len(episode.scenes) >= 1
        assert len(episode.scenes[0].dialogues) >= 2


def test_generate_film_script_adaptation_mock_has_adaptation_notes() -> None:
    output = generate_film_script_adaptation_mock(make_film_input())

    assert output.adaptation_notes is not None
    assert output.adaptation_notes.source_mode == "film_script"
    assert output.adaptation_notes.adaptation_strategy is not None
    assert len(output.adaptation_notes.short_drama_hooks) > 0


def test_generate_film_script_adaptation_mock_metadata_marks_mock_generation() -> None:
    output = generate_film_script_adaptation_mock(make_film_input())

    assert output.metadata["generation_mode"] == "mock"
    assert output.metadata["source_mode"] == "film_script"
    assert output.metadata["prompt_template_name"] == "film_script_to_short_drama_v1.md"
    assert output.metadata["context_policy"] == "current_project_only"


def test_generate_film_script_adaptation_mock_records_ai_options_metadata() -> None:
    output = generate_film_script_adaptation_mock(
        make_film_input(
            ai_options=AIRequestOptions(
                provider="mimo",
                model="mimo-v2.5-pro",
                purpose="film_adaptation",
            )
        )
    )

    assert output.metadata["ai_options"]["purpose"] == "film_adaptation"
    assert output.metadata["provider"] == "mimo"
    assert output.metadata["model"] == "mimo-v2.5-pro"
    assert output.metadata["purpose"] == "film_adaptation"


def test_generate_film_script_adaptation_llm_returns_short_drama_output(monkeypatch) -> None:
    FakeFilmLLMClient.calls = []
    monkeypatch.setattr(
        "app.services.script_generation.film_adaptation.LLMClient",
        FakeFilmLLMClient,
    )
    input_data = make_film_input(
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="film_adaptation",
        ),
        metadata={"source_title": "虚构电影片段"},
    )

    output = generate_film_script_adaptation_llm(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "film_script"
    assert output.project_title == "旧片场复仇夜"
    assert output.metadata["generation_mode"] == "llm"
    assert output.metadata["provider"] == "deepseek"
    assert output.metadata["model"] == "deepseek-chat"
    assert output.metadata["purpose"] == "film_adaptation"
    assert output.metadata["source_title"] == "虚构电影片段"
    assert "source_text" not in output.metadata
    assert FakeFilmLLMClient.calls == [{"provider": "deepseek", "model": "deepseek-chat"}]


def test_generate_film_script_adaptation_llm_requires_source_text() -> None:
    with pytest.raises(ValueError, match="requires source_text"):
        generate_film_script_adaptation_llm(make_film_input(source_text=""))


def test_generate_film_script_adaptation_llm_rejects_non_film_source_mode() -> None:
    with pytest.raises(ValueError, match="only supports source_mode='film_script'"):
        generate_film_script_adaptation_llm(
            make_film_input(source_mode="idea", idea_text="一个旧片场悬疑故事。")
        )


def test_generate_film_script_adaptation_mock_rejects_non_film_source_mode() -> None:
    with pytest.raises(ValueError) as exc_info:
        generate_film_script_adaptation_mock(
            make_film_input(source_mode="idea", idea_text="一个旧片场悬疑故事。")
        )

    assert "only supports source_mode='film_script'" in str(exc_info.value)
