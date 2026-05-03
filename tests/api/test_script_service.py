from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.idea import IdeaInput
from app.schemas.script import ScriptOutput
from app.services.script_service import generate_script_mock


def make_idea_input(**overrides) -> IdeaInput:
    data = {
        "idea_text": "一个被裁员的中年男人发现公司老板用 AI 伪造财报",
        "script_type": "短剧",
        "genre": "都市悬疑",
        "episode_count": 1,
        "episode_duration": "3-5分钟",
        "target_platform": "短视频平台",
        "tone": "节奏快、反转强",
        "audience": "短剧观众",
        "style_requirements": "开头强冲突，结尾反转",
    }
    data.update(overrides)
    return IdeaInput(**data)


def test_generate_script_mock_episode_count_one_returns_one_episode() -> None:
    output = generate_script_mock(make_idea_input(episode_count=1))

    assert isinstance(output, ScriptOutput)
    assert len(output.episodes) == 1
    assert output.episodes[0].episode_number == 1
    assert output.episodes[0].scenes


def test_generate_script_mock_episode_count_four_returns_four_episodes() -> None:
    output = generate_script_mock(make_idea_input(episode_count=4))

    assert len(output.episodes) == 4
    assert [episode.episode_number for episode in output.episodes] == [1, 2, 3, 4]


def test_generate_script_mock_episode_titles_and_summaries_reflect_episode_number() -> None:
    output = generate_script_mock(make_idea_input(episode_count=4))

    for episode in output.episodes:
        assert f"第{episode.episode_number}集" in episode.title
        assert f"第{episode.episode_number}集" in episode.summary
        assert episode.scenes[0].scene_number == 1
