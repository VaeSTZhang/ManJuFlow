import json
from pathlib import Path

from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript
from app.schemas.script_generation import (
    AdaptationNotes,
    ShortDramaGenerationInput,
    ShortDramaScriptOutput,
)
from app.services.llm_client import LLMClient
from app.services.script_generation.metadata import build_script_generation_metadata
from app.services.script_generation.validation import resolve_target_episode_count
from app.services.text_cleaner import clean_chinese_spacing


FILM_SCRIPT_PROMPT_TEMPLATE_NAME = "film_script_to_short_drama_v1.md"


def load_film_script_prompt_template(
    template_name: str = FILM_SCRIPT_PROMPT_TEMPLATE_NAME,
) -> str:
    prompts_dir = Path(__file__).resolve().parents[2] / "prompts"
    prompt_path = prompts_dir / template_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Film script adaptation prompt file not found: {template_name}")

    return prompt_path.read_text(encoding="utf-8")


def _build_film_adaptation_characters() -> list[CharacterProfile]:
    return [
        CharacterProfile(
            name="许映",
            role="女主角，回到废弃片场的过气女演员",
            age="29",
            personality="敏感、倔强、外冷内热",
            arc="从逃避父亲遗作到主动追查失踪真相。",
        ),
        CharacterProfile(
            name="周祁",
            role="制片人，也是父亲旧案知情人",
            age="35",
            personality="圆滑、克制、藏有秘密",
            arc="从阻止许映开机到被迫面对当年旧案。",
        ),
    ]


def _build_film_adaptation_episode(episode_number: int) -> EpisodeScript:
    clue_names = ["摄影机", "旧皮箱", "场记板", "破损胶片", "道具戒指"]
    clue = clue_names[(episode_number - 1) % len(clue_names)]

    return EpisodeScript(
        episode_number=episode_number,
        title=f"第{episode_number}集：{clue}里的线索",
        summary=(
            f"许映在废弃片场追查父亲未完成的最后一镜，"
            f"第{episode_number}个关键道具“{clue}”暴露出旧案的新矛盾。"
        ),
        hook=f"{clue}中出现一条指向周祁的旧线索，许映发现父亲当年可能不是意外失踪。",
        scenes=[
            SceneScript(
                scene_number=1,
                location="废弃片场主棚",
                time="午夜",
                description=(
                    f"许映按照父亲遗留剧本进入主棚，发现{clue}被摆在摄影机前。"
                    "周祁试图阻止她继续拍摄，两人在冷光和灰尘中对峙。"
                ),
                dialogues=[
                    DialogueLine(
                        character="许映",
                        line=f"这个{clue}，为什么会出现在我爸最后一场戏里？",
                    ),
                    DialogueLine(
                        character="周祁",
                        line="你再查下去，只会把当年所有人都拖回来。",
                    ),
                ],
                visual_notes=(
                    "竖屏中景，许映站在旧摄影机前，周祁从暗处压近，"
                    "道具作为前景形成悬疑焦点，适合低成本片场拍摄。"
                ),
                emotion_curve="试探→对峙→反转",
            )
        ],
    )


def generate_film_script_adaptation_mock(
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    if input_data.source_mode != "film_script":
        raise ValueError("generate_film_script_adaptation_mock only supports source_mode='film_script'.")

    load_film_script_prompt_template()

    project_title = input_data.project_title or "旧片场最后一镜"
    episode_count = resolve_target_episode_count(input_data) or input_data.target_episode_count
    episodes = [
        _build_film_adaptation_episode(episode_number)
        for episode_number in range(1, episode_count + 1)
    ]
    metadata = build_script_generation_metadata(input_data)
    metadata.update(
        {
            "prompt_template_name": FILM_SCRIPT_PROMPT_TEMPLATE_NAME,
        }
    )

    return ShortDramaScriptOutput(
        project_title=project_title,
        source_mode="film_script",
        logline="过气女演员回到废弃片场拍完父亲遗作，却发现每个道具都指向父亲失踪案的真相。",
        world_setting="现代都市边缘的废弃片场，旧电影工业遗迹与家族悬疑交织。",
        characters=_build_film_adaptation_characters(),
        adaptation_notes=AdaptationNotes(
            source_mode="film_script",
            adaptation_strategy=(
                "将电影剧本中的慢铺垫改为短剧强事件推进，"
                "围绕废弃片场、父亲遗作和道具线索形成分集钩子。"
            ),
            preserved_elements=[
                "女主回到废弃片场",
                "父亲未完成的最后一镜",
                "制片人隐藏旧案",
            ],
            changed_elements=[
                "压缩事业低谷铺垫",
                "合并片场工作人员支线",
                "提前让摄影机自动亮起作为开场钩子",
            ],
            short_drama_hooks=[
                "每集一个道具线索",
                "每集结尾反转指向旧案真相",
                "制片人每次阻止都暴露新矛盾",
            ],
            risk_notes=[
                "需确认原始电影剧本或长剧本的合法改编授权。",
                "当前输出为 mock 改编草案，需人工确认。",
            ],
        ),
        episode_count=episode_count,
        episodes=episodes,
        metadata=metadata,
    )


def generate_film_script_adaptation_llm(
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    if input_data.source_mode != "film_script":
        raise ValueError("generate_film_script_adaptation_llm only supports source_mode='film_script'.")

    source_text = (input_data.source_text or "").strip()
    if not source_text:
        raise ValueError("source_mode='film_script' requires source_text.")

    prompt_template = load_film_script_prompt_template()
    input_payload = input_data.model_dump()
    input_payload["source_text"] = source_text
    input_json = json.dumps(input_payload, ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": prompt_template,
        },
        {
            "role": "user",
            "content": f"请根据以下输入生成结构化短剧改编 JSON：\n{input_json}",
        },
    ]

    provider = input_data.ai_options.provider if input_data.ai_options else None
    model = input_data.ai_options.model if input_data.ai_options else None
    content = LLMClient(provider=provider, model=model).chat(messages)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response was not valid JSON.") from exc

    cleaned_data = clean_chinese_spacing(data)

    try:
        output = ShortDramaScriptOutput.model_validate(cleaned_data)
    except ValueError as exc:
        raise ValueError("LLM response did not match ShortDramaScriptOutput schema.") from exc

    metadata = {
        **output.metadata,
        **build_script_generation_metadata(input_data, generation_mode="llm"),
        "prompt_template_name": FILM_SCRIPT_PROMPT_TEMPLATE_NAME,
    }
    source_title = input_data.metadata.get("source_title")
    if source_title:
        metadata["source_title"] = source_title

    return output.model_copy(update={"metadata": metadata})
