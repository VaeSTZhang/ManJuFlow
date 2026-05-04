from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation.generator import generate_short_drama_script_mock


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


def test_generate_short_drama_script_mock_idea_requires_idea_text():
    input_data = ShortDramaGenerationInput(source_mode="idea")

    with pytest.raises(ValueError, match="requires idea_text"):
        generate_short_drama_script_mock(input_data)
