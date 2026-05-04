from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation import (  # noqa: E402
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


def test_generate_novel_adaptation_mock_rejects_non_novel_source_mode() -> None:
    with pytest.raises(ValueError) as exc_info:
        generate_novel_adaptation_mock(
            make_novel_input(source_mode="idea", idea_text="一个旧书店悬疑故事。")
        )

    assert "only supports source_mode='novel'" in str(exc_info.value)
