from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript
from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation.validation import (
    ScriptGenerationContractError,
    resolve_target_episode_count,
    validate_target_episode_count_contract,
)


def make_episode(episode_number: int) -> EpisodeScript:
    return EpisodeScript(
        episode_number=episode_number,
        title=f"第{episode_number}集：旧楼线索",
        summary="角色发现新的虚构线索，冲突继续升级。",
        hook="她翻开下一页，发现自己的名字出现在剧本里。",
        scenes=[
            SceneScript(
                scene_number=1,
                location="旧楼走廊",
                time="夜晚",
                description="角色在旧楼走廊里发现一页遗落剧本。",
                dialogues=[
                    DialogueLine(character="林灯", line="这不是我写的结局。"),
                    DialogueLine(character="周岚", line="可它知道你今晚会回来。"),
                ],
                visual_notes="低成本旧楼场景，竖屏近景突出纸页和人物表情。",
                emotion_curve="疑惑→紧张→反转",
            )
        ],
    )


def make_output(
    *,
    episode_count: int = 3,
    episode_numbers: list[int] | None = None,
) -> ShortDramaScriptOutput:
    numbers = episode_numbers or [1, 2, 3]
    return ShortDramaScriptOutput(
        project_title="测试短剧：旧楼灯火",
        source_mode="film_script",
        logline="年轻编剧回到旧楼，发现一份遗稿预告了项目被盗真相。",
        world_setting="当代都市旧楼与影视公司之间，创作署名和家庭秘密交织。",
        characters=[
            CharacterProfile(
                name="林灯",
                role="主角，回到旧楼的短剧编剧",
                age="29",
                personality="冷静、敏锐、执拗",
                arc="从逃避旧楼真相到主动完成父亲留下的最后一场戏。",
            )
        ],
        adaptation_notes=None,
        episode_count=episode_count,
        episodes=[make_episode(number) for number in numbers],
        metadata={"provider": "deepseek", "model": "deepseek-chat"},
    )


def make_input_with_target(target_episode_count: int = 3) -> ShortDramaGenerationInput:
    return ShortDramaGenerationInput(
        source_mode="film_script",
        project_title="测试短剧：旧楼灯火",
        source_text="安全虚构电影剧本片段。",
        target_episode_count=target_episode_count,
    )


def make_input_with_adaptation_target(
    source_mode: str = "film_script",
    target_episode_count: int = 3,
) -> ShortDramaGenerationInput:
    return ShortDramaGenerationInput(
        source_mode=source_mode,
        project_title="测试短剧：旧楼灯火",
        source_text="安全虚构改编来源片段。",
        adaptation_notes={"target_episode_count": target_episode_count},
    )


def test_resolve_target_episode_count_reads_explicit_top_level_target():
    input_data = make_input_with_target(4)

    assert resolve_target_episode_count(input_data) == 4


def test_resolve_target_episode_count_reads_adaptation_notes_target():
    input_data = make_input_with_adaptation_target("film_script", 3)

    assert resolve_target_episode_count(input_data) == 3


def test_resolve_target_episode_count_prefers_explicit_top_level_target():
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="安全虚构改编来源片段。",
        target_episode_count=4,
        adaptation_notes={"target_episode_count": 3},
    )

    assert resolve_target_episode_count(input_data) == 4


def test_resolve_target_episode_count_rejects_invalid_adaptation_notes_target():
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        source_text="安全虚构改编来源片段。",
        adaptation_notes={"target_episode_count": 0},
    )

    with pytest.raises(ScriptGenerationContractError, match="positive integer"):
        resolve_target_episode_count(input_data)


def test_validate_target_episode_count_contract_accepts_matching_output():
    input_data = make_input_with_target(3)
    output = make_output(episode_count=3, episode_numbers=[1, 2, 3])

    validated = validate_target_episode_count_contract(input_data, output)

    assert validated is output


def test_validate_target_episode_count_contract_rejects_episode_count_mismatch():
    input_data = make_input_with_target(3)
    output = make_output(episode_count=1, episode_numbers=[1, 2, 3])

    with pytest.raises(ValueError, match="requested=3, episode_count=1, episodes=3"):
        validate_target_episode_count_contract(input_data, output)


def test_validate_target_episode_count_contract_rejects_idea_one_episode_when_target_is_three():
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text="安全虚构灵感。",
        target_episode_count=3,
    )
    output = make_output(episode_count=1, episode_numbers=[1])

    with pytest.raises(ValueError, match="requested=3, episode_count=1, episodes=1"):
        validate_target_episode_count_contract(input_data, output)


def test_validate_target_episode_count_contract_rejects_film_adaptation_notes_target_mismatch():
    input_data = make_input_with_adaptation_target("film_script", 3)
    output = make_output(episode_count=1, episode_numbers=[1])

    with pytest.raises(ValueError, match="requested=3, episode_count=1, episodes=1"):
        validate_target_episode_count_contract(input_data, output)


def test_validate_target_episode_count_contract_rejects_novel_adaptation_notes_target_mismatch():
    input_data = make_input_with_adaptation_target("novel", 3)
    output = make_output(episode_count=1, episode_numbers=[1])

    with pytest.raises(ValueError, match="requested=3, episode_count=1, episodes=1"):
        validate_target_episode_count_contract(input_data, output)


def test_validate_target_episode_count_contract_rejects_episode_length_mismatch():
    input_data = make_input_with_target(3)
    output = make_output(episode_count=3, episode_numbers=[1])

    with pytest.raises(ValueError, match="requested=3, episode_count=3, episodes=1"):
        validate_target_episode_count_contract(input_data, output)


def test_validate_target_episode_count_contract_rejects_non_continuous_episode_numbers():
    input_data = make_input_with_target(3)
    output = make_output(episode_count=3, episode_numbers=[1, 3, 4])

    with pytest.raises(ValueError, match=r"episode_numbers=\[1, 3, 4\]"):
        validate_target_episode_count_contract(input_data, output)


def test_validate_target_episode_count_contract_skips_when_target_not_explicitly_provided():
    input_data = ShortDramaGenerationInput(
        source_mode="film_script",
        project_title="测试短剧：旧楼灯火",
        source_text="安全虚构电影剧本片段。",
    )
    output = make_output(episode_count=5, episode_numbers=[1, 2, 3, 4, 5])

    validated = validate_target_episode_count_contract(input_data, output)

    assert validated is output


def test_validate_target_episode_count_contract_error_omits_source_and_provider_payload():
    input_data = make_input_with_target(3)
    output = make_output(episode_count=1, episode_numbers=[1])

    with pytest.raises(ValueError) as exc_info:
        validate_target_episode_count_contract(input_data, output)

    message = str(exc_info.value)
    assert "安全虚构电影剧本片段" not in message
    assert "source_text" not in message
    assert "provider" not in message
    assert "deepseek-chat" not in message
