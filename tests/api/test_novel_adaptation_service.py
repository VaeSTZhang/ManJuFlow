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
    generate_novel_adaptation_llm,
    generate_novel_adaptation_mock,
    load_novel_prompt_template,
)


def make_novel_input(**overrides) -> ShortDramaGenerationInput:
    data = {
        "project_title": "掌声背后的日记",
        "source_mode": "novel",
        "source_text": "虚构小说片段：女主在旧书店发现母亲日记，追查舞台事故真相。",
        "target_episode_count": 4,
        "adaptation_goal": "把小说叙事改成可拍的短剧剧本。",
        "main_characters": "沈南星、顾闻舟",
        "key_relationships": "女主与母亲旧案、管理员隐瞒真相。",
    }
    data.update(overrides)
    return ShortDramaGenerationInput(**data)


def make_fake_novel_output_json() -> str:
    output = ShortDramaScriptOutput(
        project_title="旧书店日记",
        source_mode="novel",
        logline="年轻编剧在旧书店发现母亲日记，追查被舞台掌声掩盖的事故真相。",
        world_setting="现代都市旧书店、废弃剧场和小型话剧团交织的悬疑情感世界。",
        characters=[
            CharacterProfile(
                name="沈南星",
                role="女主角，发现母亲日记的年轻编剧",
                age="25",
                personality="敏感、执拗、观察细致",
                arc="从逃避母亲旧事到主动揭开舞台事故真相。",
            ),
            CharacterProfile(
                name="顾闻舟",
                role="旧剧场管理员，掌握事故线索",
                age="32",
                personality="沉默、谨慎、内心有愧",
                arc="从隐瞒真相到帮助沈南星还原事故。",
            ),
        ],
        adaptation_notes=AdaptationNotes(
            source_mode="novel",
            adaptation_strategy="将小说心理描写外化为寻找日记线索、舞台对峙和短剧分集钩子。",
            preserved_elements=["母亲日记", "舞台事故", "顾闻舟隐藏线索"],
            changed_elements=["压缩书店背景", "合并旁支人物", "提前舞台事故线索"],
            short_drama_hooks=["每集揭开一页日记", "掌声录音中出现求救声"],
            risk_notes=["输入为虚构小说片段，后续需人工确认完整改编方向。"],
        ),
        episode_count=1,
        episodes=[
            EpisodeScript(
                episode_number=1,
                title="第1集：日记里的掌声",
                summary="沈南星在旧书店发现母亲日记，线索指向一场被隐藏的舞台事故。",
                hook="日记最后一页夹着一张旧剧场后台钥匙。",
                scenes=[
                    SceneScript(
                        scene_number=1,
                        location="旧书店后仓",
                        time="傍晚",
                        description="沈南星翻出母亲日记，顾闻舟突然出现阻止她继续阅读。",
                        dialogues=[
                            DialogueLine(character="沈南星", line="这本日记，为什么会写到你？"),
                            DialogueLine(character="顾闻舟", line="有些掌声，最好永远别再被听见。"),
                        ],
                        visual_notes="旧书堆和黄昏侧光包围人物，日记作为前景。",
                        emotion_curve="发现→追问→隐瞒",
                    )
                ],
            )
        ],
        metadata={"source": "fake-novel-llm"},
    )

    return output.model_dump_json()


class FakeNovelLLMClient:
    calls: list[dict[str, str | None]] = []

    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        self.provider = provider
        self.model = model
        self.calls.append({"provider": provider, "model": model})

    def chat(self, messages: list[dict[str, str]]) -> str:
        assert "novel_to_short_drama_v1" in messages[0]["content"]
        assert "source_text" in messages[1]["content"]
        return make_fake_novel_output_json()


def test_load_novel_prompt_template_reads_prompt() -> None:
    prompt = load_novel_prompt_template()

    assert "novel" in prompt
    assert "ShortDramaScriptOutput" in prompt


def test_generate_novel_adaptation_mock_returns_short_drama_output() -> None:
    output = generate_novel_adaptation_mock(make_novel_input())

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.project_title == "掌声背后的日记"


def test_generate_novel_adaptation_mock_uses_novel_source_mode() -> None:
    output = generate_novel_adaptation_mock(make_novel_input())

    assert output.source_mode == "novel"


def test_generate_novel_adaptation_mock_matches_target_episode_count() -> None:
    output = generate_novel_adaptation_mock(make_novel_input(target_episode_count=6))

    assert output.episode_count == 6
    assert len(output.episodes) == 6


def test_generate_novel_adaptation_mock_episode_numbers_increment() -> None:
    output = generate_novel_adaptation_mock(make_novel_input(target_episode_count=4))

    assert [episode.episode_number for episode in output.episodes] == [1, 2, 3, 4]


def test_generate_novel_adaptation_mock_each_episode_has_scene_and_dialogues() -> None:
    output = generate_novel_adaptation_mock(make_novel_input(target_episode_count=3))

    for episode in output.episodes:
        assert len(episode.scenes) >= 1
        assert len(episode.scenes[0].dialogues) >= 2


def test_generate_novel_adaptation_mock_has_novel_adaptation_notes() -> None:
    output = generate_novel_adaptation_mock(make_novel_input())

    assert output.adaptation_notes is not None
    assert output.adaptation_notes.source_mode == "novel"
    assert output.adaptation_notes.adaptation_strategy is not None
    assert any(
        keyword in output.adaptation_notes.adaptation_strategy
        for keyword in ["心理描写", "场景", "人物关系"]
    )


def test_generate_novel_adaptation_mock_metadata_marks_mock_generation() -> None:
    output = generate_novel_adaptation_mock(make_novel_input())

    assert output.metadata["generation_mode"] == "mock"
    assert output.metadata["source_mode"] == "novel"
    assert output.metadata["prompt_template_name"] == "novel_to_short_drama_v1.md"
    assert output.metadata["context_policy"] == "current_project_only"


def test_generate_novel_adaptation_mock_records_ai_options_metadata() -> None:
    output = generate_novel_adaptation_mock(
        make_novel_input(
            ai_options=AIRequestOptions(
                provider="kimi",
                model="kimi-k2.5",
                purpose="novel_adaptation",
            )
        )
    )

    assert output.metadata["ai_options"]["purpose"] == "novel_adaptation"
    assert output.metadata["provider"] == "kimi"
    assert output.metadata["model"] == "kimi-k2.5"
    assert output.metadata["purpose"] == "novel_adaptation"


def test_generate_novel_adaptation_llm_returns_short_drama_output(monkeypatch) -> None:
    FakeNovelLLMClient.calls = []
    monkeypatch.setattr(
        "app.services.script_generation.novel_adaptation.LLMClient",
        FakeNovelLLMClient,
    )
    input_data = make_novel_input(
        ai_options=AIRequestOptions(
            provider="deepseek",
            model="deepseek-chat",
            purpose="novel_adaptation",
        ),
        metadata={"source_title": "虚构小说片段"},
    )

    output = generate_novel_adaptation_llm(input_data)

    assert isinstance(output, ShortDramaScriptOutput)
    assert output.source_mode == "novel"
    assert output.project_title == "旧书店日记"
    assert output.metadata["generation_mode"] == "llm"
    assert output.metadata["provider"] == "deepseek"
    assert output.metadata["model"] == "deepseek-chat"
    assert output.metadata["purpose"] == "novel_adaptation"
    assert output.metadata["source_title"] == "虚构小说片段"
    assert output.metadata["prompt_template_name"] == "novel_to_short_drama_v1.md"
    assert output.metadata["context_policy"] == "current_project_only"
    assert "source_text" not in output.metadata
    assert FakeNovelLLMClient.calls == [{"provider": "deepseek", "model": "deepseek-chat"}]


def test_generate_novel_adaptation_llm_requires_source_text() -> None:
    with pytest.raises(ValueError, match="requires source_text"):
        generate_novel_adaptation_llm(make_novel_input(source_text=""))


def test_generate_novel_adaptation_llm_rejects_non_novel_source_mode() -> None:
    with pytest.raises(ValueError, match="only supports source_mode='novel'"):
        generate_novel_adaptation_llm(
            make_novel_input(source_mode="idea", idea_text="一个旧书店悬疑故事。")
        )


def test_generate_novel_adaptation_mock_rejects_non_novel_source_mode() -> None:
    with pytest.raises(ValueError) as exc_info:
        generate_novel_adaptation_mock(
            make_novel_input(source_mode="idea", idea_text="一个旧书店悬疑故事。")
        )

    assert "only supports source_mode='novel'" in str(exc_info.value)
