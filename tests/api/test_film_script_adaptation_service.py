from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation import (  # noqa: E402
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


def test_generate_film_script_adaptation_mock_rejects_non_film_source_mode() -> None:
    with pytest.raises(ValueError) as exc_info:
        generate_film_script_adaptation_mock(
            make_film_input(source_mode="idea", idea_text="一个旧片场悬疑故事。")
        )

    assert "only supports source_mode='film_script'" in str(exc_info.value)
