from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings
from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript, ScriptOutput
from app.schemas.script_generation import AIRequestOptions, ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation.generator import (
    generate_idea_short_drama_script_llm,
    generate_short_drama_script,
    generate_short_drama_script_mock,
)


def make_fake_script_output() -> ScriptOutput:
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
        episodes=[
            EpisodeScript(
                episode_number=1,
                title="第1集：归来",
                summary="沈知远回到公司，发现许竞正在推动疑似抄袭的新项目。",
                hook="沈知远在旧硬盘里发现当年被篡改的署名记录。",
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
        ],
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
    assert output.episode_count == 1
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
            episodes=[],
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
            episodes=[],
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
